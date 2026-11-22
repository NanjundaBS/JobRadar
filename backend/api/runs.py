import asyncio
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import RunLog
from backend.schemas import RunLogOut

router = APIRouter(prefix="/api", tags=["runs"])


@router.get("/runs")
async def get_runs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RunLog).order_by(desc(RunLog.started_at)).limit(50)
    )
    runs = result.scalars().all()
    return [RunLogOut.model_validate(r) for r in runs]


@router.post("/runs/trigger")
async def trigger_run():
    """Manually trigger a full pipeline run in the background."""
    from backend.pipeline import run_pipeline

    async def _run():
        try:
            await run_pipeline()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Manual trigger failed: {e}")

    asyncio.create_task(_run())
    return {"status": "triggered", "message": "Pipeline run started in background — check the dashboard in a few minutes."}
