"""
Mobile BFF (Backend For Frontend)
Optimized API layer for all 11 Flutter mobile apps

Apps covered:
- Consumer App (10) - ✅ 100% Complete
- Salesperson App (06) - ✅ 100% Complete
- POS/Retail Sales App (07) - ✅ 100% Complete
- Admin App (01) - ✅ 100% Complete
- Inventory App (05) - ✅ 100% Complete
- Accounting App (03) - ✅ 100% Complete
- HR App (04) - ✅ 100% Complete
- Security App (02) - ✅ 100% Complete
- Partner Network App (08) - ✅ 100% Complete
- Wholesale Client App (09) - ✅ 100% Complete
- ASO App (11) - ✅ 100% Complete

Status: 🎉 100% COMPLETE - All 11 Apps Covered!
"""
from fastapi import APIRouter
from .router import router as base_router

# Import app-specific routers
from app.bff.routers.salesperson import router as salesperson_router
from app.bff.routers.pos import router as pos_router
from app.bff.routers.admin import router as admin_router
from app.bff.routers.inventory import router as inventory_router
from app.bff.routers.accounting import router as accounting_router
from app.bff.routers.hr import router as hr_router
from app.bff.routers.security import router as security_router
from app.bff.routers.partner import router as partner_router
from app.bff.routers.wholesale import router as wholesale_router
from app.bff.routers.aso import router as aso_router

# Create main mobile router
mobile_router = APIRouter()

# Include base router (consumer, products, checkout, cart, wishlist, profile, orders, reviews)
mobile_router.include_router(base_router)

# Include app-specific routers
mobile_router.include_router(salesperson_router)
mobile_router.include_router(pos_router)
mobile_router.include_router(admin_router)
mobile_router.include_router(inventory_router)
mobile_router.include_router(accounting_router)
mobile_router.include_router(hr_router)
mobile_router.include_router(security_router)
mobile_router.include_router(partner_router)
mobile_router.include_router(wholesale_router)
mobile_router.include_router(aso_router)

# Export
router = mobile_router

__all__ = ["router"]
