from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class ResumeVersion(Base):
    """A job-specific resume revision (see docs/DATA_MODEL.md's ResumeVersion).

    `generated_content` is the fully assembled resume content (master resume content
    with every ACCEPTED/EDITED suggestion applied) captured at creation time, so a
    version stays reproducible even if the underlying candidate profile changes later.
    """

    __tablename__ = "resume_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id"))
    job_description_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"))
    match_analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_analyses.id"))
    applied_suggestion_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    generated_content: Mapped[dict[str, object]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
