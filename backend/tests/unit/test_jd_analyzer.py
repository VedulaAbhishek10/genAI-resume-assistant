from app.llm.base import LLMClient, SchemaT
from app.schemas.job import (
    JobRequirementExtraction,
    JobRequirementItem,
    RequirementCategory,
    RequirementImportance,
)
from app.services.jd_analyzer import extract_job_requirements


class FakeLLMClient(LLMClient):
    def __init__(self, result: JobRequirementExtraction) -> None:
        self.result = result
        self.last_prompt: str | None = None

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        self.last_prompt = prompt
        assert schema is JobRequirementExtraction
        return self.result  # type: ignore[return-value]


async def test_extract_job_requirements_includes_job_text_in_prompt() -> None:
    expected = JobRequirementExtraction(
        role_title="Senior Backend Engineer",
        requirements=[
            JobRequirementItem(
                text="5+ years of Python experience",
                category=RequirementCategory.EXPERIENCE,
                importance=RequirementImportance.REQUIRED,
            )
        ],
    )
    fake_client = FakeLLMClient(expected)

    result = await extract_job_requirements(
        "Senior Backend Engineer role requiring 5+ years of Python.", fake_client
    )

    assert result is expected
    assert fake_client.last_prompt is not None
    assert "Senior Backend Engineer role" in fake_client.last_prompt
    assert "Do not invent skills" in fake_client.last_prompt
