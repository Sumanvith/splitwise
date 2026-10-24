import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.cache import cache_ping
from app.core.dependencies import DbSession
from app.core.limiter import limiter

logger = logging.getLogger("app")
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
@limiter.exempt
async def live():
    return {"status": "alive"}


@router.get("/ready")
@limiter.exempt
async def ready(db: DbSession):
    checks = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        logger.warning("readiness: database check failed", exc_info=True)
        checks["database"] = "down"

    checks["redis"] = "ok" if await cache_ping() else "down"

    # Only the database decides readiness: the app works without the cache.
    if checks["database"] == "down":
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "checks": checks}
        )
    return {"status": "ready", "checks": checks}