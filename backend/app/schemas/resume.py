from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    employer: str
    job_title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class SkillItem(BaseModel):
    name: str
    category: str | None = None


class EducationItem(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    dates: str | None = None
    achievements: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str
    issuing_organization: str | None = None
    issue_date: str | None = None


class CandidateProfileExtraction(BaseModel):
    """Structured candidate profile extracted from resume text (see docs/AI_SYSTEM.md)."""

    professional_summary: str | None = None
    experiences: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills: list[SkillItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certifications: list[CertificationItem] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: Literal["uploaded"]
    extracted_text: str
    candidate_profile: CandidateProfileExtraction
