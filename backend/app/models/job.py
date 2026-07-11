from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_text: Mapped[str] = mapped_column(Text)
    role_title: Mapped[str | None]
    company: Mapped[str | None]
    seniority: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    requirements: Mapped[list[JobRequirement]] = relationship(
        back_populates="job_description", cascade="all, delete-orphan"
    )


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_description_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"))
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str]
    importance: Mapped[str]

    job_description: Mapped[JobDescription] = relationship(back_populates="requirements")
