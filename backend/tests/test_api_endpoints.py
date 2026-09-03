"""Tests for REST API endpoints: Companies, Calls history/detail, Dev trigger, Documents."""
import io
from app.db.models import CallJob, CallResult, Document


def test_companies_crud(client):
    # Create company
    resp = client.post("/companies/", json={"name": "New Co", "phone_number": "+14155552671"})
    assert resp.status_code == 201
    company_data = resp.json()
    assert company_data["name"] == "New Co"
    company_id = company_data["id"]


    # Get company
    resp_get = client.get(f"/companies/{company_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["id"] == company_id

    # Reject duplicate phone number
    resp_dup = client.post("/companies/", json={"name": "Another Co", "phone_number": "+14155552671"})
    assert resp_dup.status_code == 409


def test_internal_dev_trigger_callback(client, sample_company, db_session):
    resp = client.post(
        f"/internal/dev/trigger-callback?company_id={sample_company.id}&caller_number=%2B16502531111"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    job_id = data["job_id"]

    job = db_session.query(CallJob).filter(CallJob.id == job_id).first()
    assert job is not None
    assert job.status == "pending"
    assert job.company_id == sample_company.id


def test_calls_list_and_detail(client, sample_company, db_session):
    job = CallJob(
        company_id=sample_company.id,
        caller_number="+16502531111",
        status="completed",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    result = CallResult(
        call_job_id=job.id,
        question_asked="Where are you located?",
        answer_given="100 Main Street, San Francisco.",
        resolved=True,
        needs_human_followup=False,
        transcript_url="https://transcript.test/1",
    )
    db_session.add(result)
    db_session.commit()

    # List calls
    resp = client.get(f"/calls/?company_id={sample_company.id}")
    assert resp.status_code == 200
    calls_list = resp.json()
    assert len(calls_list) == 1
    assert calls_list[0]["id"] == job.id
    assert calls_list[0]["result"]["question_asked"] == "Where are you located?"

    # Detail view
    resp_detail = client.get(f"/calls/{job.id}")
    assert resp_detail.status_code == 200
    detail_data = resp_detail.json()
    assert detail_data["id"] == job.id
    assert detail_data["result"]["answer_given"] == "100 Main Street, San Francisco."


def test_documents_upload_and_list(client, sample_company, db_session):
    file_content = b"Frequently Asked Questions:\n\nQ: What are your hours?\nA: 9am - 5pm."
    files = {"file": ("faq.txt", io.BytesIO(file_content), "text/plain")}
    data = {"company_id": sample_company.id}

    resp = client.post("/documents/upload", data=data, files=files)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["filename"] == "faq.txt"
    assert res_data["chunks_count"] >= 1

    # List documents
    resp_list = client.get(f"/documents/?company_id={sample_company.id}")
    assert resp_list.status_code == 200
    doc_list = resp_list.json()
    assert len(doc_list) == 1
    assert doc_list[0]["filename"] == "faq.txt"
