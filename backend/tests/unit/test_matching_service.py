import uuid

from app.llm.base import LLMClient, SchemaT
from app.models.evidence import CandidateEvidence
from app.schemas.matching import MatchClassification, RequirementMatchExtraction
from app.services.matching_service import classify_requirement_match


def _evidence(text: str) -> CandidateEvidence:
    return CandidateEvidence(
        id=uuid.uuid4(),
        candidate_profile_id=uuid.uuid4(),
        evidence_type="skill",
        source_entity_type="skill",
        source_entity_id=uuid.uuid4(),
        text=text,
        evidence_metadata={},
    )


class FakeLLMClient(LLMClient):
    def __init__(self, result: RequirementMatchExtraction) -> None:
        self.result = result
        self.last_prompt: str | None = None

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        self.last_prompt = prompt
        assert schema is RequirementMatchExtraction
        return self.result  # type: ignore[return-value]


async def test_classify_requirement_match_resolves_indices_to_evidence_objects() -> None:
    python_evidence = _evidence("Built backend services in Python.")
    sql_evidence = _evidence("Designed PostgreSQL schemas.")
    fake_client = FakeLLMClient(
        RequirementMatchExtraction(
            classification=MatchClassification.STRONG_MATCH,
            explanation="Matches Python experience.",
            confidence=0.9,
            supporting_evidence_indices=[1],
        )
    )

    extraction, supporting = await classify_requirement_match(
        "Experience with Python", [python_evidence, sql_evidence], fake_client
    )

    assert extraction.classification == MatchClassification.STRONG_MATCH
    assert supporting == [python_evidence]
    assert fake_client.last_prompt is not None
    assert "1. Built backend services in Python." in fake_client.last_prompt
    assert "2. Designed PostgreSQL schemas." in fake_client.last_prompt


async def test_classify_requirement_match_ignores_out_of_range_indices() -> None:
    evidence = _evidence("Some evidence.")
    fake_client = FakeLLMClient(
        RequirementMatchExtraction(
            classification=MatchClassification.PARTIAL_MATCH,
            explanation="Loosely related.",
            confidence=0.4,
            supporting_evidence_indices=[1, 5, 0, -1],
        )
    )

    _extraction, supporting = await classify_requirement_match(
        "Some requirement", [evidence], fake_client
    )

    assert supporting == [evidence]


async def test_classify_requirement_match_with_no_evidence_renders_placeholder() -> None:
    fake_client = FakeLLMClient(
        RequirementMatchExtraction(
            classification=MatchClassification.NO_EVIDENCE,
            explanation="No evidence provided.",
            confidence=1.0,
            supporting_evidence_indices=[],
        )
    )

    extraction, supporting = await classify_requirement_match(
        "Experience with Rust", [], fake_client
    )

    assert extraction.classification == MatchClassification.NO_EVIDENCE
    assert supporting == []
    assert "(no evidence available)" in (fake_client.last_prompt or "")
