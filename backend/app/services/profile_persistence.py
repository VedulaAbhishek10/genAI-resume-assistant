import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import (
    CandidateProfile,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)
from app.models.resume import Resume
from app.schemas.resume import CandidateProfileExtraction
from app.services.evidence_service import generate_evidence


async def persist_resume_and_profile(
    db: AsyncSession,
    resume_id: uuid.UUID,
    filename: str,
    document_type: str,
    extracted_text: str,
    profile: CandidateProfileExtraction,
) -> CandidateProfile:
    candidate_profile = CandidateProfile(
        id=uuid.uuid4(),
        professional_summary=profile.professional_summary,
        experiences=[
            Experience(id=uuid.uuid4(), **item.model_dump()) for item in profile.experiences
        ],
        projects=[Project(id=uuid.uuid4(), **item.model_dump()) for item in profile.projects],
        skills=[Skill(id=uuid.uuid4(), **item.model_dump()) for item in profile.skills],
        education=[Education(id=uuid.uuid4(), **item.model_dump()) for item in profile.education],
        certifications=[
            Certification(id=uuid.uuid4(), **item.model_dump())
            for item in profile.certifications
        ],
    )
    candidate_profile.evidence = generate_evidence(candidate_profile)

    resume = Resume(
        id=resume_id,
        candidate_profile=candidate_profile,
        filename=filename,
        document_type=document_type,
        extracted_text=extracted_text,
    )

    db.add(candidate_profile)
    db.add(resume)
    await db.commit()
    await db.refresh(candidate_profile)
    return candidate_profile
