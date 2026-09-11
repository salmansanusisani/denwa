"""Local test for app/api/webhooks.py -no real Telnyx account needed-

Generates a real Ed25519 keypair locally, signs test payloads exactly the
way Telnyx signs them ({timestamp}|{raw_body}, base64 signature), and
verifies against our own webhook handler using that keypair's PUBLIC key
as TELNYX_PUBLIC_KEY. This proves the verification logic is correct;
swapping in the real TELNYX_PUBLIC_KEY later requires no code changes.

Run: python test_webhook.py
"""
import base64
import json
import os
import time

from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey

_signing_key = SigningKey.generate()
_public_key_b64 = _signing_key.verify_key.encode(encoder=Base64Encoder).decode("utf-8")

os.environ["TELNYX_PUBLIC_KEY"] = _public_key_b64
os.environ["WEBHOOK_SKIP_SIGNATURE_CHECK"] = "false"
os.environ["WORKER_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test_webhook.db"

if os.path.exists("./test_webhook.db"):
    os.remove("./test_webhook.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.db.database import SessionLocal, init_db  # noqa: E402
from app.db.models import Company, CallJob, TelephonyEvent  # noqa: E402
from app.queue.job_queue import dequeue  # noqa: E402

client = TestClient(app)


def sign(body_dict: dict, timestamp=None):
    raw_body = json.dumps(body_dict).encode("utf-8")
    ts = timestamp or str(int(time.time()))
    signed_payload = f"{ts}|{raw_body.decode('utf-8')}".encode("utf-8")
    signature = _signing_key.sign(signed_payload).signature
    return raw_body, ts, base64.b64encode(signature).decode("utf-8")


def post(body_dict: dict, timestamp=None, signature=None):
    raw_body, ts, sig = sign(body_dict, timestamp)
    headers = {"Content-Type": "application/json"}
    headers["telnyx-signature-ed25519"] = signature if signature is not None else sig
    if ts:
        headers["telnyx-timestamp"] = ts
    return client.post("/webhooks/telephony", content=raw_body, headers=headers)


def make_event(event_id, event_type, from_number=None, to_number=None, hangup_cause=None):
    payload = {"call_control_id": f"cc_{event_id}"}
    if from_number:
        payload["from"] = from_number
    if to_number:
        payload["to"] = to_number
    if hangup_cause:
        payload["hangup_cause"] = hangup_cause
    return {
        "data": {
            "record_type": "event",
            "id": event_id,
            "event_type": event_type,
            "payload": payload,
        },
        "meta": {"attempt": 1, "delivered_to": "https://example-ngrok-url/webhooks/telephony"},
    }


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
    init_db()
    seed_company()
    results = []

    event1 = make_event("evt_001", "call.hangup", "+962791234567", "+962799999999", "no_answer")
    r = post(event1)
    results.append(check("Valid signed call.hangup/no_answer -> 200", r.status_code == 200))

    db = SessionLocal()
    results.append(check("Exactly 1 CallJob created", db.query(CallJob).count() == 1))
    results.append(check("Exactly 1 TelephonyEvent created", db.query(TelephonyEvent).count() == 1))
    db.close()

    r = post(event1, signature="dG90YWxseV93cm9uZ19zaWduYXR1cmU=")
    results.append(check("Invalid signature -> 403", r.status_code == 403))

    r = client.post(
        "/webhooks/telephony",
        content=json.dumps(event1).encode("utf-8"),
        headers={"Content-Type": "application/json", "telnyx-timestamp": str(int(time.time()))},
    )
    results.append(check("Missing signature header -> 403", r.status_code == 403))

    old_ts = str(int(time.time()) - 999999)
    r = post(event1, timestamp=old_ts)
    results.append(check("Stale timestamp (replay) -> 403", r.status_code == 403))

    r = post(event1)
    results.append(check("Duplicate event id -> 200 (idempotent)", r.status_code == 200))
    db = SessionLocal()
    results.append(check("Duplicate event created NO new CallJob", db.query(CallJob).count() == 1))
    db.close()

    event2 = make_event("evt_002", "call.answered", "+962791234567", "+962799999999")
    r = post(event2)
    results.append(check("call.answered event -> 200, ignored", r.status_code == 200))
    db = SessionLocal()
    results.append(check("Non-hangup event created NO new CallJob", db.query(CallJob).count() == 1))
    db.close()

    event3 = make_event("evt_003", "call.hangup", "+962791234567", "+962799999999", "normal_clearing")
    r = post(event3)
    results.append(check("hangup_cause=normal_clearing -> 200, ignored", r.status_code == 200))
    db = SessionLocal()
    results.append(check("Non-missed hangup created NO new CallJob", db.query(CallJob).count() == 1))
    db.close()

    event4 = make_event("evt_004", "call.hangup", "+962791234567", "+962700000000", "no_answer")
    r = post(event4)
    results.append(check("Unknown business number -> 200 (no crash)", r.status_code == 200))
    db = SessionLocal()
    results.append(check("Unknown business number created NO new CallJob", db.query(CallJob).count() == 1))
    db.close()

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
