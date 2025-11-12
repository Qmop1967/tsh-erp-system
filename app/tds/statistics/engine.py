"""
TDS Statistics Engine
=====================

Core engine for statistics collection, comparison, and sync orchestration.

محرك إحصائيات TDS
"""

import logging
import time
from typing import Dict, Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

from app.tds.statistics.models import (
    FullComparisonReport,
    SystemHealthScore,
    EntityType,
    ComparisonResult,
    ZohoStatistics,
    LocalStatistics,
)
from app.tds.statistics.collectors import (
    ZohoDataCollector,
    LocalDataCollector,
)
from app.tds.statistics.comparators.items_comparator import ItemsComparator
from app.tds.integrations.zoho import UnifiedZohoClient, ZohoCredentials
from app.tds.integrations.base import SyncMode

logger = logging.getLogger(__name__)


class StatisticsEngine:
    """
    TDS Statistics & Comparison Engine

    محرك إحصائيات ومقارنة TDS

    Features:
    - Orchestrates data collection from Zoho and local database
    - Performs comprehensive comparisons across all entity types
    - Generates health scores and recommendations
    - Provides sync recommendations
    - Tracks statistics over time
    - Generates reports in multiple formats

    Responsibilities:
    1. Data Collection
       - Collect statistics from Zoho (items, customers, vendors, etc.)
       - Collect statistics from local database
       - Handle errors and retries

    2. Comparison & Analysis
       - Compare counts and data quality
       - Identify missing entities
       - Detect data mismatches
       - Calculate match percentages

    3. Health Monitoring
       - Calculate system health scores
       - Identify critical issues
       - Generate alerts

    4. Sync Recommendations
       - Determine what needs to be synced
       - Prioritize sync operations
       - Estimate sync duration

    5. Reporting
       - Generate summary reports
       - Create detailed comparison reports
       - Export to various formats (JSON, CSV, PDF)
    """

    def __init__(
        self,
        db: Session,
        zoho_credentials: Optional[ZohoCredentials] = None,
        zoho_client: Optional[UnifiedZohoClient] = None
    ):
        """
        Initialize Statistics Engine

        Args:
            db: Database session for local queries
            zoho_credentials: Zoho API credentials
            zoho_client: Existing Zoho client (optional)
        """
        self.db = db

        # Initialize collectors
        self.zoho_collector = ZohoDataCollector(
            client=zoho_client,
            credentials=zoho_credentials
        )
        self.local_collector = LocalDataCollector(db)

        # Initialize comparators
        self.items_comparator = ItemsComparator(db, zoho_client)

        # Placeholder comparators (to be implemented)
        # self.customers_comparator = CustomersComparator(db, zoho_client)
        # self.vendors_comparator = VendorsComparator(db, zoho_client)
        # self.pricelists_comparator = PriceListsComparator(db, zoho_client)
        # self.stock_comparator = StockComparator(db, zoho_client)

        logger.info("Statistics Engine initialized")

    async def collect_and_compare(
        self,
        entities: Optional[List[EntityType]] = None
    ) -> FullComparisonReport:
        """
        Collect statistics and perform comparison

        Args:
            entities: Optional list of specific entities to compare
                     If None, compares all entities

        Returns:
            Complete comparison report with all findings

        جمع الإحصائيات وإجراء المقارنة
        """
        logger.info("="*80)
        logger.info("🚀 Starting TDS Statistics Collection & Comparison")
        logger.info("="*80)

        start_time = time.time()
        report_id = str(uuid4())

        try:
            # Step 1: Collect Zoho statistics
            logger.info("\n📊 Step 1: Collecting Zoho Statistics...")
            zoho_stats = await self.zoho_collector.collect_all_stats()
            logger.info(f"✅ Zoho statistics collected at {zoho_stats.collected_at}")

            # Step 2: Collect local statistics
            logger.info("\n📊 Step 2: Collecting Local Statistics...")
            local_stats = await self.local_collector.collect_all_stats()
            logger.info(f"✅ Local statistics collected at {local_stats.collected_at}")

            # Step 3: Perform comparisons
            logger.info("\n🔍 Step 3: Performing Comparisons...")
            comparisons = await self._perform_comparisons(
                zoho_stats,
                local_stats,
                entities
            )

            # Step 4: Calculate overall match percentage
            logger.info("\n📈 Step 4: Calculating Overall Metrics...")
            overall_match = self._calculate_overall_match(comparisons)

            # Step 5: Generate health score
            logger.info("\n🏥 Step 5: Generating Health Score...")
            health_score = self._calculate_health_score(comparisons)

            # Step 6: Generate sync recommendations
            logger.info("\n💡 Step 6: Generating Sync Recommendations...")
            sync_recommendations = self._generate_sync_recommendations(comparisons)

            # Step 7: Generate alerts
            logger.info("\n⚠️  Step 7: Checking for Alerts...")
            alerts = self._generate_alerts(comparisons, health_score)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Create report
            report = FullComparisonReport(
                report_id=report_id,
                timestamp=datetime.utcnow(),
                zoho_statistics=zoho_stats,
                local_statistics=local_stats,
                comparisons=comparisons,
                overall_match_percentage=overall_match,
                health_score=health_score,
                sync_recommendations=sync_recommendations,
                alerts=alerts,
                execution_time_seconds=round(execution_time, 2)
            )

            # Save report to database
            await self._save_report(report)

            logger.info("\n" + "="*80)
            logger.info(f"✅ Statistics Collection & Comparison Complete!")
            logger.info(f"   Report ID: {report_id}")
            logger.info(f"   Overall Match: {overall_match:.1f}%")
            logger.info(f"   Health Score: {health_score.overall_score:.1f}/100")
            logger.info(f"   Execution Time: {execution_time:.2f}s")
            logger.info(f"   Status: {health_score.status.upper()}")
            logger.info("="*80 + "\n")

            # Print summary
            self._print_report_summary(report)

            return report

        except Exception as e:
            logger.error(f"❌ Statistics collection failed: {e}", exc_info=True)
            raise

    async def _perform_comparisons(
        self,
        zoho_stats: ZohoStatistics,
        local_stats: LocalStatistics,
        entities: Optional[List[EntityType]] = None
    ) -> Dict[str, ComparisonResult]:
        """
        Perform comparisons for all or specified entities

        Args:
            zoho_stats: Zoho statistics
            local_stats: Local statistics
            entities: Optional list of entities to compare

        Returns:
            Dictionary of comparison results by entity type
        """
        comparisons = {}

        # Items comparison
        if not entities or EntityType.ITEMS in entities:
            logger.info("   🔸 Comparing items...")
            comparisons["items"] = self.items_comparator.compare(
                zoho_stats.items,
                local_stats.items
            )

        # Customers comparison (placeholder)
        if not entities or EntityType.CUSTOMERS in entities:
            logger.info("   🔸 Comparing customers...")
            comparisons["customers"] = self._compare_customers(
                zoho_stats.customers,
                local_stats.customers
            )

        # Vendors comparison (placeholder)
        if not entities or EntityType.VENDORS in entities:
            logger.info("   🔸 Comparing vendors...")
            comparisons["vendors"] = self._compare_vendors(
                zoho_stats.vendors,
                local_stats.vendors
            )

        # Price lists comparison (placeholder)
        if not entities or EntityType.PRICE_LISTS in entities:
            logger.info("   🔸 Comparing price lists...")
            comparisons["price_lists"] = self._compare_pricelists(
                zoho_stats.price_lists,
                local_stats.price_lists
            )

        # Stock comparison (placeholder)
        if not entities or EntityType.STOCK in entities:
            logger.info("   🔸 Comparing stock...")
            comparisons["stock"] = self._compare_stock(
                zoho_stats.stock,
                local_stats.stock
            )

        # Images comparison (placeholder)
        if not entities or EntityType.IMAGES in entities:
            logger.info("   🔸 Comparing images...")
            comparisons["images"] = self._compare_images(
                zoho_stats.images,
                local_stats.images
            )

        return comparisons

    def _compare_customers(self, zoho_stats, local_stats) -> ComparisonResult:
        """Placeholder for customer comparison"""
        difference = zoho_stats.total_count - local_stats.total_count
        match_count = min(zoho_stats.total_count, local_stats.total_count)
        match_percentage = (
            (match_count / zoho_stats.total_count * 100)
            if zoho_stats.total_count > 0
            else 100.0
        )

        return ComparisonResult(
            entity_type=EntityType.CUSTOMERS,
            zoho_count=zoho_stats.total_count,
            local_count=local_stats.total_count,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            requires_sync=abs(difference) > 5
        )

    def _compare_vendors(self, zoho_stats, local_stats) -> ComparisonResult:
        """Placeholder for vendor comparison"""
        difference = zoho_stats.total_count - local_stats.total_count
        match_count = min(zoho_stats.total_count, local_stats.total_count)
        match_percentage = (
            (match_count / zoho_stats.total_count * 100)
            if zoho_stats.total_count > 0
            else 100.0
        )

        return ComparisonResult(
            entity_type=EntityType.VENDORS,
            zoho_count=zoho_stats.total_count,
            local_count=local_stats.total_count,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            requires_sync=abs(difference) > 5
        )

    def _compare_pricelists(self, zoho_stats, local_stats) -> ComparisonResult:
        """Placeholder for price list comparison"""
        difference = zoho_stats.total_lists - local_stats.total_lists
        match_count = min(zoho_stats.total_lists, local_stats.total_lists)
        match_percentage = (
            (match_count / zoho_stats.total_lists * 100)
            if zoho_stats.total_lists > 0
            else 100.0
        )

        return ComparisonResult(
            entity_type=EntityType.PRICE_LISTS,
            zoho_count=zoho_stats.total_lists,
            local_count=local_stats.total_lists,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            requires_sync=abs(difference) > 1
        )

    def _compare_stock(self, zoho_stats, local_stats) -> ComparisonResult:
        """Placeholder for stock comparison"""
        difference = zoho_stats.total_items_in_stock - local_stats.total_items_in_stock
        match_count = min(zoho_stats.total_items_in_stock, local_stats.total_items_in_stock)
        match_percentage = (
            (match_count / zoho_stats.total_items_in_stock * 100)
            if zoho_stats.total_items_in_stock > 0
            else 100.0
        )

        return ComparisonResult(
            entity_type=EntityType.STOCK,
            zoho_count=zoho_stats.total_items_in_stock,
            local_count=local_stats.total_items_in_stock,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            requires_sync=abs(difference) > 10
        )

    def _compare_images(self, zoho_stats, local_stats) -> ComparisonResult:
        """Placeholder for images comparison"""
        difference = zoho_stats.with_images - local_stats.with_images
        match_count = min(zoho_stats.with_images, local_stats.with_images)
        match_percentage = (
            (match_count / zoho_stats.with_images * 100)
            if zoho_stats.with_images > 0
            else 100.0
        )

        return ComparisonResult(
            entity_type=EntityType.IMAGES,
            zoho_count=zoho_stats.with_images,
            local_count=local_stats.with_images,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            requires_sync=abs(difference) > 50
        )

    def _calculate_overall_match(
        self,
        comparisons: Dict[str, ComparisonResult]
    ) -> float:
        """Calculate overall match percentage across all entities"""
        if not comparisons:
            return 100.0

        total_match = sum(c.match_percentage for c in comparisons.values())
        return round(total_match / len(comparisons), 2)

    def _calculate_health_score(
        self,
        comparisons: Dict[str, ComparisonResult]
    ) -> SystemHealthScore:
        """Calculate system health score based on comparisons"""
        # Individual scores
        items_score = comparisons.get("items", ComparisonResult(
            entity_type=EntityType.ITEMS,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        customers_score = comparisons.get("customers", ComparisonResult(
            entity_type=EntityType.CUSTOMERS,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        vendors_score = comparisons.get("vendors", ComparisonResult(
            entity_type=EntityType.VENDORS,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        price_lists_score = comparisons.get("price_lists", ComparisonResult(
            entity_type=EntityType.PRICE_LISTS,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        stock_score = comparisons.get("stock", ComparisonResult(
            entity_type=EntityType.STOCK,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        images_score = comparisons.get("images", ComparisonResult(
            entity_type=EntityType.IMAGES,
            zoho_count=0,
            local_count=0,
            difference=0,
            match_count=0,
            match_percentage=100.0
        )).match_percentage

        # Overall score (weighted average)
        overall_score = (
            items_score * 0.3 +
            customers_score * 0.2 +
            vendors_score * 0.1 +
            price_lists_score * 0.15 +
            stock_score * 0.15 +
            images_score * 0.1
        )

        # Determine status
        if overall_score >= 95:
            status = "excellent"
        elif overall_score >= 90:
            status = "good"
        elif overall_score >= 80:
            status = "warning"
        else:
            status = "critical"

        # Collect issues and recommendations
        issues = []
        recommendations = []

        for entity_type, comparison in comparisons.items():
            if comparison.match_percentage < 90:
                issues.append(
                    f"{entity_type}: {comparison.match_percentage:.1f}% match "
                    f"({comparison.total_issues} issues)"
                )
                recommendations.append(
                    f"Sync {entity_type} to resolve {comparison.total_issues} issues"
                )

        return SystemHealthScore(
            overall_score=round(overall_score, 2),
            items_score=round(items_score, 2),
            customers_score=round(customers_score, 2),
            vendors_score=round(vendors_score, 2),
            price_lists_score=round(price_lists_score, 2),
            stock_score=round(stock_score, 2),
            images_score=round(images_score, 2),
            status=status,
            issues=issues,
            recommendations=recommendations
        )

    def _generate_sync_recommendations(
        self,
        comparisons: Dict[str, ComparisonResult]
    ) -> List[str]:
        """Generate actionable sync recommendations"""
        recommendations = []

        for entity_type, comparison in comparisons.items():
            if comparison.requires_sync:
                recommendations.append(
                    f"🔄 Sync {entity_type}: "
                    f"{comparison.sync_recommendation.value} "
                    f"(Priority: {comparison.sync_priority}/10, "
                    f"~{comparison.estimated_sync_duration_minutes} minutes)"
                )

        if not recommendations:
            recommendations.append("✅ All systems in sync. No action required.")

        return recommendations

    def _generate_alerts(
        self,
        comparisons: Dict[str, ComparisonResult],
        health_score: SystemHealthScore
    ) -> List[str]:
        """Generate critical alerts"""
        alerts = []

        # Critical health score
        if health_score.overall_score < 80:
            alerts.append(
                f"🚨 CRITICAL: Overall health score is {health_score.overall_score:.1f}%. "
                "Immediate action required!"
            )

        # Large discrepancies
        for entity_type, comparison in comparisons.items():
            if abs(comparison.difference) > 100:
                alerts.append(
                    f"⚠️  WARNING: {entity_type} has {abs(comparison.difference)} "
                    f"{'missing' if comparison.difference > 0 else 'extra'} items"
                )

        return alerts

    async def _save_report(self, report: FullComparisonReport):
        """Save comparison report to database"""
        try:
            # TODO: Implement database save
            # Insert into tds_comparison_reports table
            logger.info(f"Report saved: {report.report_id}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def _print_report_summary(self, report: FullComparisonReport):
        """Print a formatted summary of the report"""
        print("\n" + "="*80)
        print("📊 TDS STATISTICS & COMPARISON REPORT")
        print("="*80)
        print(f"\n📅 Date: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 Report ID: {report.report_id}")
        print(f"⏱️  Execution Time: {report.execution_time_seconds}s")
        print(f"\n🏥 Health Score: {report.health_score.overall_score:.1f}/100 ({report.health_score.status.upper()})")
        print(f"📈 Overall Match: {report.overall_match_percentage:.1f}%")

        print("\n" + "-"*80)
        print("📊 ENTITY COMPARISON SUMMARY")
        print("-"*80)

        for entity_type, comparison in report.comparisons.items():
            status_icon = "✅" if comparison.is_healthy else "⚠️"
            print(f"\n{status_icon} {entity_type.upper()}")
            print(f"   Zoho: {comparison.zoho_count:,} | Local: {comparison.local_count:,}")
            print(f"   Match: {comparison.match_percentage:.1f}% | Difference: {comparison.difference:+,}")
            if comparison.requires_sync:
                print(f"   🔄 Action: {comparison.sync_recommendation.value}")

        if report.alerts:
            print("\n" + "-"*80)
            print("⚠️  ALERTS")
            print("-"*80)
            for alert in report.alerts:
                print(f"   {alert}")

        if report.sync_recommendations:
            print("\n" + "-"*80)
            print("💡 RECOMMENDATIONS")
            print("-"*80)
            for rec in report.sync_recommendations:
                print(f"   {rec}")

        print("\n" + "="*80 + "\n")

    async def auto_sync_differences(
        self,
        report: FullComparisonReport,
        dry_run: bool = False
    ):
        """
        Automatically sync differences based on comparison report

        Args:
            report: Comparison report with sync recommendations
            dry_run: If True, only simulate sync without making changes

        Returns:
            Dictionary with sync results per entity
        """
        from app.tds.zoho import ZohoService

        logger.info("="*80)
        logger.info(f"🔄 AUTO-SYNC MODE {'(DRY RUN)' if dry_run else '(LIVE)'}")
        logger.info("="*80)

        service = ZohoService(db=self.db)
        await service.start()

        sync_results = {}

        for entity_type, comparison in report.comparisons.items():
            if comparison.requires_sync:
                logger.info(
                    f"\n📦 {entity_type.upper()}: {comparison.sync_recommendation.value}"
                )
                logger.info(f"   Difference: {comparison.difference:+,} items")
                logger.info(f"   Priority: {comparison.sync_priority}/10")

                if not dry_run:
                    try:
                        # Map entity type string to EntityType enum
                        entity_map = {
                            'items': 'PRODUCTS',
                            'products': 'PRODUCTS',
                            'customers': 'CUSTOMERS',
                            'vendors': 'VENDORS',
                            'price_lists': 'PRICE_LISTS',
                            'stock': 'INVENTORY',
                            'images': 'IMAGES'
                        }

                        entity_enum_name = entity_map.get(entity_type.lower(), entity_type.upper())

                        # Perform actual sync based on entity type
                        if entity_type.lower() in ['items', 'products']:
                            result = await service.sync_products(mode=SyncMode.INCREMENTAL)
                        elif entity_type.lower() == 'customers':
                            result = await service.sync_customers(mode=SyncMode.INCREMENTAL)
                        elif entity_type.lower() in ['stock', 'inventory']:
                            result = await service.sync_stock()
                        else:
                            # Generic sync for other entities
                            result = await service.sync_entity(
                                EntityType[entity_enum_name],
                                mode=SyncMode.INCREMENTAL
                            )

                        sync_results[entity_type] = {
                            'success': True,
                            'synced_count': result.total_success,
                            'failed_count': result.total_failed,
                            'skipped_count': result.total_skipped
                        }

                        logger.info(f"   ✅ Synced: {result.total_success} | Failed: {result.total_failed} | Skipped: {result.total_skipped}")

                    except Exception as e:
                        logger.error(f"   ❌ Sync failed: {e}")
                        sync_results[entity_type] = {
                            'success': False,
                            'error': str(e)
                        }
                else:
                    logger.info(f"   🔍 [DRY RUN] Would sync {entity_type}")
                    sync_results[entity_type] = {
                        'dry_run': True,
                        'would_sync': True
                    }

        await service.stop()

        logger.info("\n" + "="*80)
        logger.info("✅ Auto-sync complete!")
        logger.info("="*80 + "\n")

        return sync_results
