import uuid
from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ApplicationStatus(StrEnum):
    SAVED = "SAVED"
    PREPARING = "PREPARING"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"


class ApplicationCreateRequest(BaseModel):
    candidate_profile_id: uuid.UUID
    job_description_id: uuid.UUID
    resume_version_id: uuid.UUID | None = None
    company: str | None = None
    role: str | None = None
    notes: str | None = None


class ApplicationUpdateRequest(BaseModel):
    status: ApplicationStatus | None = None
    resume_version_id: uuid.UUID | None = None
    notes: str | None = None
    application_date: date | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_profile_id: uuid.UUID
    job_description_id: uuid.UUID
    resume_version_id: uuid.UUID | None
    company: str | None
    role: str | None
    status: ApplicationStatus
    notes: str | None
    application_date: date | None
    created_at: datetime
