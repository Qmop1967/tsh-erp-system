"""
Zoho Sync Orchestrator
======================

Orchestrates all Zoho sync operations.
Consolidates zoho_bulk_sync.py, zoho_stock_sync.py, zoho_processor.py,
zoho_sync_worker.py, and zoho_entity_handlers.py.

منسق عمليات المزامنة مع Zoho

Features:
- Full sync (initial import)
- Incremental sync (delta updates)
- Real-time sync (webhooks)
- Scheduled sync (cron jobs)
- Batch processing
- Parallel execution
- Progress tracking
- Error recovery
- Conflict resolution
- Data transformation

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from .client import UnifiedZohoClient, ZohoAPI
from ...core.queue import TDSQueueService
from ....core.events.event_bus import EventBus
from ....db.database import get_db

logger = logging.getLogger(__name__)


class SyncMode(str, Enum):
    """وضع المزامنة"""
    FULL = "full"               # Full sync - import all data
    INCREMENTAL = "incremental" # Only changes since last sync
    REALTIME = "realtime"       # Real-time webhook-based
    SCHEDULED = "scheduled"     # Scheduled cron job


class SyncStatus(str, Enum):
    """حالة المزامنة"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class EntityType(str, Enum):
    """أنواع الكيانات"""
    PRODUCTS = "products"
    INVENTORY = "inventory"
    CUSTOMERS = "customers"
    INVOICES = "invoices"
    ORDERS = "orders"
    BILLS = "bills"
    CONTACTS = "contacts"
    SALESORDERS = "salesorders"
    PURCHASEORDERS = "purchaseorders"


@dataclass
class SyncConfig:
    """Sync configuration"""
    entity_type: EntityType
    mode: SyncMode = SyncMode.INCREMENTAL
    batch_size: int = 100
    max_concurrent: int = 5
    enable_retry: bool = True
    enable_validation: bool = True
    enable_transformation: bool = True
    filter_params: Optional[Dict[str, Any]] = None


@dataclass
class SyncResult:
    """Sync operation result"""
    sync_id: str
    entity_type: EntityType
    status: SyncStatus
    mode: SyncMode
    total_processed: int = 0
    total_success: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate sync duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_processed == 0:
            return 0.0
        return (self.total_success / self.total_processed) * 100


