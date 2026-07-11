from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMClient(ABC):
    """Provider-agnostic interface for all LLM interactions (see docs/AI_SYSTEM.md)."""

    @abstractmethod
    async def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        """Generate free-form text for a prompt."""

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: type[SchemaT], *, temperature: float = 0.0
    ) -> SchemaT:
        """Generate a response validated against the given Pydantic schema."""
