import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.db.session import DbDep
from app.models.candidate import CandidateProfile
from app.models.evidence import CandidateEvidence
from app.schemas.evidence import CandidateEvidenceRead

router = APIRouter(prefix="/candidate-profiles", tags=["candidate-evidence"])


@router.get(
    "/{candidate_profile_id}/evidence",
    response_model=list[CandidateEvidenceRead],
)
async def list_candidate_evidence(
    candidate_profile_id: uuid.UUID, db: DbDep
) -> list[CandidateEvidence]:
    profile = await db.get(CandidateProfile, candidate_profile_id)
    if profile is None:
        raise NotFoundError(f"Candidate profile '{candidate_profile_id}' was not found.")

    result = await db.execute(
        select(CandidateEvidence)
        .where(CandidateEvidence.candidate_profile_id == candidate_profile_id)
        .order_by(CandidateEvidence.created_at)
    )
    return list(result.scalars().all())
