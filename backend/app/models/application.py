from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    job_description_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"))
    resume_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resume_versions.id"))
    company: Mapped[str | None]
    role: Mapped[str | None]
    status: Mapped[str] = mapped_column(default="SAVED")
    notes: Mapped[str | None] = mapped_column(Text)
    application_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
