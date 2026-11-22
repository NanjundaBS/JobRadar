import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db
from backend.scheduler import create_scheduler
from backend.api.jobs import router as jobs_router
from backend.api.runs import router as runs_router
from backend.api.status import router as status_router

# Logging setup
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 JobRadar API starting up...")
    await init_db()
    logger.info("✅ Database initialized")

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("⏰ Scheduler started: 11:00 AM IST + 4:30 PM IST daily")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("JobRadar API shut down")


app = FastAPI(
    title="JobRadar API",
    description="DevOps Job Intelligence Platform — scrape, score, enrich, email",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


app.include_router(jobs_router)
app.include_router(runs_router)
app.include_router(status_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
