from app.llm.base import LLMClient, SchemaT
from app.schemas.generation import BulletSuggestionExtraction
from app.services.tailoring_service import generate_bullet_suggestion, validate_grounding


def test_validate_grounding_passes_when_no_new_numbers_introduced() -> None:
    original = "Built backend services in Python."
    suggested = "Developed backend services using Python."

    assert validate_grounding(original, suggested) is True


def test_validate_grounding_fails_when_new_metric_introduced() -> None:
    original = "Built backend services in Python."
    suggested = "Built backend services in Python, improving performance by 30%."

    assert validate_grounding(original, suggested) is False


def test_validate_grounding_passes_when_original_number_is_reused() -> None:
    original = "Reduced latency by 30% across the platform."
    suggested = "Cut platform latency by 30% through targeted optimizations."

    assert validate_grounding(original, suggested) is True


def test_validate_grounding_fails_when_number_changed() -> None:
    original = "Reduced latency by 30%."
    suggested = "Reduced latency by 50%."

    assert validate_grounding(original, suggested) is False


class FakeLLMClient(LLMClient):
    def __init__(self, result: BulletSuggestionExtraction) -> None:
        self.result = result
        self.last_prompt: str | None = None

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        self.last_prompt = prompt
        assert schema is BulletSuggestionExtraction
        return self.result  # type: ignore[return-value]


async def test_generate_bullet_suggestion_includes_requirement_and_original_text() -> None:
    fake_client = FakeLLMClient(
        BulletSuggestionExtraction(
            suggested_text="Developed RESTful APIs using Python and FastAPI.",
            reason="Aligns terminology with the requirement's phrasing.",
            confidence=0.85,
        )
    )

    result = await generate_bullet_suggestion(
        "Experience building RESTful APIs",
        "Built APIs using Python and FastAPI.",
        fake_client,
    )

    assert result.suggested_text == "Developed RESTful APIs using Python and FastAPI."
    assert fake_client.last_prompt is not None
    assert "Experience building RESTful APIs" in fake_client.last_prompt
    assert "Built APIs using Python and FastAPI." in fake_client.last_prompt
    assert "must not add any employer" in fake_client.last_prompt
