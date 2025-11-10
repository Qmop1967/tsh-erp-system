# Zoho Webhook Setup - Implementation Complete

**Date:** November 9, 2025
**Status:** ✅ Ready for Deployment
**Author:** Claude Code (Senior Software Engineer)

---

## 📋 Summary

Successfully implemented a unified Zoho webhook system following the TSH ERP Ecosystem's monolith + BFF architecture. All Zoho webhook operations now flow through TDS (TSH Datasync), ensuring consistency, maintainability, and scalability.

---

## 🎯 What Was Implemented

### 1. TDS Webhook API Router
**Location:** `app/tds/api/webhooks.py`

A clean, production-ready webhook router with:
- 6 webhook endpoints for different Zoho entities
- 2 monitoring endpoints (health & stats)
- Automatic deduplication
- Error handling and logging
- Authentication via webhook API key

### 2. Webhook Endpoints

#### Data Ingestion Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tds/webhooks/products` | POST | Receive product/item updates from Zoho Books |
| `/api/tds/webhooks/customers` | POST | Receive customer/contact updates from Zoho Books |
| `/api/tds/webhooks/invoices` | POST | Receive invoice updates from Zoho Books |
| `/api/tds/webhooks/orders` | POST | Receive sales order updates from Zoho Books |
| `/api/tds/webhooks/stock` | POST | Receive stock adjustment updates from Zoho Inventory |
| `/api/tds/webhooks/prices` | POST | Receive price list updates from Zoho Books |

#### Monitoring Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tds/webhooks/health` | GET | System health check and metrics |
| `/api/tds/webhooks/stats` | GET | Detailed processing statistics (24hr window) |

### 3. Architecture Integration

```
Zoho Books
    ↓ (HTTP POST)
/api/tds/webhooks/{entity}
    ↓
TDS Webhook Router
    ↓
ProcessorService
    ↓
TDSInboxEvent (stored)
    ↓
TDSSyncQueue (queued)
    ↓
Background Workers
    ↓
Database Sync
```

**Key Features:**
- ✅ Automatic deduplication (10-minute window)
- ✅ Idempotency keys for safe retries
- ✅ Full audit trail via TDSInboxEvent
- ✅ Background processing via TDSSyncQueue
- ✅ Health monitoring and statistics
- ✅ Graceful error handling

### 4. Files Modified/Created

**Created:**
- `app/tds/api/webhooks.py` - Main webhook router (461 lines)
- `test_webhook_setup.py` - Local testing script

**Modified:**
- `app/tds/api/__init__.py` - Export webhook router
- `app/tds/api/statistics.py` - Fixed import issues
- `app/main.py` - Registered webhook router

---

## 🚀 Next Steps

### Step 1: Deploy to Production

```bash
# From your local machine
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Deploy via Docker
./deploy.sh

# Or deploy TDS specifically
./deploy_tds_autosync.sh
```

### Step 2: Configure Zoho Books Webhooks

1. **Log in to Zoho Books**
   - URL: https://books.zoho.com
   - Navigate to: Settings → Automation → Webhooks

2. **Create/Update Each Webhook**

   For each entity type, configure:

   **Products/Items:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/products`
   - Method: POST
   - Events: Item Created, Item Updated, Item Deleted
   - Headers: `X-Webhook-Key: [your-webhook-key]` (optional)

   **Customers/Contacts:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/customers`
   - Method: POST
   - Events: Contact Created, Contact Updated, Contact Deleted

   **Invoices:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/invoices`
   - Method: POST
   - Events: Invoice Created, Invoice Updated, Invoice Deleted

   **Sales Orders:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/orders`
   - Method: POST
   - Events: Sales Order Created, Sales Order Updated, Sales Order Deleted

   **Stock Adjustments:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/stock`
   - Method: POST
   - Events: Stock Adjustment Created, Stock Adjustment Updated

   **Price Lists:**
   - URL: `https://erp.tsh.sale/api/tds/webhooks/prices`
   - Method: POST
   - Events: Price List Created, Price List Updated

### Step 3: Test Webhooks

#### Option 1: Use Zoho's Test Button
1. In Zoho Books webhook settings
2. Click "Test Webhook" next to each configured webhook
3. Verify response: `202 Accepted` with success message

#### Option 2: Make a Real Change
1. Update a product in Zoho Books (e.g., change description)
2. Wait 5-10 seconds
3. Check webhook was received:

```bash
ssh root@167.71.39.50
# Check health
curl https://erp.tsh.sale/api/tds/webhooks/health

# Check stats
curl https://erp.tsh.sale/api/tds/webhooks/stats

# Check database
PGPASSWORD="your-password" psql tsh_erp -c "
SELECT id, entity_type, entity_id, status, created_at
FROM tds_inbox_events
ORDER BY created_at DESC
LIMIT 10;
"
```

#### Option 3: Manual Test via curl

```bash
curl -X POST https://erp.tsh.sale/api/tds/webhooks/products \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Key: your-key-here" \
  -d '{
    "entity_id": "TEST123",
    "organization_id": "748369814",
    "item": {
      "item_id": "TEST123",
      "name": "Test Product",
      "sku": "TEST-SKU"
    }
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Product webhook processed and queued",
  "event_id": "...",
  "idempotency_key": "zoho:product:TEST123:update",
  "queued": true
}
```

