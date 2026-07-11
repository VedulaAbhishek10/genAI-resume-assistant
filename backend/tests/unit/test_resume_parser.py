from app.llm.base import LLMClient, SchemaT
from app.schemas.resume import CandidateProfileExtraction, SkillItem
from app.services.resume_parser import extract_candidate_profile


class FakeLLMClient(LLMClient):
    def __init__(self, structured_result: CandidateProfileExtraction) -> None:
        self.structured_result = structured_result
        self.last_prompt: str | None = None

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        self.last_prompt = prompt
        assert schema is CandidateProfileExtraction
        return self.structured_result  # type: ignore[return-value]


async def test_extract_candidate_profile_returns_llm_result_and_includes_resume_text() -> None:
    expected = CandidateProfileExtraction(skills=[SkillItem(name="Python")])
    fake_client = FakeLLMClient(expected)

    result = await extract_candidate_profile("Jordan Sample\nSkills: Python", fake_client)

    assert result is expected
    assert fake_client.last_prompt is not None
    assert "Jordan Sample" in fake_client.last_prompt
    assert "Do not invent employers" in fake_client.last_prompt
