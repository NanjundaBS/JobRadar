from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
import uuid


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    company_type: str
    career_url: Optional[str] = None
    job_title: str
    job_url: str
    location: Optional[str] = None
    experience_required: Optional[str] = None
    matched_skills: Optional[list] = None
    why_it_matches: Optional[str] = None
    job_description_short: Optional[str] = None
    hr_email: Optional[str] = None
    hr_email_verified: bool = False
    source: str
    match_score: int
    date_posted: Optional[date] = None
    is_new: bool
    status: str
    created_at: datetime


class JobsResponse(BaseModel):
    items: List[JobOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total_jobs: int
    new_today: int
    companies_hiring: int
    top_skills: List[dict]
    top_sources: List[dict]
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None


class RunLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    jobs_found: int
    jobs_new: int
    status: str
    error_message: Optional[str] = None
