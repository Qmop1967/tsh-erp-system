"""
Repository Interfaces

Abstract repository interfaces following the Repository Pattern.
"""

from .base_repository import IBaseRepository
from .customer_repository import ICustomerRepository
from .product_repository import IProductRepository
from .order_repository import IOrderRepository
from .inventory_repository import IInventoryRepository, IStockMovementRepository

__all__ = [
    "IBaseRepository",
    "ICustomerRepository",
    "IProductRepository",
    "IOrderRepository",
    "IInventoryRepository",
    "IStockMovementRepository"
]
