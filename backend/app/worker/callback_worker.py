"""Pulls a pending job, asks AI/ML for the task string + resultSchema, calls CALL-E, stores the result.

This is the piece that wires Backend + AI/ML + CALL-E together (Architecture doc, Steps 3-6).

TODO(backend, with AI/ML):
1. dequeue a job id (app.queue.job_queue.dequeue).
2. Load the CallJob + Company from the DB.
3. resolve_region(caller_number) (app.region.resolver).
4. Call the AI/ML task-builder for this company (likely import from the ai-ml package, or an
   internal HTTP call if it ends up running as its own service) -> (task_string, result_schema).
5. CalleClient().create_and_wait(task, {phone, region}, result_schema).
6. Write a CallResult row from the structured response; update CallJob.status.
"""


async def run_worker_loop():
    """TODO(backend): simple while-True loop for the hackathon is fine."""
    raise NotImplementedError
