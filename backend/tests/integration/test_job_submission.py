from httpx import ASGITransport, AsyncClient

from app.api.jobs import _llm_client_dependency
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.job import (
    JobRequirementExtraction,
    JobRequirementItem,
    RequirementCategory,
    RequirementImportance,
)


class FakeLLMClient(LLMClient):
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        result = JobRequirementExtraction(
            role_title="Senior Backend Engineer",
            company="Example Corp",
            seniority="senior",
            requirements=[
                JobRequirementItem(
                    text="5+ years of Python experience",
                    category=RequirementCategory.EXPERIENCE,
                    importance=RequirementImportance.REQUIRED,
                ),
                JobRequirementItem(
                    text="Experience with Kubernetes",
                    category=RequirementCategory.SKILL,
                    importance=RequirementImportance.PREFERRED,
                ),
            ],
        )
        return result  # type: ignore[return-value]


async def test_submit_job_extracts_and_persists_requirements() -> None:
    app.dependency_overrides[_llm_client_dependency] = lambda: FakeLLMClient()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/jobs",
                json={
                    "text": (
                        "Senior Backend Engineer at Example Corp. Requirements: 5+ years "
                        "of Python experience. Preferred: Experience with Kubernetes."
                    )
                },
            )

        assert response.status_code == 201
        body = response.json()
        assert body["role_title"] == "Senior Backend Engineer"
        assert body["company"] == "Example Corp"
        assert body["seniority"] == "senior"
        assert len(body["requirements"]) == 2

        required = next(r for r in body["requirements"] if r["importance"] == "required")
        preferred = next(r for r in body["requirements"] if r["importance"] == "preferred")
        assert required["category"] == "experience"
        assert preferred["category"] == "skill"
    finally:
        app.dependency_overrides.clear()


async def test_submit_job_rejects_blank_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/jobs", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_submit_job_rejects_missing_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/jobs", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
