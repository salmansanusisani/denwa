"""Intake trigger, call history, call detail."""
from fastapi import APIRouter

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/intake")
def trigger_intake(company_id: int, caller_number: str):
    """TODO(backend): the 'Simulate missed call' button hits this.
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
