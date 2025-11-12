"""
TDS API Module
==============

RESTful API endpoints for TDS (TSH Data Sync).

واجهة برمجة التطبيقات لـ TDS
"""

# Import webhooks router
from .webhooks import router as webhooks_router

# Statistics router has dependency issues - will be fixed separately
# from .statistics import router as statistics_router

__all__ = [
    'webhooks_router',
    # 'statistics_router',  # TODO: Fix import dependencies
]

__version__ = "4.0.0"
