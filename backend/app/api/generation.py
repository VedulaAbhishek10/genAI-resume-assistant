import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.session import DbDep
from app.llm.base import LLMClient
from app.llm.provider import get_llm_client
from app.schemas.generation import ResumeSuggestionRead, ResumeSuggestionUpdateRequest
from app.services.suggestion_service import (
    generate_suggestions_for_analysis,
    list_suggestions_for_analysis,
    update_suggestion_review,
)

router = APIRouter(tags=["suggestions"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _llm_client_dependency(settings: SettingsDep) -> LLMClient:
    return get_llm_client(settings)


LLMClientDep = Annotated[LLMClient, Depends(_llm_client_dependency)]


@router.post(
    "/match-analyses/{match_analysis_id}/suggestions",
    status_code=201,
    response_model=list[ResumeSuggestionRead],
)
async def create_suggestions(
    match_analysis_id: uuid.UUID, db: DbDep, llm_client: LLMClientDep
) -> list[ResumeSuggestionRead]:
    suggestions = await generate_suggestions_for_analysis(db, match_analysis_id, llm_client)
    return [ResumeSuggestionRead.model_validate(s) for s in suggestions]


@router.get(
    "/match-analyses/{match_analysis_id}/suggestions",
    response_model=list[ResumeSuggestionRead],
)
async def list_suggestions(match_analysis_id: uuid.UUID, db: DbDep) -> list[ResumeSuggestionRead]:
    suggestions = await list_suggestions_for_analysis(db, match_analysis_id)
    return [ResumeSuggestionRead.model_validate(s) for s in suggestions]


@router.patch("/suggestions/{suggestion_id}", response_model=ResumeSuggestionRead)
async def review_suggestion(
    suggestion_id: uuid.UUID,
    request: ResumeSuggestionUpdateRequest,
    db: DbDep,
) -> ResumeSuggestionRead:
    suggestion = await update_suggestion_review(
        db, suggestion_id, request.review_status, request.edited_text
    )
    return ResumeSuggestionRead.model_validate(suggestion)
