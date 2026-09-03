"""Tests for persistent DB-backed job queue."""
from app.db.models import CallJob
from app.queue.job_queue import enqueue, dequeue


def test_enqueue_and_dequeue(db_session, sample_company):
    job1 = CallJob(company_id=sample_company.id, caller_number="+16502531111", status="pending")
    job2 = CallJob(company_id=sample_company.id, caller_number="+16502532222", status="pending")
    db_session.add_all([job1, job2])
    db_session.commit()

    # Dequeue first job
    claimed_id_1 = dequeue(db=db_session)
    assert claimed_id_1 == job1.id
    db_session.refresh(job1)
    assert job1.status == "in_progress"

    # Dequeue second job
    claimed_id_2 = dequeue(db=db_session)
    assert claimed_id_2 == job2.id
    db_session.refresh(job2)
    assert job2.status == "in_progress"

    # Queue empty
    empty_id = dequeue(db=db_session)
    assert empty_id is None


def test_enqueue_replaces_status(db_session, sample_company):
    job = CallJob(company_id=sample_company.id, caller_number="+16502531111", status="failed")
    db_session.add(job)
    db_session.commit()

    enqueue(job.id, db=db_session)
    db_session.refresh(job)
    assert job.status == "pending"
