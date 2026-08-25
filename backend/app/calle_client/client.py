"""CALL-E client wrapper. Build against the stable one-shot Calls API
(package equivalents: @call-e/calle@0.2.2 JS / calle-ai==0.2.0 Python) — NOT Goal Runs (still preview).

Reference call shape (docs/ARCHITECTURE.md Section 6):

    task: str                 # instruction, pre-seeded with the prepared answer content
    recipient: {phone, region}
    resultSchema: dict         # JSON Schema for the structured result

TODO(backend):
- Wrap auth (CALLE_API_KEY) and base URL (CALLE_BASE_URL) from app.config.
- Add an idempotency key per job (e.g. the CallJob id) so retries don't double-dial.
- Handle errors from CALL-E (401, rate_limit_exceeded w/ Retry-After, etc).
- Either poll via createAndWait, or expose a webhook receiver for call.completed /
  call.failed / call.result_validation_failed and store the result from there.
"""
import httpx

from app.config import CALLE_API_KEY, CALLE_BASE_URL


class CalleClient:
    def __init__(self, api_key: str = CALLE_API_KEY, base_url: str = CALLE_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    async def create_and_wait(self, task: str, recipient: dict, result_schema: dict) -> dict:
        """TODO(backend): POST to CALL-E's create-call endpoint, wait for the terminal result."""
        raise NotImplementedError
