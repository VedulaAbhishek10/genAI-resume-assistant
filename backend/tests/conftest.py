import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings


@pytest.fixture(autouse=True)
async def _clean_database() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE resumes, candidate_profiles, experiences, projects, "
                "skills, education, certifications, candidate_evidence, "
                "job_descriptions, job_requirements, match_analyses, "
                "requirement_matches, resume_suggestions RESTART IDENTITY CASCADE"
            )
        )
    await engine.dispose()
