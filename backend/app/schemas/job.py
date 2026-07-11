import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequirementCategory(StrEnum):
    SKILL = "skill"
    EXPERIENCE = "experience"
    RESPONSIBILITY = "responsibility"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


class RequirementImportance(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    OPTIONAL = "optional"


class JobRequirementItem(BaseModel):
    text: str
    category: RequirementCategory
    importance: RequirementImportance


class JobRequirementExtraction(BaseModel):
    """Structured job requirements extracted from a job description (see docs/AI_SYSTEM.md)."""

    role_title: str | None = None
    company: str | None = None
    seniority: str | None = None
    requirements: list[JobRequirementItem] = Field(default_factory=list)


class JobSubmissionRequest(BaseModel):
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Job description text must not be blank.")
        return value


class JobRequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    category: RequirementCategory
    importance: RequirementImportance


class JobDescriptionResponse(BaseModel):
    id: uuid.UUID
    source_text: str
    role_title: str | None
    company: str | None
    seniority: str | None
    requirements: list[JobRequirementRead]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
