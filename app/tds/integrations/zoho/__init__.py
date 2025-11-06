"""
TDS Zoho Integration Module
============================

Unified Zoho integration for TSH ERP system.
Consolidates all Zoho services into one central module.

خدمة Zoho موحدة ومركزية لنظام TSH ERP

Features:
- Unified API client for Books, Inventory, and CRM
- OAuth authentication with auto-refresh
- Real-time webhook processing
- Batch sync operations
- Rate limiting and retry logic
- Comprehensive monitoring and alerts

Author: TSH ERP Team
Date: November 6, 2025
Version: 2.0.0
"""

from .client import UnifiedZohoClient, ZohoAPI, ZohoAPIError
from .auth import ZohoAuthManager, ZohoCredentials, ZohoAuthError
from .sync import ZohoSyncOrchestrator, SyncConfig, SyncResult, SyncMode, EntityType, SyncStatus
from .webhooks import ZohoWebhookManager, WebhookEvent, WebhookStatus, WebhookPayload
from .processors import ProductProcessor, InventoryProcessor, CustomerProcessor
from .stock_sync import UnifiedStockSyncService, StockSyncConfig, StockItem

__all__ = [
    # Core components
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

    # Stock Sync
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

__version__ = '2.0.0'
