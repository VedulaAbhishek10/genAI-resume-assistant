import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExperienceContent(BaseModel):
    employer: str
    job_title: str
    start_date: str | None
    end_date: str | None
    description: str | None
    achievements: list[str]


class ProjectContent(BaseModel):
    name: str
    description: str | None
    technologies: list[str]
    achievements: list[str]


class SkillContent(BaseModel):
    name: str
    category: str | None


class EducationContent(BaseModel):
    institution: str
    degree: str | None
    field_of_study: str | None
    dates: str | None
    achievements: list[str]


class CertificationContent(BaseModel):
    name: str
    issuing_organization: str | None
    issue_date: str | None


class GeneratedResumeContent(BaseModel):
    """The fully assembled, job-tailored resume content for one ResumeVersion.

    Captured once at version-creation time so the version stays reproducible even if
    the underlying candidate profile changes afterward.
    """

    professional_summary: str | None
    experiences: list[ExperienceContent]
    projects: list[ProjectContent]
    skills: list[SkillContent]
    education: list[EducationContent]
    certifications: list[CertificationContent]


class ResumeVersionCreateRequest(BaseModel):
    match_analysis_id: uuid.UUID


class ResumeVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    job_description_id: uuid.UUID
    match_analysis_id: uuid.UUID
    applied_suggestion_ids: list[uuid.UUID]
    generated_content: GeneratedResumeContent
    created_at: datetime
