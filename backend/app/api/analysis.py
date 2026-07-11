import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.db.session import DbDep
from app.llm.base import LLMClient
from app.llm.provider import get_llm_client
from app.schemas.matching import MatchAnalysisResponse
from app.services.match_analysis_service import run_match_analysis

router = APIRouter(prefix="/match-analyses", tags=["matching"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _llm_client_dependency(settings: SettingsDep) -> LLMClient:
    return get_llm_client(settings)


LLMClientDep = Annotated[LLMClient, Depends(_llm_client_dependency)]


class MatchAnalysisRequest(BaseModel):
    candidate_profile_id: uuid.UUID
    job_description_id: uuid.UUID


@router.post("", status_code=201, response_model=MatchAnalysisResponse)
async def create_match_analysis(
    request: MatchAnalysisRequest,
    db: DbDep,
    llm_client: LLMClientDep,
    settings: SettingsDep,
) -> MatchAnalysisResponse:
    return await run_match_analysis(
        db,
        candidate_profile_id=request.candidate_profile_id,
        job_description_id=request.job_description_id,
        llm_client=llm_client,
        settings=settings,
    )
