"""In-memory job queue for the hackathon. Swap for Redis + BullMQ-equivalent if time allows.

TODO(backend): a simple `queue.Queue` + background thread/asyncio task is enough — the DoD only
requires 5 consecutive runs without a stuck job, not production durability.
"""
from queue import Queue

pending_jobs: Queue = Queue()


def enqueue(call_job_id: int) -> None:
    """TODO(backend): push a job id onto the queue for the worker to pick up."""
    raise NotImplementedError


def dequeue() -> int | None:
    """TODO(backend): pop the next job id, or None if empty."""
    raise NotImplementedError
