import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import InvalidRequestError, NotFoundError
from app.models.candidate import CandidateProfile
from app.models.evidence import CandidateEvidence
from app.models.matching import MatchAnalysis, RequirementMatch
from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.models.suggestion import ResumeSuggestion
from app.schemas.generation import ReviewStatus
from app.schemas.resume_version import (
    CertificationContent,
    EducationContent,
    ExperienceContent,
    GeneratedResumeContent,
    ProjectContent,
    SkillContent,
)

_APPLIED_REVIEW_STATUSES = (ReviewStatus.ACCEPTED.value, ReviewStatus.EDITED.value)

# Keyed by (source_entity_id, original_text) rather than evidence_id alone: a single
# entity (e.g. one Experience) can have multiple achievement bullets, each its own
# evidence row, so the original text disambiguates which bullet a rewrite replaces.
_ReplacementMap = dict[tuple[uuid.UUID, str], str]


async def _load_profile_with_content(
    db: AsyncSession, candidate_profile_id: uuid.UUID
) -> CandidateProfile:
    result = await db.execute(
        select(CandidateProfile)
        .options(
            selectinload(CandidateProfile.experiences),
            selectinload(CandidateProfile.projects),
            selectinload(CandidateProfile.skills),
            selectinload(CandidateProfile.education),
            selectinload(CandidateProfile.certifications),
        )
        .where(CandidateProfile.id == candidate_profile_id)
    )
    return result.scalar_one()


async def _load_applied_suggestions(
    db: AsyncSession, match_analysis_id: uuid.UUID
) -> list[ResumeSuggestion]:
    result = await db.execute(
        select(ResumeSuggestion)
        .join(RequirementMatch, ResumeSuggestion.requirement_match_id == RequirementMatch.id)
        .where(RequirementMatch.match_analysis_id == match_analysis_id)
        .where(ResumeSuggestion.review_status.in_(_APPLIED_REVIEW_STATUSES))
        .order_by(ResumeSuggestion.created_at)
    )
    return list(result.scalars().all())


async def _build_replacement_map(
    db: AsyncSession, suggestions: list[ResumeSuggestion]
) -> _ReplacementMap:
    evidence_ids = {
        uuid.UUID(evidence_id)
        for suggestion in suggestions
        for evidence_id in suggestion.evidence_ids
    }
    evidence_by_id: dict[uuid.UUID, CandidateEvidence] = {}
    if evidence_ids:
        result = await db.execute(
            select(CandidateEvidence).where(CandidateEvidence.id.in_(evidence_ids))
        )
        evidence_by_id = {evidence.id: evidence for evidence in result.scalars().all()}

    replacements: _ReplacementMap = {}
    for suggestion in suggestions:
        final_text = suggestion.suggested_text
        if suggestion.review_status == ReviewStatus.EDITED and suggestion.edited_text:
            final_text = suggestion.edited_text
        for evidence_id in suggestion.evidence_ids:
            evidence = evidence_by_id.get(uuid.UUID(evidence_id))
            if evidence is not None:
                replacements[(evidence.source_entity_id, evidence.text)] = final_text
    return replacements


def _assemble_generated_content(
    profile: CandidateProfile, replacements: _ReplacementMap
) -> GeneratedResumeContent:
    def resolve(entity_id: uuid.UUID, text: str) -> str:
        return replacements.get((entity_id, text), text)

    return GeneratedResumeContent(
        professional_summary=profile.professional_summary,
        experiences=[
            ExperienceContent(
                employer=experience.employer,
                job_title=experience.job_title,
                start_date=experience.start_date,
                end_date=experience.end_date,
                description=(
                    resolve(experience.id, experience.description)
                    if experience.description
                    else None
                ),
                achievements=[
                    resolve(experience.id, achievement) for achievement in experience.achievements
                ],
            )
            for experience in profile.experiences
        ],
        projects=[
            ProjectContent(
                name=project.name,
                description=(
                    resolve(project.id, project.description) if project.description else None
                ),
                technologies=list(project.technologies),
                achievements=[
                    resolve(project.id, achievement) for achievement in project.achievements
                ],
            )
            for project in profile.projects
        ],
        skills=[
            SkillContent(name=resolve(skill.id, skill.name), category=skill.category)
            for skill in profile.skills
        ],
        education=[
            EducationContent(
                institution=education.institution,
                degree=education.degree,
                field_of_study=education.field_of_study,
                dates=education.dates,
                achievements=[
                    resolve(education.id, achievement) for achievement in education.achievements
                ],
            )
            for education in profile.education
        ],
        certifications=[
            CertificationContent(
                name=certification.name,
                issuing_organization=certification.issuing_organization,
                issue_date=certification.issue_date,
            )
            for certification in profile.certifications
        ],
    )


async def create_resume_version(
    db: AsyncSession, resume_id: uuid.UUID, match_analysis_id: uuid.UUID
) -> ResumeVersion:
    """Assemble and persist a job-specific resume version.

    Deterministic: no LLM calls. Combines the master resume's content with every
    ACCEPTED/EDITED suggestion tied to the given match analysis (ADR-009 — the human
    review decision, not the AI, determines what gets applied).
    """
    resume = await db.get(Resume, resume_id)
    if resume is None:
        raise NotFoundError(f"Resume '{resume_id}' was not found.")

    match_analysis = await db.get(MatchAnalysis, match_analysis_id)
    if match_analysis is None:
        raise NotFoundError(f"Match analysis '{match_analysis_id}' was not found.")

    if match_analysis.candidate_profile_id != resume.candidate_profile_id:
        raise InvalidRequestError(
            f"Match analysis '{match_analysis_id}' does not belong to the candidate "
            f"profile behind resume '{resume_id}'."
        )

    profile = await _load_profile_with_content(db, resume.candidate_profile_id)
    suggestions = await _load_applied_suggestions(db, match_analysis_id)
    replacements = await _build_replacement_map(db, suggestions)
    generated_content = _assemble_generated_content(profile, replacements)

    resume_version = ResumeVersion(
        id=uuid.uuid4(),
        resume_id=resume_id,
        job_description_id=match_analysis.job_description_id,
        match_analysis_id=match_analysis_id,
        applied_suggestion_ids=[str(suggestion.id) for suggestion in suggestions],
        generated_content=generated_content.model_dump(),
    )
    db.add(resume_version)
    await db.commit()
    await db.refresh(resume_version, attribute_names=["created_at"])
    return resume_version


async def list_resume_versions(db: AsyncSession, resume_id: uuid.UUID) -> list[ResumeVersion]:
    result = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume_id)
        .order_by(ResumeVersion.created_at)
    )
    return list(result.scalars().all())


async def get_resume_version(db: AsyncSession, resume_version_id: uuid.UUID) -> ResumeVersion:
    resume_version = await db.get(ResumeVersion, resume_version_id)
    if resume_version is None:
        raise NotFoundError(f"Resume version '{resume_version_id}' was not found.")
    return resume_version
