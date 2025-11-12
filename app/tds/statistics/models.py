"""
TDS Statistics Models
======================

Data models for statistics collection, comparison, and reporting.

نماذج البيانات لإحصائيات TDS
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Entity types for statistics"""
    ITEMS = "items"
    CUSTOMERS = "customers"
    VENDORS = "vendors"
    PRICE_LISTS = "price_lists"
    STOCK = "stock"
    IMAGES = "images"


class SourceSystem(str, Enum):
    """Source system identifier"""
    ZOHO = "zoho"
    LOCAL = "local"


class SyncRecommendation(str, Enum):
    """Sync recommendation types"""
    FULL_SYNC = "full_sync"
    INCREMENTAL_SYNC = "incremental_sync"
    NO_SYNC_NEEDED = "no_sync_needed"
    MANUAL_REVIEW = "manual_review"


# ============================================================================
# Statistics Models
# ============================================================================

@dataclass
class ItemStatistics:
    """
    Item/Product statistics
    إحصائيات المنتجات
    """
    total_count: int
    active_count: int
    inactive_count: int
    with_images_count: int
    without_images_count: int
    by_category: Dict[str, int] = field(default_factory=dict)
    by_brand: Dict[str, int] = field(default_factory=dict)
    average_price: float = 0.0
    total_stock_value: float = 0.0
    low_stock_count: int = 0
    out_of_stock_count: int = 0

    @property
    def image_coverage_percentage(self) -> float:
        """Calculate image coverage percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.with_images_count / self.total_count) * 100


@dataclass
class CustomerStatistics:
    """
    Customer statistics
    إحصائيات العملاء
    """
    total_count: int
    active_count: int
    inactive_count: int
    by_type: Dict[str, int] = field(default_factory=dict)
    by_country: Dict[str, int] = field(default_factory=dict)
    by_price_list: Dict[str, int] = field(default_factory=dict)
    total_credit_limit: float = 0.0
    with_outstanding_balance: int = 0
    average_credit_limit: float = 0.0


@dataclass
class VendorStatistics:
    """
    Vendor/Supplier statistics
    إحصائيات الموردين
    """
    total_count: int
    active_count: int
    inactive_count: int
    by_country: Dict[str, int] = field(default_factory=dict)
    total_payables: float = 0.0
    with_outstanding_payables: int = 0


@dataclass
class PriceListStatistics:
    """
    Price list statistics
    إحصائيات قوائم الأسعار
    """
    total_lists: int
    active_lists: int
    inactive_lists: int
    total_items_mapped: int
    lists_by_currency: Dict[str, int] = field(default_factory=dict)
    coverage_percentage: float = 0.0
    items_per_list: Dict[str, int] = field(default_factory=dict)


@dataclass
class StockStatistics:
    """
    Stock/Inventory statistics
    إحصائيات المخزون
    """
    total_items_in_stock: int
    out_of_stock_count: int
    low_stock_count: int
    total_stock_value: float
    average_stock_per_item: float
    by_warehouse: Dict[str, int] = field(default_factory=dict)
    items_with_negative_stock: int = 0
    total_reserved_stock: int = 0


@dataclass
class ImageStatistics:
    """
    Image statistics
    إحصائيات الصور
    """
    total_items: int
    with_images: int
    without_images: int
    total_images_count: int
    average_images_per_item: float
    broken_image_links: int = 0

    @property
    def coverage_percentage(self) -> float:
        """Calculate image coverage percentage"""
        if self.total_items == 0:
            return 0.0
        return (self.with_images / self.total_items) * 100


# ============================================================================
# Complete System Statistics
# ============================================================================

@dataclass
class ZohoStatistics:
    """
    Complete Zoho system statistics
    إحصائيات نظام Zoho الكاملة
    """
    items: ItemStatistics
    customers: CustomerStatistics
    vendors: VendorStatistics
    price_lists: PriceListStatistics
    stock: StockStatistics
    images: ImageStatistics
    collected_at: datetime


@dataclass
class LocalStatistics:
    """
    Complete local TSH ERP statistics
    إحصائيات نظام TSH ERP المحلية الكاملة
    """
    items: ItemStatistics
    customers: CustomerStatistics
    vendors: VendorStatistics
    price_lists: PriceListStatistics
    stock: StockStatistics
    images: ImageStatistics
    collected_at: datetime


# ============================================================================
# Comparison Models
# ============================================================================

@dataclass
class DataMismatch:
    """
    Represents a data mismatch between systems
    يمثل عدم تطابق البيانات بين الأنظمة
    """
    field: str
    zoho_value: Any
    local_value: Any
    severity: str  # 'low', 'medium', 'high'


@dataclass
class MissingEntity:
    """
    Entity missing from one system
    كيان مفقود من أحد الأنظمة
    """
    id: str
    name: str
    entity_type: str
    missing_from: SourceSystem
    zoho_id: Optional[str] = None
    local_id: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class MismatchedEntity:
    """
    Entity with mismatched data between systems
    كيان بيانات غير متطابقة بين الأنظمة
    """
    entity_id: str
    entity_name: str
    entity_type: str
    mismatches: List[DataMismatch] = field(default_factory=list)
    zoho_last_modified: Optional[datetime] = None
    local_last_modified: Optional[datetime] = None

    @property
    def critical_mismatches(self) -> List[DataMismatch]:
        """Get only critical mismatches"""
        return [m for m in self.mismatches if m.severity == 'high']


@dataclass
class ComparisonResult:
    """
    Comparison result for a single entity type
    نتيجة المقارنة لنوع كيان واحد
    """
    entity_type: EntityType
    zoho_count: int
    local_count: int
    difference: int
    match_count: int
    match_percentage: float
    missing_in_local: List[MissingEntity] = field(default_factory=list)
    missing_in_zoho: List[MissingEntity] = field(default_factory=list)
    mismatched_entities: List[MismatchedEntity] = field(default_factory=list)
    requires_sync: bool = False
    sync_recommendation: SyncRecommendation = SyncRecommendation.NO_SYNC_NEEDED
    sync_priority: int = 0  # 1-10, higher = more urgent
    estimated_sync_duration_minutes: int = 0

    @property
    def total_issues(self) -> int:
        """Total number of issues found"""
        return (
            len(self.missing_in_local) +
            len(self.missing_in_zoho) +
            len(self.mismatched_entities)
        )

    @property
    def is_healthy(self) -> bool:
        """Check if comparison is healthy (>95% match)"""
        return self.match_percentage >= 95.0


@dataclass
class SystemHealthScore:
    """
    Overall system health score
    درجة صحة النظام الإجمالية
    """
    overall_score: float  # 0-100
    items_score: float
    customers_score: float
    vendors_score: float
    price_lists_score: float
    stock_score: float
    images_score: float
    status: str  # 'excellent', 'good', 'warning', 'critical'
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.overall_score >= 90.0


@dataclass
class FullComparisonReport:
    """
    Complete comparison report across all entities
    تقرير المقارنة الكامل لجميع الكيانات
    """
    report_id: str
    timestamp: datetime
    zoho_statistics: ZohoStatistics
    local_statistics: LocalStatistics
    comparisons: Dict[str, ComparisonResult] = field(default_factory=dict)
    overall_match_percentage: float = 0.0
    health_score: Optional[SystemHealthScore] = None
    sync_recommendations: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    @property
    def requires_immediate_attention(self) -> bool:
        """Check if report requires immediate attention"""
        return self.overall_match_percentage < 90.0

    @property
    def critical_issues(self) -> List[str]:
        """Get list of critical issues"""
        issues = []
        for entity_type, comparison in self.comparisons.items():
            if comparison.match_percentage < 90.0:
                issues.append(
                    f"{entity_type}: {comparison.match_percentage:.1f}% match "
                    f"({comparison.total_issues} issues)"
                )
        return issues


# ============================================================================
# Report Export Models
# ============================================================================

@dataclass
class SummaryReportData:
    """
    Data for summary report export
    بيانات تقرير الملخص للتصدير
    """
    report_date: str
    overall_match: float
    total_items_zoho: int
    total_items_local: int
    total_customers_zoho: int
    total_customers_local: int
    total_vendors_zoho: int
    total_vendors_local: int
    critical_issues: List[str]
    recommendations: List[str]


@dataclass
class DetailedReportData:
    """
    Data for detailed report export
    بيانات التقرير المفصل للتصدير
    """
    summary: SummaryReportData
    items_comparison: ComparisonResult
    customers_comparison: ComparisonResult
    vendors_comparison: ComparisonResult
    price_lists_comparison: ComparisonResult
    stock_comparison: ComparisonResult
    images_comparison: ComparisonResult
    missing_entities: List[MissingEntity]
    mismatched_entities: List[MismatchedEntity]


# ============================================================================
# Historical Tracking Models
# ============================================================================

@dataclass
class StatisticsSnapshot:
    """
    Historical snapshot of statistics
    لقطة تاريخية للإحصائيات
    """
    snapshot_id: str
    snapshot_date: datetime
    source_system: SourceSystem
    entity_type: EntityType
    total_count: int
    active_count: int
    statistics_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """
    Trend analysis over time
    تحليل الاتجاهات عبر الزمن
    """
    entity_type: EntityType
    period_days: int
    snapshots: List[StatisticsSnapshot] = field(default_factory=list)
    growth_rate: float = 0.0
    trend_direction: str = "stable"  # 'growing', 'declining', 'stable'
    anomalies_detected: List[str] = field(default_factory=list)
