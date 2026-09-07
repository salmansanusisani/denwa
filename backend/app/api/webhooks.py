"""Real telephony webhook -  the actual production entry point (spec Step 03-05).

This is NOT a customer-facing "simulate missed call" feature. It is the
endpoint Telnyx calls for real call state changes on our business number.

Provider: Telnyx Call Control API (v2).

IMPORTANT / NOT YET FULLY VERIFIED:
Telnyx's exact set of `hangup_cause` values for a "call rang and nobody
picked up" scenario has not been confirmed against a real live test call
yet. MISSED_HANGUP_CAUSES below is a best-effort mapping based on Telnyx's
public docs. On the first real end-to-end test, we should log and inspect the raw
payload (see the logger.info call below) and adjust this set if the actual
cause differs from what's listed.
"""
import base64
import json
import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from sqlalchemy.orm import Session

from app.config import TELNYX_PUBLIC_KEY, WEBHOOK_SKIP_SIGNATURE_CHECK, WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS
from app.db.database import get_db
from app.db.models import CallJob, TelephonyEvent
from app.api.companies import get_company_by_business_number
from app.utils.phone import normalize_phone_number
from app.queue.job_queue import enqueue

logger = logging.getLogger("denwa.webhooks")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# The only event type we act on. call.initiated / call.answered / etc. are
# ignored — we only need to know how a call ended.
RELEVANT_EVENT_TYPE = "call.hangup"

# Best-effort mapping of Telnyx hangup_cause -> "this was a missed call".
# NOT YET CONFIRMED against a real call — verify on first live test (see
# module docstring above) and adjust if needed.
MISSED_HANGUP_CAUSES = {"no_answer", "originator_cancel", "call_rejected", "timeout"}


def _verify_telnyx_signature(raw_body: bytes, signature_header, timestamp_header) -> bool:
    """Validate the request actually came from Telnyx.

    Telnyx signs `{timestamp}|{raw_body}` with Ed25519 and sends the
    signature in the `telnyx-signature-ed25519` header (base64) alongside
    `telnyx-timestamp`. Verification uses our account's PUBLIC key — this
    is asymmetric signing, not a shared HMAC secret.
    Docs: https://developers.telnyx.com/docs/development/sdk/python/webhooks
    """
    if WEBHOOK_SKIP_SIGNATURE_CHECK:
        logger.warning("WEBHOOK_SKIP_SIGNATURE_CHECK is enabled — signature check bypassed. DEV ONLY.")
        return True

    if not TELNYX_PUBLIC_KEY:
        logger.error("TELNYX_PUBLIC_KEY is not configured; rejecting webhook.")
        return False

    if not signature_header or not timestamp_header:
        return False

    # Replay-attack guard: reject stale timestamps.
    try:
        ts = int(timestamp_header)
    except ValueError:
        return False
    if abs(time.time() - ts) > WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS:
        logger.warning("Rejected webhook: timestamp outside tolerance window.")
        return False

    try:
        verify_key = VerifyKey(TELNYX_PUBLIC_KEY, encoder=Base64Encoder)
        signed_payload = f"{timestamp_header}|{raw_body.decode('utf-8')}".encode("utf-8")
        signature_bytes = base64.b64decode(signature_header)
        verify_key.verify(signed_payload, signature_bytes)
        return True
    except (BadSignatureError, ValueError, Exception):
        return False


@router.post("/telephony")
async def telephony_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()

    # --- 1. Authenticity ---------------------------------------------------
    signature_header = request.headers.get("telnyx-signature-ed25519")
    timestamp_header = request.headers.get("telnyx-timestamp")
    if not _verify_telnyx_signature(raw_body, signature_header, timestamp_header):
        logger.warning("Rejected webhook: invalid, missing, or stale Telnyx signature.")
        return Response(status_code=403, content="Invalid signature")

    # --- 2. Payload parsing / validation -------------------------------------
    # NOTE: Telnyx wraps the actual event fields inside a top-level "data"
    # object, alongside a sibling "meta" object with delivery info:
    #   { "data": { "id": ..., "event_type": ..., "payload": {...} }, "meta": {...} }
    # (Confirmed against a real webhook delivery on 2026-09 — the original
    # assumption that id/event_type sat at the root was wrong and caused
    # every real event to be rejected as "missing id/event_type".)
    try:
        envelope = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.warning("Rejected webhook: body is not valid JSON.")
        return Response(status_code=400, content="Malformed JSON body")

    event = envelope.get("data") or {}
    event_id = event.get("id")
    event_type = event.get("event_type")
    payload = event.get("payload") or {}

    if not event_id or not event_type:
        logger.warning("Rejected webhook: missing id/event_type. Keys=%s", list(envelope.keys()))
        return Response(status_code=400, content="Missing required fields")

    # --- 3. Event-type filter -----------------------------------------------
    if event_type != RELEVANT_EVENT_TYPE:
        return Response(status_code=200, content="Ignored: not a call.hangup event")

    hangup_cause = payload.get("hangup_cause")
    logger.info("call.hangup received: hangup_cause=%s call_control_id=%s", hangup_cause, payload.get("call_control_id"))

    if hangup_cause not in MISSED_HANGUP_CAUSES:
        return Response(status_code=200, content="Ignored: not a missed-call hangup_cause")

    from_number = payload.get("from")
    to_number = payload.get("to")
    if not from_number or not to_number:
        logger.warning("Rejected webhook: missing from/to in payload. Payload=%s", payload)
        return Response(status_code=400, content="Missing from/to in payload")

    # --- 4. Idempotency / dedup ---------------------------------------------
    existing = db.query(TelephonyEvent).filter(TelephonyEvent.provider_event_id == event_id).first()
    if existing is not None:
        logger.info("Duplicate webhook for event id=%s — ignoring.", event_id)
        return Response(status_code=200, content="Duplicate event, already processed")

    # --- 5. Normalize numbers ------------------------------------------------
    normalized_caller = normalize_phone_number(from_number)
    normalized_business = normalize_phone_number(to_number)
    if normalized_caller is None or normalized_business is None:
        logger.warning(
            "Rejected webhook: unparseable phone numbers. From=%s To=%s", from_number, to_number
        )
        return Response(status_code=200, content="Unparseable phone numbers")

    # --- 6. Company routing ---------------------------------------------------
    company = get_company_by_business_number(db, normalized_business)
    if company is None:
        logger.warning("No company found for business_number=%s (event id=%s)", normalized_business, event_id)
        return Response(status_code=200, content="Unknown business number")

    # --- 7. Persist event + create job ----------------------------------------
    occurred_at_raw = payload.get("occurred_at")
    try:
        occurred_at = datetime.fromisoformat(occurred_at_raw.replace("Z", "+00:00")) if occurred_at_raw else datetime.now(timezone.utc)
    except (ValueError, AttributeError):
        occurred_at = datetime.now(timezone.utc)

    telephony_event = TelephonyEvent(
        provider_event_id=event_id,
        company_id=company.id,
        business_number=normalized_business,
        caller_number=normalized_caller,
        event_type=hangup_cause,
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
        "Created CallJob id=%s for company_id=%s from event id=%s (hangup_cause=%s)",
        call_job.id, company.id, event_id, hangup_cause,
    )
    return Response(status_code=200, content="Callback job created")
