"""
TDS Sync Orchestrator Enhancement: Redis Caching Integration
=============================================================

This module enhances the existing ZohoSyncOrchestrator with Redis caching
to avoid re-syncing already synced data.

تحسين منسق المزامنة: دمج التخزين المؤقت باستخدام Redis

Features Added:
- Check Redis cache before syncing each entity
- Skip entities that haven't changed (content hash comparison)
- Track sync state (hash, timestamp, count)
- Bulk cache checking for performance
- Automatic cache updates after successful sync
- Statistics tracking (skipped, synced, cache hits)

Author: TSH ERP Team
Date: November 13, 2025
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from .sync import ZohoSyncOrchestrator, SyncConfig, SyncResult
from ...services.tds_cache_service import TDSCacheService

logger = logging.getLogger(__name__)


class CachedZohoSyncOrchestrator(ZohoSyncOrchestrator):
    """
    Enhanced Sync Orchestrator with Redis Caching

    منسق المزامنة المحسّن مع التخزين المؤقت

    This class extends the base ZohoSyncOrchestrator to add intelligent
    caching that avoids re-syncing unchanged data.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with caching enabled"""
        super().__init__(*args, **kwargs)
        self.cache_enabled = True  # Can be toggled for testing
        self.cache_stats = {
            'total_checked': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'skipped': 0,
            'synced': 0
        }

    async def _process_entities_batch(
        self,
        entities: List[Dict[str, Any]],
        config: SyncConfig,
        result: SyncResult
    ):
        """
        Enhanced batch processing with Redis cache checking

        Process:
        1. Bulk check which entities need syncing (cache lookup)
        2. Skip unchanged entities (cache hit)
        3. Sync only changed/new entities
        4. Update cache after successful sync

        Args:
            entities: List of entities to process
            config: Sync configuration
            result: Result object to update
        """
        if not entities:
            logger.info("No entities to process")
            return

        logger.info(
            f"🔍 Processing {len(entities)} entities with cache checking "
            f"(cache_enabled: {self.cache_enabled})"
        )

        # STEP 1: Bulk cache check (if enabled)
        entities_to_sync = entities
        skipped_count = 0

        if self.cache_enabled:
            # Map entity type to cache entity type
            cache_entity_type = self._map_entity_type_for_cache(config.entity_type)

            # Bulk check which entities should be synced
            entities_to_sync, cache_stats = await TDSCacheService.bulk_check_should_sync(
                entity_type=cache_entity_type,
                entities=entities
            )

            skipped_count = cache_stats['skipped']
            result.total_skipped += skipped_count

            # Update cache statistics
            self.cache_stats['total_checked'] += cache_stats['total']
            self.cache_stats['cache_hits'] += skipped_count
            self.cache_stats['cache_misses'] += cache_stats['to_sync']
            self.cache_stats['skipped'] += skipped_count

            logger.info(
                f"✅ Cache check complete: {cache_stats['total']} total, "
                f"{cache_stats['to_sync']} to sync, {cache_stats['skipped']} skipped"
            )
            logger.debug(f"Skip reasons: {cache_stats['reasons']}")

        # STEP 2: Process only entities that need syncing
        if not entities_to_sync:
            logger.info("ℹ️  All entities are up-to-date (cached). Nothing to sync.")
            return

        logger.info(f"🔄 Syncing {len(entities_to_sync)} entities...")

        # Split into batches
        batches = [
            entities_to_sync[i:i + config.batch_size]
            for i in range(0, len(entities_to_sync), config.batch_size)
        ]

        import asyncio

        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def process_batch(batch: List[Dict], batch_num: int):
            async with semaphore:
                logger.debug(
                    f"Processing batch {batch_num + 1}/{len(batches)} "
                    f"({len(batch)} entities)"
                )

                for entity in batch:
                    entity_id = self._get_entity_id(entity, config)

                    try:
                        # Validate entity
                        if config.enable_validation:
                            if not await self._validate_entity(entity, config):
                                logger.warning(f"Validation failed for entity: {entity_id}")
                                result.total_skipped += 1
                                continue

                        # Transform entity
                        if config.enable_transformation:
                            entity = await self._transform_entity(entity, config)

                        # Save to database
                        local_id = await self._save_entity(entity, config)

                        # SUCCESS: Mark entity as synced in cache
                        if self.cache_enabled:
                            cache_entity_type = self._map_entity_type_for_cache(config.entity_type)
                            await TDSCacheService.mark_entity_synced(
                                entity_type=cache_entity_type,
                                entity_id=str(entity_id),
                                entity_data=entity,
                                local_id=str(local_id) if local_id else None
                            )
                            self.cache_stats['synced'] += 1

                        result.total_success += 1
                        result.total_processed += 1

                        # Publish entity synced event
                        await self._publish_event("tds.zoho.entity.synced", {
                            "entity_type": config.entity_type,
                            "entity_id": entity_id,
                            "sync_id": result.sync_id,
                            "cached": True
                        })

                        logger.debug(f"✅ Synced and cached: {cache_entity_type}:{entity_id}")

                    except Exception as e:
                        result.total_failed += 1
                        result.total_processed += 1
                        result.errors.append({
                            "entity_id": entity_id,
                            "error": str(e)
                        })
                        logger.error(
                            f"❌ Failed to process entity {entity_id}: {str(e)}",
                            exc_info=True
                        )

        # Process all batches concurrently
        await asyncio.gather(
            *[process_batch(batch, i) for i, batch in enumerate(batches)],
            return_exceptions=True
        )

        # STEP 3: Log cache statistics
        if self.cache_enabled:
            cache_hit_rate = (
                (self.cache_stats['cache_hits'] / self.cache_stats['total_checked'] * 100)
                if self.cache_stats['total_checked'] > 0
                else 0
            )
            logger.info(
                f"📊 Cache Statistics: "
                f"Hit Rate: {cache_hit_rate:.1f}%, "
                f"Total Checked: {self.cache_stats['total_checked']}, "
                f"Skipped: {self.cache_stats['skipped']}, "
                f"Synced: {self.cache_stats['synced']}"
            )

    def _map_entity_type_for_cache(self, entity_type) -> str:
        """
        Map EntityType enum to cache entity type string

        Args:
            entity_type: EntityType enum value

        Returns:
            Cache entity type string
        """
        from .sync import EntityType

        mapping = {
            EntityType.PRODUCTS: 'product',
            EntityType.INVENTORY: 'product',
            EntityType.CUSTOMERS: 'customer',
            EntityType.CONTACTS: 'customer',
            EntityType.INVOICES: 'invoice',
            EntityType.ORDERS: 'order',
            EntityType.SALESORDERS: 'order',
            EntityType.BILLS: 'bill',
            EntityType.PURCHASEORDERS: 'purchaseorder',
        }

        return mapping.get(entity_type, str(entity_type).lower())

    def _get_entity_id(self, entity: Dict[str, Any], config: SyncConfig) -> str:
        """
        Extract entity ID from entity data

        Args:
            entity: Entity data
            config: Sync configuration

        Returns:
            Entity ID string
        """
        from .sync import EntityType

        # Map entity type to ID field
        id_fields = {
            EntityType.PRODUCTS: 'item_id',
            EntityType.INVENTORY: 'item_id',
            EntityType.CUSTOMERS: 'contact_id',
            EntityType.CONTACTS: 'contact_id',
            EntityType.INVOICES: 'invoice_id',
            EntityType.ORDERS: 'salesorder_id',
            EntityType.SALESORDERS: 'salesorder_id',
            EntityType.BILLS: 'bill_id',
            EntityType.PURCHASEORDERS: 'purchaseorder_id',
        }

        id_field = id_fields.get(config.entity_type, 'id')
        return str(entity.get(id_field, 'unknown'))

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics for this orchestrator instance

        Returns:
            Dictionary with cache statistics
        """
        global_stats = await TDSCacheService.get_sync_statistics()

        return {
            'cache_enabled': self.cache_enabled,
            'session_stats': self.cache_stats,
            'global_cache_stats': global_stats
        }

    async def clear_entity_cache(self, entity_type: str, entity_id: str = None):
        """
        Clear cache for specific entity or all entities of a type

        Args:
            entity_type: Entity type to clear
            entity_id: Optional specific entity ID

        Returns:
            Number of cache entries cleared
        """
        cache_entity_type = self._map_entity_type_for_cache(entity_type)
        return await TDSCacheService.invalidate_entity_cache(
            cache_entity_type,
            entity_id
        )

    def enable_caching(self):
        """Enable cache checking"""
        self.cache_enabled = True
        logger.info("✅ Redis caching enabled for sync operations")

    def disable_caching(self):
        """Disable cache checking (for testing or force sync)"""
        self.cache_enabled = False
        logger.warning("⚠️  Redis caching disabled - all entities will be synced")

    def reset_cache_stats(self):
        """Reset cache statistics"""
        self.cache_stats = {
            'total_checked': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'skipped': 0,
            'synced': 0
        }
        logger.info("Cache statistics reset")
