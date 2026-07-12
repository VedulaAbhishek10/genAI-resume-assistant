from pathlib import Path

from httpx import ASGITransport, AsyncClient

from app.api.analysis import _llm_client_dependency as analysis_llm_dependency
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
                company="Initech",
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
                reason="Aligns terminology with the requirement.",
                confidence=0.88,
            )
        else:
            raise AssertionError(f"Unexpected schema requested: {schema}")

        return result  # type: ignore[return-value]


async def _setup_candidate_and_job(client: AsyncClient) -> tuple[str, str]:
    resume_content = (FIXTURES / "sample_resume.pdf").read_bytes()
    resume_response = await client.post(
        "/api/v1/resumes",
        files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
    )
    candidate_profile_id: str = resume_response.json()["candidate_profile_id"]

    job_response = await client.post(
        "/api/v1/jobs",
        json={"text": "Backend Engineer role requiring Python API experience."},
    )
    job_description_id: str = job_response.json()["id"]
    return candidate_profile_id, job_description_id


async def test_create_list_get_and_update_application(tmp_path: Path) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    for dep in (resumes_llm_dependency, jobs_llm_dependency, analysis_llm_dependency):
        app.dependency_overrides[dep] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            candidate_profile_id, job_description_id = await _setup_candidate_and_job(client)

            create_response = await client.post(
                "/api/v1/applications",
                json={
                    "candidate_profile_id": candidate_profile_id,
                    "job_description_id": job_description_id,
                },
            )
            assert create_response.status_code == 201
            application = create_response.json()
            # company/role default from the job description when not provided.
            assert application["company"] == "Initech"
            assert application["role"] == "Backend Engineer"
            assert application["status"] == "SAVED"

            list_response = await client.get(
                "/api/v1/applications", params={"candidate_profile_id": candidate_profile_id}
            )
            assert list_response.status_code == 200
            assert len(list_response.json()) == 1

            get_response = await client.get(f"/api/v1/applications/{application['id']}")
            assert get_response.status_code == 200

            update_response = await client.patch(
                f"/api/v1/applications/{application['id']}",
                json={"status": "APPLIED", "notes": "Submitted via referral."},
            )
            assert update_response.status_code == 200
            updated = update_response.json()
            assert updated["status"] == "APPLIED"
            assert updated["notes"] == "Submitted via referral."
    finally:
        app.dependency_overrides.clear()


async def test_update_application_with_mismatched_resume_version_returns_400(
    tmp_path: Path,
) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    for dep in (resumes_llm_dependency, jobs_llm_dependency, analysis_llm_dependency):
        app.dependency_overrides[dep] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # A resume version generated for one job description...
            resume_content = (FIXTURES / "sample_resume.pdf").read_bytes()
            resume_response = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
            )
            resume_id = resume_response.json()["id"]
            candidate_profile_id = resume_response.json()["candidate_profile_id"]

            first_job_response = await client.post(
                "/api/v1/jobs",
                json={"text": "Backend Engineer role requiring Python API experience."},
            )
            first_job_id = first_job_response.json()["id"]

            analysis_response = await client.post(
                "/api/v1/match-analyses",
                json={
                    "candidate_profile_id": candidate_profile_id,
                    "job_description_id": first_job_id,
                },
            )
            match_analysis_id = analysis_response.json()["id"]

            version_response = await client.post(
                f"/api/v1/resumes/{resume_id}/versions",
                json={"match_analysis_id": match_analysis_id},
            )
            resume_version_id = version_response.json()["id"]

            # ...cannot be attached to an application for a different job description.
            _, second_job_id = await _setup_candidate_and_job(client)
            application_response = await client.post(
                "/api/v1/applications",
                json={
                    "candidate_profile_id": candidate_profile_id,
                    "job_description_id": second_job_id,
                },
            )
            application_id = application_response.json()["id"]

            response = await client.patch(
                f"/api/v1/applications/{application_id}",
                json={"resume_version_id": resume_version_id},
            )
            assert response.status_code == 400
            assert response.json()["error"]["code"] == "INVALID_REQUEST"
    finally:
        app.dependency_overrides.clear()


async def test_get_unknown_application_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/applications/00000000-0000-0000-0000-000000000000"
        )
    assert response.status_code == 404
