from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.resumes import _llm_client_dependency
from app.core.config import Settings, get_settings
from app.llm.base import LLMClient, SchemaT
from app.main import app
from app.schemas.resume import CandidateProfileExtraction, SkillItem

FIXTURES = Path(__file__).parent.parent / "fixtures"


class FakeLLMClient(LLMClient):
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        return CandidateProfileExtraction(skills=[SkillItem(name="Python")])  # type: ignore[return-value]


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(tmp_path))

    app.dependency_overrides[get_settings] = _override_settings
    app.dependency_overrides[_llm_client_dependency] = lambda: FakeLLMClient()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_upload_valid_pdf_is_accepted(client: TestClient) -> None:
    content = (FIXTURES / "sample_resume.pdf").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("sample_resume.pdf", content, "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "sample_resume.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["size_bytes"] == len(content)
    assert body["status"] == "uploaded"
    assert "Jordan Sample" in body["extracted_text"]
    assert body["candidate_profile"]["skills"] == [{"name": "Python", "category": None}]


def test_upload_valid_docx_is_accepted(client: TestClient) -> None:
    content = (FIXTURES / "sample_resume.docx").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "sample_resume.docx",
                content,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["content_type"] == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_upload_unsupported_file_type_is_rejected(client: TestClient) -> None:
    content = (FIXTURES / "not_a_resume.txt").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("not_a_resume.txt", content, "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_upload_empty_file_is_rejected(client: TestClient) -> None:
    content = (FIXTURES / "empty.pdf").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("empty.pdf", content, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


def test_upload_corrupt_pdf_is_rejected(client: TestClient) -> None:
    content = (FIXTURES / "corrupt.pdf").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("corrupt.pdf", content, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_DOCUMENT"


def test_upload_oversized_file_is_rejected(client: TestClient) -> None:
    def _override_settings() -> Settings:
        return Settings(upload_storage_dir=str(FIXTURES), max_upload_size_mb=0)

    app.dependency_overrides[get_settings] = _override_settings
    content = (FIXTURES / "sample_resume.pdf").read_bytes()

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("sample_resume.pdf", content, "application/pdf")},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"
