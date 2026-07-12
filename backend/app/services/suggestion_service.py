import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.llm.base import LLMClient
from app.models.evidence import CandidateEvidence
from app.models.job import JobRequirement
from app.models.matching import RequirementMatch
from app.models.suggestion import ResumeSuggestion
from app.schemas.generation import ReviewStatus
from app.services.tailoring_service import generate_bullet_suggestion, validate_grounding

_GROUNDED_CLASSIFICATIONS = ("STRONG_MATCH", "PARTIAL_MATCH")


async def generate_suggestions_for_analysis(
    db: AsyncSession,
    match_analysis_id: uuid.UUID,
    llm_client: LLMClient,
) -> list[ResumeSuggestion]:
    """Generate grounded rewrite suggestions for every evidence-backed match in an analysis.

    Only requirement matches with supporting evidence (STRONG_MATCH/PARTIAL_MATCH)
    produce suggestions — there is nothing to rewrite for a NO_EVIDENCE requirement
    without fabricating content (ADR-008), which is exactly the case the human should
    address by adding real experience, not one the AI should paper over.
    """
    matches_result = await db.execute(
        select(RequirementMatch, JobRequirement)
        .join(JobRequirement, RequirementMatch.job_requirement_id == JobRequirement.id)
        .where(RequirementMatch.match_analysis_id == match_analysis_id)
        .where(RequirementMatch.classification.in_(_GROUNDED_CLASSIFICATIONS))
    )

    suggestions: list[ResumeSuggestion] = []
    for match, requirement in matches_result.all():
        if not match.evidence_ids:
            continue

        for evidence_id in match.evidence_ids:
            evidence = await db.get(CandidateEvidence, uuid.UUID(evidence_id))
            if evidence is None:
                continue

            extraction = await generate_bullet_suggestion(
                requirement.text, evidence.text, llm_client
            )
            is_grounded = validate_grounding(evidence.text, extraction.suggested_text)

            suggestion = ResumeSuggestion(
                id=uuid.uuid4(),
                requirement_match_id=match.id,
                original_text=evidence.text,
                suggested_text=extraction.suggested_text,
                reason=extraction.reason,
                evidence_ids=[str(evidence.id)],
                confidence=extraction.confidence,
                is_grounded=is_grounded,
                review_status="PENDING",
            )
            db.add(suggestion)
            suggestions.append(suggestion)

    await db.commit()
    for suggestion in suggestions:
        await db.refresh(suggestion, attribute_names=["created_at"])
    return suggestions


async def list_suggestions_for_analysis(
    db: AsyncSession, match_analysis_id: uuid.UUID
) -> list[ResumeSuggestion]:
    result = await db.execute(
        select(ResumeSuggestion)
        .join(RequirementMatch, ResumeSuggestion.requirement_match_id == RequirementMatch.id)
        .where(RequirementMatch.match_analysis_id == match_analysis_id)
        .order_by(ResumeSuggestion.created_at)
    )
    return list(result.scalars().all())


async def update_suggestion_review(
    db: AsyncSession,
    suggestion_id: uuid.UUID,
    review_status: ReviewStatus,
    edited_text: str | None,
) -> ResumeSuggestion:
    """Update a suggestion's review status.

    Never touches the underlying CandidateEvidence or resume content (ADR-009) — an
    "EDITED" suggestion just records the human's edited text on the suggestion row
    itself, for use when a tailored resume version is later assembled (Phase 7).
    """
    suggestion = await db.get(ResumeSuggestion, suggestion_id)
    if suggestion is None:
        raise NotFoundError(f"Suggestion '{suggestion_id}' was not found.")

    suggestion.review_status = review_status
    suggestion.edited_text = edited_text if review_status == ReviewStatus.EDITED else None

    await db.commit()
    await db.refresh(suggestion, attribute_names=["review_status", "edited_text"])
    return suggestion
