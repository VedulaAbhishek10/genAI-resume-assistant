from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.candidate import CandidateProfile

# Must match Settings.embedding_dimension (sentence-transformers/all-MiniLM-L6-v2).
# Changing embedding models to one with a different output dimension requires a new
# migration to alter this column.
EMBEDDING_DIMENSION = 384


class CandidateEvidence(Base):
    __tablename__ = "candidate_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    evidence_type: Mapped[str]
    source_entity_type: Mapped[str]
    source_entity_id: Mapped[uuid.UUID]
    text: Mapped[str] = mapped_column(Text)
    evidence_metadata: Mapped[dict[str, str | None]] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSION))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="evidence")
