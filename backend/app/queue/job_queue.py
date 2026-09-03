"""Persistent, database-backed job queue for Denwa.

Uses CallJob.status in the database as the single source of truth:
pending -> in_progress -> done / failed.
Crash-safe and persistent without requiring external infrastructure (e.g. Redis).
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import CallJob


def enqueue(call_job_id: int, db: Optional[Session] = None) -> None:
    """Ensure the specified CallJob is in 'pending' status."""
    if db is not None:
        job = db.query(CallJob).filter(CallJob.id == call_job_id).first()
        if job and job.status != "pending":
            job.status = "pending"
            db.commit()
    else:
        with SessionLocal() as session:
            job = session.query(CallJob).filter(CallJob.id == call_job_id).first()
            if job and job.status != "pending":
                job.status = "pending"
                session.commit()


def dequeue(db: Optional[Session] = None) -> Optional[int]:
    """Atomically claim the next pending CallJob and mark it 'in_progress'.

    Returns the call_job_id or None if the queue is empty.
    """
    if db is not None:
        job = (
            db.query(CallJob)
            .filter(CallJob.status == "pending")
            .order_by(CallJob.created_at.asc(), CallJob.id.asc())
            .first()
        )
        if job:
            job.status = "in_progress"
            db.commit()
            return job.id
        return None

    with SessionLocal() as session:
        job = (
            session.query(CallJob)
            .filter(CallJob.status == "pending")
            .order_by(CallJob.created_at.asc(), CallJob.id.asc())
            .first()
        )
        if job:
            job.status = "in_progress"
            session.commit()
            return job.id
        return None