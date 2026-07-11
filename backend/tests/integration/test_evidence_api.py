import uuid
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from app.api.resumes import _llm_client_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.resume import CandidateProfileExtraction, ExperienceItem, SkillItem

FIXTURES = Path(__file__).parent.parent / "fixtures"


class FakeLLMClient(LLMClient):
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        result = CandidateProfileExtraction(
            professional_summary="Experienced engineer.",
            experiences=[
                ExperienceItem(
                    employer="Example Corp",
                    job_title="Senior Engineer",
                    achievements=["Shipped a major feature"],
                )
            ],
            skills=[SkillItem(name="Python")],
        )
        return result  # type: ignore[return-value]


async def test_list_evidence_for_uploaded_resume(tmp_path: Path) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    app.dependency_overrides[_llm_client_dependency] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            content = (FIXTURES / "sample_resume.pdf").read_bytes()
            upload_response = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", content, "application/pdf")},
            )
            assert upload_response.status_code == 201
            candidate_profile_id = upload_response.json()["candidate_profile_id"]

            evidence_response = await client.get(
                f"/api/v1/candidate-profiles/{candidate_profile_id}/evidence"
            )

        assert evidence_response.status_code == 200
        evidence = evidence_response.json()
        texts = {item["text"] for item in evidence}
        assert "Shipped a major feature" in texts
        assert "Python" in texts
        for item in evidence:
            assert item["candidate_profile_id"] == candidate_profile_id
            assert item["source_entity_id"]
            assert item["source_entity_type"]
    finally:
        app.dependency_overrides.clear()


async def test_list_evidence_for_unknown_profile_returns_404(tmp_path: Path) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/candidate-profiles/{uuid.uuid4()}/evidence")

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
