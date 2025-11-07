# API Routes
from .branches import router as branches_router
# from .products import router as products_router  # Temporarily disabled for stability
from .customers import router as customers_router
from .sales_refactored import router as sales_router  # ✅ Phase 5 P3 Batch 1: Refactored
from .inventory import router as inventory_router
from .accounting import router as accounting_router
from .pos import router as pos_router
from .cashflow import router as cashflow_router

__all__ = [
    "branches_router",
    "products_router", 
    "customers_router",
    "sales_router",
    "inventory_router",
    "accounting_router",
    "pos_router",
    "cashflow_router"
] 