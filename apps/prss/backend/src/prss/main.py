"""
TSH After-Sales Operations System (PRSS) - Main Application
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prss.config import settings
from prss.db import init_db
from prss.api.v1 import returns, inspections, maintenance, decisions, reports
from prss.utils.logging import setup_logging
from prss.utils.request_id import RequestIDMiddleware

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting PRSS application...")
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    logger.info("Shutting down PRSS application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TSH After-Sales Operations System - Comprehensive returns, repairs, and warranty management",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Request ID middleware
if settings.enable_request_id:
    app.add_middleware(RequestIDMiddleware)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": settings.docs_url,
        "openapi": settings.openapi_url
    }


# API v1 routes
API_V1_PREFIX = settings.api_v1_prefix

app.include_router(returns.router, prefix=API_V1_PREFIX, tags=["returns"])
app.include_router(inspections.router, prefix=API_V1_PREFIX, tags=["inspections"])
app.include_router(maintenance.router, prefix=API_V1_PREFIX, tags=["maintenance"])
app.include_router(decisions.router, prefix=API_V1_PREFIX, tags=["decisions"])
app.include_router(reports.router, prefix=API_V1_PREFIX, tags=["reports"])


# Authentication endpoint
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.models.all_models import User
from prss.security.auth import verify_password, create_access_token
from prss.schemas.user import Token


@app.post(f"{API_V1_PREFIX}/auth/token", response_model=Token, tags=["authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - get JWT token"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value,
            "scopes": user.scopes or []
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "prss.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
