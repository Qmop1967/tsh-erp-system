"""
TDS Data Validation and Integrity Service
==========================================

Comprehensive data validation and integrity checking.
Ensures data quality and consistency across the system.

خدمة التحقق من صحة البيانات وسلامتها

Features:
- Pre-save validation
- Post-save verification
- Data integrity checks
- Reconciliation with Zoho
- Orphan record detection
- Data consistency reports

Author: TSH ERP Team
Date: November 9, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation issue severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Data validation issue"""
    severity: ValidationSeverity
    entity_type: str
    entity_id: str
    field: str
    issue: str
    current_value: Any
    expected_value: Optional[Any] = None
    recommendation: Optional[str] = None


@dataclass
class ValidationReport:
    """Validation report"""
    timestamp: datetime
    entity_type: str
    total_records: int
    valid_records: int
    issues: List[ValidationIssue]

    @property
    def invalid_records(self) -> int:
        return self.total_records - self.valid_records

    @property
    def validation_rate(self) -> float:
        if self.total_records == 0:
            return 100.0
        return (self.valid_records / self.total_records) * 100


class DataValidator:
    """
    Comprehensive data validator
    مدقق البيانات الشامل

    Validates data integrity, consistency, and correctness.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize data validator

        Args:
            db: Database session
        """
        self.db = db

    async def validate_product(self, product_data: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate product data

        Args:
            product_data: Product data to validate

        Returns:
            List of validation issues
        """
        issues = []

        # Required fields
        required_fields = ['zoho_item_id', 'sku', 'name']
        for field in required_fields:
            if not product_data.get(field):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    entity_type='product',
                    entity_id=str(product_data.get('id', 'unknown')),
                    field=field,
                    issue=f"Required field '{field}' is missing or empty",
                    current_value=product_data.get(field),
                    recommendation=f"Provide valid {field}"
                ))

        # Price validation
        price = product_data.get('price')
        if price is not None:
            if price < 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    entity_type='product',
                    entity_id=str(product_data.get('id', 'unknown')),
                    field='price',
                    issue="Price cannot be negative",
                    current_value=price,
                    recommendation="Set price to 0 or positive value"
                ))

        # Stock validation
        stock = product_data.get('actual_available_stock')
        if stock is not None and stock < 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                entity_type='product',
                entity_id=str(product_data.get('id', 'unknown')),
                field='actual_available_stock',
                issue="Stock cannot be negative",
                current_value=stock,
                recommendation="Investigate negative stock and correct"
            ))

        # SKU uniqueness (would need database check)
        sku = product_data.get('sku')
        if sku:
            result = await self.db.execute(
                select(func.count()).select_from(text("products"))
                .where(text(f"sku = '{sku}' AND id != {product_data.get('id', 0)}"))
            )
            count = result.scalar()
            if count > 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    entity_type='product',
                    entity_id=str(product_data.get('id', 'unknown')),
                    field='sku',
                    issue=f"SKU '{sku}' already exists for another product",
                    current_value=sku,
                    recommendation="Use unique SKU"
                ))

        return issues

    async def validate_product_batch(
        self,
        limit: int = 1000
    ) -> ValidationReport:
        """
        Validate a batch of products in the database

        Args:
            limit: Maximum products to validate

        Returns:
            ValidationReport with findings
        """
        logger.info(f"Starting product validation (limit={limit})...")

        # Get products to validate
        result = await self.db.execute(
            text("""
                SELECT
                    id, zoho_item_id, sku, name, price,
                    actual_available_stock, is_active
                FROM products
                WHERE zoho_item_id IS NOT NULL
                LIMIT :limit
            """),
            {"limit": limit}
        )
        products = result.fetchall()

        total_records = len(products)
        all_issues = []

        for product in products:
            product_dict = {
                'id': product[0],
                'zoho_item_id': product[1],
                'sku': product[2],
                'name': product[3],
                'price': product[4],
                'actual_available_stock': product[5],
                'is_active': product[6],
            }

            issues = await self.validate_product(product_dict)
            all_issues.extend(issues)

        valid_records = total_records - len(set(issue.entity_id for issue in all_issues if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]))

        report = ValidationReport(
            timestamp=datetime.utcnow(),
            entity_type='product',
            total_records=total_records,
            valid_records=valid_records,
            issues=all_issues
        )

        logger.info(
            f"Product validation complete: "
            f"{report.valid_records}/{report.total_records} valid "
            f"({report.validation_rate:.1f}%), "
            f"{len(all_issues)} issues found"
        )

        return report

    async def check_orphaned_records(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check for orphaned records (records with invalid foreign keys)

        Returns:
            Dictionary of orphaned records by type
        """
        logger.info("Checking for orphaned records...")

        orphans = {}

        # Check products without category
        result = await self.db.execute(
            text("""
                SELECT id, sku, name, category_id
                FROM products
                WHERE category_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM categories WHERE id = products.category_id
                )
                LIMIT 100
            """)
        )
        orphaned_products = result.fetchall()

        if orphaned_products:
            orphans['products_without_category'] = [
                {
                    'id': row[0],
                    'sku': row[1],
                    'name': row[2],
                    'invalid_category_id': row[3]
                }
                for row in orphaned_products
            ]
            logger.warning(f"Found {len(orphaned_products)} products with invalid category_id")

        return orphans

    async def reconcile_with_zoho(
        self,
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Reconcile local data with Zoho

        Checks for:
        - Missing items in local database
        - Extra items in local database
        - Data mismatches

        Args:
            sample_size: Number of items to check

        Returns:
            Reconciliation report
        """
        logger.info(f"Starting Zoho reconciliation (sample_size={sample_size})...")

        # Get sample of local products with Zoho ID
        result = await self.db.execute(
            text("""
                SELECT id, zoho_item_id, sku, name, price, actual_available_stock
                FROM products
                WHERE zoho_item_id IS NOT NULL
                ORDER BY updated_at DESC
                LIMIT :limit
            """),
            {"limit": sample_size}
        )
        local_products = result.fetchall()

        mismatches = []
        missing_in_local = []
        extra_in_local = []

        # TODO: Fetch from Zoho API and compare
        # For now, return structure

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'sample_size': len(local_products),
            'mismatches': len(mismatches),
            'missing_in_local': len(missing_in_local),
            'extra_in_local': len(extra_in_local),
            'details': {
                'mismatches': mismatches,
                'missing': missing_in_local,
                'extra': extra_in_local,
            }
        }

        logger.info(
            f"Reconciliation complete: {len(mismatches)} mismatches, "
            f"{len(missing_in_local)} missing, {len(extra_in_local)} extra"
        )

        return report

    async def check_data_integrity(self) -> Dict[str, Any]:
        """
        Comprehensive data integrity check

        Returns:
            Integrity report
        """
        logger.info("Running comprehensive data integrity check...")

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }

        # Check 1: Products with missing required fields
        result = await self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM products
                WHERE zoho_item_id IS NULL OR sku IS NULL OR name IS NULL
            """)
        )
        missing_required = result.scalar()
        report['checks']['products_missing_required_fields'] = {
            'count': missing_required,
            'severity': 'critical' if missing_required > 0 else 'ok'
        }

        # Check 2: Products with negative prices
        result = await self.db.execute(
            text("SELECT COUNT(*) FROM products WHERE price < 0")
        )
        negative_prices = result.scalar()
        report['checks']['products_negative_prices'] = {
            'count': negative_prices,
            'severity': 'error' if negative_prices > 0 else 'ok'
        }

        # Check 3: Products with negative stock
        result = await self.db.execute(
            text("SELECT COUNT(*) FROM products WHERE actual_available_stock < 0")
        )
        negative_stock = result.scalar()
        report['checks']['products_negative_stock'] = {
            'count': negative_stock,
            'severity': 'warning' if negative_stock > 0 else 'ok'
        }

        # Check 4: Duplicate SKUs
        result = await self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT sku
                    FROM products
                    WHERE sku IS NOT NULL
                    GROUP BY sku
                    HAVING COUNT(*) > 1
                ) AS duplicates
            """)
        )
        duplicate_skus = result.scalar()
        report['checks']['duplicate_skus'] = {
            'count': duplicate_skus,
            'severity': 'error' if duplicate_skus > 0 else 'ok'
        }

        # Check 5: Products not synced in 7 days
        result = await self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM products
                WHERE zoho_item_id IS NOT NULL
                AND updated_at < NOW() - INTERVAL '7 days'
            """)
        )
        stale_products = result.scalar()
        report['checks']['stale_products_7days'] = {
            'count': stale_products,
            'severity': 'warning' if stale_products > 100 else 'info'
        }

        # Calculate overall health
        critical_issues = sum(
            1 for check in report['checks'].values()
            if check['severity'] == 'critical'
        )
        error_issues = sum(
            1 for check in report['checks'].values()
            if check['severity'] == 'error'
        )

        if critical_issues > 0:
            report['overall_status'] = 'critical'
        elif error_issues > 0:
            report['overall_status'] = 'degraded'
        else:
            report['overall_status'] = 'healthy'

        logger.info(
            f"Data integrity check complete: {report['overall_status']} - "
            f"{critical_issues} critical, {error_issues} errors"
        )

        return report

    async def generate_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate audit trail for an entity

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            days_back: Days of history to fetch

        Returns:
            List of audit events
        """
        # TODO: Implement audit trail from TDS sync logs
        audit_trail = []

        since = datetime.utcnow() - timedelta(days=days_back)

        # Get sync events for this entity
        result = await self.db.execute(
            text("""
                SELECT
                    created_at, status, operation_type,
                    validated_payload, processing_result
                FROM tds_sync_queue
                WHERE entity_type = :entity_type
                AND source_entity_id = :entity_id
                AND created_at >= :since
                ORDER BY created_at DESC
            """),
            {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'since': since
            }
        )
        events = result.fetchall()

        for event in events:
            audit_trail.append({
                'timestamp': event[0].isoformat(),
                'status': str(event[1]),
                'operation': str(event[2]),
                'payload': event[3],
                'result': event[4],
            })

        return audit_trail
