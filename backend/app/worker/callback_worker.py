"""Callback worker

Pulls pending CallJobs from the database queue, retrieves verified knowledge context
via AI/ML, resolves region, invokes CALL-E with idempotency keys, and captures the
structured CallResult in the database.
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import CallJob, CallResult, Company
from app.queue.job_queue import dequeue
from app.region.resolver import resolve_region
from app.integrations.ai_ml import get_verified_context_and_task
from app.calle_client.client import CalleClient, CalleError

logger = logging.getLogger("denwa.worker")


async def process_job(
    job_id: int,
    db: Session,
    calle_client: Optional[CalleClient] = None,
) -> bool:
    """Process a single CallJob end-to-end.

    Returns True if successfully completed, False if failed.
    """
    job = db.query(CallJob).filter(CallJob.id == job_id).first()
    if not job:
        logger.error("Job id=%s not found in database", job_id)
        return False


    job.status = "in_progress"
    db.commit()

    company = db.query(Company).filter(Company.id == job.company_id).first()
    if not company:
        logger.error("Company id=%s not found for CallJob id=%s", job.company_id, job.id)
        job.status = "failed"
        db.commit()
        return False

    client = calle_client or CalleClient()

    try:
        
        region = resolve_region(job.caller_number)
        logger.info("Resolved region=%s for caller=%s (job_id=%s)", region, job.caller_number, job.id)

        
        task_data = get_verified_context_and_task(
            company_id=company.id,
            caller_number=job.caller_number,
        )
        task = task_data["task"]
        result_schema = task_data["result_schema"]

        recipient = {
            "phone": job.caller_number,
            "region": region,
        }

    
        idempotency_key = f"calljob-{job.id}"
        logger.info("Initiating CALL-E callback for job_id=%s", job.id)
        structured_result = await client.create_and_wait(
            task=task,
            recipient=recipient,
            result_schema=result_schema,
            idempotency_key=idempotency_key,
        )

        
        call_result = CallResult(
            call_job_id=job.id,
            question_asked=structured_result.get("question_asked", ""),
            answer_given=structured_result.get("answer_given", ""),
            resolved=structured_result.get("resolved", False),
            needs_human_followup=structured_result.get("needs_human_followup", False),
            transcript_url=structured_result.get("transcript_url"),
        )
        db.add(call_result)

        
        job.status = "completed"
        db.commit()
        logger.info("Successfully completed CallJob id=%s (resolved=%s)", job.id, call_result.resolved)
        return True

    except Exception as exc:
        logger.error("Failed processing CallJob id=%s: %s", job.id, exc, exc_info=True)
        job.status = "failed"
        db.commit()
        return False


async def run_worker_loop(
    poll_interval: float = 1.0,
    max_iterations: Optional[int] = None,
    calle_client: Optional[CalleClient] = None,
) -> None:
    """Continuous polling loop for the background callback worker."""
    logger.info("Starting Denwa callback worker loop...")
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        iterations += 1
        with SessionLocal() as db:
            job_id = dequeue(db)
            if job_id is not None:
                logger.info("Worker picked up job_id=%s", job_id)
                await process_job(job_id=job_id, db=db, calle_client=calle_client)
            else:
                await asyncio.sleep(poll_interval)

