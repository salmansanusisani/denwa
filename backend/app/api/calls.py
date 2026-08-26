"""Intake trigger, call history, call detail."""
from fastapi import APIRouter

router = APIRouter(prefix="/calls", tags=["calls"])
internal_router = APIRouter(prefix="/internal/dev", tags=["internal-dev"])


@internal_router.post("/trigger-callback")
def trigger_intake(company_id: int, caller_number: str):
    """INTERNAL/DEV ONLY — not part of the product surface.
    Used by backend/AI-ML/CALL-E integration testing to create a CallJob
    without waiting on a real phone call. Frontend must NOT expose this.
    Creates a pending CallJob and pushes it onto the queue (app.queue.job_queue).
    """
    raise NotImplementedError


@router.get("/")
def list_calls(company_id: int):
    """TODO(backend): return CallJob + CallResult rows for the dashboard table."""
    raise NotImplementedError


@router.get("/{call_job_id}")
def get_call_detail(call_job_id: int):
    """TODO(backend): full structured result + transcript link for the detail view."""
    raise NotImplementedError
