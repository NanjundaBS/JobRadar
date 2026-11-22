import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Text, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database import Base


class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_new: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="run", lazy="select")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(50), default="Unknown")
    career_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    hr_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hr_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    funding_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_enriched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    company_type: Mapped[str] = mapped_column(String(50), default="Unknown")
    career_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    job_title: Mapped[str] = mapped_column(String(500), index=True)
    job_url: Mapped[str] = mapped_column(String(2000))
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    experience_required: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    matched_skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    why_it_matches: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_description_short: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hr_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hr_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(100), index=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    date_posted: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    dedup_key: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("run_logs.id"), nullable=True)
    run: Mapped[Optional["RunLog"]] = relationship("RunLog", back_populates="jobs")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
