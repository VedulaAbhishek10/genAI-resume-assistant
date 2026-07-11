from pathlib import Path

from app.llm.base import LLMClient
from app.schemas.resume import CandidateProfileExtraction

PROMPT_VERSION = "resume_extraction_v1"
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "resume_extraction.md"


def _render_prompt(resume_text: str) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(resume_text=resume_text)


async def extract_candidate_profile(
    resume_text: str, llm_client: LLMClient
) -> CandidateProfileExtraction:
    prompt = _render_prompt(resume_text)
    return await llm_client.generate_structured(
        prompt, CandidateProfileExtraction, temperature=0.0
    )
