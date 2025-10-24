"""
After-Sales Operations (ASO) API Router
========================================
"""

from fastapi import APIRouter
from .returns import router as returns_router
from .inspections import router as inspections_router
from .maintenance import router as maintenance_router
from .decisions import router as decisions_router
from .reports import router as reports_router

# Create main ASO router
router = APIRouter(prefix="/aso", tags=["After-Sales Operations"])

# Include sub-routers
router.include_router(returns_router)
router.include_router(inspections_router)
router.include_router(maintenance_router)
router.include_router(decisions_router)
router.include_router(reports_router)

__all__ = ["router"]
