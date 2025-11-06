"""
Zoho Stock Sync Service - Optimized Paginated Batch Processing
Syncs item stock quantities from Zoho Inventory with minimal API calls
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.zoho_inventory_client import ZohoInventoryClient
from app.services.zoho_books_client import ZohoBooksClient
from app.tds.core.service import TDSService
from app.models.zoho_sync import SourceType, EntityType, OperationType

logger = logging.getLogger(__name__)


class ZohoStockSyncService:
    """
    Optimized service for syncing stock quantities from Zoho

    Features:
    - Paginated batch processing (200 items per API call)
    - Bulk database updates
    - TDS event integration
    - Minimal API calls
    - Progress tracking
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize stock sync service

        Args:
            db: Async database session
        """
        self.db = db
        self.zoho_client = ZohoInventoryClient(db)
        self.tds_service = TDSService(db)
        self.stats = {
            "total_items_from_zoho": 0,
            "api_calls_made": 0,
            "products_updated": 0,
            "products_created": 0,
            "products_skipped": 0,
            "errors": []
        }

    async def sync_all_stock(
        self,
        batch_size: int = 200,
        active_only: bool = True,
        with_stock_only: bool = False,
        db_batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Sync all item stock from Zoho Inventory using pagination

        Args:
            batch_size: Items per Zoho API call (max 200)
            active_only: Only sync active items
            with_stock_only: Only sync items with stock > 0
            db_batch_size: Number of products to update in database batch

        Returns:
            Statistics dictionary
        """
        logger.info("=" * 70)
        logger.info("🔄 Starting Zoho Stock Sync - Paginated Batch Mode")
        logger.info("=" * 70)

        start_time = datetime.now()

        # Create TDS sync run
        sync_run = await self.tds_service.create_sync_run(
            run_type=SourceType.ZOHO,
            entity_type=EntityType.PRODUCT,
            configuration={
                "task": "stock_sync",
                "batch_size": batch_size,
                "active_only": active_only,
                "with_stock_only": with_stock_only
            }
        )

        try:
            # Build filters for Zoho API
            filters = {}
            if active_only:
                filters["filter_by"] = "Status.Active"

            # Fetch items from Zoho with pagination
            items_batch = []
            page_number = 0

            logger.info(f"📥 Fetching items from Zoho (batch size: {batch_size})")

            async for zoho_item in self.zoho_client.fetch_items_paginated(
                per_page=batch_size,
                filters=filters
            ):
                self.stats["total_items_from_zoho"] += 1

                # Filter items with no stock if requested
                if with_stock_only:
                    stock = zoho_item.get("stock_on_hand", 0)
                    if stock <= 0:
                        self.stats["products_skipped"] += 1
                        continue

                # Add to batch
                items_batch.append(zoho_item)

                # Process batch when it reaches db_batch_size
                if len(items_batch) >= db_batch_size:
                    page_number += 1
                    await self._process_stock_batch(items_batch, page_number)
                    items_batch = []

                # Log progress every 500 items
                if self.stats["total_items_from_zoho"] % 500 == 0:
                    logger.info(
                        f"   Progress: {self.stats['total_items_from_zoho']} items fetched, "
                        f"{self.stats['products_updated']} updated"
                    )

            # Process remaining items
            if items_batch:
                page_number += 1
                await self._process_stock_batch(items_batch, page_number)

            # Calculate API calls made
            # Each page call is 1 API call (200 items max per call)
            self.stats["api_calls_made"] = (self.stats["total_items_from_zoho"] + batch_size - 1) // batch_size

            duration = (datetime.now() - start_time).total_seconds()

            # Complete TDS sync run
            await self.tds_service.complete_sync_run(
                sync_run_id=sync_run.id,
                total_processed=self.stats["total_items_from_zoho"],
                successful=self.stats["products_updated"] + self.stats["products_created"],
                failed=len(self.stats["errors"])
            )

            logger.info("=" * 70)
            logger.info("✅ Stock Sync Completed Successfully")
            logger.info("=" * 70)
            logger.info(f"   Total items from Zoho:  {self.stats['total_items_from_zoho']}")
            logger.info(f"   API calls made:         {self.stats['api_calls_made']}")
            logger.info(f"   Products updated:       {self.stats['products_updated']}")
            logger.info(f"   Products created:       {self.stats['products_created']}")
            logger.info(f"   Products skipped:       {self.stats['products_skipped']}")
            logger.info(f"   Errors:                 {len(self.stats['errors'])}")
            logger.info(f"   Duration:               {duration:.2f} seconds")
            logger.info(f"   Avg items/API call:     {self.stats['total_items_from_zoho'] / max(self.stats['api_calls_made'], 1):.1f}")
            logger.info("=" * 70)

            return {
                "success": True,
                "stats": self.stats,
                "duration_seconds": duration,
                "sync_run_id": str(sync_run.id)
            }

        except Exception as e:
            logger.error(f"❌ Stock sync failed: {e}", exc_info=True)

            # Mark sync run as failed
            from app.models.zoho_sync import EventStatus
            sync_run.status = EventStatus.FAILED
            sync_run.error_summary = str(e)
            await self.db.commit()

            return {
                "success": False,
                "error": str(e),
                "stats": self.stats
            }

    async def _process_stock_batch(
        self,
        items_batch: List[Dict],
        batch_number: int
    ) -> None:
        """
        Process a batch of items - bulk update in database

        Args:
            items_batch: List of Zoho items
            batch_number: Batch number for logging
        """
        if not items_batch:
            return

        logger.info(f"📦 Processing batch #{batch_number} ({len(items_batch)} items)")

        try:
            # Build bulk upsert query
            # Using PostgreSQL's INSERT ... ON CONFLICT for efficiency
            query = text("""
                INSERT INTO products (
                    zoho_item_id,
                    sku,
                    name,
                    description,
                    price,
                    stock_quantity,
                    is_active,
                    last_synced,
                    updated_at,
                    created_at
                )
                VALUES (
                    :zoho_item_id,
                    :sku,
                    :name,
                    :description,
                    :price,
                    :stock_quantity,
                    :is_active,
                    :last_synced,
                    :updated_at,
                    :created_at
                )
                ON CONFLICT (zoho_item_id)
                DO UPDATE SET
                    stock_quantity = EXCLUDED.stock_quantity,
                    price = EXCLUDED.price,
                    name = EXCLUDED.name,
                    sku = EXCLUDED.sku,
                    description = EXCLUDED.description,
                    is_active = EXCLUDED.is_active,
                    last_synced = EXCLUDED.last_synced,
                    updated_at = EXCLUDED.updated_at
                RETURNING id, (xmax = 0) AS inserted
            """)

            # Execute batch upsert
            for item in items_batch:
                try:
                    result = await self.db.execute(query, {
                        "zoho_item_id": item.get("item_id"),
                        "sku": item.get("sku", ""),
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "price": float(item.get("rate", 0)),
                        "stock_quantity": int(item.get("stock_on_hand", 0)),
                        "is_active": item.get("status") == "active",
                        "last_synced": datetime.now(),
                        "updated_at": datetime.now(),
                        "created_at": datetime.now()
                    })

                    row = result.fetchone()
                    if row:
                        was_inserted = row[1]
                        if was_inserted:
                            self.stats["products_created"] += 1
                        else:
                            self.stats["products_updated"] += 1

                except Exception as item_error:
                    logger.error(f"Failed to upsert item {item.get('item_id')}: {item_error}")
                    self.stats["errors"].append({
                        "item_id": item.get("item_id"),
                        "error": str(item_error)
                    })

            # Commit the batch
            await self.db.commit()

            logger.debug(f"   ✅ Batch #{batch_number} committed to database")

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to process batch #{batch_number}: {e}")
            self.stats["errors"].append({
                "batch": batch_number,
                "error": str(e)
            })

    async def sync_stock_for_specific_items(
        self,
        zoho_item_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Sync stock for specific Zoho item IDs
        Useful for targeted updates

        Args:
            zoho_item_ids: List of Zoho item IDs to sync

        Returns:
            Statistics dictionary
        """
        logger.info(f"🎯 Syncing stock for {len(zoho_item_ids)} specific items")

        stats = {
            "requested": len(zoho_item_ids),
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        for item_id in zoho_item_ids:
            try:
                # Fetch item details from Zoho
                item = await self.zoho_client.fetch_item_stock(item_id)

                if item:
                    # Update in database
                    query = text("""
                        UPDATE products
                        SET stock_quantity = :stock_quantity,
                            last_synced = :last_synced,
                            updated_at = :updated_at
                        WHERE zoho_item_id = :zoho_item_id
                    """)

                    await self.db.execute(query, {
                        "zoho_item_id": item_id,
                        "stock_quantity": int(item.get("stock_on_hand", 0)),
                        "last_synced": datetime.now(),
                        "updated_at": datetime.now()
                    })

                    stats["updated"] += 1

            except Exception as e:
                logger.error(f"Failed to sync item {item_id}: {e}")
                stats["failed"] += 1
                stats["errors"].append({
                    "item_id": item_id,
                    "error": str(e)
                })

        await self.db.commit()

        logger.info(f"✅ Specific item sync complete: {stats['updated']}/{stats['requested']}")
        return stats

    async def get_sync_statistics(self) -> Dict[str, Any]:
        """
        Get current sync statistics from database

        Returns:
            Statistics dictionary
        """
        try:
            result = await self.db.execute(text("""
                SELECT
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN zoho_item_id IS NOT NULL THEN 1 END) as with_zoho_id,
                    COUNT(CASE WHEN stock_quantity > 0 THEN 1 END) as with_stock,
                    SUM(stock_quantity) as total_stock,
                    MAX(last_synced) as last_sync_time,
                    COUNT(CASE
                        WHEN last_synced IS NULL
                        OR last_synced < NOW() - INTERVAL '24 hours'
                        THEN 1
                    END) as stale_products
                FROM products
                WHERE is_active = true
            """))

            row = result.fetchone()

            return {
                "total_products": row[0] or 0,
                "with_zoho_id": row[1] or 0,
                "with_stock": row[2] or 0,
                "total_stock_quantity": int(row[3] or 0),
                "last_sync_time": row[4].isoformat() if row[4] else None,
                "stale_products": row[5] or 0
            }

        except Exception as e:
            logger.error(f"Failed to get sync statistics: {e}")
            return {"error": str(e)}