### Step 4: Verify Flutter Consumer App (via Chrome DevTools)

After deployment, test that the consumer app displays correct prices:

1. Open Chrome DevTools MCP
2. Navigate to consumer app
3. Check that product prices match Zoho Books
4. Verify price list selection works correctly
5. Test product search and filtering

---

## 🔧 Configuration

### Environment Variables

Make sure these are set in your `.env` or production environment:

```bash
# Optional: Webhook authentication key
WEBHOOK_API_KEY=your-secret-key-here

# Optional: Zoho webhook signature verification
ZOHO_WEBHOOK_SECRET=your-zoho-secret

# Database connection (should already be configured)
DATABASE_URL=postgresql://...
```

### Webhook API Key Setup

If you want to secure webhooks with an API key:

1. Generate a secure key:
```bash
openssl rand -hex 32
```

2. Add to `.env`:
```bash
WEBHOOK_API_KEY=<generated-key>
```

3. Add to Zoho webhook headers:
```
X-Webhook-Key: <generated-key>
```

---

## 📊 Monitoring

### Health Check
```bash
curl https://erp.tsh.sale/api/tds/webhooks/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "webhooks_received_24h": 150,
  "queue_size": 5,
  "system": "tds",
  "timestamp": "2025-11-09T..."
}
```

### Statistics
```bash
curl https://erp.tsh.sale/api/tds/webhooks/stats
```

**Expected Response:**
```json
{
  "period": "last_24_hours",
  "total_received": 150,
  "total_processed": 148,
  "total_failed": 2,
  "success_rate": 98.67,
  "timestamp": "2025-11-09T..."
}
```

### Database Monitoring

```sql
-- Check recent webhooks
SELECT
  entity_type,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE status = 'processed') as processed,
  COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM tds_inbox_events
WHERE received_at >= NOW() - INTERVAL '24 hours'
GROUP BY entity_type;

-- Check queue depth
SELECT
  entity_type,
  COUNT(*) as pending
FROM tds_sync_queue
WHERE status = 'pending'
GROUP BY entity_type;
```

---

## 🐛 Troubleshooting

### Webhook Not Received

**Check 1: Zoho Configuration**
- Verify URL is correct: `https://erp.tsh.sale/api/tds/webhooks/{entity}`
- Check method is POST
- Verify events are selected

**Check 2: Network/Firewall**
```bash
# Test from external network
curl -I https://erp.tsh.sale/api/tds/webhooks/health
```

**Check 3: Service Logs**
```bash
ssh root@167.71.39.50
journalctl -u tsh-erp -f | grep webhook
```

### Webhook Returns Error

**401 Unauthorized:**
- Check `X-Webhook-Key` header matches `WEBHOOK_API_KEY`
- Or remove `WEBHOOK_API_KEY` from `.env` for development

**500 Internal Server Error:**
- Check service logs for details
- Verify database connection
- Check ProcessorService is working

**422 Validation Error:**
- Check payload structure matches expected format
- Verify required fields are present

### Sync Not Happening

**Check Queue:**
```sql
SELECT * FROM tds_sync_queue WHERE status = 'pending' LIMIT 10;
```

**Check Workers:**
```bash
# Verify background workers are running
ps aux | grep worker
journalctl -u tsh-erp | grep worker
```

**Manual Trigger:**
```bash
# Force sync from Zoho
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/products
```

---

## 📝 Architecture Notes

### Why TDS?

All Zoho operations go through TDS (TSH Datasync) per the unified architecture:
- ✅ Single source of truth
- ✅ Consistent error handling
- ✅ Unified monitoring
- ✅ Simplified maintenance
- ✅ Reduced code duplication

### Design Decisions

1. **ProcessorService over WebhookManager:**
   - Simpler dependency graph
   - Leverages existing infrastructure
   - Easier to test and maintain

2. **Async/Background Processing:**
   - Fast webhook responses (< 100ms)
   - Prevents Zoho timeout/retry storms
   - Scalable worker model

3. **Deduplication:**
   - Prevents duplicate processing
   - Safe for Zoho retries
   - 10-minute window balances safety vs memory

---

## ✅ Success Criteria

- [x] Webhook endpoints created and registered
- [x] Code committed to git
- [ ] Deployed to production VPS
- [ ] Configured in Zoho Books
- [ ] Tested with real webhook event
- [ ] Verified sync happens within 5 minutes
- [ ] Flutter consumer app displays correct prices

---

## 🎉 Summary

The Zoho webhook system is now **ready for deployment**. The implementation:

1. ✅ Follows the unified TDS architecture
2. ✅ Uses existing ProcessorService infrastructure
3. ✅ Provides comprehensive monitoring
4. ✅ Handles errors gracefully
5. ✅ Scales with background workers
6. ✅ Maintains full audit trail

**Next:** Deploy to production and configure Zoho Books webhook URLs.

---

**Questions or Issues?**
- Check service logs: `journalctl -u tsh-erp -f`
- Monitor health: `curl https://erp.tsh.sale/api/tds/webhooks/health`
- Review code: `app/tds/api/webhooks.py`

---

🤖 Generated by Claude Code
Senior Software Engineer for TSH ERP Ecosystem
