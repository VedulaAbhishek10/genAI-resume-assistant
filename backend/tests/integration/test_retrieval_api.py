from pathlib import Path

from httpx import ASGITransport, AsyncClient

from app.api.resumes import _llm_client_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.resume import CandidateProfileExtraction, ExperienceItem

FIXTURES = Path(__file__).parent.parent / "fixtures"


class FakeLLMClient(LLMClient):
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        result = CandidateProfileExtraction(
            experiences=[
                ExperienceItem(
                    employer="Acme",
                    job_title="Engineer",
                    achievements=[
                        "Deployed and managed Kubernetes clusters for production workloads.",
                        "Designed and implemented backend services in Python.",
                        "Enjoys watercolor painting as a creative hobby.",
                    ],
                )
            ],
        )
        return result  # type: ignore[return-value]


async def test_retrieve_ranks_semantically_relevant_evidence_first(tmp_path: Path) -> None:
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

            response = await client.get(
                f"/api/v1/candidate-profiles/{candidate_profile_id}/retrieve",
                params={"query": "Experience with container orchestration and Kubernetes"},
            )

        assert response.status_code == 200
        results = response.json()
        assert len(results) == 3
        texts_by_rank = [item["evidence"]["text"] for item in results]
        assert texts_by_rank[0] == (
            "Deployed and managed Kubernetes clusters for production workloads."
        )
        assert texts_by_rank[-1] == "Enjoys watercolor painting as a creative hobby."
        # results are ordered by descending similarity
        similarities = [item["similarity"] for item in results]
        assert similarities == sorted(similarities, reverse=True)
    finally:
        app.dependency_overrides.clear()


async def test_retrieve_for_unknown_profile_returns_404() -> None:
    import uuid

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/candidate-profiles/{uuid.uuid4()}/retrieve",
            params={"query": "anything"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


async def test_retrieve_rejects_blank_query() -> None:
    import uuid

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/candidate-profiles/{uuid.uuid4()}/retrieve",
            params={"query": ""},
        )

    assert response.status_code == 422
