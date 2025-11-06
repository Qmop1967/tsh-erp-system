# TDS Zoho Integration

## Unified Zoho Integration for TSH ERP

**Version:** 2.0.0
**Status:** Production Ready ✅

---

## Overview

Complete, unified integration with Zoho Books, Zoho Inventory, and Zoho CRM. This module consolidates 15+ separate services into a single, cohesive system.

---

## Quick Start

```python
from app.tds.integrations.zoho import (
    UnifiedZohoClient,
    ZohoAuthManager,
    ZohoSyncOrchestrator,
    ZohoCredentials,
    SyncConfig,
    SyncMode,
    EntityType
)

# Setup
credentials = ZohoCredentials(
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token",
    organization_id="your_org_id"
)

# Auth
auth = ZohoAuthManager(credentials, auto_refresh=True)
await auth.start()

# Client
async with UnifiedZohoClient(auth, credentials.organization_id) as zoho:
    # Fetch products
    products = await zoho.get(ZohoAPI.INVENTORY, "items")

    # Sync
    orchestrator = ZohoSyncOrchestrator(zoho)
    result = await orchestrator.sync_entity(SyncConfig(
        entity_type=EntityType.PRODUCTS,
        mode=SyncMode.FULL
    ))
```

---

## Components

### 1. UnifiedZohoClient (`client.py`)
- Unified API client for Books, Inventory, CRM
- Connection pooling
- Rate limiting (100 req/min)
- Retry with exponential backoff
- Batch operations
- Paginated fetch

### 2. ZohoAuthManager (`auth.py`)
- OAuth 2.0 authentication
- Automatic token refresh
- Background refresh task
- Multi-organization support

### 3. ZohoSyncOrchestrator (`sync.py`)
- Full sync (initial import)
- Incremental sync (delta updates)
- Real-time sync (webhooks)
- Batch processing
- Progress tracking
- Error recovery

### 4. ZohoWebhookManager (`webhooks.py`)
- Signature validation
- Deduplication
- Async processing
- Health monitoring
- Event replay

### 5. Entity Processors (`processors/`)
- ProductProcessor
- InventoryProcessor
- CustomerProcessor

### 6. Utilities (`utils/`)
- RateLimiter - Token bucket algorithm
- RetryStrategy - Exponential backoff

---

## Features

✅ **Multi-API Support**
- Zoho Books
- Zoho Inventory
- Zoho CRM

✅ **Sync Operations**
- Full sync
- Incremental sync
- Real-time sync
- Scheduled sync

✅ **Advanced Features**
- Automatic token refresh
- Rate limiting
- Retry logic
- Batch operations
- Event-driven
- Monitoring & alerts

✅ **Production Ready**
- Comprehensive error handling
- Health checks
- Metrics tracking
- Full logging
- Type hints
- Documented

---

## Architecture

```
zoho/
├── client.py           # Unified API client
├── auth.py             # OAuth manager
├── sync.py             # Sync orchestrator
├── webhooks.py         # Webhook manager
├── processors/         # Entity processors
│   ├── products.py
│   ├── inventory.py
│   └── customers.py
└── utils/              # Utilities
    ├── rate_limiter.py
    └── retry.py
```

---

## Configuration

```python
# Environment variables
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id
ZOHO_WEBHOOK_SECRET=your_webhook_secret
```

---

## Events

**Sync Events:**
- `tds.zoho.sync.started`
- `tds.zoho.sync.completed`
- `tds.zoho.sync.failed`
- `tds.zoho.entity.synced`

**Webhook Events:**
- `tds.zoho.webhook.received`
- `tds.zoho.webhook.processed`

**API Events:**
- `tds.zoho.api.success`
- `tds.zoho.api.failed`

**Auth Events:**
- `tds.zoho.token.refreshed`
- `tds.zoho.token.refresh_failed`

---

## Documentation

- [Complete Plan](../../../../../TDS_ZOHO_UNIFICATION_PLAN.md)
- [Quick Start](../../../../../TDS_ZOHO_QUICK_START.md)
- [Phase 2 Complete](../../../../../TDS_ZOHO_PHASE2_COMPLETE.md)

---

## Statistics

**Replaces:** 15 services (~5,685 lines)
**New Code:** ~3,000 lines
**Reduction:** 47% less code

---

**Author:** TSH ERP Team
**Date:** November 6, 2025
**License:** Proprietary