class ZohoSyncOrchestrator:
    """
    Zoho Sync Orchestrator
    منسق عمليات المزامنة مع Zoho

    Orchestrates all sync operations between Zoho and local database.
    """

    # Entity type to Zoho API endpoint mapping
    ENTITY_ENDPOINTS = {
        EntityType.PRODUCTS: (ZohoAPI.INVENTORY, "items"),
        EntityType.INVENTORY: (ZohoAPI.INVENTORY, "items"),
        EntityType.CUSTOMERS: (ZohoAPI.BOOKS, "contacts"),
        EntityType.INVOICES: (ZohoAPI.BOOKS, "invoices"),
        EntityType.ORDERS: (ZohoAPI.INVENTORY, "salesorders"),
        EntityType.BILLS: (ZohoAPI.BOOKS, "bills"),
        EntityType.CONTACTS: (ZohoAPI.BOOKS, "contacts"),
        EntityType.SALESORDERS: (ZohoAPI.INVENTORY, "salesorders"),
        EntityType.PURCHASEORDERS: (ZohoAPI.INVENTORY, "purchaseorders"),
    }

    def __init__(
        self,
        zoho_client: UnifiedZohoClient,
        db: Optional[Any] = None,
        event_bus: Optional[EventBus] = None,
        queue: Optional[TDSQueueService] = None
    ):
        """
        Initialize Sync Orchestrator

        Args:
            zoho_client: Unified Zoho client instance
            db: Database session for storing sync results
            event_bus: Event bus for publishing events
            queue: TDS queue for async processing
        """
        self.zoho = zoho_client
        self.db = db
        self.event_bus = event_bus
        self.queue = queue

        # Active sync operations
        self._active_syncs: Dict[str, SyncResult] = {}
        self._sync_lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "total_entities_synced": 0
        }

    async def sync_entity(
        self,
        config: SyncConfig,
        entity_ids: Optional[List[str]] = None
    ) -> SyncResult:
        """
        Sync a specific entity type

        Args:
            config: Sync configuration
            entity_ids: Optional list of specific entity IDs to sync

        Returns:
            SyncResult: Sync operation results
        """
        # Generate sync ID
        sync_id = f"sync_{config.entity_type}_{datetime.utcnow().timestamp()}"

        # Initialize result
        result = SyncResult(
            sync_id=sync_id,
            entity_type=config.entity_type,
            status=SyncStatus.IN_PROGRESS,
            mode=config.mode,
            started_at=datetime.utcnow()
        )

        # Track active sync
        async with self._sync_lock:
            self._active_syncs[sync_id] = result

        try:
            # Publish start event
            await self._publish_event("tds.zoho.sync.started", {
                "sync_id": sync_id,
                "entity_type": config.entity_type,
                "mode": config.mode,
                "batch_size": config.batch_size
            })

            logger.info(
                f"Starting {config.mode} sync for {config.entity_type} "
                f"(sync_id: {sync_id})"
            )

            # Execute sync based on mode
            if config.mode == SyncMode.FULL:
                await self._full_sync(config, result)
            elif config.mode == SyncMode.INCREMENTAL:
                await self._incremental_sync(config, result)
            elif entity_ids:
                await self._partial_sync(config, result, entity_ids)
            else:
                raise ValueError(f"Invalid sync configuration: {config}")

            # Mark as completed
            result.status = SyncStatus.COMPLETED
            result.completed_at = datetime.utcnow()

            # Update stats
            self.stats["total_syncs"] += 1
            self.stats["successful_syncs"] += 1
            self.stats["total_entities_synced"] += result.total_success

            logger.info(
                f"Sync completed: {sync_id} - "
                f"Processed: {result.total_processed}, "
                f"Success: {result.total_success}, "
                f"Failed: {result.total_failed}, "
                f"Duration: {result.duration}"
            )

            # Publish completion event
            await self._publish_event("tds.zoho.sync.completed", {
                "sync_id": sync_id,
                "entity_type": config.entity_type,
                "total_processed": result.total_processed,
                "total_success": result.total_success,
                "total_failed": result.total_failed,
                "duration_seconds": result.duration.total_seconds() if result.duration else 0
            })

        except Exception as e:
            result.status = SyncStatus.FAILED
            result.completed_at = datetime.utcnow()
            result.error_message = str(e)

            self.stats["total_syncs"] += 1
            self.stats["failed_syncs"] += 1

            logger.error(f"Sync failed: {sync_id} - {str(e)}", exc_info=True)

            # Publish failure event
            await self._publish_event("tds.zoho.sync.failed", {
                "sync_id": sync_id,
                "entity_type": config.entity_type,
                "error": str(e)
            })

        finally:
            # Remove from active syncs
            async with self._sync_lock:
                if sync_id in self._active_syncs:
                    del self._active_syncs[sync_id]

        return result

    async def _full_sync(self, config: SyncConfig, result: SyncResult):
        """
        Perform full sync - import all entities

        Args:
            config: Sync configuration
            result: Result object to update
        """
        logger.info(f"Performing full sync for {config.entity_type}")

        # Get API endpoint
        api_type, endpoint = self.ENTITY_ENDPOINTS[config.entity_type]

        # Fetch all entities with pagination
        all_entities = await self.zoho.paginated_fetch(
            api_type=api_type,
            endpoint=endpoint,
            params=config.filter_params or {},
            page_size=config.batch_size
        )

        logger.info(
            f"Fetched {len(all_entities)} {config.entity_type} from Zoho"
        )

        # Process entities in batches
        await self._process_entities_batch(
            entities=all_entities,
            config=config,
            result=result
        )

    async def _incremental_sync(self, config: SyncConfig, result: SyncResult):
        """
        Perform incremental sync - only changed entities

        Args:
            config: Sync configuration
            result: Result object to update
        """
        logger.info(f"Performing incremental sync for {config.entity_type}")

        # Get last sync time
        last_sync_time = await self._get_last_sync_time(config.entity_type)

        # Get API endpoint
        api_type, endpoint = self.ENTITY_ENDPOINTS[config.entity_type]

        # Add filter for modified since last sync
        params = config.filter_params or {}
        if last_sync_time:
            params['last_modified_time'] = last_sync_time.isoformat()

        # Fetch changed entities
        changed_entities = await self.zoho.paginated_fetch(
            api_type=api_type,
            endpoint=endpoint,
            params=params,
            page_size=config.batch_size
        )

        logger.info(
            f"Found {len(changed_entities)} changed {config.entity_type} "
            f"since {last_sync_time}"
        )

        if not changed_entities:
            logger.info(f"No changes found for {config.entity_type}")
            return

        # Process entities in batches
        await self._process_entities_batch(
            entities=changed_entities,
            config=config,
            result=result
        )

        # Update last sync time
        await self._update_last_sync_time(config.entity_type)

    async def _partial_sync(
        self,
        config: SyncConfig,
        result: SyncResult,
        entity_ids: List[str]
    ):
        """
        Sync specific entities by ID

        Args:
            config: Sync configuration
            result: Result object to update
            entity_ids: List of entity IDs to sync
        """
        logger.info(
            f"Performing partial sync for {len(entity_ids)} "
            f"{config.entity_type}"
        )

        # Get API endpoint
        api_type, endpoint = self.ENTITY_ENDPOINTS[config.entity_type]

        # Fetch specific entities
        entities = []
        for entity_id in entity_ids:
            try:
                entity_data = await self.zoho.get(
                    api_type=api_type,
                    endpoint=f"{endpoint}/{entity_id}"
                )
                entities.append(entity_data)
            except Exception as e:
                logger.warning(f"Failed to fetch {entity_id}: {str(e)}")
                result.total_failed += 1

        # Process entities
        await self._process_entities_batch(
            entities=entities,
            config=config,
            result=result
        )

    async def _process_entities_batch(
        self,
        entities: List[Dict[str, Any]],
        config: SyncConfig,
        result: SyncResult
    ):
        """
        Process entities in batches

        Args:
            entities: List of entities to process
            config: Sync configuration
            result: Result object to update
        """
        # Split into batches
        batches = [
            entities[i:i + config.batch_size]
            for i in range(0, len(entities), config.batch_size)
        ]

        logger.info(
            f"Processing {len(entities)} entities in {len(batches)} batches"
        )

        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def process_batch(batch: List[Dict], batch_num: int):
            async with semaphore:
                logger.debug(
                    f"Processing batch {batch_num + 1}/{len(batches)} "
                    f"({len(batch)} entities)"
                )

                for entity in batch:
                    try:
                        # Validate entity
                        if config.enable_validation:
                            if not await self._validate_entity(entity, config):
                                result.total_skipped += 1
                                continue

                        # Transform entity
                        if config.enable_transformation:
                            entity = await self._transform_entity(entity, config)

                        # Save to database
                        await self._save_entity(entity, config)

                        result.total_success += 1
                        result.total_processed += 1

                        # Publish entity synced event
                        await self._publish_event("tds.zoho.entity.synced", {
                            "entity_type": config.entity_type,
                            "entity_id": entity.get('item_id') or entity.get('contact_id'),
                            "sync_id": result.sync_id
                        })

                    except Exception as e:
                        result.total_failed += 1
                        result.total_processed += 1
                        result.errors.append({
                            "entity_id": entity.get('item_id') or entity.get('contact_id'),
                            "error": str(e)
                        })
                        logger.error(
                            f"Failed to process entity: {str(e)}",
                            exc_info=True
                        )

        # Process all batches concurrently
        await asyncio.gather(
            *[process_batch(batch, i) for i, batch in enumerate(batches)],
            return_exceptions=True
        )

    async def _validate_entity(
        self,
        entity: Dict[str, Any],
        config: SyncConfig
    ) -> bool:
        """
        Validate entity data

        Args:
            entity: Entity data
            config: Sync configuration

        Returns:
            bool: True if valid
        """
        # Basic validation - check required fields
        if config.entity_type == EntityType.PRODUCTS:
            return bool(entity.get('item_id') and entity.get('name'))
        elif config.entity_type == EntityType.CUSTOMERS:
            return bool(entity.get('contact_id') and entity.get('contact_name'))

        return True

    async def _transform_entity(
        self,
        entity: Dict[str, Any],
        config: SyncConfig
    ) -> Dict[str, Any]:
        """
        Transform entity data for local database

        Args:
            entity: Entity data
            config: Sync configuration

        Returns:
            dict: Transformed entity
        """
        # Add metadata
        entity['_zoho_synced_at'] = datetime.utcnow().isoformat()
        entity['_entity_type'] = config.entity_type

        return entity

    async def _save_entity(
        self,
        entity: Dict[str, Any],
        config: SyncConfig
    ):
        """
        Save entity to database

        Args:
            entity: Entity data
            config: Sync configuration
        """
        try:
            # Route to appropriate handler based on entity type
            if config.entity_type in [EntityType.PRODUCTS, EntityType.INVENTORY]:
                await self._save_product(entity)
            elif config.entity_type == EntityType.CUSTOMERS:
                await self._save_customer(entity)
            elif config.entity_type == EntityType.INVOICES:
                await self._save_invoice(entity)
            else:
                logger.warning(f"No handler for entity type: {config.entity_type}")

        except Exception as e:
            logger.error(f"Failed to save {config.entity_type} entity: {str(e)}", exc_info=True)
            raise

    async def _save_product(self, entity: Dict[str, Any]):
        """Save product entity to database"""
        from .processors.products import ProductProcessor
        from ....db.database import get_async_db

        # Transform using processor
        processor = ProductProcessor()
        if not processor.validate(entity):
            logger.warning(f"Product validation failed: {entity.get('item_id')}")
            return

        transformed = processor.transform(entity)

        # Map to database columns
        product_data = {
            'zoho_item_id': transformed.get('zoho_item_id'),
            'sku': transformed.get('sku') or transformed.get('product_code', f"SKU-{transformed.get('zoho_item_id')}"),
            'name': transformed.get('name'),
            'description': transformed.get('description', ''),
            'category': transformed.get('category'),
            'price': float(transformed.get('rate', 0)),
            'cost_price': float(transformed.get('cost_price', 0)),
            'unit_price': float(transformed.get('rate', 0)),
            'actual_available_stock': int(transformed.get('actual_available_stock', 0)),
            'image_url': transformed.get('image_url'),
            'is_active': transformed.get('is_active', True),
            'unit_of_measure': transformed.get('unit', 'piece'),
            'brand': transformed.get('brand'),
            'is_trackable': transformed.get('track_inventory', True),
        }

        # Get async database session
        async for db in get_async_db():
            try:
                # Use raw SQL for upsert (asyncpg)
                from sqlalchemy import text

                # Check if product exists
                check_query = text("""
                    SELECT id FROM products WHERE zoho_item_id = :zoho_item_id
                """)
                result = await db.execute(check_query, {'zoho_item_id': product_data['zoho_item_id']})
                existing = result.fetchone()

                if existing:
                    # Update existing product
                    update_query = text("""
                        UPDATE products SET
                            sku = :sku,
                            name = :name,
                            description = :description,
                            category = :category,
                            price = :price,
                            cost_price = :cost_price,
                            unit_price = :unit_price,
                            actual_available_stock = :actual_available_stock,
                            image_url = :image_url,
                            is_active = :is_active,
                            brand = :brand,
                            is_trackable = :is_trackable,
                            updated_at = NOW()
                        WHERE zoho_item_id = :zoho_item_id
                    """)
                    await db.execute(update_query, product_data)
                    logger.debug(f"Updated product: {product_data['zoho_item_id']}")
                else:
                    # Insert new product
                    # First ensure category exists
                    if not product_data.get('category_id'):
                        # Create or get default category
                        cat_check = text("SELECT id FROM categories WHERE name = 'General' LIMIT 1")
                        cat_result = await db.execute(cat_check)
                        cat_row = cat_result.fetchone()

                        if cat_row:
                            product_data['category_id'] = cat_row[0]
                        else:
                            cat_insert = text("""
                                INSERT INTO categories (name, is_active, created_at)
                                VALUES ('General', true, NOW())
                                RETURNING id
                            """)
                            cat_result = await db.execute(cat_insert)
                            product_data['category_id'] = cat_result.fetchone()[0]

                    insert_query = text("""
                        INSERT INTO products (
                            zoho_item_id, sku, name, description, category, category_id,
                            price, cost_price, unit_price, actual_available_stock,
                            image_url, is_active, unit_of_measure, brand, is_trackable,
                            created_at, updated_at
                        ) VALUES (
                            :zoho_item_id, :sku, :name, :description, :category, :category_id,
                            :price, :cost_price, :unit_price, :actual_available_stock,
                            :image_url, :is_active, :unit_of_measure, :brand, :is_trackable,
                            NOW(), NOW()
                        )
                    """)
                    await db.execute(insert_query, product_data)
                    logger.debug(f"Inserted new product: {product_data['zoho_item_id']}")

                await db.commit()

            except Exception as e:
                await db.rollback()
                logger.error(f"Database error saving product: {str(e)}")
                raise
            finally:
                break  # Exit the async generator

    async def _save_customer(self, entity: Dict[str, Any]):
        """Save customer entity to database"""
        # TODO: Implement customer save
        logger.debug(f"Saving customer: {entity.get('contact_id')}")
        pass

    async def _save_invoice(self, entity: Dict[str, Any]):
        """Save invoice entity to database"""
        # TODO: Implement invoice save
        logger.debug(f"Saving invoice: {entity.get('invoice_id')}")
        pass

    async def _get_last_sync_time(
        self,
        entity_type: EntityType
    ) -> Optional[datetime]:
        """Get last sync time for entity type"""
        # TODO: Implement - fetch from database
        return None

    async def _update_last_sync_time(self, entity_type: EntityType):
        """Update last sync time for entity type"""
        # TODO: Implement - update in database
        pass

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to event bus"""
        if self.event_bus:
            try:
                from ....core.events.base_event import BaseEvent
                event = BaseEvent(
                    event_type=event_type,
                    module="tds.zoho",
                    data=data
                )
                await self.event_bus.publish(event)
            except Exception as e:
                logger.warning(f"Failed to publish event {event_type}: {e}")

    def get_active_syncs(self) -> Dict[str, SyncResult]:
        """Get all active sync operations"""
        return self._active_syncs.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            **self.stats,
            "active_syncs": len(self._active_syncs)
        }

    async def cancel_sync(self, sync_id: str) -> bool:
        """
        Cancel an active sync operation

        Args:
            sync_id: Sync ID to cancel

        Returns:
            bool: True if cancelled
        """
        async with self._sync_lock:
            if sync_id in self._active_syncs:
                self._active_syncs[sync_id].status = SyncStatus.CANCELLED
                logger.info(f"Sync cancelled: {sync_id}")
                return True

        return False
