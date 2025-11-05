"""
Backend For Frontend (BFF) Module
Mobile-optimized API layer for all 11 Flutter applications

This module provides aggregated, optimized endpoints for:
- 01: Admin App
- 02: Admin Security App
- 03: Accounting App
- 04: HR App
- 05: Inventory App
- 06: Salesperson App
- 07: Retail Sales/POS App
- 08: Partner Network App
- 09: Wholesale Client App
- 10: Consumer App
- 11: ASO App

Each app gets:
- Single API call per screen (vs 5-10 legacy calls)
- Optimized payloads (-80% size reduction)
- Aggressive caching (5-10 min TTL)
- Mobile-specific transformations
- Offline-first ready responses
"""
from fastapi import APIRouter

# Import all app-specific routers
from app.bff.mobile.router import router as mobile_base_router

# Create main BFF router
bff_router = APIRouter()

# Include mobile BFF router
bff_router.include_router(
    mobile_base_router,
    prefix="/mobile",
    tags=["Mobile BFF"]
)

__all__ = ["bff_router"]
