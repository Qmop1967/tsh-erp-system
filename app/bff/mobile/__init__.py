"""
Mobile BFF (Backend For Frontend)
Optimized API layer for Flutter mobile apps (Consumer & Salesperson)
"""
from .router import router
from .schemas import *
from .aggregators import *

__all__ = ["router"]
