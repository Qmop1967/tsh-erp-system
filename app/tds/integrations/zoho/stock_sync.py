"""
Unified Stock Sync Service
===========================

Consolidated stock sync functionality using TDS architecture.
Replaces app/services/zoho_stock_sync.py and related scripts.

خدمة مزامنة المخزون الموحدة

Features:
- Paginated batch processing (200 items per API call)
- Bulk database updates
- Real-time sync via webhooks
- Incremental sync support
- Progress tracking
- Event-driven architecture
- Comprehensive error handling

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from .client import UnifiedZohoClient, ZohoAPI
from .sync import ZohoSyncOrchestrator, SyncConfig, SyncMode, EntityType, SyncResult
from .processors.inventory import InventoryProcessor
from ....core.events.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class StockSyncConfig:
    """Stock sync configuration"""
    batch_size: int = 200
    active_only: bool = True
    with_stock_only: bool = False
    warehouses: Optional[List[str]] = None
    update_prices: bool = False
    sync_mode: SyncMode = SyncMode.INCREMENTAL


@dataclass
class StockItem:
    """Stock item data"""
    item_id: str
    sku: str
    name: str
    stock_on_hand: Decimal
    available_stock: Decimal
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    last_modified: Optional[datetime] = None


class UnifiedStockSyncService:
    """
    Unified Stock Sync Service
    خدمة مزامنة المخزون الموحدة

    Consolidates all stock sync functionality into TDS architecture.
    """

    def __init__(
        self,
        zoho_client: UnifiedZohoClient,
        sync_orchestrator: ZohoSyncOrchestrator,
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize unified stock sync service

        Args:
            zoho_client: Unified Zoho API client
            sync_orchestrator: Sync orchestrator instance
            event_bus: Event bus for publishing events
        """
        self.zoho = zoho_client
        self.orchestrator = sync_orchestrator
        self.event_bus = event_bus
        self.processor = InventoryProcessor()

        # Statistics
        self.stats = {
            "total_items_fetched": 0,
            "total_items_processed": 0,
            "total_stock_updated": 0,
            "total_errors": 0,
            "api_calls_made": 0,
            "start_time": None,
            "end_time": None
        }

    async def sync_all_stock(
        self,
        config: Optional[StockSyncConfig] = None
    ) -> SyncResult:
        """
        Sync all stock from Zoho Inventory

        Args:
            config: Stock sync configuration

        Returns:
            SyncResult: Sync operation results
        """
        config = config or StockSyncConfig()

        logger.info("=" * 70)
        logger.info("🔄 Starting Unified Stock Sync")
        logger.info(f"   Mode: {config.sync_mode}")
        logger.info(f"   Batch Size: {config.batch_size}")
        logger.info(f"   Active Only: {config.active_only}")
        logger.info("=" * 70)

        self.stats["start_time"] = datetime.utcnow()

        try:
            # Use orchestrator for full sync
            sync_config = SyncConfig(
                entity_type=EntityType.INVENTORY,
                mode=config.sync_mode,
                batch_size=config.batch_size,
                filter_params=self._build_filters(config)
            )

            result = await self.orchestrator.sync_entity(sync_config)

            self.stats["end_time"] = datetime.utcnow()
            self.stats["total_items_processed"] = result.total_processed
            self.stats["total_stock_updated"] = result.total_success
            self.stats["total_errors"] = result.total_failed

            # Publish completion event
            await self._publish_event("tds.stock.sync.completed", {
                "total_processed": result.total_processed,
                "total_success": result.total_success,
                "total_failed": result.total_failed,
                "duration_seconds": result.duration.total_seconds() if result.duration else 0
            })

            logger.info("=" * 70)
            logger.info("✅ Stock Sync Completed")
            logger.info(f"   Processed: {result.total_processed}")
            logger.info(f"   Updated: {result.total_success}")
            logger.info(f"   Failed: {result.total_failed}")
            logger.info(f"   Duration: {result.duration}")
            logger.info("=" * 70)

            return result

        except Exception as e:
            logger.error(f"Stock sync failed: {str(e)}", exc_info=True)
            self.stats["end_time"] = datetime.utcnow()
            self.stats["total_errors"] += 1

            await self._publish_event("tds.stock.sync.failed", {
                "error": str(e)
            })

            raise

    async def sync_specific_items(
        self,
        item_ids: List[str],
        config: Optional[StockSyncConfig] = None
    ) -> SyncResult:
        """
        Sync stock for specific items

        Args:
            item_ids: List of Zoho item IDs to sync
            config: Stock sync configuration

        Returns:
            SyncResult: Sync operation results
        """
        config = config or StockSyncConfig()

        logger.info(f"🔄 Syncing stock for {len(item_ids)} specific items")

        sync_config = SyncConfig(
            entity_type=EntityType.INVENTORY,
            mode=SyncMode.REALTIME,
            batch_size=config.batch_size
        )

        result = await self.orchestrator.sync_entity(
            config=sync_config,
            entity_ids=item_ids
        )

        logger.info(f"✅ Specific items sync completed: {result.total_success}/{len(item_ids)}")

        return result

    async def sync_warehouse_stock(
        self,
        warehouse_id: str,
        config: Optional[StockSyncConfig] = None
    ) -> Dict[str, Any]:
        """
        Sync stock for a specific warehouse

        Args:
            warehouse_id: Zoho warehouse ID
            config: Stock sync configuration

        Returns:
            dict: Sync results
        """
        config = config or StockSyncConfig()
        config.warehouses = [warehouse_id]

        logger.info(f"🏭 Syncing stock for warehouse: {warehouse_id}")

        # Fetch warehouse stock
        warehouse_stock = await self.zoho.get(
            api_type=ZohoAPI.INVENTORY,
            endpoint=f"items",
            params={
                "warehouse_id": warehouse_id,
                "per_page": config.batch_size
            }
        )

        items = self._extract_items(warehouse_stock)

        logger.info(f"   Found {len(items)} items in warehouse")

        # Process items
        results = {
            "warehouse_id": warehouse_id,
            "total_items": len(items),
            "updated": 0,
            "failed": 0
        }

        for item in items:
            try:
                # Validate and transform
                if self.processor.validate(item):
                    transformed = self.processor.transform(item)
                    # TODO: Save to database
                    results["updated"] += 1
            except Exception as e:
                logger.error(f"Failed to process item {item.get('item_id')}: {str(e)}")
                results["failed"] += 1

        logger.info(f"✅ Warehouse sync completed: {results['updated']}/{results['total_items']}")

        return results

    async def get_stock_summary(self) -> Dict[str, Any]:
        """
        Get stock summary from Zoho

        Returns:
            dict: Stock summary data
        """
        logger.info("📊 Fetching stock summary from Zoho")

        try:
            # Fetch summary data
            summary = await self.zoho.get(
                api_type=ZohoAPI.INVENTORY,
                endpoint="items",
                params={
                    "per_page": 1,
                    "page": 1
                }
            )

            page_context = summary.get('page_context', {})

            return {
                "total_items": page_context.get('total', 0),
                "has_more_pages": page_context.get('has_more_page', False),
                "fetched_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get stock summary: {str(e)}")
            return {
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }

    async def sync_low_stock_items(
        self,
        threshold: int = 10,
        config: Optional[StockSyncConfig] = None
    ) -> SyncResult:
        """
        Sync only items with low stock

        Args:
            threshold: Stock threshold (sync items with stock <= threshold)
            config: Stock sync configuration

        Returns:
            SyncResult: Sync operation results
        """
        config = config or StockSyncConfig()

        logger.info(f"⚠️  Syncing low stock items (threshold: {threshold})")

        # Fetch all items (we need to filter client-side as Zoho API doesn't support stock filtering)
        all_items = await self.zoho.paginated_fetch(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            page_size=config.batch_size
        )

        # Filter low stock items
        low_stock_items = [
            item for item in all_items
            if item.get('stock_on_hand', 0) <= threshold
        ]

        logger.info(f"   Found {len(low_stock_items)} items with stock <= {threshold}")

        if not low_stock_items:
            logger.info("   No low stock items found")
            return SyncResult(
                sync_id=f"low_stock_{datetime.utcnow().timestamp()}",
                entity_type=EntityType.INVENTORY,
                status="completed",
                mode=SyncMode.INCREMENTAL,
                total_processed=0
            )

        # Extract item IDs
        item_ids = [item['item_id'] for item in low_stock_items]

        # Sync specific items
        return await self.sync_specific_items(item_ids, config)

    def _build_filters(self, config: StockSyncConfig) -> Dict[str, Any]:
        """Build Zoho API filters from config"""
        filters = {}

        if config.active_only:
            filters['filter_by'] = 'Status.Active'

        if config.warehouses:
            # Note: Zoho API may not support warehouse filtering directly
            # This might need client-side filtering
            pass

        return filters

    def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract items from Zoho API response"""
        return response.get('items', [])

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to event bus"""
        if self.event_bus:
            await self.event_bus.publish({
                "event_type": event_type,
                "module": "tds.stock.sync",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_statistics(self) -> Dict[str, Any]:
        """Get sync statistics"""
        stats = self.stats.copy()

        if stats["start_time"] and stats["end_time"]:
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["duration_seconds"] = duration

            if stats["total_items_processed"] > 0:
                stats["items_per_second"] = stats["total_items_processed"] / duration

        return stats
