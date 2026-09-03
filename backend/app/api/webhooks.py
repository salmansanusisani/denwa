"""Real telephony webhook — the actual production entry point (spec Step 03-05).

This is NOT a customer-facing "simulate missed call" feature. It is the
endpoint Twilio calls when a real customer call to a real business number
goes unanswered.

Flow:
    Twilio POSTs form-encoded data
    -> verify X-Twilio-Signature (reject if invalid/missing)
    -> validate required fields are present
    -> ignore event types we don't care about (only no-answer / busy matter)
    -> dedupe on CallSid (Twilio's unique id for this call)
    -> normalize phone numbers
    -> resolve Company from the business number (`To`)
    -> persist TelephonyEvent + create CallJob(status="pending")
    -> enqueue the job for the worker
    -> always return 200 quickly (Twilio retries aggressively on non-2xx)

We MUST NOT do slow work (AI/ML retrieval, CALL-E calls) inside this
handler — that belongs to the worker (app/worker/callback_worker.py).
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from app.config import TWILIO_AUTH_TOKEN, WEBHOOK_SKIP_SIGNATURE_CHECK
from app.db.database import get_db
from app.db.models import CallJob, TelephonyEvent
from app.api.companies import get_company_by_business_number
from app.utils.phone import normalize_phone_number
from app.queue.job_queue import enqueue

logger = logging.getLogger("denwa.webhooks")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Twilio CallStatus values that represent a genuinely missed call.
# Everything else (completed, in-progress, ringing, ...) is ignored.
MISSED_CALL_STATUSES = {"no-answer", "busy", "failed"}


def _verify_twilio_signature(request: Request, form: dict) -> bool:
    """Validate the request actually came from Twilio."""
    if WEBHOOK_SKIP_SIGNATURE_CHECK:
        logger.warning("WEBHOOK_SKIP_SIGNATURE_CHECK is enabled — signature check bypassed. DEV ONLY.")
        return True

    if not TWILIO_AUTH_TOKEN:
        logger.error("TWILIO_AUTH_TOKEN is not configured; rejecting webhook.")
        return False

    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        return False

    # Reconstruct public URL if behind reverse proxy / ngrok tunnel
    url = str(request.url)
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if forwarded_proto and forwarded_host:
        path_and_query = request.url.path
        if request.url.query:
            path_and_query += f"?{request.url.query}"
        url = f"{forwarded_proto}://{forwarded_host}{path_and_query}"

    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(url, form, signature)
@router.post("/telephony")
async def telephony_webhook(request: Request, db: Session = Depends(get_db)):
    form = dict((await request.form()).items())

    # --- 1. Authenticity ---------------------------------------------------
    if not _verify_twilio_signature(request, form):
        logger.warning("Rejected webhook: invalid or missing Twilio signature.")
        # 403, not 500 - this is an auth failure, not a server error.
        return Response(status_code=403, content="Invalid signature")

    # --- 2. Payload validation ----------------------------------------------
    call_sid = form.get("CallSid")
    from_number = form.get("From")
    to_number = form.get("To")
    call_status = form.get("CallStatus")

    if not all([call_sid, from_number, to_number, call_status]):
        logger.warning("Rejected webhook: missing required fields. Payload keys=%s", list(form.keys()))
        return Response(status_code=400, content="Missing required fields")

    # --- 3. Event-type filter -----------------------------------------------
    # Twilio calls this webhook for every status change (ringing, answered,
    # completed, ...), not just missed calls. We only act on missed calls;
    # anything else is acknowledged and dropped.
    if call_status not in MISSED_CALL_STATUSES:
        return Response(status_code=200, content="Ignored: not a missed-call status")

    # --- 4. Idempotency / dedup ---------------------------------------------
    # Twilio may redeliver the same event (retries, duplicate status
    # callbacks). CallSid is Twilio's unique id for the call, so it's our
    # dedup key, one CallSid must never produce more than one CallJob.
    existing = db.query(TelephonyEvent).filter(TelephonyEvent.provider_event_id == call_sid).first()
    if existing is not None:
        logger.info("Duplicate webhook for CallSid=%s — ignoring.", call_sid)
        return Response(status_code=200, content="Duplicate event, already processed")

    # --- 5. Normalize numbers ------------------------------------------------
    normalized_caller = normalize_phone_number(from_number)
    normalized_business = normalize_phone_number(to_number)
    if normalized_caller is None or normalized_business is None:
        logger.warning(
            "Rejected webhook: unparseable phone numbers. From=%s To=%s", from_number, to_number
        )
        # 200: this is a data problem on the provider/caller side, not
        # something Twilio should retry.
        return Response(status_code=200, content="Unparseable phone numbers")

    # --- 6. Company routing ---------------------------------------------------
    company = get_company_by_business_number(db, normalized_business)
    if company is None:
        logger.warning("No company found for business_number=%s (CallSid=%s)", normalized_business, call_sid)
        return Response(status_code=200, content="Unknown business number")

    # --- 7. Persist event + create job ----------------------------------------
    occurred_at = datetime.now(timezone.utc)

    telephony_event = TelephonyEvent(
        provider_event_id=call_sid,
        company_id=company.id,
        business_number=normalized_business,
        caller_number=normalized_caller,
        event_type=call_status,
        occurred_at=occurred_at,
    )
    db.add(telephony_event)

    call_job = CallJob(
        company_id=company.id,
        caller_number=normalized_caller,
        status="pending",
    )
    db.add(call_job)

    db.commit()
    db.refresh(call_job)

    # --- 8. Enqueue for the worker ----------------------------------------------
    enqueue(call_job.id)

    logger.info(
        "Created CallJob id=%s for company_id=%s from CallSid=%s", call_job.id, company.id, call_sid
    )
    return Response(status_code=200, content="Callback job created")
