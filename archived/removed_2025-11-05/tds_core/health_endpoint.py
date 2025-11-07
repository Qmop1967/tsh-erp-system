"""
Health Check Endpoints for TSH ERP FastAPI Application
Add these endpoints to your main.py file
"""
from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
import os

# Assuming you have these imports from your app
# from core.database import get_db
# from core.config import settings

router = APIRouter(tags=["Health"])

# Application start time
APP_START_TIME = time.time()


@router.get("/ready")
async def ready():
    """
    Lightweight readiness check for deployment health checks.
    Used by deployment scripts and load balancers.
    Returns: Plain text "ok" with 200 status
    """
    return Response(content="ok", media_type="text/plain", status_code=200)


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check including database connectivity.
    Returns: JSON with detailed health status
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": int(time.time() - APP_START_TIME),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENV", "development")
    }

    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["database"] = {
            "status": "connected",
            "type": "postgresql"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = {
            "status": "disconnected",
            "error": str(e)
        }
        return JSONResponse(
            status_code=503,
            content=health_status
        )

    return JSONResponse(status_code=200, content=health_status)


@router.get("/liveness")
async def liveness():
    """
    Kubernetes/Docker liveness probe.
    Just checks if the application is running.
    """
    return Response(content="alive", media_type="text/plain")


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity checks.
    """
    return {"status": "pong", "timestamp": time.time()}


# Add these routes to your main.py:
# app.include_router(router)
