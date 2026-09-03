"""CALL-E client wrapper. Built against the stable Calls API.

Features:
- Auth via CALLE_API_KEY and base URL via CALLE_BASE_URL.
- Idempotency-Key header support per CallJob.
- Explicit error handling for 401 Unauthorized, 429 Rate Limit (with Retry-After), and 5xx/network failures.
- Polling for terminal call states (completed, failed, result_validation_failed).
- Structured response parsing conforming to shared data contract.
"""
import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

from app.config import CALLE_API_KEY, CALLE_BASE_URL

logger = logging.getLogger("denwa.calle_client")


class CalleError(Exception):
    """Base exception for CALL-E client failures."""
    pass


class CalleAuthError(CalleError):
    """Authentication failed (401 / 403)."""
    pass


class CalleRateLimitError(CalleError):
    """Rate limit exceeded (429)."""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class CalleCallFailedError(CalleError):
    """Call ended in a terminal failed or validation failed state."""
    def __init__(self, message: str, call_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.call_data = call_data or {}


class CalleClient:
    def __init__(
        self,
        api_key: str = CALLE_API_KEY,
        base_url: str = CALLE_BASE_URL,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = (base_url or "https://api.call-e.com").rstrip("/")
        self.timeout = timeout

    def _get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = str(idempotency_key)
        return headers

    def _handle_error_response(self, response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            raise CalleAuthError(f"CALL-E authentication failure ({response.status_code}): {response.text}")
        if response.status_code == 429:
            retry_after = None
            retry_header = response.headers.get("Retry-After")
            if retry_header:
                try:
                    retry_after = float(retry_header)
                except ValueError:
                    pass
            raise CalleRateLimitError(
                f"CALL-E rate limit exceeded (429): {response.text}", retry_after=retry_after
            )
        if response.is_error:
            raise CalleError(f"CALL-E API error ({response.status_code}): {response.text}")

    async def create_call(
        self,
        task: str,
        recipient: Dict[str, str],
        result_schema: Dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate an outbound call via CALL-E."""
        if not self.api_key:
            raise CalleAuthError("CALLE_API_KEY is not configured")

        url = f"{self.base_url}/v1/calls"
        payload = {
            "task": task,
            "recipient": recipient,
            "resultSchema": result_schema,
        }
        headers = self._get_headers(idempotency_key=idempotency_key)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                self._handle_error_response(response)
                return response.json()
            except httpx.HTTPError as exc:
                if not isinstance(exc, (CalleError,)):
                    raise CalleError(f"HTTP communication error connecting to CALL-E: {exc}") from exc
                raise

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Fetch current status and result of an existing call."""
        if not self.api_key:
            raise CalleAuthError("CALLE_API_KEY is not configured")

        url = f"{self.base_url}/v1/calls/{call_id}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                self._handle_error_response(response)
                return response.json()
            except httpx.HTTPError as exc:
                if not isinstance(exc, (CalleError,)):
                    raise CalleError(f"HTTP communication error polling CALL-E call {call_id}: {exc}") from exc
                raise

    async def create_and_wait(
        self,
        task: str,
        recipient: Dict[str, str],
        result_schema: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        poll_interval: float = 2.0,
        max_wait_seconds: float = 120.0,
    ) -> Dict[str, Any]:
        """Initiate a call and poll until completion, returning structured result.

        Raises CalleError or CalleCallFailedError on any terminal failure or timeout.
        """
        call_init = await self.create_call(
            task=task,
            recipient=recipient,
            result_schema=result_schema,
            idempotency_key=idempotency_key,
        )

        status = call_init.get("status")

        if status == "completed":
            return self._extract_result(call_init)
        if status in ("failed", "result_validation_failed"):
            raise CalleCallFailedError(f"CALL-E call immediately finished with status '{status}'", call_init)

        call_id = call_init.get("id") or call_init.get("call_id")
        if not call_id:

            if "result" in call_init or "resolved" in call_init:
                return self._extract_result(call_init)
            raise CalleError("No call_id returned from CALL-E call initiation")

    
        elapsed = 0.0
        while elapsed < max_wait_seconds:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            call_data = await self.get_call(call_id)
            current_status = call_data.get("status")
            logger.debug("Polled call_id=%s, status=%s", call_id, current_status)

            if current_status == "completed":
                return self._extract_result(call_data)
            if current_status in ("failed", "result_validation_failed", "canceled"):
                raise CalleCallFailedError(
                    f"CALL-E call {call_id} ended with status '{current_status}'", call_data
                )

        raise CalleError(f"Timed out waiting for CALL-E call {call_id} after {max_wait_seconds}s")

    def _extract_result(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured fields matching the shared CallResult data contract."""
        result_payload = call_data.get("result") or call_data.get("structured_result") or {}
        if not isinstance(result_payload, dict):
            result_payload = {}

        return {
            "question_asked": result_payload.get("question_asked") or call_data.get("question_asked") or "",
            "answer_given": result_payload.get("answer_given") or call_data.get("answer_given") or "",
            "resolved": bool(result_payload.get("resolved", call_data.get("resolved", False))),
            "needs_human_followup": bool(
                result_payload.get("needs_human_followup", call_data.get("needs_human_followup", False))
            ),
            "transcript_url": call_data.get("transcript_url") or call_data.get("recording_url"),
        }

