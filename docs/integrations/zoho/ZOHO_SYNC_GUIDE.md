# Zoho Sync Guide

**Complete Zoho Books/Inventory Integration for TSH ERP**
Last Updated: November 13, 2025

---

## Table of Contents
1. [Overview](#overview)
2. [Setup & Configuration](#setup--configuration)
3. [Webhook Integration](#webhook-integration)
4. [API Integration](#api-integration)
5. [Sync Operations](#sync-operations)
6. [Image Syncing](#image-syncing)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

### What is Zoho Sync?

The Zoho Sync system provides bidirectional integration between TSH ERP and Zoho Books/Inventory, enabling:
- Real-time data synchronization
- Automated inventory updates
- Order and invoice processing
- Product catalog management
- Customer data sync

### Integration Architecture

```
┌──────────────────────────────────────────────────┐
│            Zoho Books/Inventory                  │
│  • Products/Items                                │
│  • Customers/Contacts                            │
│  • Sales Orders                                  │
│  • Invoices                                      │
│  • Payments                                      │
│  • Inventory Levels                              │
└────────────┬─────────────────────────────────────┘
             │
             │ Webhooks (Real-time)
             │ REST API (Polling)
             ↓
┌──────────────────────────────────────────────────┐
│              TSH ERP - Zoho Integration          │
│                                                  │
│  ┌────────────────┐        ┌─────────────────┐  │
│  │  Webhook       │        │   API Client    │  │
│  │  Handler       │        │   (MCP)         │  │
│  └────────┬───────┘        └────────┬────────┘  │
│           │                         │           │
│           └──────────┬──────────────┘           │
│                      ↓                          │
│           ┌──────────────────────┐              │
│           │   TDS Integration    │              │
│           │   (Sync Engine)      │              │
│           └──────────┬───────────┘              │
│                      │                          │
│                      ↓                          │
│           ┌──────────────────────┐              │
│           │  PostgreSQL Database │              │
│           └──────────────────────┘              │
└──────────────────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────┐
│         TSH ERP Applications                     │
│  • Web Admin (React)                             │
│  • Mobile App (Flutter)                          │
│  • Consumer App (Flutter Web)                    │
└──────────────────────────────────────────────────┘
```

### Supported Entities

| Entity | Zoho Books | Zoho Inventory | Sync Direction |
|--------|-----------|---------------|----------------|
| Products/Items | ✅ | ✅ | Zoho → TSH (Read-only) |
| Customers/Contacts | ✅ | ✅ | Bidirectional |
| Sales Orders | ✅ | ✅ | TSH → Zoho |
| Invoices | ✅ | ✅ | Zoho → TSH |
| Payments | ✅ | ❌ | Zoho → TSH |
| Stock Levels | ❌ | ✅ | Zoho → TSH |
| Price Lists | ✅ | ✅ | Zoho → TSH |
| Credit Notes | ✅ | ❌ | Zoho → TSH |

---

## Setup & Configuration

### Prerequisites

1. **Zoho Account**
   - Active Zoho Books OR Zoho Inventory subscription
   - Admin access to create OAuth apps

2. **TSH ERP Setup**
   - TSH ERP backend deployed
   - PostgreSQL database configured
   - Internet-accessible webhook endpoint

### Step 1: Create Zoho OAuth App

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Click "Add Client"
3. Select "Server-based Applications"
4. Fill in details:
   - **Client Name:** TSH ERP Integration
   - **Homepage URL:** https://erp.tsh.sale
   - **Authorized Redirect URIs:** https://erp.tsh.sale/auth/zoho/callback

5. Note down:
   - Client ID
   - Client Secret

### Step 2: Generate Refresh Token

```bash
# 1. Get authorization code
open "https://accounts.zoho.com/oauth/v2/auth?scope=ZohoBooks.fullaccess.all&client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://erp.tsh.sale/auth/zoho/callback&access_type=offline"

# 2. Exchange code for refresh token
curl -X POST https://accounts.zoho.com/oauth/v2/token \
  -d "code=AUTHORIZATION_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://erp.tsh.sale/auth/zoho/callback" \
  -d "grant_type=authorization_code"

# 3. Save the refresh_token from response
```

### Step 3: Configure TSH ERP

Add to `.env`:

```bash
# Zoho OAuth
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ZOHO_REFRESH_TOKEN=1000.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ZOHO_ORGANIZATION_ID=748369814

# Zoho API Configuration
ZOHO_API_BASE_URL=https://www.zohoapis.com
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
ZOHO_API_VERSION=v3

# Sync Configuration
ZOHO_SYNC_ENABLED=true
ZOHO_WEBHOOK_SECRET=your_webhook_secret_key
ZOHO_RATE_LIMIT_PER_MINUTE=20
ZOHO_BATCH_SIZE=200
```

### Step 4: Verify Connection

```bash
# Test Zoho API connection
curl http://localhost:8000/api/zoho/test-connection

# Expected response:
{
  "status": "connected",
  "organization": "TSH Trading",
  "organization_id": "748369814",
  "api_version": "v3"
}
```

---

## Webhook Integration

### Configure Zoho Webhooks

**1. Access Zoho Webhooks:**
- Zoho Books: Settings → Automation → Webhooks
- Zoho Inventory: Settings → Webhooks

**2. Create Webhook:**
```
URL: https://erp.tsh.sale/api/webhooks/zoho
Method: POST
Events to Subscribe:
  ✓ Item Created
  ✓ Item Updated
  ✓ Item Deleted
  ✓ Contact Created
  ✓ Contact Updated
  ✓ Sales Order Created
  ✓ Sales Order Updated
  ✓ Invoice Created
  ✓ Invoice Updated
  ✓ Payment Created
```

**3. Webhook Secret:**
- Generate a secure random string
- Add to Zoho webhook configuration
- Add to TSH ERP `.env` as `ZOHO_WEBHOOK_SECRET`

### Webhook Handler

TSH ERP automatically processes Zoho webhooks:

```python
# app/routers/webhooks.py
@router.post("/webhooks/zoho")
async def handle_zoho_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify webhook signature
    # 2. Parse payload
    # 3. Queue for processing via TDS
    # 4. Return 200 OK immediately
    pass
```

### Webhook Payload Examples

**Item Created:**
```json
{
  "event_type": "item_created",
  "data": {
    "item_id": "2646610000000113574",
    "name": "Product Name",
    "sku": "SKU123",
    "rate": 99.99,
    "stock_on_hand": 100
  }
}
```

**Sales Order Created:**
```json
{
  "event_type": "salesorder_created",
  "data": {
    "salesorder_id": "2646610000012345678",
    "customer_id": "2646610000009876543",
    "total": 1500.00,
    "status": "confirmed"
  }
}
```

### Webhook Troubleshooting

**Common Issues:**

1. **Webhooks Not Received:**
```bash
# Check webhook endpoint accessibility
curl -X POST https://erp.tsh.sale/api/webhooks/zoho \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Should return 200 OK
```

2. **Signature Verification Fails:**
```bash
# Verify webhook secret matches
# Check logs: docker-compose logs api | grep "webhook"
```

3. **Processing Delays:**
```bash
# Check TDS queue
curl http://localhost:8000/api/tds/queue

# Increase workers if needed
docker-compose up -d --scale tds-worker=5
```

---

## API Integration

### Zoho MCP (Model Context Protocol)

TSH ERP includes an MCP server for Zoho API access.

**Configuration:**
```json
// .claude/mcp_settings.json
{
  "mcpServers": {
    "zoho": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-zoho"],
      "env": {
        "ZOHO_CLIENT_ID": "1000.XXX",
        "ZOHO_CLIENT_SECRET": "xxx",
        "ZOHO_REFRESH_TOKEN": "1000.xxx",
        "ZOHO_ORGANIZATION_ID": "748369814"
      }
    }
  }
}
```

### Available MCP Tools

**Items/Products:**
```python
# List items
mcp__zoho__ZohoBooks_list_items(
    organization_id="748369814",
    page=1,
    per_page=200
)

# Get item details
mcp__zoho__ZohoBooks_get_item(
    item_id="2646610000000113574",
    organization_id="748369814"
)
```

**Contacts:**
```python
# List contacts
mcp__zoho__ZohoBooks_list_contacts(
    organization_id="748369814",
    filter_by="Status.Active"
)

# Get contact details
mcp__zoho__ZohoBooks_get_contact(
    contact_id="2646610000009876543",
    organization_id="748369814"
)
```

**Sales Orders:**
```python
# List sales orders
mcp__zoho__ZohoBooks_list_sales_orders(
    organization_id="748369814",
    filter_by="Status.Open"
)

# Get sales order details
mcp__zoho__ZohoBooks_get_sales_order(
    salesorder_id="2646610000012345678",
    organization_id="748369814"
)
```

**Invoices:**
```python
# List invoices
mcp__zoho__ZohoBooks_list_invoices(
    organization_id="748369814",
    status="unpaid"
)

# Get invoice details
mcp__zoho__ZohoBooks_get_invoice(
    invoice_id="2646610000011111111",
    organization_id="748369814"
)
```

### Rate Limiting

Zoho API has rate limits:
- **20 API calls per minute** (default)
- **1000 API calls per day**

TSH ERP automatically handles rate limiting:
```python
# Automatic retry with backoff
# Queued requests when limit reached
# Distributed across workers
```

---

## Sync Operations

### Full Sync vs. Incremental Sync

**Full Sync:**
- Syncs all entities from Zoho
- Runs on initial setup
- Can be triggered manually
- Takes 10-30 minutes

**Incremental Sync:**
- Only syncs changed entities
- Triggered by webhooks
- Real-time (< 1 minute delay)
- Continuous operation

### Manual Sync

**Via API:**
```bash
# Sync all products
curl -X POST http://localhost:8000/api/zoho/sync/products \
  -H "Authorization: Bearer YOUR_TOKEN"

# Sync all contacts
curl -X POST http://localhost:8000/api/zoho/sync/contacts

# Sync sales orders (last 7 days)
curl -X POST http://localhost:8000/api/zoho/sync/salesorders \
  -d '{"days": 7}'
```

**Via Dashboard:**
1. Go to https://erp.tsh.sale/settings/zoho-sync
2. Select entity type
3. Click "Sync Now"
4. Monitor progress

**Via Python:**
```python
from app.integrations.zoho.sync import sync_all_products

async def manual_sync(db: AsyncSession):
    result = await sync_all_products(db)
    print(f"Synced {result.total_synced} products")
```

### Scheduled Sync

**Automatic scheduled sync for stock levels:**

```bash
# Cron job (every 30 minutes)
*/30 * * * * curl -X POST http://localhost:8000/api/tds/stock/sync
```

**Or use environment variable:**
```bash
TDS_STOCK_SYNC_INTERVAL_MINUTES=30
```

### Sync Monitoring

**Dashboard:**
- https://erp.tsh.sale/tds-admin
- Real-time sync status
- Success/failure rates
- Queue depth

**Metrics:**
```bash
# Get sync statistics
curl http://localhost:8000/api/zoho/sync/stats

Response:
{
  "total_syncs_today": 45,
  "success_rate": 99.2,
  "avg_sync_time_seconds": 12.5,
  "entities_synced": {
    "products": 1250,
    "contacts": 340,
    "orders": 89
  }
}
```

---

## Image Syncing

### Product Image Sync

Zoho product images are automatically downloaded and stored in TSH ERP.

**Image Sync Flow:**
```
Zoho Product Created/Updated
    ↓
Webhook Received
    ↓
TDS Processes Product
    ↓
Image URL Extracted
    ↓
Image Downloaded (async)
    ↓
Stored in Database (Base64 or File)
    ↓
CDN URL Generated
    ↓
Available in TSH Apps
```

### Image Access Fix

**Problem:** Zoho image URLs expire after ~7 days

**Solution:** TSH ERP caches images locally

**Configuration:**
```bash
# .env
ZOHO_IMAGE_CACHE_ENABLED=true
ZOHO_IMAGE_CACHE_DIR=/var/www/tsh-erp/images/products/
ZOHO_IMAGE_CDN_URL=https://erp.tsh.sale/images/products/
```

**Manual Image Sync:**
```bash
# Sync all product images
curl -X POST http://localhost:8000/api/zoho/sync/images

# Sync images for specific product
curl -X POST http://localhost:8000/api/zoho/sync/images/2646610000000113574
```

### Image URL Format

**Zoho Original:** (Expires in 7 days)
```
https://www.zohoapis.com/books/v3/items/2646610000000113574/image
```

**TSH Cached:** (Permanent)
```
https://erp.tsh.sale/images/products/item_2646610000000113574_9be7e082.jpg
```

---

## Troubleshooting

### Common Issues

#### 1. OAuth Token Expired

**Symptoms:**
- API calls return 401 Unauthorized
- Sync fails with auth errors

**Solution:**
```bash
# Refresh tokens are automatically renewed
# If still failing, regenerate refresh token:
# Follow Step 2 in Setup section

# Update .env with new token
ZOHO_REFRESH_TOKEN=new_token_here

# Restart services
docker-compose restart api tds-worker
```

#### 2. Webhook Signature Mismatch

**Symptoms:**
- Webhooks rejected
- Logs show "Invalid signature"

**Solution:**
```bash
# Verify webhook secret matches
# In Zoho: Settings → Webhooks → Edit → Secret

# Update .env
ZOHO_WEBHOOK_SECRET=correct_secret_here

# Restart
docker-compose restart api
```

#### 3. Rate Limit Exceeded

**Symptoms:**
- 429 Too Many Requests errors
- Sync delays

**Solution:**
```bash
# Reduce batch size
ZOHO_BATCH_SIZE=100  # Default: 200

# Reduce rate limit
ZOHO_RATE_LIMIT_PER_MINUTE=15  # Default: 20

# Add more workers (spreads load)
docker-compose up -d --scale tds-worker=5
```

#### 4. Data Inconsistency

**Symptoms:**
- Products in Zoho not in TSH
- Stock levels don't match

**Solution:**
```bash
# Run full sync
curl -X POST http://localhost:8000/api/zoho/sync/full

# Compare records
curl http://localhost:8000/api/zoho/compare

# Force re-sync specific entity
curl -X POST http://localhost:8000/api/zoho/sync/products/2646610000000113574?force=true
```

### Debug Mode

Enable detailed Zoho sync logging:

```bash
# .env
ZOHO_DEBUG=true
ZOHO_LOG_API_CALLS=true

# Restart
docker-compose restart api tds-worker

# View logs
docker-compose logs -f api | grep "ZOHO"
```

---

## Best Practices

### 1. Error Handling

- ✅ Always enable dead letter queue
- ✅ Monitor failed syncs daily
- ✅ Set up alerts for high error rates
- ✅ Retry failed items automatically

### 2. Performance Optimization

- ✅ Use batch API calls when possible
- ✅ Cache frequently accessed data
- ✅ Enable compression for API responses
- ✅ Use pagination for large datasets

### 3. Data Integrity

- ✅ Zoho is the source of truth for products
- ✅ TSH creates orders, Zoho confirms
- ✅ Always validate data before sync
- ✅ Keep audit logs of all changes

### 4. Security

- ✅ Store credentials in environment variables
- ✅ Use HTTPS for all API calls
- ✅ Verify webhook signatures
- ✅ Rotate refresh tokens periodically

### 5. Monitoring

- ✅ Track sync success rates
- ✅ Monitor API usage vs. limits
- ✅ Alert on sync failures
- ✅ Review dead letter queue daily

---

## Migration Checklist

If migrating from old Zoho integration:

- [ ] Export current Zoho mappings
- [ ] Backup database
- [ ] Configure new OAuth app
- [ ] Set up webhooks
- [ ] Run initial full sync
- [ ] Verify data accuracy
- [ ] Monitor for 48 hours
- [ ] Decommission old integration

---

## API Reference

### Zoho Sync Endpoints

```
POST   /api/zoho/sync/full              - Full sync all entities
POST   /api/zoho/sync/products          - Sync products
POST   /api/zoho/sync/contacts          - Sync contacts
POST   /api/zoho/sync/salesorders       - Sync sales orders
POST   /api/zoho/sync/invoices          - Sync invoices
POST   /api/zoho/sync/images            - Sync product images
GET    /api/zoho/sync/stats             - Sync statistics
GET    /api/zoho/test-connection        - Test Zoho connection
GET    /api/zoho/compare                - Compare data consistency
```

---

## Related Documentation

- **TDS Integration:** [TDS_INTEGRATION_GUIDE.md](../tds/TDS_INTEGRATION_GUIDE.md)
- **MCP Setup:** [ZOHO_MCP_SETUP.md](../../.mcp/ZOHO_MCP_SETUP.md)
- **Deployment:** [DEPLOYMENT_GUIDE.md](../../.claude/DEPLOYMENT_GUIDE.md)

---

## Support

**Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Review logs: `docker-compose logs api tds-worker | grep ZOHO`
- Contact: #zoho-integration

**External Resources:**
- [Zoho Books API Docs](https://www.zoho.com/books/api/v3/)
- [Zoho Inventory API Docs](https://www.zoho.com/inventory/api/v1/)
- [Zoho OAuth Guide](https://www.zoho.com/accounts/protocol/oauth.html)

---

**Status:** ✅ Production Ready
**Last Updated:** November 13, 2025
**Maintainer:** TSH ERP Team
