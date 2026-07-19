from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GenAI Resume Assistant"
    app_env: str = "development"
    log_level: str = "INFO"

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_device: str = "cpu"
    retrieval_top_k: int = 5

    max_upload_size_mb: int = 10
    upload_storage_dir: str = "data/uploads"

    # Origins allowed to call the API from a browser (the frontend dev server by
    # default). Override with a JSON array via CORS_ALLOWED_ORIGINS if needed.
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/resume_assistant"

    # Deterministic match-scoring weights (see docs/ROADMAP.md M5.3); must sum to 1.0
    # across whichever components are actually present for a given analysis.
    weight_required_skills: float = 0.30
    weight_experience_alignment: float = 0.25
    weight_responsibility_alignment: float = 0.20
    weight_preferred_skills: float = 0.10
    weight_education_certifications: float = 0.05
    weight_semantic_evidence_quality: float = 0.10

    @property
    def scoring_weights(self) -> dict[str, float]:
        return {
            "required_skills": self.weight_required_skills,
            "experience_alignment": self.weight_experience_alignment,
            "responsibility_alignment": self.weight_responsibility_alignment,
            "preferred_skills": self.weight_preferred_skills,
            "education_certifications": self.weight_education_certifications,
            "semantic_evidence_quality": self.weight_semantic_evidence_quality,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
