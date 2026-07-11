from pathlib import Path

from app.llm.base import LLMClient
from app.schemas.job import JobRequirementExtraction

PROMPT_VERSION = "jd_extraction_v1"
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "jd_extraction.md"


def _render_prompt(job_text: str) -> str:
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(job_text=job_text)


async def extract_job_requirements(
    job_text: str, llm_client: LLMClient
) -> JobRequirementExtraction:
    prompt = _render_prompt(job_text)
    return await llm_client.generate_structured(
        prompt, JobRequirementExtraction, temperature=0.0
    )
