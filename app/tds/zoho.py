"""
TDS Zoho Integration Facade
============================

🎯 SINGLE POINT OF ACCESS for all Zoho operations in TSH ERP

This module provides a unified interface to all Zoho integration functionality,
replacing the scattered services in app/services/zoho_*.py

نقطة الدخول الموحدة لجميع عمليات Zoho في نظام TSH ERP

Usage:
    from app.tds.zoho import ZohoService

    # Initialize
    service = ZohoService()
    await service.start()

    # Sync data
    result = await service.sync_products()

    # Handle webhook
    await service.process_webhook(event_data)

    # Cleanup
    await service.stop()

Architecture:
    This facade consolidates 15 scattered services (168KB) into one unified interface.
    All actual implementation is in app/tds/integrations/zoho/

Migration from Legacy Services:
    ❌ OLD: from app.services.zoho_service import ZohoService
    ✅ NEW: from app.tds.zoho import ZohoService

    ❌ OLD: from app.services.zoho_auth_service import ZohoAuthService
    ✅ NEW: from app.tds.zoho import ZohoService (includes auth)

    ❌ OLD: from app.services.zoho_processor import ProcessorService
    ✅ NEW: from app.tds.zoho import ZohoService (includes processors)

Author: TSH ERP Team
Date: January 7, 2025
Version: 3.0.0
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# Import all TDS Zoho components
from app.tds.integrations.zoho import (
    # Core
    UnifiedZohoClient,
    ZohoAuthManager,
    ZohoSyncOrchestrator,
    ZohoWebhookManager,
    UnifiedStockSyncService,

    # Client
    ZohoAPI,
    ZohoAPIError,

    # Auth
    ZohoCredentials,
    ZohoAuthError,

    # Sync
    SyncConfig,
    SyncResult,
    SyncMode,
    EntityType,
    SyncStatus,

    # Stock Sync
    StockSyncConfig,
    StockItem,

    # Webhooks
    WebhookEvent,
    WebhookStatus,
    WebhookPayload,

    # Processors
    ProductProcessor,
    InventoryProcessor,
    CustomerProcessor,
)

# Import structured logging
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class ZohoService:
    """
    Unified Zoho Service - Single Entry Point for All Zoho Operations

    This service replaces ALL scattered zoho_*.py services:
    - zoho_service.py (55KB) - Main service
    - zoho_auth_service.py - Auth operations
    - zoho_books_client.py - Books API
    - zoho_inventory_client.py - Inventory API
    - zoho_bulk_sync.py - Sync operations
    - zoho_stock_sync.py - Stock sync
    - zoho_processor.py - Data processing
    - zoho_queue.py - Queue management
    - zoho_monitoring.py - Monitoring
    - zoho_alert.py - Alerts
    - zoho_webhook_health.py - Webhook health
    - And 4 more...

    All functionality is now unified in TDS.
    """

    def __init__(
        self,
        credentials: Optional[ZohoCredentials] = None,
        db: Optional[Session] = None,
        auto_start: bool = False
    ):
        """
        Initialize Zoho Service

        Args:
            credentials: Zoho API credentials (optional, loads from env if not provided)
            db: Database session for storing sync results
            auto_start: Automatically start auth manager and client
        """
        self.db = db
        self._started = False

        # Load credentials from environment if not provided
        if credentials is None:
            credentials = self._load_credentials_from_env()

        self.credentials = credentials

        # Initialize core components
        self.auth = ZohoAuthManager(credentials, auto_refresh=True)
        self.client = UnifiedZohoClient(self.auth, credentials.organization_id)
        self.sync = ZohoSyncOrchestrator(self.client, db=db)
        self.webhooks = ZohoWebhookManager(self.client, db=db)
        self.stock_sync = UnifiedStockSyncService(self.client, db=db)

        # Initialize processors
        self.processors = {
            EntityType.PRODUCTS: ProductProcessor(self.client, db),
            EntityType.CUSTOMERS: CustomerProcessor(self.client, db),
            EntityType.INVENTORY: InventoryProcessor(self.client, db),
        }

        if auto_start:
            import asyncio
            asyncio.create_task(self.start())

    def _load_credentials_from_env(self) -> ZohoCredentials:
        """Load Zoho credentials from environment variables"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        return ZohoCredentials(
            client_id=os.getenv("ZOHO_CLIENT_ID", ""),
            client_secret=os.getenv("ZOHO_CLIENT_SECRET", ""),
            refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", ""),
            organization_id=os.getenv("ZOHO_ORGANIZATION_ID", "")
        )

    async def start(self):
        """Start all Zoho service components"""
        if self._started:
            logger.warning("ZohoService already started")
            return

        logger.info("Starting Zoho Service...")

        try:
            # Start auth manager
            await self.auth.start()
            logger.info("✅ Zoho Auth Manager started")

            # Start API client
            await self.client.start_session()
            logger.info("✅ Zoho API Client started")

            self._started = True
            logger.info("✅ Zoho Service fully initialized")

        except Exception as e:
            logger.error(f"Failed to start Zoho Service: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop all Zoho service components"""
        if not self._started:
            return

        logger.info("Stopping Zoho Service...")

        try:
            # Close API client session
            await self.client.close_session()
            logger.info("✅ Zoho API Client stopped")

            # Stop auth manager
            await self.auth.stop()
            logger.info("✅ Zoho Auth Manager stopped")

            self._started = False
            logger.info("✅ Zoho Service fully stopped")

        except Exception as e:
            logger.error(f"Error stopping Zoho Service: {e}", exc_info=True)

    # ============================================================================
    # SYNC OPERATIONS (replaces zoho_bulk_sync.py, zoho_sync_service.py)
    # ============================================================================

    async def sync_entity(
        self,
        entity_type: EntityType,
        mode: SyncMode = SyncMode.INCREMENTAL,
        since: Optional[datetime] = None
    ) -> SyncResult:
        """
        Sync a specific entity type from Zoho

        Args:
            entity_type: Type of entity to sync (products, customers, etc.)
            mode: Sync mode (full or incremental)
            since: Start date for incremental sync

        Returns:
            SyncResult with statistics
        """
        if not self._started:
            await self.start()

        config = SyncConfig(
            entity_type=entity_type,
            mode=mode,
            since=since
        )

        logger.info(f"Starting {entity_type.value} sync in {mode.value} mode")
        result = await self.sync.sync_entity(config)
        logger.info(f"Sync complete: {result.total_processed} processed, {result.total_succeeded} succeeded")

        return result

    async def sync_products(self, mode: SyncMode = SyncMode.INCREMENTAL) -> SyncResult:
        """Sync products from Zoho"""
        return await self.sync_entity(EntityType.PRODUCTS, mode)

    async def sync_customers(self, mode: SyncMode = SyncMode.INCREMENTAL) -> SyncResult:
        """Sync customers from Zoho"""
        return await self.sync_entity(EntityType.CUSTOMERS, mode)

    async def sync_inventory(self, mode: SyncMode = SyncMode.INCREMENTAL) -> SyncResult:
        """Sync inventory from Zoho"""
        return await self.sync_entity(EntityType.INVENTORY, mode)

    async def sync_all(self, mode: SyncMode = SyncMode.INCREMENTAL) -> Dict[str, SyncResult]:
        """
        Sync all entities from Zoho

        Returns:
            Dictionary mapping entity types to their sync results
        """
        results = {}

        for entity_type in [EntityType.PRODUCTS, EntityType.CUSTOMERS, EntityType.INVENTORY]:
            try:
                results[entity_type.value] = await self.sync_entity(entity_type, mode)
            except Exception as e:
                logger.error(f"Failed to sync {entity_type.value}: {e}")
                results[entity_type.value] = None

        return results

    # ============================================================================
    # WEBHOOK OPERATIONS (replaces zoho_webhook_health.py, zoho_processor.py)
    # ============================================================================

    async def process_webhook(self, event_data: Dict[str, Any]) -> WebhookEvent:
        """
        Process incoming Zoho webhook

        Args:
            event_data: Webhook payload from Zoho

        Returns:
            WebhookEvent with processing result
        """
        if not self._started:
            await self.start()

        logger.info(f"Processing webhook: {event_data.get('event_type', 'unknown')}")
        event = await self.webhooks.process_event(event_data)
        logger.info(f"Webhook processed: {event.status}")

        return event

    async def get_webhook_health(self) -> Dict[str, Any]:
        """
        Get webhook system health status

        Returns:
            Health status dictionary
        """
        return await self.webhooks.get_health_status()

    # ============================================================================
    # STOCK SYNC OPERATIONS (replaces zoho_stock_sync.py)
    # ============================================================================

    async def sync_stock(self, config: Optional[StockSyncConfig] = None) -> SyncResult:
        """
        Sync stock/inventory levels from Zoho

        Args:
            config: Stock sync configuration

        Returns:
            SyncResult with stock sync statistics
        """
        if not self._started:
            await self.start()

        logger.info("Starting stock sync from Zoho")
        result = await self.stock_sync.sync(config)
        logger.info(f"Stock sync complete: {result.total_succeeded} items updated")

        return result

    # ============================================================================
    # API OPERATIONS (replaces zoho_books_client.py, zoho_inventory_client.py)
    # ============================================================================

    async def api_call(
        self,
        api: ZohoAPI,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a direct API call to Zoho

        Args:
            api: Which API to call (BOOKS, INVENTORY, CRM)
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body

        Returns:
            API response data
        """
        if not self._started:
            await self.start()

        return await self.client.request(api, endpoint, method, params, data)

    # ============================================================================
    # AUTH OPERATIONS (replaces zoho_token_manager.py, zoho_token_refresh_scheduler.py)
    # ============================================================================

    async def refresh_token(self) -> str:
        """
        Manually refresh access token

        Returns:
            New access token
        """
        return await self.auth.refresh_access_token()

    def get_access_token(self) -> str:
        """
        Get current access token

        Returns:
            Current valid access token
        """
        return self.auth.get_access_token()

    # ============================================================================
    # MONITORING & HEALTH (replaces zoho_monitoring.py, zoho_alert.py)
    # ============================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Get Zoho service status

        Returns:
            Status dictionary with component health
        """
        return {
            "started": self._started,
            "auth": {
                "authenticated": self.auth.is_authenticated(),
                "token_expires_at": self.auth.get_token_expiry(),
            },
            "client": {
                "session_active": self.client.is_session_active(),
            },
            "sync": {
                "last_sync": None,  # TODO: Track last sync time
            }
        }


# ============================================================================
# CONVENIENCE EXPORTS - Make imports easier
# ============================================================================

__all__ = [
    # Main service
    'ZohoService',

    # Re-export core components for advanced usage
    'UnifiedZohoClient',
    'ZohoAuthManager',
    'ZohoSyncOrchestrator',
    'ZohoWebhookManager',
    'UnifiedStockSyncService',

    # Client
    'ZohoAPI',
    'ZohoAPIError',

    # Auth
    'ZohoCredentials',
    'ZohoAuthError',

    # Sync
    'SyncConfig',
    'SyncResult',
    'SyncMode',
    'EntityType',
    'SyncStatus',

    # Stock
    'StockSyncConfig',
    'StockItem',

    # Webhooks
    'WebhookEvent',
    'WebhookStatus',
    'WebhookPayload',

    # Processors
    'ProductProcessor',
    'InventoryProcessor',
    'CustomerProcessor',
]

__version__ = '3.0.0'
