#Tests for Telephony Webhook handling: auth, idempotency, routing, payload validation.

import base64
import json
import time

from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey

from app.db.models import CallJob, TelephonyEvent

# Generated once per test run; the corresponding public key is injected into
# TELNYX_PUBLIC_KEY by the `client` fixture in conftest.py so verification
# succeeds without needing a real Telnyx account.
from tests.conftest import TEST_SIGNING_KEY


def sign(body_dict: dict, timestamp=None):
    raw_body = json.dumps(body_dict).encode("utf-8")
    ts = timestamp or str(int(time.time()))
    signed_payload = f"{ts}|{raw_body.decode('utf-8')}".encode("utf-8")
    signature = TEST_SIGNING_KEY.sign(signed_payload).signature
    return raw_body, ts, base64.b64encode(signature).decode("utf-8")


def post(client, body_dict: dict, timestamp=None, signature=None):
    raw_body, ts, sig = sign(body_dict, timestamp)
    headers = {"Content-Type": "application/json", "telnyx-timestamp": ts}
    headers["telnyx-signature-ed25519"] = signature if signature is not None else sig
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


def test_webhook_valid_signature_creates_job(client, db_session, sample_company):
    event = make_event("evt_unit_001", "call.hangup", "+16502531111", sample_company.phone_number, "no_answer")
    resp = post(client, event)
    assert resp.status_code == 200

    jobs = db_session.query(CallJob).all()
    assert len(jobs) == 1
    assert jobs[0].status == "pending"
    assert jobs[0].company_id == sample_company.id

    events = db_session.query(TelephonyEvent).all()
    assert len(events) == 1
    assert events[0].provider_event_id == "evt_unit_001"


def test_webhook_invalid_signature_rejected(client, db_session, sample_company):
    event = make_event("evt_unit_002", "call.hangup", "+16502531111", sample_company.phone_number, "no_answer")
    resp = post(client, event, signature="dG90YWxseV93cm9uZ19zaWduYXR1cmU=")
    assert resp.status_code == 403
    assert db_session.query(CallJob).count() == 0


def test_webhook_missing_signature_rejected(client, db_session, sample_company):
    event = make_event("evt_unit_003", "call.hangup", "+16502531111", sample_company.phone_number, "no_answer")
    raw_body = json.dumps(event).encode("utf-8")
    resp = client.post(
        "/webhooks/telephony",
        content=raw_body,
        headers={"Content-Type": "application/json", "telnyx-timestamp": str(int(time.time()))},
    )
    assert resp.status_code == 403
    assert db_session.query(CallJob).count() == 0


def test_webhook_idempotency_duplicate_event_id(client, db_session, sample_company):
    event = make_event("evt_dup_001", "call.hangup", "+16502531111", sample_company.phone_number, "call_rejected")

    resp1 = post(client, event)
    assert resp1.status_code == 200

    resp2 = post(client, event)
    assert resp2.status_code == 200

    assert db_session.query(CallJob).count() == 1
    assert db_session.query(TelephonyEvent).count() == 1


def test_webhook_ignores_non_missed_call(client, db_session, sample_company):
    event = make_event("evt_completed_001", "call.hangup", "+16502531111", sample_company.phone_number, "normal_clearing")
    resp = post(client, event)
    assert resp.status_code == 200
    assert db_session.query(CallJob).count() == 0


def test_webhook_ignores_non_hangup_event_type(client, db_session, sample_company):
    event = make_event("evt_initiated_001", "call.initiated", "+16502531111", sample_company.phone_number)
    resp = post(client, event)
    assert resp.status_code == 200
    assert db_session.query(CallJob).count() == 0


def test_webhook_unknown_business_number_no_crash(client, db_session):
    event = make_event("evt_unknown_001", "call.hangup", "+16502531111", "+16505559999", "no_answer")
    resp = post(client, event)
    assert resp.status_code == 200
    assert db_session.query(CallJob).count() == 0


def test_webhook_stale_timestamp_rejected(client, db_session, sample_company):
    event = make_event("evt_stale_001", "call.hangup", "+16502531111", sample_company.phone_number, "no_answer")
    old_ts = str(int(time.time()) - 999999)
    resp = post(client, event, timestamp=old_ts)
    assert resp.status_code == 403
    assert db_session.query(CallJob).count() == 0