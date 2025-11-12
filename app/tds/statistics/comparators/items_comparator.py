"""
Items Comparator
================

Compares item/product statistics between Zoho and local systems.

مقارنة إحصائيات المنتجات
"""

import logging
from typing import List
from sqlalchemy.orm import Session

from app.models.migration import MigrationItem
from app.tds.integrations.zoho import UnifiedZohoClient, ZohoAPI
from app.tds.statistics.models import (
    ItemStatistics,
    ComparisonResult,
    EntityType,
    MissingEntity,
    MismatchedEntity,
    DataMismatch,
    SourceSystem,
    SyncRecommendation,
)

logger = logging.getLogger(__name__)


class ItemsComparator:
    """
    Compares item/product data between Zoho Inventory and TSH ERP

    يقارن بيانات المنتجات بين Zoho و TSH ERP

    Features:
    - Identifies missing items in either system
    - Detects data mismatches (prices, names, status, etc.)
    - Provides sync recommendations
    - Calculates match percentage
    """

    def __init__(
        self,
        db: Session = None,
        zoho_client: UnifiedZohoClient = None
    ):
        """
        Initialize items comparator

        Args:
            db: Database session for local queries
            zoho_client: Zoho API client for detailed comparisons
        """
        self.db = db
        self.zoho_client = zoho_client

    def compare(
        self,
        zoho_stats: ItemStatistics,
        local_stats: ItemStatistics
    ) -> ComparisonResult:
        """
        Compare item statistics from both systems

        Args:
            zoho_stats: Statistics from Zoho
            local_stats: Statistics from local database

        Returns:
            ComparisonResult with detailed comparison

        مقارنة إحصائيات المنتجات من كلا النظامين
        """
        logger.info("Comparing items between Zoho and Local...")

        # Calculate differences
        difference = zoho_stats.total_count - local_stats.total_count

        # Calculate match count (items present in both systems)
        # This would require detailed item-by-item comparison
        # For now, use minimum of both counts as approximation
        match_count = min(zoho_stats.total_count, local_stats.total_count)

        # Calculate match percentage
        if zoho_stats.total_count > 0:
            match_percentage = (match_count / zoho_stats.total_count) * 100
        else:
            match_percentage = 100.0

        # Determine if sync is required
        requires_sync = abs(difference) > 10 or match_percentage < 95.0

        # Determine sync recommendation
        if abs(difference) > 100:
            sync_recommendation = SyncRecommendation.FULL_SYNC
            sync_priority = 10
        elif abs(difference) > 10:
            sync_recommendation = SyncRecommendation.INCREMENTAL_SYNC
            sync_priority = 7
        elif match_percentage < 95.0:
            sync_recommendation = SyncRecommendation.MANUAL_REVIEW
            sync_priority = 5
        else:
            sync_recommendation = SyncRecommendation.NO_SYNC_NEEDED
            sync_priority = 1

        # Estimate sync duration (rough calculation)
        items_to_sync = abs(difference)
        estimated_sync_duration_minutes = max(1, int(items_to_sync / 100))  # ~100 items/min

        logger.info(
            f"Items comparison: Zoho={zoho_stats.total_count}, "
            f"Local={local_stats.total_count}, "
            f"Match={match_percentage:.1f}%"
        )

        result = ComparisonResult(
            entity_type=EntityType.ITEMS,
            zoho_count=zoho_stats.total_count,
            local_count=local_stats.total_count,
            difference=difference,
            match_count=match_count,
            match_percentage=round(match_percentage, 2),
            missing_in_local=[],  # Will be populated by detailed comparison
            missing_in_zoho=[],   # Will be populated by detailed comparison
            mismatched_entities=[],  # Will be populated by detailed comparison
            requires_sync=requires_sync,
            sync_recommendation=sync_recommendation,
            sync_priority=sync_priority,
            estimated_sync_duration_minutes=estimated_sync_duration_minutes
        )

        # If database and client available, perform detailed comparison
        if self.db and self.zoho_client:
            self._detailed_comparison(result)

        return result

    async def _detailed_comparison(self, result: ComparisonResult):
        """
        Perform detailed item-by-item comparison

        Args:
            result: ComparisonResult to populate with detailed findings

        مقارنة تفصيلية عنصر بعنصر
        """
        logger.info("Performing detailed items comparison...")

        try:
            # Fetch all Zoho items
            zoho_items = await self.zoho_client.paginated_fetch(
                api_type=ZohoAPI.INVENTORY,
                endpoint="items",
                page_size=200
            )

            # Create Zoho items map (zoho_item_id -> item)
            zoho_items_map = {item["item_id"]: item for item in zoho_items}
            zoho_item_ids = set(zoho_items_map.keys())

            # Fetch all local items
            local_items = self.db.query(MigrationItem).all()

            # Create local items map (zoho_item_id -> item)
            local_items_map = {}
            local_zoho_ids = set()

            for item in local_items:
                if item.zoho_item_id:
                    local_items_map[item.zoho_item_id] = item
                    local_zoho_ids.add(item.zoho_item_id)

            # Find missing items
            missing_in_local_ids = zoho_item_ids - local_zoho_ids
            missing_in_zoho_ids = local_zoho_ids - zoho_item_ids

            # Populate missing in local
            for zoho_id in missing_in_local_ids:
                zoho_item = zoho_items_map[zoho_id]
                result.missing_in_local.append(
                    MissingEntity(
                        id=zoho_id,
                        name=zoho_item.get("name", "Unknown"),
                        entity_type="item",
                        missing_from=SourceSystem.LOCAL,
                        zoho_id=zoho_id
                    )
                )

            # Populate missing in Zoho
            for zoho_id in missing_in_zoho_ids:
                local_item = local_items_map[zoho_id]
                result.missing_in_zoho.append(
                    MissingEntity(
                        id=str(local_item.id),
                        name=local_item.name_en or "Unknown",
                        entity_type="item",
                        missing_from=SourceSystem.ZOHO,
                        local_id=str(local_item.id),
                        zoho_id=zoho_id
                    )
                )

            # Find mismatched items (present in both but with different data)
            common_ids = zoho_item_ids & local_zoho_ids

            for zoho_id in common_ids:
                zoho_item = zoho_items_map[zoho_id]
                local_item = local_items_map[zoho_id]

                mismatches = []

                # Compare name
                zoho_name = zoho_item.get("name", "")
                local_name = local_item.name_en or ""
                if zoho_name != local_name:
                    mismatches.append(DataMismatch(
                        field="name",
                        zoho_value=zoho_name,
                        local_value=local_name,
                        severity="medium"
                    ))

                # Compare price
                zoho_price = float(zoho_item.get("rate", 0) or 0)
                local_price = float(local_item.selling_price_usd or 0)
                if abs(zoho_price - local_price) > 0.01:
                    mismatches.append(DataMismatch(
                        field="price",
                        zoho_value=zoho_price,
                        local_value=local_price,
                        severity="high"
                    ))

                # Compare status
                zoho_status = zoho_item.get("status", "")
                local_status = "active" if local_item.is_active else "inactive"
                if zoho_status != local_status:
                    mismatches.append(DataMismatch(
                        field="status",
                        zoho_value=zoho_status,
                        local_value=local_status,
                        severity="low"
                    ))

                # If there are mismatches, add to result
                if mismatches:
                    result.mismatched_entities.append(
                        MismatchedEntity(
                            entity_id=zoho_id,
                            entity_name=zoho_name,
                            entity_type="item",
                            mismatches=mismatches
                        )
                    )

            # Update match count with actual comparison
            result.match_count = len(common_ids) - len(result.mismatched_entities)
            result.match_percentage = (
                (result.match_count / result.zoho_count * 100)
                if result.zoho_count > 0
                else 100.0
            )

            logger.info(
                f"Detailed comparison complete: "
                f"{len(result.missing_in_local)} missing in local, "
                f"{len(result.missing_in_zoho)} missing in Zoho, "
                f"{len(result.mismatched_entities)} mismatched"
            )

        except Exception as e:
            logger.error(f"Detailed comparison failed: {e}", exc_info=True)
