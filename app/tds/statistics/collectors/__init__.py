"""
TDS Statistics Collectors
==========================

Data collectors for Zoho and local TSH ERP systems.
"""

from app.tds.statistics.collectors.zoho_collector import ZohoDataCollector
from app.tds.statistics.collectors.local_collector import LocalDataCollector

__all__ = [
    "ZohoDataCollector",
    "LocalDataCollector",
]
