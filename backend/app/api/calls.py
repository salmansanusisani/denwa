"""Intake trigger, call history, call detail."""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import CallJob, CallResult, Company
from app.queue.job_queue import enqueue
from app.utils.phone import normalize_phone_number

logger = logging.getLogger("denwa.calls")

router = APIRouter(prefix="/calls", tags=["calls"])
internal_router = APIRouter(prefix="/internal/dev", tags=["internal-dev"])


def _format_job_with_result(job: CallJob, result: Optional[CallResult] = None) -> Dict[str, Any]:
    formatted: Dict[str, Any] = {
        "id": job.id,
        "company_id": job.company_id,
        "caller_number": job.caller_number,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "result": None,
    }
    if result:
        formatted["result"] = {
            "id": result.id,
            "call_job_id": result.call_job_id,
            "question_asked": result.question_asked,
            "answer_given": result.answer_given,
            "resolved": result.resolved,
            "needs_human_followup": result.needs_human_followup,
            "transcript_url": result.transcript_url,
        }
    return formatted


@internal_router.post("/trigger-callback")
def trigger_intake(
    company_id: int,
    caller_number: str,
    db: Session = Depends(get_db),
):
    """INTERNAL/DEV ONLY — not part of the product surface.

    Used by backend/AI-ML/CALL-E integration testing to create a CallJob
    without waiting on a real phone call. Frontend must NOT expose this.
    Creates a pending CallJob and pushes it onto the database queue.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")

    normalized_caller = normalize_phone_number(caller_number)
    if not normalized_caller:
        raise HTTPException(status_code=422, detail="Invalid phone number format")

    job = CallJob(
        company_id=company.id,
        caller_number=normalized_caller,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    enqueue(job.id, db=db)
    logger.info("Dev trigger created CallJob id=%s for company_id=%s", job.id, company.id)

    return {
        "status": "ok",
        "job_id": job.id,
        "call_job": _format_job_with_result(job),
    }


@router.get("/")
def list_calls(
    company_id: int = Query(..., description="The ID of the company"),
    db: Session = Depends(get_db),
):
    """Return CallJob + CallResult rows for the company dashboard."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")

    jobs = (
        db.query(CallJob)
        .filter(CallJob.company_id == company_id)
        .order_by(CallJob.created_at.desc())
        .all()
    )

    job_ids = [j.id for j in jobs]
    results = (
        db.query(CallResult)
        .filter(CallResult.call_job_id.in_(job_ids))
        .all()
        if job_ids
        else []
    )
    result_by_job = {r.call_job_id: r for r in results}

    return [_format_job_with_result(j, result_by_job.get(j.id)) for j in jobs]


@router.get("/{call_job_id}")
def get_call_detail(
    call_job_id: int,
    db: Session = Depends(get_db),
):
    """Full structured result + transcript link for the call detail view."""
    job = db.query(CallJob).filter(CallJob.id == call_job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Call job with id {call_job_id} not found")

    result = db.query(CallResult).filter(CallResult.call_job_id == call_job_id).first()
    return _format_job_with_result(job, result)

