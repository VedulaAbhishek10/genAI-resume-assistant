import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.core.exceptions import NotFoundError
from app.db.session import DbDep
from app.models.candidate import CandidateProfile
from app.models.evidence import CandidateEvidence
from app.schemas.evidence import CandidateEvidenceRead, RetrievedEvidence
from app.services.retrieval_service import retrieve_relevant_evidence

router = APIRouter(prefix="/candidate-profiles", tags=["candidate-evidence"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def _get_profile_or_404(candidate_profile_id: uuid.UUID, db: DbDep) -> CandidateProfile:
    profile = await db.get(CandidateProfile, candidate_profile_id)
    if profile is None:
        raise NotFoundError(f"Candidate profile '{candidate_profile_id}' was not found.")
    return profile


@router.get(
    "/{candidate_profile_id}/evidence",
    response_model=list[CandidateEvidenceRead],
)
async def list_candidate_evidence(
    candidate_profile_id: uuid.UUID, db: DbDep
) -> list[CandidateEvidence]:
    await _get_profile_or_404(candidate_profile_id, db)

    result = await db.execute(
        select(CandidateEvidence)
        .where(CandidateEvidence.candidate_profile_id == candidate_profile_id)
        .order_by(CandidateEvidence.created_at)
    )
    return list(result.scalars().all())


@router.get(
    "/{candidate_profile_id}/retrieve",
    response_model=list[RetrievedEvidence],
)
async def retrieve_evidence_for_query(
    candidate_profile_id: uuid.UUID,
    db: DbDep,
    settings: SettingsDep,
    query: Annotated[str, Query(min_length=1)],
    top_k: Annotated[int | None, Query(ge=1, le=50)] = None,
) -> list[RetrievedEvidence]:
    await _get_profile_or_404(candidate_profile_id, db)

    results = await retrieve_relevant_evidence(db, candidate_profile_id, query, settings, top_k)
    return [
        RetrievedEvidence(
            evidence=CandidateEvidenceRead.model_validate(evidence),
            similarity=1.0 - distance,
        )
        for evidence, distance in results
    ]
