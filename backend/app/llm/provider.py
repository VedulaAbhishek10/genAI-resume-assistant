from app.core.config import Settings
from app.llm.base import LLMClient
from app.llm.ollama import OllamaClient


def get_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "ollama":
        return OllamaClient(base_url=settings.ollama_base_url, model=settings.ollama_model)
    raise ValueError(f"Unsupported LLM provider: '{settings.llm_provider}'")
