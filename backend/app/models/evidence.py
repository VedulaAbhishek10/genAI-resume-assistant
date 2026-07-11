from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.candidate import CandidateProfile


class CandidateEvidence(Base):
    __tablename__ = "candidate_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    evidence_type: Mapped[str]
    source_entity_type: Mapped[str]
    source_entity_id: Mapped[uuid.UUID]
    text: Mapped[str] = mapped_column(Text)
    evidence_metadata: Mapped[dict[str, str | None]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="evidence")
