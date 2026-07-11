import json

import httpx
from pydantic import ValidationError

from app.core.exceptions import LLMProviderError, LLMValidationError
from app.llm.base import LLMClient, SchemaT


class OllamaClient(LLMClient):
    """LLMClient implementation backed by a local Ollama server."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 60.0,
        max_structured_attempts: int = 2,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_structured_attempts = max_structured_attempts

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": temperature},
        }
        response = await self._post(payload)
        text = response.get("response")
        if not isinstance(text, str):
            raise LLMProviderError("Ollama response did not contain a 'response' field.")
        return text

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": schema.model_json_schema(),
            "options": {"temperature": temperature},
        }

        last_error: Exception | None = None
        for _ in range(self._max_structured_attempts):
            response = await self._post(payload)
            raw = self._extract_structured_text(response)
            if raw is None:
                last_error = LLMValidationError(
                    "Ollama response did not contain usable structured output text."
                )
                continue
            try:
                data = json.loads(raw)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                continue

        raise LLMValidationError(
            f"Ollama returned invalid structured output after "
            f"{self._max_structured_attempts} attempt(s): {last_error}"
        )

    @staticmethod
    def _extract_structured_text(response: dict[str, object]) -> str | None:
        """Return the model's structured output text.

        Some "thinking" models (e.g. Qwen3) place structured JSON output in the
        'thinking' field instead of 'response' even when thinking mode is disabled
        on the server side; fall back to it defensively.
        """
        text = response.get("response")
        if isinstance(text, str) and text.strip():
            return text
        thinking = response.get("thinking")
        if isinstance(thinking, str) and thinking.strip():
            return thinking
        return None

    async def _post(self, payload: dict[str, object]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/generate", json=payload)
                response.raise_for_status()
                result: dict[str, object] = response.json()
                return result
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Ollama request failed: {exc}") from exc
