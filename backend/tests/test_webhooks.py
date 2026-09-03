"""Tests for Telephony Webhook handling: auth, idempotency, routing, payload validation."""
from twilio.request_validator import RequestValidator

from app.db.models import CallJob, TelephonyEvent

AUTH_TOKEN = "test_twilio_secret_token"
WEBHOOK_URL = "http://testserver/webhooks/telephony"


def compute_sig(params: dict) -> str:
    validator = RequestValidator(AUTH_TOKEN)
    return validator.compute_signature(WEBHOOK_URL, params)


def test_webhook_valid_signature_creates_job(client, db_session, sample_company):
    params = {
        "CallSid": "CA_test_unit_001",
        "From": "+16502531111",
        "To": sample_company.phone_number,
        "CallStatus": "no-answer",
    }
    sig = compute_sig(params)
    resp = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": sig})
    assert resp.status_code == 200

    jobs = db_session.query(CallJob).all()
    assert len(jobs) == 1
    assert jobs[0].status == "pending"
    assert jobs[0].company_id == sample_company.id

    events = db_session.query(TelephonyEvent).all()
    assert len(events) == 1
    assert events[0].provider_event_id == "CA_test_unit_001"


def test_webhook_invalid_signature_rejected(client, db_session, sample_company):
    params = {
        "CallSid": "CA_test_unit_002",
        "From": "+16502531111",
        "To": sample_company.phone_number,
        "CallStatus": "no-answer",
    }
    resp = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": "invalid_sig"})
    assert resp.status_code == 403
    assert db_session.query(CallJob).count() == 0


def test_webhook_missing_signature_rejected(client, db_session, sample_company):
    params = {
        "CallSid": "CA_test_unit_003",
        "From": "+16502531111",
        "To": sample_company.phone_number,
        "CallStatus": "no-answer",
    }
    resp = client.post("/webhooks/telephony", data=params)
    assert resp.status_code == 403
    assert db_session.query(CallJob).count() == 0


def test_webhook_idempotency_duplicate_callsid(client, db_session, sample_company):
    params = {
        "CallSid": "CA_dup_001",
        "From": "+16502531111",
        "To": sample_company.phone_number,
        "CallStatus": "busy",
    }
    sig = compute_sig(params)
    resp1 = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": sig})
    assert resp1.status_code == 200

    resp2 = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": sig})
    assert resp2.status_code == 200

    assert db_session.query(CallJob).count() == 1
    assert db_session.query(TelephonyEvent).count() == 1


def test_webhook_ignores_non_missed_call(client, db_session, sample_company):
    params = {
        "CallSid": "CA_completed_001",
        "From": "+16502531111",
        "To": sample_company.phone_number,
        "CallStatus": "completed",
    }
    sig = compute_sig(params)
    resp = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": sig})
    assert resp.status_code == 200
    assert db_session.query(CallJob).count() == 0


def test_webhook_unknown_business_number_no_crash(client, db_session):
    params = {
        "CallSid": "CA_unknown_001",
        "From": "+16502531111",
        "To": "+16505559999",
        "CallStatus": "no-answer",
    }
    sig = compute_sig(params)
    resp = client.post("/webhooks/telephony", data=params, headers={"X-Twilio-Signature": sig})
    assert resp.status_code == 200
    assert db_session.query(CallJob).count() == 0
