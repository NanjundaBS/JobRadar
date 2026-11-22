from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "JobRadar API",
        "version": "1.0.0",
    }
