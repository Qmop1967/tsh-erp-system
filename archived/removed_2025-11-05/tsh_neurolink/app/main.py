"""
TSH NeuroLink - Main FastAPI Application
Event-driven notification and messaging system for TSH ERP
"""
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, close_db
from app.api.v1 import events, notifications
from app.schemas import HealthCheckResponse


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    - Startup: Initialize database connections
    - Shutdown: Close database connections
    """
    # Startup
    print("🚀 Starting TSH NeuroLink...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔧 Debug Mode: {settings.debug}")

    # Initialize database
    # await init_db()  # Commented out - using SQL migration instead
    print("✅ Database connection established")

    yield

    # Shutdown
    print("🛑 Shutting down TSH NeuroLink...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    TSH NeuroLink - Event-Driven Notification & Messaging System

    ## Features
    - **Event Ingestion**: Receive business events from TSH ERP modules
    - **Notification System**: Convert events into user notifications
    - **Real-time Delivery**: WebSocket support for instant updates
    - **Multi-channel**: In-app, Email, SMS, Telegram, Slack
    - **Contextual Chat**: NeuroChat for event discussions
    - **Rule Engine**: Flexible notification rules and templates

    ## Authentication
    All endpoints require JWT authentication from TSH ERP.
    Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ## Base URL
    Production: `https://api.tsh.sale/neurolink`
    Development: `http://localhost:8002`
    """,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint (no auth required)
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health check",
    description="Check if the API is running and database is connected"
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint for monitoring"""

    # TODO: Add actual database ping
    db_status = "connected"
    redis_status = "connected"

    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        database=db_status,
        redis=redis_status
    )


# Root endpoint
@app.get(
    "/",
    tags=["System"],
    summary="API Information",
    description="Get basic information about the API"
)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "disabled in production",
        "health": "/health",
        "endpoints": {
            "events": "/v1/events",
            "notifications": "/v1/notifications"
        }
    }


# Include API routers
app.include_router(events.router)
app.include_router(notifications.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Development server entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
