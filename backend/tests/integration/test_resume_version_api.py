import io
from pathlib import Path

import fitz
from docx import Document as DocxDocument
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


async def test_create_list_get_and_export_resume_version(tmp_path: Path) -> None:
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
            resume_content = (FIXTURES / "sample_resume.pdf").read_bytes()
            resume_response = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
            )
            assert resume_response.status_code == 201
            resume_id = resume_response.json()["id"]

            job_response = await client.post(
                "/api/v1/jobs",
                json={"text": "Backend Engineer role requiring Python API experience."},
            )
            job_description_id = job_response.json()["id"]

            analysis_response = await client.post(
                "/api/v1/match-analyses",
                json={
                    "candidate_profile_id": resume_response.json()["candidate_profile_id"],
                    "job_description_id": job_description_id,
                },
            )
            match_analysis_id = analysis_response.json()["id"]

            suggestions_response = await client.post(
                f"/api/v1/match-analyses/{match_analysis_id}/suggestions"
            )
            suggestion = suggestions_response.json()[0]
            await client.patch(
                f"/api/v1/suggestions/{suggestion['id']}",
                json={"review_status": "ACCEPTED"},
            )

            create_response = await client.post(
                f"/api/v1/resumes/{resume_id}/versions",
                json={"match_analysis_id": match_analysis_id},
            )
            assert create_response.status_code == 201
            version = create_response.json()
            assert version["resume_id"] == resume_id
            assert version["job_description_id"] == job_description_id
            assert len(version["applied_suggestion_ids"]) == 1
            experiences = version["generated_content"]["experiences"]
            assert experiences[0]["achievements"] == [
                "Developed RESTful APIs in Python using FastAPI."
            ]

            list_response = await client.get(f"/api/v1/resumes/{resume_id}/versions")
            assert list_response.status_code == 200
            assert len(list_response.json()) == 1

            get_response = await client.get(f"/api/v1/resume-versions/{version['id']}")
            assert get_response.status_code == 200

            docx_response = await client.get(
                f"/api/v1/resume-versions/{version['id']}/export/docx"
            )
            assert docx_response.status_code == 200
            assert docx_response.headers["content-type"].startswith(
                "application/vnd.openxmlformats"
            )
            docx_document = DocxDocument(io.BytesIO(docx_response.content))
            docx_text = "\n".join(p.text for p in docx_document.paragraphs)
            assert "Developed RESTful APIs in Python using FastAPI." in docx_text

            pdf_response = await client.get(
                f"/api/v1/resume-versions/{version['id']}/export/pdf"
            )
            assert pdf_response.status_code == 200
            assert pdf_response.headers["content-type"] == "application/pdf"
            assert pdf_response.content.startswith(b"%PDF")
            with fitz.open(stream=pdf_response.content, filetype="pdf") as pdf_document:
                pdf_text = "\n".join(page.get_text() for page in pdf_document)
            assert "Developed RESTful APIs" in pdf_text
    finally:
        app.dependency_overrides.clear()


async def test_create_version_with_mismatched_resume_and_analysis_returns_400(
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
            resume_content = (FIXTURES / "sample_resume.pdf").read_bytes()
            first_resume = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
            )
            second_resume = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", resume_content, "application/pdf")},
            )

            job_response = await client.post(
                "/api/v1/jobs",
                json={"text": "Backend Engineer role requiring Python API experience."},
            )

            analysis_response = await client.post(
                "/api/v1/match-analyses",
                json={
                    "candidate_profile_id": first_resume.json()["candidate_profile_id"],
                    "job_description_id": job_response.json()["id"],
                },
            )

            response = await client.post(
                f"/api/v1/resumes/{second_resume.json()['id']}/versions",
                json={"match_analysis_id": analysis_response.json()["id"]},
            )
            assert response.status_code == 400
            assert response.json()["error"]["code"] == "INVALID_REQUEST"
    finally:
        app.dependency_overrides.clear()


async def test_get_unknown_resume_version_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/resume-versions/00000000-0000-0000-0000-000000000000"
        )
    assert response.status_code == 404
