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
    ollama_model: str = "llama3.1"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    max_upload_size_mb: int = 10
    upload_storage_dir: str = "data/uploads"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/resume_assistant"


@lru_cache
def get_settings() -> Settings:
    return Settings()
