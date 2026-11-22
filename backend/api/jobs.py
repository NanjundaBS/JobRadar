import csv
import io
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Job, RunLog
from backend.schemas import JobOut, JobsResponse, StatsResponse

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", response_model=JobsResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    company_type: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("match_score", enum=["match_score", "date_posted", "company_name", "created_at"]),
    sort_dir: str = Query("desc", enum=["asc", "desc"]),
    run_id: Optional[uuid.UUID] = None,
    is_new: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Job)

    if company_type:
        q = q.where(Job.company_type == company_type)
    if source:
        q = q.where(Job.source == source)
    if min_score is not None:
        q = q.where(Job.match_score >= min_score)
    if status:
        q = q.where(Job.status == status)
    if run_id:
        q = q.where(Job.run_id == run_id)
    if is_new is not None:
        q = q.where(Job.is_new == is_new)
    if search:
        term = f"%{search}%"
        q = q.where(or_(
            Job.company_name.ilike(term),
            Job.job_title.ilike(term),
            Job.job_description_short.ilike(term),
            Job.why_it_matches.ilike(term),
        ))

    # Count total
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Sort
    sort_col = getattr(Job, sort_by, Job.match_score)
    q = q.order_by(desc(sort_col) if sort_dir == "desc" else asc(sort_col))

    # Paginate
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    jobs = result.scalars().all()

    return JobsResponse(
        items=[JobOut.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, -(-total // page_size)),
    )


@router.patch("/jobs/{job_id}/status")
async def update_job_status(
    job_id: uuid.UUID,
    status: str = Query(..., enum=["new", "applied", "saved", "ignored"]),
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    await db.commit()
    return {"id": str(job_id), "status": status}


@router.get("/jobs/export/csv")
async def export_jobs_csv(
    min_score: int = Query(0),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Job).where(Job.match_score >= min_score)
    if status:
        q = q.where(Job.status == status)
    q = q.order_by(desc(Job.match_score))
    result = await db.execute(q)
    jobs = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Company", "Type", "Career URL", "Job Title", "Job URL",
        "Experience", "Matched Skills", "Why It Matches", "Description",
        "HR Email", "HR Email Verified", "Source", "Score", "Date Posted", "Status"
    ])
    for j in jobs:
        writer.writerow([
            j.company_name, j.company_type, j.career_url or "",
            j.job_title, j.job_url,
            j.experience_required or "",
            ", ".join(j.matched_skills or []),
            j.why_it_matches or "",
            j.job_description_short or "",
            j.hr_email or "Not available",
            "Yes" if j.hr_email_verified else "No",
            j.source, j.match_score,
            str(j.date_posted) if j.date_posted else "",
            j.status,
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),  # utf-8-sig for Excel compatibility
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobradar-jobs.csv"},
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    from datetime import datetime

    today = datetime.utcnow().date()

    total = (await db.execute(select(func.count(Job.id)))).scalar_one()
    new_today = (await db.execute(
        select(func.count(Job.id)).where(func.date(Job.created_at) == today)
    )).scalar_one()
    companies = (await db.execute(
        select(func.count(func.distinct(Job.company_name)))
    )).scalar_one()

    # Top skills from matched_skills JSON arrays
    all_skills_result = await db.execute(
        select(Job.matched_skills).where(Job.matched_skills.isnot(None))
    )
    skill_counts: dict[str, int] = {}
    for (skills,) in all_skills_result.fetchall():
        for s in (skills or []):
            skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skills = sorted(
        [{"skill": k, "count": v} for k, v in skill_counts.items()],
        key=lambda x: -x["count"]
    )[:10]

    # Top sources
    source_result = await db.execute(
        select(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .order_by(desc(func.count(Job.id)))
    )
    top_sources = [{"source": r[0], "count": r[1]} for r in source_result.fetchall()]

    # Last run
    last_run_result = await db.execute(
        select(RunLog).order_by(desc(RunLog.started_at)).limit(1)
    )
    last_run = last_run_result.scalar_one_or_none()

    return StatsResponse(
        total_jobs=total,
        new_today=new_today,
        companies_hiring=companies,
        top_skills=top_skills,
        top_sources=top_sources,
        last_run_at=last_run.started_at if last_run else None,
        last_run_status=last_run.status if last_run else None,
    )
