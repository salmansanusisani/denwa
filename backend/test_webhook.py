"""Local test for app/api/webhooks.py — no real Twilio account needed.

Uses the official `twilio` SDK's RequestValidator to generate a REAL,
correctly-signed request (same HMAC-SHA1 algorithm Twilio itself uses),
against a fake auth token we control. This proves the verification logic
is correct; swapping in the real TWILIO_AUTH_TOKEN later requires no code
changes.

Run: python test_webhook.py
"""
import os

os.environ["TWILIO_AUTH_TOKEN"] = "fake_test_auth_token_12345"
os.environ["WEBHOOK_SKIP_SIGNATURE_CHECK"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test_webhook.db"

from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator

# Reset test DB each run
if os.path.exists("./test_webhook.db"):
    os.remove("./test_webhook.db")

from app.main import app  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.db.models import Company  # noqa: E402

client = TestClient(app)

WEBHOOK_URL = "http://testserver/webhooks/telephony"
AUTH_TOKEN = "fake_test_auth_token_12345"


def sign(params: dict) -> str:
    validator = RequestValidator(AUTH_TOKEN)
    return validator.compute_signature(WEBHOOK_URL, params)


def post(params: dict, signature: str | None):
    headers = {}
    if signature is not None:
        headers["X-Twilio-Signature"] = signature
    return client.post("/webhooks/telephony", data=params, headers=headers)


def seed_company():
    db = SessionLocal()
    company = Company(name="Test Cafe", phone_number="+962799999999")
    db.add(company)
    db.commit()
    db.refresh(company)
    db.close()
    return company


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    from app.db.database import init_db
    init_db()
    company = seed_company()

    results = []

    # --- Test 1: valid signed missed-call event -> 200, job created ---
    params = {
        "CallSid": "CA_test_001",
        "From": "+962791234567",
        "To": "+962799999999",
        "CallStatus": "no-answer",
    }
    sig = sign(params)
    r = post(params, sig)
    results.append(check("Valid signed no-answer event -> 200", r.status_code == 200))

    db = SessionLocal()
    from app.db.models import CallJob, TelephonyEvent
    job_count = db.query(CallJob).count()
    event_count = db.query(TelephonyEvent).count()
    results.append(check("Exactly 1 CallJob created", job_count == 1))
    results.append(check("Exactly 1 TelephonyEvent created", event_count == 1))
    db.close()

    # --- Test 2: invalid signature -> 403, no job created ---
    r = post(params, "totally_wrong_signature")
    results.append(check("Invalid signature -> 403", r.status_code == 403))

    # --- Test 3: missing signature header -> 403 ---
    r = post(params, None)
    results.append(check("Missing signature header -> 403", r.status_code == 403))

    # --- Test 4: duplicate CallSid (same event replayed) -> 200, no new job ---
    sig2 = sign(params)  # same params/CallSid as test 1
    r = post(params, sig2)
    results.append(check("Duplicate CallSid -> 200 (idempotent)", r.status_code == 200))
    db = SessionLocal()
    job_count_after_dup = db.query(CallJob).count()
    results.append(check("Duplicate event created NO new CallJob", job_count_after_dup == 1))
    db.close()

    # --- Test 5: non-missed-call status (e.g. "completed") -> 200, no job ---
    params2 = {
        "CallSid": "CA_test_002",
        "From": "+962791234567",
        "To": "+962799999999",
        "CallStatus": "completed",
    }
    sig3 = sign(params2)
    r = post(params2, sig3)
    results.append(check("CallStatus=completed -> 200, ignored", r.status_code == 200))
    db = SessionLocal()
    job_count_after_completed = db.query(CallJob).count()
    results.append(check("Ignored status created NO new CallJob", job_count_after_completed == 1))
    db.close()

    # --- Test 6: unknown business number -> 200, no job, no crash ---
    params3 = {
        "CallSid": "CA_test_003",
        "From": "+962791234567",
        "To": "+962700000000",  # not a registered company
        "CallStatus": "no-answer",
    }
    sig4 = sign(params3)
    r = post(params3, sig4)
    results.append(check("Unknown business number -> 200 (no crash)", r.status_code == 200))
    db = SessionLocal()
    job_count_after_unknown = db.query(CallJob).count()
    results.append(check("Unknown business number created NO new CallJob", job_count_after_unknown == 1))
    db.close()

    # --- Test 7: enqueue actually happened for test 1's job ---
    from app.queue.job_queue import dequeue
    dequeued_id = dequeue()
    results.append(check("Job was enqueued for the worker to pick up", dequeued_id is not None))

    print()
    total = len(results)
    passed = sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
