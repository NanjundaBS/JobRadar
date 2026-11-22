import asyncio
import hashlib
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.database import AsyncSessionLocal
from backend.models import Job, RunLog, Company
from backend.scorer import filter_and_score_jobs
from backend.scrapers import get_all_scrapers
from backend.scrapers.base import RawJob

logger = logging.getLogger(__name__)

DEVOPS_KEYWORDS = [
    "DevOps Engineer", "AWS DevOps", "Cloud Engineer", "Platform Engineer",
    "Infrastructure Engineer", "Site Reliability Engineer", "SRE",
    "Release Engineer", "Build Engineer", "DevSecOps"
]


def make_dedup_key(company: str, title: str, location: str = "") -> str:
    """Create a stable deduplication key."""
    raw = f"{company.lower().strip()}|{title.lower().strip()}|{location.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


async def run_pipeline(run_id: Optional[uuid.UUID] = None) -> dict:
    """Main pipeline: scrape → dedupe → score → save → email."""
    async with AsyncSessionLocal() as db:
        # Create RunLog
        if run_id is None:
            run = RunLog(id=uuid.uuid4(), started_at=datetime.utcnow(), status="running")
            db.add(run)
            await db.commit()
            await db.refresh(run)
            run_id = run.id
        else:
            run = await db.get(RunLog, run_id)

        logger.info(f"Pipeline started: run_id={run_id}")
        total_new = 0
        total_found = 0

        try:
            # 1. Scrape from all sources
            scrapers = get_all_scrapers()
            all_raw_jobs: list[RawJob] = []

            for scraper in scrapers:
                try:
                    logger.info(f"Scraping {scraper.source_name}...")
                    jobs = await scraper.fetch_jobs(DEVOPS_KEYWORDS)
                    logger.info(f"{scraper.source_name}: {len(jobs)} jobs fetched")
                    all_raw_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Scraper {scraper.source_name} failed: {e}", exc_info=True)

            logger.info(f"Total raw jobs before dedupe: {len(all_raw_jobs)}")

            # 2. Deduplicate by company + title + location
            seen_keys = set()
            deduped = []
            for job in all_raw_jobs:
                key = make_dedup_key(job.company, job.title, job.location or "")
                if key not in seen_keys:
                    seen_keys.add(key)
                    deduped.append(job)

            logger.info(f"After dedupe: {len(deduped)} unique jobs")
            total_found = len(deduped)

            # 3. Score and filter
            scored = filter_and_score_jobs(deduped)
            logger.info(f"After scoring: {len(scored)} jobs pass threshold (score >= 20)")

            # 4. Fetch existing dedup keys to detect new jobs
            existing_result = await db.execute(select(Job.dedup_key))
            existing_keys = set(row[0] for row in existing_result.fetchall())

            # 5. Enrich from Company table and save
            new_count = 0
            for item in scored:
                rj: RawJob = item["raw_job"]
                dedup_key = make_dedup_key(rj.company, rj.title, rj.location or "")
                is_new = dedup_key not in existing_keys

                # Look up company info for enrichment
                comp_result = await db.execute(
                    select(Company).where(Company.name == rj.company)
                )
                company = comp_result.scalar_one_or_none()

                # Determine company type from scrapers data or Company table
                company_type = "Unknown"
                career_url = rj.career_url
                hr_email = None
                hr_email_verified = False

                if company:
                    company_type = company.type or "Unknown"
                    career_url = career_url or company.career_url
                    hr_email = company.hr_email
                    hr_email_verified = company.hr_email_verified
                elif rj.raw_data and rj.raw_data.get("company_type"):
                    company_type = rj.raw_data["company_type"]

                job_data = dict(
                    company_name=rj.company,
                    company_type=company_type,
                    career_url=career_url,
                    job_title=rj.title,
                    job_url=rj.job_url,
                    location=rj.location,
                    experience_required=rj.experience_text[:200] if rj.experience_text else None,
                    matched_skills=item["matched_skills"],
                    why_it_matches=item["why_it_matches"],
                    job_description_short=(rj.description or "")[:500],
                    hr_email=hr_email,
                    hr_email_verified=hr_email_verified,
                    source=rj.source,
                    match_score=item["score"],
                    date_posted=rj.date_posted,
                    is_new=is_new,
                    status="new",
                    dedup_key=dedup_key,
                    raw_data=rj.raw_data or {},
                    run_id=run_id,
                )

                # Upsert: insert or update on conflict
                stmt = pg_insert(Job).values(**job_data, id=uuid.uuid4())
                stmt = stmt.on_conflict_do_update(
                    index_elements=["dedup_key"],
                    set_={
                        "match_score": item["score"],
                        "why_it_matches": item["why_it_matches"],
                        "matched_skills": item["matched_skills"],
                        "is_new": is_new,
                        "run_id": run_id,
                        "updated_at": datetime.utcnow(),
                    },
                )
                await db.execute(stmt)
                if is_new:
                    new_count += 1

            await db.commit()
            total_new = new_count

            # 6. Update RunLog
            run.finished_at = datetime.utcnow()
            run.jobs_found = total_found
            run.jobs_new = total_new
            run.status = "done"
            await db.commit()

            logger.info(f"Pipeline done: {total_found} found, {total_new} new, {len(scored)} scored")

            # 7. Trigger email
            try:
                from backend.email_agent import send_job_report_email
                await send_job_report_email(run_id=run_id, db=db)
            except Exception as e:
                logger.error(f"Email send failed (non-fatal): {e}")

            return {"status": "done", "found": total_found, "new": total_new, "scored": len(scored)}

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            if run:
                run.status = "error"
                run.error_message = str(e)[:1000]
                run.finished_at = datetime.utcnow()
                await db.commit()
            raise
