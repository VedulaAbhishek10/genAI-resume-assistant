import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.resumes import _llm_client_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.models.candidate import CandidateProfile, Skill
from app.models.resume import Resume
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
            experiences=[ExperienceItem(employer="Example Corp", job_title="Senior Engineer")],
            skills=[SkillItem(name="Python")],
        )
        return result  # type: ignore[return-value]


@pytest.fixture
async def db_session_factory() -> AsyncGenerator[async_sessionmaker]:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def test_upload_persists_candidate_profile_and_resume(
    tmp_path: Path, db_session_factory: async_sessionmaker
) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    app.dependency_overrides[_llm_client_dependency] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            content = (FIXTURES / "sample_resume.pdf").read_bytes()
            response = await client.post(
                "/api/v1/resumes",
                files={"file": ("sample_resume.pdf", content, "application/pdf")},
            )

        assert response.status_code == 201
        resume_id = uuid.UUID(response.json()["id"])

        async with db_session_factory() as session:
            resume = await session.get(Resume, resume_id)
            assert resume is not None
            assert resume.filename == "sample_resume.pdf"
            assert resume.document_type == "pdf"
            assert "Jordan Sample" in resume.extracted_text

            candidate_profile = await session.get(CandidateProfile, resume.candidate_profile_id)
            assert candidate_profile is not None
            assert candidate_profile.professional_summary == "Experienced engineer."

            skills = (
                (
                    await session.execute(
                        select(Skill).where(Skill.candidate_profile_id == candidate_profile.id)
                    )
                )
                .scalars()
                .all()
            )
            assert [skill.name for skill in skills] == ["Python"]
    finally:
        app.dependency_overrides.clear()
