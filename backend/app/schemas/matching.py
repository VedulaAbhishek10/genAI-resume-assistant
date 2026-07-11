import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.evidence import CandidateEvidenceRead
from app.schemas.job import RequirementCategory, RequirementImportance


class MatchClassification(StrEnum):
    STRONG_MATCH = "STRONG_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    NO_EVIDENCE = "NO_EVIDENCE"


class RequirementMatchExtraction(BaseModel):
    """LLM classification of one job requirement against retrieved evidence.

    `supporting_evidence_indices` refers to the 1-based position of items in the
    numbered evidence list given in the prompt, not database IDs — the LLM is not
    asked to reproduce UUIDs, which it cannot do reliably. The application maps
    indices back to actual evidence records deterministically.
    """

    classification: MatchClassification
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_indices: list[int] = Field(default_factory=list)


class RequirementMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_requirement_id: uuid.UUID
    requirement_text: str
    category: RequirementCategory
    importance: RequirementImportance
    classification: MatchClassification
    explanation: str
    confidence: float
    evidence: list[CandidateEvidenceRead]


class GapItem(BaseModel):
    requirement_text: str
    category: RequirementCategory
    importance: RequirementImportance
    classification: MatchClassification


class MatchAnalysisResponse(BaseModel):
    id: uuid.UUID
    candidate_profile_id: uuid.UUID
    job_description_id: uuid.UUID
    overall_score: float
    component_scores: dict[str, float]
    requirement_matches: list[RequirementMatchRead]
    gaps: list[GapItem]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
