"""
Mobile BFF (Backend for Frontend) Services

This package contains services that aggregate data from multiple sources
to reduce the number of API calls required by mobile applications.

Key Features:
- Single endpoint returns complete data
- Reduces API calls by 70-80%
- Optimized for mobile bandwidth
- Aggressive caching for performance
"""

from .base_bff import BaseBFFService
from .product_bff import ProductBFFService
from .customer_bff import CustomerBFFService
from .order_bff import OrderBFFService

__all__ = [
    "BaseBFFService",
    "ProductBFFService",
    "CustomerBFFService",
    "OrderBFFService",
]
