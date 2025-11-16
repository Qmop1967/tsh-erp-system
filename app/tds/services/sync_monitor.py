"""
Sync Monitoring Service
=======================

Monitors and reports on TDS Core sync status across all entities.

خدمة مراقبة المزامنة - تتبع حالة المزامنة لجميع الكيانات

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class SyncHealthStatus(str, Enum):
    """Sync health status levels"""
    HEALTHY = "healthy"       # All syncs working, >95% success rate
    WARNING = "warning"       # Some issues, 85-95% success rate
    CRITICAL = "critical"     # Major issues, <85% success rate
    UNKNOWN = "unknown"       # No sync data available


@dataclass
class EntitySyncStatus:
    """Status for a specific entity type"""
    entity_type: str
    total_records: int = 0
    synced_records: int = 0
    failed_records: int = 0
    last_sync_time: Optional[datetime] = None
    success_rate: float = 0.0
    missing_count: int = 0
    duplicate_count: int = 0
    health_status: SyncHealthStatus = SyncHealthStatus.UNKNOWN
    errors: List[str] = field(default_factory=list)


@dataclass
class OverallSyncStatus:
    """Overall sync system status"""
    timestamp: datetime
    health_status: SyncHealthStatus
    total_entities: int = 0
    healthy_entities: int = 0
    warning_entities: int = 0
    critical_entities: int = 0
    entity_statuses: Dict[str, EntitySyncStatus] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class SyncMonitoringService:
    """
    Service for monitoring TDS Core sync status

    Provides comprehensive visibility into:
    - Sync completeness for each entity type
    - Success/failure rates
    - Missing records (in Zoho but not local)
    - Duplicate records
    - Data quality issues
    - Performance metrics
    """

    # Entity type to database table mapping
    ENTITY_TABLE_MAPPING = {
        'products': 'products',
        'customers': 'customers',
        'vendors': 'vendors',
        'invoices': 'invoices',
        'payments': 'payments',
        'credit_notes': 'credit_notes',
        'bills': 'bills',
        'sales_orders': 'sales_orders',
        'purchase_orders': 'purchase_orders',
        'users': 'users',
    }

    def __init__(self, db: Session):
        """
        Initialize monitoring service

        Args:
            db: Database session
        """
        self.db = db

    def get_overall_status(self) -> OverallSyncStatus:
        """
        Get overall sync status for all entities

        Returns:
            OverallSyncStatus with comprehensive system status
        """
        logger.info("Generating overall sync status report")

        status = OverallSyncStatus(
            timestamp=datetime.utcnow(),
            health_status=SyncHealthStatus.UNKNOWN
        )

        # Check each entity type
        for entity_type, table_name in self.ENTITY_TABLE_MAPPING.items():
            try:
                entity_status = self._get_entity_status(entity_type, table_name)
                status.entity_statuses[entity_type] = entity_status
                status.total_entities += 1

                # Count by health status
                if entity_status.health_status == SyncHealthStatus.HEALTHY:
                    status.healthy_entities += 1
                elif entity_status.health_status == SyncHealthStatus.WARNING:
                    status.warning_entities += 1
                elif entity_status.health_status == SyncHealthStatus.CRITICAL:
                    status.critical_entities += 1

            except Exception as e:
                logger.error(f"Error getting status for {entity_type}: {str(e)}")
                status.entity_statuses[entity_type] = EntitySyncStatus(
                    entity_type=entity_type,
                    health_status=SyncHealthStatus.UNKNOWN,
                    errors=[str(e)]
                )

        # Determine overall health
        status.health_status = self._calculate_overall_health(status)

        # Generate recommendations
        status.recommendations = self._generate_recommendations(status)

        return status

    def _get_entity_status(self, entity_type: str, table_name: str) -> EntitySyncStatus:
        """
        Get sync status for a specific entity

        Args:
            entity_type: Entity type name
            table_name: Database table name

        Returns:
            EntitySyncStatus
        """
        status = EntitySyncStatus(entity_type=entity_type)

        try:
            # Check if table exists
            if not self._table_exists(table_name):
                status.errors.append(f"Table {table_name} does not exist")
                status.health_status = SyncHealthStatus.UNKNOWN
                return status

            # Get total records count
            status.total_records = self._get_record_count(table_name)

            # Get synced records count (records with zoho_*_id)
            status.synced_records = self._get_synced_record_count(table_name, entity_type)

            # Get last sync time
            status.last_sync_time = self._get_last_sync_time(table_name, entity_type)

            # Detect duplicates
            status.duplicate_count = self._detect_duplicates(table_name, entity_type)

            # Calculate success rate
            if status.total_records > 0:
                status.success_rate = (status.synced_records / status.total_records) * 100
            else:
                status.success_rate = 0.0

            # Calculate missing count (failed syncs)
            status.failed_records = status.total_records - status.synced_records

            # Determine health status
            status.health_status = self._determine_entity_health(status)

        except Exception as e:
            logger.error(f"Error checking {entity_type} status: {str(e)}")
            status.errors.append(str(e))
            status.health_status = SyncHealthStatus.UNKNOWN

        return status

    def _table_exists(self, table_name: str) -> bool:
        """Check if table exists in database"""
        try:
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = :table_name
                )
            """)
            result = self.db.execute(query, {'table_name': table_name})
            return result.scalar()
        except Exception:
            return False

    def _get_record_count(self, table_name: str) -> int:
        """Get total record count for table"""
        try:
            query = text(f"SELECT COUNT(*) FROM {table_name}")
            result = self.db.execute(query)
            return result.scalar() or 0
        except Exception as e:
            logger.warning(f"Could not count records in {table_name}: {e}")
            return 0

    def _get_synced_record_count(self, table_name: str, entity_type: str) -> int:
        """Get count of records that have been synced from Zoho"""
        try:
            # Different entity types have different Zoho ID column names
            zoho_id_column = self._get_zoho_id_column(entity_type)

            query = text(f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE {zoho_id_column} IS NOT NULL
                AND {zoho_id_column} != ''
            """)
            result = self.db.execute(query)
            return result.scalar() or 0
        except Exception as e:
            logger.warning(f"Could not count synced records in {table_name}: {e}")
            return 0

    def _get_zoho_id_column(self, entity_type: str) -> str:
        """Get Zoho ID column name for entity type"""
        mapping = {
            'products': 'zoho_item_id',
            'customers': 'zoho_contact_id',
            'vendors': 'zoho_vendor_id',
            'invoices': 'zoho_invoice_id',
            'payments': 'zoho_payment_id',
            'credit_notes': 'zoho_creditnote_id',
            'bills': 'zoho_bill_id',
            'sales_orders': 'zoho_salesorder_id',
            'purchase_orders': 'zoho_purchaseorder_id',
            'users': 'zoho_user_id',
        }
        return mapping.get(entity_type, 'zoho_id')

    def _get_last_sync_time(self, table_name: str, entity_type: str) -> Optional[datetime]:
        """Get last sync time for entity type"""
        try:
            # Check if updated_at column exists
            query = text(f"""
                SELECT MAX(updated_at) FROM {table_name}
                WHERE {self._get_zoho_id_column(entity_type)} IS NOT NULL
            """)
            result = self.db.execute(query)
            return result.scalar()
        except Exception:
            return None

    def _detect_duplicates(self, table_name: str, entity_type: str) -> int:
        """Detect duplicate records based on Zoho ID"""
        try:
            zoho_id_column = self._get_zoho_id_column(entity_type)

            query = text(f"""
                SELECT COUNT(*) - COUNT(DISTINCT {zoho_id_column})
                FROM {table_name}
                WHERE {zoho_id_column} IS NOT NULL
                AND {zoho_id_column} != ''
            """)
            result = self.db.execute(query)
            return result.scalar() or 0
        except Exception as e:
            logger.warning(f"Could not detect duplicates in {table_name}: {e}")
            return 0

    def _determine_entity_health(self, status: EntitySyncStatus) -> SyncHealthStatus:
        """Determine health status for entity based on metrics"""
        # If no records, unknown
        if status.total_records == 0:
            return SyncHealthStatus.UNKNOWN

        # If duplicates found, warning at minimum
        if status.duplicate_count > 0:
            if status.success_rate < 85:
                return SyncHealthStatus.CRITICAL
            return SyncHealthStatus.WARNING

        # Based on success rate
        if status.success_rate >= 95:
            return SyncHealthStatus.HEALTHY
        elif status.success_rate >= 85:
            return SyncHealthStatus.WARNING
        else:
            return SyncHealthStatus.CRITICAL

    def _calculate_overall_health(self, status: OverallSyncStatus) -> SyncHealthStatus:
        """Calculate overall system health"""
        if status.total_entities == 0:
            return SyncHealthStatus.UNKNOWN

        # If any critical, system is critical
        if status.critical_entities > 0:
            return SyncHealthStatus.CRITICAL

        # If more than 25% warnings, system is warning
        if status.warning_entities > (status.total_entities * 0.25):
            return SyncHealthStatus.WARNING

        # If all healthy, system is healthy
        if status.healthy_entities == status.total_entities:
            return SyncHealthStatus.HEALTHY

        return SyncHealthStatus.WARNING

    def _generate_recommendations(self, status: OverallSyncStatus) -> List[str]:
        """Generate actionable recommendations based on status"""
        recommendations = []

        for entity_type, entity_status in status.entity_statuses.items():
            if entity_status.health_status == SyncHealthStatus.CRITICAL:
                recommendations.append(
                    f"CRITICAL: {entity_type} has {entity_status.failed_records} failed syncs "
                    f"({entity_status.success_rate:.1f}% success rate). Run full sync immediately."
                )

            if entity_status.duplicate_count > 0:
                recommendations.append(
                    f"WARNING: {entity_type} has {entity_status.duplicate_count} duplicate records. "
                    f"Run deduplication process."
                )

            if entity_status.last_sync_time:
                time_since_sync = datetime.utcnow() - entity_status.last_sync_time
                if time_since_sync > timedelta(hours=24):
                    recommendations.append(
                        f"WARNING: {entity_type} last synced {time_since_sync.days} days ago. "
                        f"Consider running incremental sync."
                    )

        return recommendations

    def get_entity_details(self, entity_type: str) -> Dict[str, Any]:
        """
        Get detailed sync information for specific entity

        Args:
            entity_type: Entity type to check

        Returns:
            dict: Detailed status information
        """
        table_name = self.ENTITY_TABLE_MAPPING.get(entity_type)
        if not table_name:
            return {"error": f"Unknown entity type: {entity_type}"}

        status = self._get_entity_status(entity_type, table_name)

        return {
            "entity_type": status.entity_type,
            "health_status": status.health_status.value,
            "metrics": {
                "total_records": status.total_records,
                "synced_records": status.synced_records,
                "failed_records": status.failed_records,
                "success_rate": f"{status.success_rate:.2f}%",
                "duplicate_count": status.duplicate_count,
            },
            "last_sync": status.last_sync_time.isoformat() if status.last_sync_time else None,
            "errors": status.errors,
        }

    def generate_html_report(self, status: OverallSyncStatus) -> str:
        """
        Generate HTML report for sync status

        Args:
            status: Overall sync status

        Returns:
            str: HTML report
        """
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TDS Core - تقرير حالة المزامنة</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
                .healthy {{ background: #2ecc71; color: white; }}
                .warning {{ background: #f39c12; color: white; }}
                .critical {{ background: #e74c3c; color: white; }}
                .unknown {{ background: #95a5a6; color: white; }}
                .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric-label {{ font-weight: bold; color: #7f8c8d; }}
                .metric-value {{ font-size: 1.5em; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }}
                th {{ background: #3498db; color: white; }}
                tr:hover {{ background: #f8f9fa; }}
                .recommendations {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>تقرير حالة مزامنة TDS Core</h1>
                <p class="timestamp">تاريخ التقرير: {status.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC</p>

                <h2>الحالة العامة</h2>
                <div class="metric">
                    <span class="metric-label">حالة النظام:</span>
                    <span class="status-badge {status.health_status.value}">{status.health_status.value.upper()}</span>
                </div>

                <div class="metric">
                    <span class="metric-label">إجمالي الكيانات:</span>
                    <span class="metric-value">{status.total_entities}</span>
                </div>

                <div class="metric">
                    <span class="metric-label">كيانات سليمة:</span>
                    <span class="metric-value" style="color: #2ecc71;">{status.healthy_entities}</span>
                </div>

                <div class="metric">
                    <span class="metric-label">تحذيرات:</span>
                    <span class="metric-value" style="color: #f39c12;">{status.warning_entities}</span>
                </div>

                <div class="metric">
                    <span class="metric-label">حرجة:</span>
                    <span class="metric-value" style="color: #e74c3c;">{status.critical_entities}</span>
                </div>

                <h2>حالة الكيانات</h2>
                <table>
                    <tr>
                        <th>نوع الكيان</th>
                        <th>إجمالي السجلات</th>
                        <th>المتزامنة</th>
                        <th>الفاشلة</th>
                        <th>المكررة</th>
                        <th>نسبة النجاح</th>
                        <th>الحالة</th>
                    </tr>
        """

        for entity_type, entity_status in status.entity_statuses.items():
            html += f"""
                    <tr>
                        <td>{entity_type}</td>
                        <td>{entity_status.total_records}</td>
                        <td>{entity_status.synced_records}</td>
                        <td>{entity_status.failed_records}</td>
                        <td>{entity_status.duplicate_count}</td>
                        <td>{entity_status.success_rate:.1f}%</td>
                        <td><span class="status-badge {entity_status.health_status.value}">{entity_status.health_status.value}</span></td>
                    </tr>
            """

        html += """
                </table>
        """

        if status.recommendations:
            html += """
                <h2>التوصيات</h2>
                <div class="recommendations">
                    <ul>
            """
            for rec in status.recommendations:
                html += f"<li>{rec}</li>"
            html += """
                    </ul>
                </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        return html
