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
from app.bff.routers.tds import router as tds_bff_router

# Import salesperson app routers (App 06)
from app.bff.routers.salesperson_gps import router as salesperson_gps_router
from app.bff.routers.salesperson_transfers import router as salesperson_transfers_router
from app.bff.routers.salesperson_commissions import router as salesperson_commissions_router

# Create main BFF router
bff_router = APIRouter()

# Include mobile BFF router
bff_router.include_router(
    mobile_base_router,
    prefix="/mobile",
    tags=["Mobile BFF"]
)

# Include TDS BFF router
bff_router.include_router(
    tds_bff_router,
    tags=["TDS BFF"]
)

# Include Salesperson App routers (App 06 - TSH Field Sales Rep)
# 33 endpoints: GPS tracking (8) + Money transfers (12) + Commissions (13)
bff_router.include_router(
    salesperson_gps_router,
    prefix="/salesperson",
    tags=["Salesperson GPS - 8 Endpoints"]
)

bff_router.include_router(
    salesperson_transfers_router,
    prefix="/salesperson",
    tags=["Salesperson Transfers - 12 Endpoints"]
)

bff_router.include_router(
    salesperson_commissions_router,
    prefix="/salesperson",
    tags=["Salesperson Commissions - 13 Endpoints"]
)

__all__ = ["bff_router"]
