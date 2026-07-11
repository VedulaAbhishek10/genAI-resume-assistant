import json

import httpx
import pytest

from app.core.exceptions import LLMProviderError, LLMValidationError
from app.llm.ollama import OllamaClient
from app.schemas.resume import CandidateProfileExtraction

_RealAsyncClient = httpx.AsyncClient


def _patch_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    def factory(*args: object, **kwargs: object) -> httpx.AsyncClient:
        return _RealAsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr("app.llm.ollama.httpx.AsyncClient", factory)


async def test_generate_returns_response_text(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "hello world"})

    _patch_transport(monkeypatch, handler)
    client = OllamaClient(base_url="http://fake-ollama", model="test-model")

    result = await client.generate("some prompt")

    assert result == "hello world"


async def test_generate_structured_returns_validated_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    valid_payload = {"professional_summary": "Engineer", "skills": [{"name": "Python"}]}

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": json.dumps(valid_payload)})

    _patch_transport(monkeypatch, handler)
    client = OllamaClient(base_url="http://fake-ollama", model="test-model")

    result = await client.generate_structured("prompt", CandidateProfileExtraction)

    assert isinstance(result, CandidateProfileExtraction)
    assert result.professional_summary == "Engineer"
    assert result.skills[0].name == "Python"


async def test_generate_structured_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(200, json={"response": "not valid json"})
        return httpx.Response(200, json={"response": json.dumps({"skills": []})})

    _patch_transport(monkeypatch, handler)
    client = OllamaClient(
        base_url="http://fake-ollama", model="test-model", max_structured_attempts=2
    )

    result = await client.generate_structured("prompt", CandidateProfileExtraction)

    assert isinstance(result, CandidateProfileExtraction)
    assert calls["count"] == 2


async def test_generate_structured_raises_after_exhausting_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "not valid json"})

    _patch_transport(monkeypatch, handler)
    client = OllamaClient(
        base_url="http://fake-ollama", model="test-model", max_structured_attempts=2
    )

    with pytest.raises(LLMValidationError):
        await client.generate_structured("prompt", CandidateProfileExtraction)


async def test_transport_failure_raises_llm_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    _patch_transport(monkeypatch, handler)
    client = OllamaClient(base_url="http://fake-ollama", model="test-model")

    with pytest.raises(LLMProviderError):
        await client.generate("prompt")
