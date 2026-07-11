from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.session import DbDep
from app.llm.base import LLMClient
from app.llm.provider import get_llm_client
from app.schemas.job import JobDescriptionResponse, JobSubmissionRequest
from app.services.jd_analyzer import extract_job_requirements
from app.services.job_persistence import persist_job_description

router = APIRouter(prefix="/jobs", tags=["jobs"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _llm_client_dependency(settings: SettingsDep) -> LLMClient:
    return get_llm_client(settings)


LLMClientDep = Annotated[LLMClient, Depends(_llm_client_dependency)]


@router.post("", status_code=201, response_model=JobDescriptionResponse)
async def submit_job(
    submission: JobSubmissionRequest,
    llm_client: LLMClientDep,
    db: DbDep,
) -> JobDescriptionResponse:
    extraction = await extract_job_requirements(submission.text, llm_client)
    job_description = await persist_job_description(db, submission.text, extraction)
    return JobDescriptionResponse.model_validate(job_description)
