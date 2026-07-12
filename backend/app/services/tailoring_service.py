import re
from pathlib import Path

from app.llm.base import LLMClient
from app.schemas.generation import BulletSuggestionExtraction

PROMPT_VERSION = "bullet_rewriting_v1"
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bullet_rewriting.md"

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?%?")


def _render_prompt(requirement_text: str, original_text: str) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(requirement_text=requirement_text, original_text=original_text)


async def generate_bullet_suggestion(
    requirement_text: str, original_text: str, llm_client: LLMClient
) -> BulletSuggestionExtraction:
    prompt = _render_prompt(requirement_text, original_text)
    # Moderate temperature: controlled rewriting benefits from some variation, unlike
    # the low-temperature extraction/classification tasks elsewhere (docs/AI_SYSTEM.md).
    return await llm_client.generate_structured(
        prompt, BulletSuggestionExtraction, temperature=0.2
    )


def _extract_numbers(text: str) -> set[str]:
    return set(_NUMBER_PATTERN.findall(text))


def validate_grounding(original_text: str, suggested_text: str) -> bool:
    """Deterministically flag suggested text that introduces unsupported numeric claims.

    Returns True if `suggested_text` appears grounded in `original_text` (introduces no
    numbers/metrics absent from the original), False otherwise. This is a narrow,
    explainable heuristic rather than exhaustive fact-checking — invented metrics
    (percentages, counts, durations) are one of the most common and highest-risk
    hallucination patterns called out in docs/AI_SYSTEM.md, and are the one class of
    fabrication a simple deterministic check can catch reliably without another LLM
    call. A suggestion failing this check should be surfaced for human review, not
    silently discarded (ADR-009).
    """
    return _extract_numbers(suggested_text).issubset(_extract_numbers(original_text))
