"""
TDS Statistics Module
=====================

Statistics collection, comparison, and reporting for TDS.

مو

دول إحصائيات TDS
"""

from app.tds.statistics.models import (
    # Entity Types
    EntityType,
    SourceSystem,
    SyncRecommendation,

    # Statistics Models
    ItemStatistics,
    CustomerStatistics,
    VendorStatistics,
    PriceListStatistics,
    StockStatistics,
    ImageStatistics,
    ZohoStatistics,
    LocalStatistics,

    # Comparison Models
    DataMismatch,
    MissingEntity,
    MismatchedEntity,
    ComparisonResult,
    SystemHealthScore,
    FullComparisonReport,

    # Report Models
    SummaryReportData,
    DetailedReportData,

    # Historical Models
    StatisticsSnapshot,
    TrendAnalysis,
)

__all__ = [
    # Entity Types
    "EntityType",
    "SourceSystem",
    "SyncRecommendation",

    # Statistics Models
    "ItemStatistics",
    "CustomerStatistics",
    "VendorStatistics",
    "PriceListStatistics",
    "StockStatistics",
    "ImageStatistics",
    "ZohoStatistics",
    "LocalStatistics",

    # Comparison Models
    "DataMismatch",
    "MissingEntity",
    "MismatchedEntity",
    "ComparisonResult",
    "SystemHealthScore",
    "FullComparisonReport",

    # Report Models
    "SummaryReportData",
    "DetailedReportData",

    # Historical Models
    "StatisticsSnapshot",
    "TrendAnalysis",
]

__version__ = "4.0.0"
