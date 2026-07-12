import uuid
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"


class BulletSuggestionExtraction(BaseModel):
    """LLM-generated rewrite of one evidence bullet (see docs/AI_SYSTEM.md)."""

    suggested_text: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class ResumeSuggestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requirement_match_id: uuid.UUID
    original_text: str
    suggested_text: str
    reason: str
    evidence_ids: list[uuid.UUID]
    confidence: float
    is_grounded: bool
    review_status: ReviewStatus
    edited_text: str | None
    created_at: datetime


class ResumeSuggestionUpdateRequest(BaseModel):
    review_status: ReviewStatus
    edited_text: str | None = None

    @model_validator(mode="after")
    def _require_edited_text_when_edited(self) -> Self:
        if self.review_status == ReviewStatus.EDITED and not (self.edited_text or "").strip():
            raise ValueError("edited_text is required when review_status is EDITED.")
        return self
