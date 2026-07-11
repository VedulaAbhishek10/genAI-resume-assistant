from pathlib import Path

from app.llm.base import LLMClient
from app.models.evidence import CandidateEvidence
from app.schemas.matching import RequirementMatchExtraction

PROMPT_VERSION = "evidence_matching_v1"
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "evidence_matching.md"


def _render_evidence_list(evidence_items: list[CandidateEvidence]) -> str:
    if not evidence_items:
        return "(no evidence available)"
    return "\n".join(f"{index}. {item.text}" for index, item in enumerate(evidence_items, start=1))


def _render_prompt(requirement_text: str, evidence_items: list[CandidateEvidence]) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(
        requirement_text=requirement_text,
        evidence_list=_render_evidence_list(evidence_items),
    )


async def classify_requirement_match(
    requirement_text: str,
    evidence_items: list[CandidateEvidence],
    llm_client: LLMClient,
) -> tuple[RequirementMatchExtraction, list[CandidateEvidence]]:
    """Classify a job requirement against retrieved evidence.

    Returns the LLM's classification along with the actual evidence objects it
    referenced (resolved from the 1-based indices it returned, out-of-range indices
    silently ignored) — the caller never has to trust LLM-produced identifiers.
    """
    prompt = _render_prompt(requirement_text, evidence_items)
    extraction = await llm_client.generate_structured(
        prompt, RequirementMatchExtraction, temperature=0.0
    )

    supporting_evidence = [
        evidence_items[index - 1]
        for index in extraction.supporting_evidence_indices
        if 1 <= index <= len(evidence_items)
    ]
    return extraction, supporting_evidence
