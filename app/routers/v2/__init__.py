"""
V2 API Routers

Clean architecture implementation of API endpoints.
"""

from .customers import router as customers_router
from .products import router as products_router
from .orders import router as orders_router
from .inventory import router as inventory_router

__all__ = ["customers_router", "products_router", "orders_router", "inventory_router"]
