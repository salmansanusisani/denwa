"""Tests for CALL-E API Client."""
import pytest
import httpx
from app.calle_client.client import (
    CalleClient,
    CalleAuthError,
    CalleRateLimitError,
    CalleCallFailedError,
    CalleError,
)


@pytest.mark.asyncio
async def test_calle_create_and_wait_success(monkeypatch):
    client = CalleClient(api_key="valid_key", base_url="https://api.call-e.test")

    # Mock response from CALL-E
    mock_response_data = {
        "id": "call_12345",
        "status": "completed",
        "result": {
            "question_asked": "What are your business hours?",
            "answer_given": "We are open Monday to Friday 9am-5pm.",
            "resolved": True,
            "needs_human_followup": False,
        },
        "transcript_url": "https://transcripts.call-e.test/call_12345",
    }

    async def mock_post(self, url, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer valid_key"
        assert kwargs["headers"]["Idempotency-Key"] == "calljob-42"
        return httpx.Response(200, json=mock_response_data, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    res = await client.create_and_wait(
        task="Greet caller",
        recipient={"phone": "+16502530000", "region": "US"},
        result_schema={},
        idempotency_key="calljob-42",
    )

    assert res["question_asked"] == "What are your business hours?"
    assert res["answer_given"] == "We are open Monday to Friday 9am-5pm."
    assert res["resolved"] is True
    assert res["needs_human_followup"] is False
    assert res["transcript_url"] == "https://transcripts.call-e.test/call_12345"


@pytest.mark.asyncio
async def test_calle_auth_error(monkeypatch):
    client = CalleClient(api_key="invalid_key", base_url="https://api.call-e.test")

    async def mock_post(self, url, **kwargs):
        return httpx.Response(401, text="Unauthorized API Key", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(CalleAuthError):
        await client.create_call(
            task="Greet caller",
            recipient={"phone": "+16502530000", "region": "US"},
            result_schema={},
        )


@pytest.mark.asyncio
async def test_calle_rate_limit(monkeypatch):
    client = CalleClient(api_key="valid_key", base_url="https://api.call-e.test")

    async def mock_post(self, url, **kwargs):
        return httpx.Response(
            429,
            text="Too Many Requests",
            headers={"Retry-After": "5"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with pytest.raises(CalleRateLimitError) as exc_info:
        await client.create_call(
            task="Greet caller",
            recipient={"phone": "+16502530000", "region": "US"},
            result_schema={},
        )
    assert exc_info.value.retry_after == 5.0
