from pathlib import Path

from httpx import ASGITransport, AsyncClient

from app.api.analysis import _llm_client_dependency as analysis_llm_dependency
from app.api.jobs import _llm_client_dependency as jobs_llm_dependency
from app.api.resumes import _llm_client_dependency as resumes_llm_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.job import (
    JobRequirementExtraction,
    JobRequirementItem,
    RequirementCategory,
    RequirementImportance,
)
from app.schemas.matching import MatchClassification, RequirementMatchExtraction
from app.schemas.resume import CandidateProfileExtraction, ExperienceItem, SkillItem

FIXTURES = Path(__file__).parent.parent / "fixtures"


class FakeLLMClient(LLMClient):
    """Dispatches by requested schema so one fake covers extraction + matching."""

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        result: (
            CandidateProfileExtraction | JobRequirementExtraction | RequirementMatchExtraction
        )
        if schema is CandidateProfileExtraction:
            result = CandidateProfileExtraction(
                experiences=[
                    ExperienceItem(
                        employer="Acme",
                        job_title="Engineer",
                        achievements=["Built production APIs using Python and FastAPI."],
                    )
                ],
                skills=[SkillItem(name="Python"), SkillItem(name="SQL")],
            )
        elif schema is JobRequirementExtraction:
            result = JobRequirementExtraction(
                role_title="Backend Engineer",
                requirements=[
                    JobRequirementItem(
                        text="Experience building APIs with Python",
                        category=RequirementCategory.SKILL,
                        importance=RequirementImportance.REQUIRED,
                    ),
                    JobRequirementItem(
                        text="Experience with Rust",
                        category=RequirementCategory.SKILL,
                        importance=RequirementImportance.PREFERRED,
                    ),
                ],
            )
        elif schema is RequirementMatchExtraction:
            # Distinguish which requirement is being classified by its requirement
            # text specifically — evidence for the *other* requirement may also
            # mention "Python", but only the Rust requirement's own text mentions
            # "Rust", so checking for that is unambiguous.
            if "Rust" in prompt:
                result = RequirementMatchExtraction(
                    classification=MatchClassification.NO_EVIDENCE,
                    explanation="No evidence of Rust experience.",
                    confidence=0.95,
                    supporting_evidence_indices=[],
                )
            else:
                result = RequirementMatchExtraction(
                    classification=MatchClassification.STRONG_MATCH,
                    explanation="Evidence directly shows Python API development.",
                    confidence=0.9,
                    supporting_evidence_indices=[1],
                )
        else:
            raise AssertionError(f"Unexpected schema requested: {schema}")

        return result  # type: ignore[return-value]


async def test_full_match_analysis_pipeline(tmp_path: Path) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    app.dependency_overrides[resumes_llm_dependency] = lambda: FakeLLMClient()
    app.dependency_overrides[jobs_llm_dependency] = lambda: FakeLLMClient()
    app.dependency_overrides[analysis_llm_dependency] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resume_content = (FIXTURES / "sample_resume.pdf").read_bytes()
            resume_response = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
            )
            assert resume_response.status_code == 201
            candidate_profile_id = resume_response.json()["candidate_profile_id"]

            job_response = await client.post(
                "/api/v1/jobs",
                json={"text": "Backend Engineer role requiring Python API experience."},
            )
            assert job_response.status_code == 201
            job_description_id = job_response.json()["id"]

            analysis_response = await client.post(
                "/api/v1/match-analyses",
                json={
                    "candidate_profile_id": candidate_profile_id,
                    "job_description_id": job_description_id,
                },
            )

        assert analysis_response.status_code == 201
        body = analysis_response.json()
        assert body["candidate_profile_id"] == candidate_profile_id
        assert body["job_description_id"] == job_description_id
        assert len(body["requirement_matches"]) == 2

        strong = next(
            m for m in body["requirement_matches"] if m["classification"] == "STRONG_MATCH"
        )
        no_evidence = next(
            m for m in body["requirement_matches"] if m["classification"] == "NO_EVIDENCE"
        )
        assert "Python" in strong["requirement_text"]
        assert "Rust" in no_evidence["requirement_text"]
        assert len(strong["evidence"]) == 1

        # Gap analysis: the NO_EVIDENCE requirement is a gap even though it's only
        # "preferred"; the STRONG_MATCH requirement is not.
        gap_texts = {gap["requirement_text"] for gap in body["gaps"]}
        assert no_evidence["requirement_text"] in gap_texts
        assert strong["requirement_text"] not in gap_texts

        assert 0.0 <= body["overall_score"] <= 1.0
        assert "required_skills" in body["component_scores"]
    finally:
        app.dependency_overrides.clear()
