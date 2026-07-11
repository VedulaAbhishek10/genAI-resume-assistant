import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.evidence import CandidateEvidence
from app.services.embedding_service import embed_text_async


async def retrieve_relevant_evidence(
    db: AsyncSession,
    candidate_profile_id: uuid.UUID,
    query_text: str,
    settings: Settings,
    top_k: int | None = None,
) -> list[tuple[CandidateEvidence, float]]:
    """Retrieve the top-K candidate evidence units most semantically similar to a query.

    Returns `(evidence, cosine_distance)` pairs ordered by ascending distance (most
    similar first). Evidence without an embedding is excluded.
    """
    k = top_k if top_k is not None else settings.retrieval_top_k
    query_embedding = await embed_text_async(query_text, settings)

    distance = CandidateEvidence.embedding.cosine_distance(query_embedding).label("distance")
    stmt = (
        select(CandidateEvidence, distance)
        .where(CandidateEvidence.candidate_profile_id == candidate_profile_id)
        .where(CandidateEvidence.embedding.is_not(None))
        .order_by(distance)
        .limit(k)
    )
    result = await db.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]
