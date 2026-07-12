from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class ResumeSuggestion(Base):
    __tablename__ = "resume_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    requirement_match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirement_matches.id")
    )
    original_text: Mapped[str] = mapped_column(Text)
    suggested_text: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    evidence_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    confidence: Mapped[float]
    is_grounded: Mapped[bool] = mapped_column(Boolean)
    review_status: Mapped[str] = mapped_column(default="PENDING")
    edited_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
