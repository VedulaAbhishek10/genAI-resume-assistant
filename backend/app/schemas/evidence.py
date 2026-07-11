import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class EvidenceType(StrEnum):
    EXPERIENCE_BULLET = "experience_bullet"
    PROJECT_BULLET = "project_bullet"
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    CERTIFICATION = "certification"
    EDUCATION_ITEM = "education_item"


class SourceEntityType(StrEnum):
    EXPERIENCE = "experience"
    PROJECT = "project"
    SKILL = "skill"
    EDUCATION = "education"
    CERTIFICATION = "certification"


class CandidateEvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_profile_id: uuid.UUID
    evidence_type: EvidenceType
    source_entity_type: SourceEntityType
    source_entity_id: uuid.UUID
    text: str
    evidence_metadata: dict[str, str | None]
    created_at: datetime
