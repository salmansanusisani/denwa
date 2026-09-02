"""In-memory job queue for the hackathon. Swap for Redis + BullMQ-equivalent if time allows."""
from queue import Queue

pending_jobs: Queue = Queue()


def enqueue(call_job_id: int) -> None:
    pending_jobs.put(call_job_id)


def dequeue() -> int | None:
    if pending_jobs.empty():
        return None
    return pending_jobs.get()