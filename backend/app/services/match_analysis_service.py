import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.llm.base import LLMClient
from app.models.candidate import CandidateProfile
from app.models.job import JobDescription, JobRequirement
from app.models.matching import MatchAnalysis, RequirementMatch
from app.schemas.evidence import CandidateEvidenceRead
from app.schemas.job import RequirementCategory, RequirementImportance
from app.schemas.matching import GapItem, MatchAnalysisResponse, RequirementMatchRead
from app.services.matching_service import classify_requirement_match
from app.services.retrieval_service import retrieve_relevant_evidence
from app.services.scoring_service import MatchScoringInput, calculate_match_score, identify_gaps


async def run_match_analysis(
    db: AsyncSession,
    candidate_profile_id: uuid.UUID,
    job_description_id: uuid.UUID,
    llm_client: LLMClient,
    settings: Settings,
) -> MatchAnalysisResponse:
    candidate_profile = await db.get(CandidateProfile, candidate_profile_id)
    if candidate_profile is None:
        raise NotFoundError(f"Candidate profile '{candidate_profile_id}' was not found.")

    job_description = await db.get(JobDescription, job_description_id)
    if job_description is None:
        raise NotFoundError(f"Job description '{job_description_id}' was not found.")

    requirements_result = await db.execute(
        select(JobRequirement).where(JobRequirement.job_description_id == job_description_id)
    )
    requirements = list(requirements_result.scalars().all())

    scoring_inputs: list[MatchScoringInput] = []
    gap_candidates: list[GapItem] = []
    requirement_matches: list[RequirementMatch] = []
    requirement_match_reads: list[RequirementMatchRead] = []

    for requirement in requirements:
        retrieved = await retrieve_relevant_evidence(
            db, candidate_profile_id, requirement.text, settings
        )
        evidence_items = [evidence for evidence, _distance in retrieved]

        extraction, supporting_evidence = await classify_requirement_match(
            requirement.text, evidence_items, llm_client
        )

        category = RequirementCategory(requirement.category)
        importance = RequirementImportance(requirement.importance)

        scoring_inputs.append(
            MatchScoringInput(
                category=category,
                importance=importance,
                classification=extraction.classification,
                confidence=extraction.confidence,
            )
        )
        gap_candidates.append(
            GapItem(
                requirement_text=requirement.text,
                category=category,
                importance=importance,
                classification=extraction.classification,
            )
        )

        requirement_match = RequirementMatch(
            id=uuid.uuid4(),
            job_requirement_id=requirement.id,
            classification=extraction.classification,
            explanation=extraction.explanation,
            confidence=extraction.confidence,
            evidence_ids=[str(evidence.id) for evidence in supporting_evidence],
        )
        requirement_matches.append(requirement_match)
        requirement_match_reads.append(
            RequirementMatchRead(
                id=requirement_match.id,
                job_requirement_id=requirement.id,
                requirement_text=requirement.text,
                category=category,
                importance=importance,
                classification=extraction.classification,
                explanation=extraction.explanation,
                confidence=extraction.confidence,
                evidence=[
                    CandidateEvidenceRead.model_validate(evidence)
                    for evidence in supporting_evidence
                ],
            )
        )

    overall_score, component_scores = calculate_match_score(
        scoring_inputs, settings.scoring_weights
    )
    gaps = identify_gaps(gap_candidates)

    match_analysis = MatchAnalysis(
        id=uuid.uuid4(),
        candidate_profile_id=candidate_profile_id,
        job_description_id=job_description_id,
        overall_score=overall_score,
        component_scores=component_scores,
        requirement_matches=requirement_matches,
    )
    db.add(match_analysis)
    await db.commit()
    await db.refresh(match_analysis, attribute_names=["created_at"])

    return MatchAnalysisResponse(
        id=match_analysis.id,
        candidate_profile_id=candidate_profile_id,
        job_description_id=job_description_id,
        overall_score=overall_score,
        component_scores=component_scores,
        requirement_matches=requirement_match_reads,
        gaps=gaps,
        created_at=match_analysis.created_at,
    )
