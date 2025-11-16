"""
TDS Cache Service
=================

Redis-based caching for TDS (TSH Data Sync) to avoid re-syncing already synced data.

Features:
- Entity sync state tracking
- Content hash comparison
- Last sync timestamp tracking
- Bulk cache operations
- Cache invalidation strategies
- Performance optimization

معالج التخزين المؤقت لمزامنة البيانات

Author: TSH ERP Team
Date: November 13, 2025
Version: 1.0.0
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class TDSCacheService:
    """
    TDS Cache Service for tracking synced entities

    Purpose:
    - Avoid re-syncing unchanged data
    - Track entity sync state (hash, timestamp, version)
    - Provide fast lookup for sync status
    - Reduce database queries and API calls
    """

    # Cache TTL settings (in seconds)
    ENTITY_STATE_TTL = 86400  # 24 hours
    SYNC_STATUS_TTL = 3600    # 1 hour
    BATCH_SYNC_TTL = 7200     # 2 hours

    # Cache key prefixes
    PREFIX_ENTITY_HASH = "tds:entity:hash"
    PREFIX_ENTITY_STATE = "tds:entity:state"
    PREFIX_SYNC_STATUS = "tds:sync:status"
    PREFIX_BATCH_SYNC = "tds:batch:sync"
    PREFIX_ENTITY_SKIP = "tds:entity:skip"

    @staticmethod
    def _calculate_content_hash(data: Dict[str, Any]) -> str:
        """
        Calculate content hash for entity data

        Args:
            data: Entity data dictionary

        Returns:
            SHA-256 hash of normalized content
        """
        # Extract fields that matter for change detection
        # Exclude metadata fields that change but don't affect actual content
        exclude_fields = {
            'zoho_synced_at',
            'created_at',
            'updated_at',
            'last_sync_attempt',
            'sync_count',
            'cached_at',
            'zoho_raw_data'  # Raw data can have field order differences
        }

        # Create normalized dictionary
        normalized = {}
        for key, value in sorted(data.items()):
            if key not in exclude_fields:
                # Convert Decimal to string for consistent hashing
                if isinstance(value, Decimal):
                    normalized[key] = str(value)
                elif isinstance(value, datetime):
                    normalized[key] = value.isoformat()
                elif value is not None:
                    normalized[key] = value

        # Calculate hash
        content_str = json.dumps(normalized, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()

        return content_hash

    @staticmethod
    async def should_sync_entity(
        entity_type: str,
        entity_id: str,
        new_data: Dict[str, Any],
        force: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Check if entity should be synced based on cache

        Args:
            entity_type: Entity type (product, customer, invoice, etc.)
            entity_id: Zoho entity ID
            new_data: New entity data from Zoho
            force: Force sync regardless of cache

        Returns:
            Tuple of (should_sync: bool, reason: str)
                - should_sync: True if entity needs to be synced
                - reason: Why sync is needed (or why skipped)
        """
        if force:
            return True, "forced_sync"

        try:
            # Build cache key
            cache_key = f"{entity_type}:{entity_id}"

            # Get cached entity state
            cached_state = await cache_manager.get(
                cache_key,
                prefix=TDSCacheService.PREFIX_ENTITY_STATE
            )

            if not cached_state:
                return True, "no_cache_entry"

            # Calculate hash of new data
            new_hash = TDSCacheService._calculate_content_hash(new_data)

            # Compare hashes
            cached_hash = cached_state.get('content_hash')
            if cached_hash != new_hash:
                return True, "content_changed"

            # Check if cached data is too old (force refresh after TTL)
            cached_at = cached_state.get('cached_at')
            if cached_at:
                cached_time = datetime.fromisoformat(cached_at)
                age_hours = (datetime.utcnow() - cached_time).total_seconds() / 3600
                if age_hours > 24:  # Refresh after 24 hours even if unchanged
                    return True, "cache_expired"

            # Check last modified time if available
            cached_modified = cached_state.get('last_modified_time')
            new_modified = new_data.get('last_modified_time')

            if cached_modified and new_modified:
                # Both are ISO timestamp strings, can compare directly
                if new_modified > cached_modified:
                    return True, "timestamp_newer"

            # Entity hasn't changed, skip sync
            logger.debug(
                f"Skipping sync for {entity_type}:{entity_id} - "
                f"content unchanged (hash: {new_hash[:8]}...)"
            )
            return False, "unchanged"

        except Exception as e:
            logger.error(f"Error checking sync status for {entity_type}:{entity_id}: {e}")
            # On error, allow sync to proceed (fail-safe)
            return True, "cache_check_error"

    @staticmethod
    async def mark_entity_synced(
        entity_type: str,
        entity_id: str,
        entity_data: Dict[str, Any],
        local_id: Optional[str] = None
    ) -> bool:
        """
        Mark entity as synced in cache

        Args:
            entity_type: Entity type
            entity_id: Zoho entity ID
            entity_data: Synced entity data
            local_id: Local database ID (if available)

        Returns:
            True if cached successfully
        """
        try:
            cache_key = f"{entity_type}:{entity_id}"

            # Calculate content hash
            content_hash = TDSCacheService._calculate_content_hash(entity_data)

            # Prepare cache state
            cache_state = {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'local_id': local_id,
                'content_hash': content_hash,
                'last_modified_time': entity_data.get('last_modified_time'),
                'cached_at': datetime.utcnow().isoformat(),
                'sync_count': 1
            }

            # Get existing state to increment sync count
            existing_state = await cache_manager.get(
                cache_key,
                prefix=TDSCacheService.PREFIX_ENTITY_STATE
            )
            if existing_state and 'sync_count' in existing_state:
                cache_state['sync_count'] = existing_state['sync_count'] + 1

            # Store in cache
            success = await cache_manager.set(
                key=cache_key,
                value=cache_state,
                ttl=TDSCacheService.ENTITY_STATE_TTL,
                prefix=TDSCacheService.PREFIX_ENTITY_STATE
            )

            if success:
                logger.debug(
                    f"Marked {entity_type}:{entity_id} as synced "
                    f"(hash: {content_hash[:8]}..., count: {cache_state['sync_count']})"
                )

            return success

        except Exception as e:
            logger.error(f"Error marking entity as synced: {e}")
            return False

    @staticmethod
    async def get_entity_sync_state(
        entity_type: str,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached sync state for entity

        Args:
            entity_type: Entity type
            entity_id: Zoho entity ID

        Returns:
            Cached state dict or None
        """
        try:
            cache_key = f"{entity_type}:{entity_id}"
            return await cache_manager.get(
                cache_key,
                prefix=TDSCacheService.PREFIX_ENTITY_STATE
            )
        except Exception as e:
            logger.error(f"Error getting entity sync state: {e}")
            return None

    @staticmethod
    async def mark_batch_sync_complete(
        entity_type: str,
        batch_id: str,
        stats: Dict[str, Any]
    ) -> bool:
        """
        Mark a batch sync operation as complete

        Args:
            entity_type: Entity type
            batch_id: Batch identifier (e.g., "2025-11-13:products:page-1")
            stats: Batch statistics (processed, skipped, failed, etc.)

        Returns:
            True if cached successfully
        """
        try:
            cache_key = f"{entity_type}:{batch_id}"
            batch_info = {
                'entity_type': entity_type,
                'batch_id': batch_id,
                'stats': stats,
                'completed_at': datetime.utcnow().isoformat()
            }

            return await cache_manager.set(
                key=cache_key,
                value=batch_info,
                ttl=TDSCacheService.BATCH_SYNC_TTL,
                prefix=TDSCacheService.PREFIX_BATCH_SYNC
            )

        except Exception as e:
            logger.error(f"Error marking batch sync complete: {e}")
            return False

    @staticmethod
    async def was_batch_synced_recently(
        entity_type: str,
        batch_id: str,
        within_hours: int = 1
    ) -> bool:
        """
        Check if batch was synced recently

        Args:
            entity_type: Entity type
            batch_id: Batch identifier
            within_hours: Time window in hours

        Returns:
            True if batch was synced within time window
        """
        try:
            cache_key = f"{entity_type}:{batch_id}"
            batch_info = await cache_manager.get(
                cache_key,
                prefix=TDSCacheService.PREFIX_BATCH_SYNC
            )

            if not batch_info:
                return False

            completed_at = batch_info.get('completed_at')
            if not completed_at:
                return False

            completed_time = datetime.fromisoformat(completed_at)
            age_hours = (datetime.utcnow() - completed_time).total_seconds() / 3600

            return age_hours <= within_hours

        except Exception as e:
            logger.error(f"Error checking batch sync status: {e}")
            return False

    @staticmethod
    async def invalidate_entity_cache(
        entity_type: str,
        entity_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cached entity data

        Args:
            entity_type: Entity type
            entity_id: Specific entity ID (if None, invalidates all entities of this type)

        Returns:
            Number of cache entries deleted
        """
        try:
            if entity_id:
                # Invalidate specific entity
                cache_key = f"{entity_type}:{entity_id}"
                await cache_manager.delete(
                    cache_key,
                    prefix=TDSCacheService.PREFIX_ENTITY_STATE
                )
                logger.info(f"Invalidated cache for {entity_type}:{entity_id}")
                return 1
            else:
                # Invalidate all entities of this type
                pattern = f"{entity_type}:*"
                deleted = await cache_manager.delete_pattern(
                    pattern,
                    prefix=TDSCacheService.PREFIX_ENTITY_STATE
                )
                logger.info(f"Invalidated {deleted} cache entries for {entity_type}")
                return deleted

        except Exception as e:
            logger.error(f"Error invalidating entity cache: {e}")
            return 0

    @staticmethod
    async def get_sync_statistics() -> Dict[str, Any]:
        """
        Get cache statistics for sync operations

        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_stats = await cache_manager.get_stats()

            # Count keys by entity type (if possible)
            # This is a rough estimate since we can't easily count by prefix
            # without scanning all keys

            return {
                'cache_backend': cache_manager.backend,
                'cache_enabled': cache_manager.is_enabled,
                'overall_stats': cache_stats,
                'tds_cache_ttl': {
                    'entity_state': TDSCacheService.ENTITY_STATE_TTL,
                    'sync_status': TDSCacheService.SYNC_STATUS_TTL,
                    'batch_sync': TDSCacheService.BATCH_SYNC_TTL
                }
            }

        except Exception as e:
            logger.error(f"Error getting sync statistics: {e}")
            return {
                'cache_enabled': False,
                'error': str(e)
            }

    @staticmethod
    async def bulk_check_should_sync(
        entity_type: str,
        entities: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Bulk check which entities should be synced

        Args:
            entity_type: Entity type
            entities: List of entity data dictionaries (must have 'item_id' or equivalent ID field)

        Returns:
            Tuple of (entities_to_sync, stats)
                - entities_to_sync: List of entities that need syncing
                - stats: Statistics dict (total, to_sync, skipped, reasons)
        """
        entities_to_sync = []
        stats = {
            'total': len(entities),
            'to_sync': 0,
            'skipped': 0,
            'reasons': {}
        }

        # Determine ID field based on entity type
        id_field_map = {
            'product': 'item_id',
            'customer': 'contact_id',
            'invoice': 'invoice_id',
            'order': 'salesorder_id',
            'bill': 'bill_id',
            'creditnote': 'creditnote_id',
        }
        id_field = id_field_map.get(entity_type, 'id')

        for entity in entities:
            entity_id = entity.get(id_field)
            if not entity_id:
                # No ID, must sync
                entities_to_sync.append(entity)
                stats['to_sync'] += 1
                stats['reasons']['no_id'] = stats['reasons'].get('no_id', 0) + 1
                continue

            should_sync, reason = await TDSCacheService.should_sync_entity(
                entity_type=entity_type,
                entity_id=str(entity_id),
                new_data=entity
            )

            if should_sync:
                entities_to_sync.append(entity)
                stats['to_sync'] += 1
            else:
                stats['skipped'] += 1

            # Track reasons
            stats['reasons'][reason] = stats['reasons'].get(reason, 0) + 1

        logger.info(
            f"Bulk check for {entity_type}: {stats['total']} total, "
            f"{stats['to_sync']} to sync, {stats['skipped']} skipped"
        )

        return entities_to_sync, stats

    @staticmethod
    async def warm_cache_from_db(
        entity_type: str,
        entities_from_db: List[Dict[str, Any]]
    ) -> int:
        """
        Warm cache from database entities

        Useful for pre-populating cache after initial sync or deployment.

        Args:
            entity_type: Entity type
            entities_from_db: List of entity records from database

        Returns:
            Number of entities cached
        """
        cached_count = 0

        for entity in entities_from_db:
            # Get entity ID
            entity_id = entity.get('zoho_item_id') or entity.get('zoho_contact_id') or entity.get('id')
            if not entity_id:
                continue

            success = await TDSCacheService.mark_entity_synced(
                entity_type=entity_type,
                entity_id=str(entity_id),
                entity_data=entity,
                local_id=entity.get('id')
            )

            if success:
                cached_count += 1

        logger.info(f"Warmed cache with {cached_count} {entity_type} entities")
        return cached_count


# Convenience functions

async def check_should_sync(
    entity_type: str,
    entity_id: str,
    data: Dict[str, Any],
    force: bool = False
) -> bool:
    """
    Quick check if entity should be synced

    Returns:
        True if should sync, False if can skip
    """
    should_sync, _ = await TDSCacheService.should_sync_entity(
        entity_type, entity_id, data, force
    )
    return should_sync


async def mark_synced(
    entity_type: str,
    entity_id: str,
    data: Dict[str, Any],
    local_id: Optional[str] = None
) -> bool:
    """
    Quick mark entity as synced

    Returns:
        True if cached successfully
    """
    return await TDSCacheService.mark_entity_synced(
        entity_type, entity_id, data, local_id
    )


async def invalidate_cache(entity_type: str, entity_id: Optional[str] = None) -> int:
    """
    Quick invalidate cache

    Returns:
        Number of entries invalidated
    """
    return await TDSCacheService.invalidate_entity_cache(entity_type, entity_id)
