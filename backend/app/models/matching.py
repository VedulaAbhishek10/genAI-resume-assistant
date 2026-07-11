from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class MatchAnalysis(Base):
    __tablename__ = "match_analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    job_description_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"))
    overall_score: Mapped[float]
    component_scores: Mapped[dict[str, float]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    requirement_matches: Mapped[list[RequirementMatch]] = relationship(
        back_populates="match_analysis", cascade="all, delete-orphan"
    )


class RequirementMatch(Base):
    __tablename__ = "requirement_matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_analyses.id"))
    job_requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_requirements.id"))
    classification: Mapped[str]
    explanation: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float]
    evidence_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    match_analysis: Mapped[MatchAnalysis] = relationship(back_populates="requirement_matches")
