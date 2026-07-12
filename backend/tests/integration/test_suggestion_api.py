from pathlib import Path

from httpx import ASGITransport, AsyncClient

from app.api.analysis import _llm_client_dependency as analysis_llm_dependency
from app.api.generation import _llm_client_dependency as generation_llm_dependency
from app.api.jobs import _llm_client_dependency as jobs_llm_dependency
from app.api.resumes import _llm_client_dependency as resumes_llm_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.generation import BulletSuggestionExtraction
from app.schemas.job import (
    JobRequirementExtraction,
    JobRequirementItem,
    RequirementCategory,
    RequirementImportance,
)
from app.schemas.matching import MatchClassification, RequirementMatchExtraction
from app.schemas.resume import CandidateProfileExtraction, ExperienceItem

FIXTURES = Path(__file__).parent.parent / "fixtures"


class FakeLLMClient(LLMClient):
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        result: (
            CandidateProfileExtraction
            | JobRequirementExtraction
            | RequirementMatchExtraction
            | BulletSuggestionExtraction
        )
        if schema is CandidateProfileExtraction:
            result = CandidateProfileExtraction(
                experiences=[
                    ExperienceItem(
                        employer="Acme",
                        job_title="Engineer",
                        achievements=["Built APIs using Python and FastAPI."],
                    )
                ],
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
                ],
            )
        elif schema is RequirementMatchExtraction:
            result = RequirementMatchExtraction(
                classification=MatchClassification.STRONG_MATCH,
                explanation="Evidence directly shows Python API development.",
                confidence=0.9,
                supporting_evidence_indices=[1],
            )
        elif schema is BulletSuggestionExtraction:
            result = BulletSuggestionExtraction(
                suggested_text="Developed RESTful APIs in Python using FastAPI.",
                reason="Aligns terminology ('developed', 'RESTful') with the requirement.",
                confidence=0.88,
            )
        else:
            raise AssertionError(f"Unexpected schema requested: {schema}")

        return result  # type: ignore[return-value]


async def _run_pipeline_to_match_analysis(client: AsyncClient) -> str:
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
    match_analysis_id: str = analysis_response.json()["id"]
    return match_analysis_id


async def test_generate_list_and_review_suggestions(tmp_path: Path) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    for dep in (
        resumes_llm_dependency,
        jobs_llm_dependency,
        analysis_llm_dependency,
        generation_llm_dependency,
    ):
        app.dependency_overrides[dep] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            match_analysis_id = await _run_pipeline_to_match_analysis(client)

            create_response = await client.post(
                f"/api/v1/match-analyses/{match_analysis_id}/suggestions"
            )
            assert create_response.status_code == 201
            suggestions = create_response.json()
            assert len(suggestions) == 1
            suggestion = suggestions[0]
            assert suggestion["original_text"] == "Built APIs using Python and FastAPI."
            assert suggestion["suggested_text"] == (
                "Developed RESTful APIs in Python using FastAPI."
            )
            assert suggestion["review_status"] == "PENDING"
            assert suggestion["is_grounded"] is True

            list_response = await client.get(
                f"/api/v1/match-analyses/{match_analysis_id}/suggestions"
            )
            assert list_response.status_code == 200
            assert len(list_response.json()) == 1

            suggestion_id = suggestion["id"]

            accept_response = await client.patch(
                f"/api/v1/suggestions/{suggestion_id}",
                json={"review_status": "ACCEPTED"},
            )
            assert accept_response.status_code == 200
            assert accept_response.json()["review_status"] == "ACCEPTED"

            edit_response = await client.patch(
                f"/api/v1/suggestions/{suggestion_id}",
                json={
                    "review_status": "EDITED",
                    "edited_text": "Built and deployed RESTful APIs in Python with FastAPI.",
                },
            )
            assert edit_response.status_code == 200
            edited_body = edit_response.json()
            assert edited_body["review_status"] == "EDITED"
            assert edited_body["edited_text"] == (
                "Built and deployed RESTful APIs in Python with FastAPI."
            )
            # The suggestion's own original_text is preserved verbatim — review
            # actions never rewrite it, only the review_status/edited_text fields.
            assert edited_body["original_text"] == "Built APIs using Python and FastAPI."
    finally:
        app.dependency_overrides.clear()


async def test_review_rejects_edited_status_without_edited_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            "/api/v1/suggestions/00000000-0000-0000-0000-000000000000",
            json={"review_status": "EDITED"},
        )

    assert response.status_code == 422


async def test_review_unknown_suggestion_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            "/api/v1/suggestions/00000000-0000-0000-0000-000000000000",
            json={"review_status": "ACCEPTED"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
