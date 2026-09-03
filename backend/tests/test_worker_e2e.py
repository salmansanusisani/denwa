"""Tests for Worker Orchestration and End-to-End Callback Execution."""
import pytest
from unittest.mock import AsyncMock

from app.db.models import CallJob, CallResult
from app.worker.callback_worker import process_job
from app.calle_client.client import CalleClient, CalleError


@pytest.mark.asyncio
async def test_worker_process_job_success(db_session, sample_company):
    job = CallJob(
        company_id=sample_company.id,
        caller_number="+16502531111",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Mock CalleClient
    mock_client = AsyncMock(spec=CalleClient)
    mock_client.create_and_wait.return_value = {
        "question_asked": "What is your return policy?",
        "answer_given": "Items can be returned within 30 days.",
        "resolved": True,
        "needs_human_followup": False,
        "transcript_url": "https://transcripts.call-e.test/job1",
    }

    success = await process_job(job_id=job.id, db=db_session, calle_client=mock_client)
    assert success is True

    db_session.refresh(job)
    assert job.status == "completed"

    result = db_session.query(CallResult).filter(CallResult.call_job_id == job.id).first()
    assert result is not None
    assert result.question_asked == "What is your return policy?"
    assert result.answer_given == "Items can be returned within 30 days."
    assert result.resolved is True
    assert result.needs_human_followup is False
    assert result.transcript_url == "https://transcripts.call-e.test/job1"


@pytest.mark.asyncio
async def test_worker_process_job_failure_updates_status(db_session, sample_company):
    job = CallJob(
        company_id=sample_company.id,
        caller_number="+16502531111",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    mock_client = AsyncMock(spec=CalleClient)
    mock_client.create_and_wait.side_effect = CalleError("CALL-E network timeout")

    success = await process_job(job_id=job.id, db=db_session, calle_client=mock_client)
    assert success is False

    db_session.refresh(job)
    assert job.status == "failed"

    result = db_session.query(CallResult).filter(CallResult.call_job_id == job.id).first()
    assert result is None
