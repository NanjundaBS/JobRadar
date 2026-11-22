import logging
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")


async def scheduled_pipeline_run():
    from backend.pipeline import run_pipeline
    logger.info("Scheduled pipeline triggered")
    try:
        result = await run_pipeline()
        logger.info(f"Scheduled run complete: {result}")
    except Exception as e:
        logger.error(f"Scheduled run failed: {e}", exc_info=True)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=IST)

    # 11:00 AM IST daily
    scheduler.add_job(
        scheduled_pipeline_run,
        CronTrigger(hour=11, minute=0, timezone=IST),
        id="morning_run",
        name="Morning job scan (11:00 AM IST)",
        replace_existing=True,
    )

    # 4:30 PM IST daily
    scheduler.add_job(
        scheduled_pipeline_run,
        CronTrigger(hour=16, minute=30, timezone=IST),
        id="afternoon_run",
        name="Afternoon job scan (4:30 PM IST)",
        replace_existing=True,
    )

    return scheduler
