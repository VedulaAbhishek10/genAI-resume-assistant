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


async def persist_resume_and_profile(
    db: AsyncSession,
    resume_id: uuid.UUID,
    filename: str,
    document_type: str,
    extracted_text: str,
    profile: CandidateProfileExtraction,
) -> CandidateProfile:
    candidate_profile = CandidateProfile(
        professional_summary=profile.professional_summary,
        experiences=[Experience(**item.model_dump()) for item in profile.experiences],
        projects=[Project(**item.model_dump()) for item in profile.projects],
        skills=[Skill(**item.model_dump()) for item in profile.skills],
        education=[Education(**item.model_dump()) for item in profile.education],
        certifications=[Certification(**item.model_dump()) for item in profile.certifications],
    )

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
