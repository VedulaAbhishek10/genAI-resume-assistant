from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.resume import Resume


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    professional_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    experiences: Mapped[list[Experience]] = relationship(
        back_populates="candidate_profile", cascade="all, delete-orphan"
    )
    projects: Mapped[list[Project]] = relationship(
        back_populates="candidate_profile", cascade="all, delete-orphan"
    )
    skills: Mapped[list[Skill]] = relationship(
        back_populates="candidate_profile", cascade="all, delete-orphan"
    )
    education: Mapped[list[Education]] = relationship(
        back_populates="candidate_profile", cascade="all, delete-orphan"
    )
    certifications: Mapped[list[Certification]] = relationship(
        back_populates="candidate_profile", cascade="all, delete-orphan"
    )
    resumes: Mapped[list[Resume]] = relationship(back_populates="candidate_profile")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    employer: Mapped[str]
    job_title: Mapped[str]
    start_date: Mapped[str | None]
    end_date: Mapped[str | None]
    description: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text)
    technologies: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="projects")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    name: Mapped[str]
    category: Mapped[str | None]

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="skills")


class Education(Base):
    __tablename__ = "education"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    institution: Mapped[str]
    degree: Mapped[str | None]
    field_of_study: Mapped[str | None]
    dates: Mapped[str | None]
    achievements: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="education")


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id"))
    name: Mapped[str]
    issuing_organization: Mapped[str | None]
    issue_date: Mapped[str | None]

    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="certifications")
