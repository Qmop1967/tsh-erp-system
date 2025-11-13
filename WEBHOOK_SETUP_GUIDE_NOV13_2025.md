# 🔗 Zoho Books Webhooks Setup Guide

**Date:** November 13, 2025  
**Status:** Ready for Configuration  
**Production URL:** https://erp.tsh.sale

---

## 🎯 Quick Status

### Current State: ✅ Webhooks Endpoints Are Live!

- ✅ Webhook endpoints deployed and running
- ✅ Health check passing: `{"status":"healthy"}`
- ⚠️ Zoho is sending webhooks but getting 422 errors (payload format issue)
- ⏳ Need to configure webhooks in Zoho Books dashboard

---

## 📋 Available Webhook Endpoints

All webhook endpoints are live at: `https://erp.tsh.sale/api/tds/webhooks/`

| Endpoint | Purpose | Zoho Module | Status |
|----------|---------|-------------|--------|
| `/api/tds/webhooks/products` | Product/Item updates | Items | ✅ Ready |
| `/api/tds/webhooks/customers` | Customer/Contact updates | Contacts | ✅ Ready |
| `/api/tds/webhooks/invoices` | Invoice updates | Invoices | ✅ Ready |
| `/api/tds/webhooks/orders` | Sales Order updates | Sales Orders | ✅ Ready |
| `/api/tds/webhooks/stock` | Stock/Inventory updates | Inventory Adjustments | ✅ Ready |
| `/api/tds/webhooks/prices` | Price List updates | Price Lists | ✅ Ready |
| `/api/tds/webhooks/bills` | Purchase Bill updates | Bills | ✅ Ready |
| `/api/tds/webhooks/credit-notes` | Credit Note updates | Credit Notes | ✅ Ready |

### Monitoring Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/tds/webhooks/health` | Health check and metrics |
| `/api/tds/webhooks/stats` | Detailed statistics |

---

## 🚀 Step-by-Step Setup in Zoho Books

### Step 1: Access Zoho Books Webhook Settings

1. **Log in to Zoho Books**
   - URL: https://books.zoho.com
   - Use your TSH Store account credentials

2. **Navigate to Webhook Settings**
   - Click on **Settings** (gear icon in top right)
   - Select **Automation** from the left sidebar
   - Click on **Webhooks**

### Step 2: Configure Each Webhook

For each entity type below, click **"+ New Webhook"** and configure:

---

#### 🔹 Webhook 1: Products/Items

**Settings:**
- **Label/Name:** `TSH Store - Item Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/products`
- **Method:** `POST`
- **Module:** `Items`

**Events to Subscribe:**
- [x] Item Created
- [x] Item Updated
- [x] Item Deleted
- [x] Item Status Changed

**Custom Headers:** (Optional)
```
X-Webhook-Key: [leave blank for now]
Content-Type: application/json
```

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 2: Customers/Contacts

**Settings:**
- **Label/Name:** `TSH Store - Contact Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/customers`
- **Method:** `POST`
- **Module:** `Contacts`

**Events to Subscribe:**
- [x] Contact Created
- [x] Contact Updated
- [x] Contact Deleted
- [x] Contact Status Changed

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 3: Invoices

**Settings:**
- **Label/Name:** `TSH Store - Invoice Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/invoices`
- **Method:** `POST`
- **Module:** `Invoices`

**Events to Subscribe:**
- [x] Invoice Created
- [x] Invoice Updated
- [x] Invoice Deleted
- [x] Invoice Sent
- [x] Invoice Payment Received
- [x] Invoice Status Changed

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 4: Sales Orders

**Settings:**
- **Label/Name:** `TSH Store - Sales Order Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/orders`
- **Method:** `POST`
- **Module:** `Sales Orders`

**Events to Subscribe:**
- [x] Sales Order Created
- [x] Sales Order Updated
- [x] Sales Order Deleted
- [x] Sales Order Confirmed
- [x] Sales Order Status Changed

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 5: Purchase Bills

**Settings:**
- **Label/Name:** `TSH Store - Purchase Bill Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/bills`
- **Method:** `POST`
- **Module:** `Bills` (Purchase Bills)

**Events to Subscribe:**
- [x] Bill Created
- [x] Bill Updated
- [x] Bill Deleted
- [x] Bill Payment Made

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 6: Credit Notes

**Settings:**
- **Label/Name:** `TSH Store - Credit Note Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/credit-notes`
- **Method:** `POST`
- **Module:** `Credit Notes`

**Events to Subscribe:**
- [x] Credit Note Created
- [x] Credit Note Updated
- [x] Credit Note Deleted
- [x] Credit Note Applied

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 7: Stock Adjustments

**Settings:**
- **Label/Name:** `TSH Store - Stock Adjustments`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/stock`
- **Method:** `POST`
- **Module:** `Inventory Adjustments`

**Events to Subscribe:**
- [x] Inventory Adjustment Created
- [x] Inventory Adjustment Updated
- [x] Inventory Adjustment Deleted

**Click:** "Save" → "Test Webhook"

---

#### 🔹 Webhook 8: Price Lists

**Settings:**
- **Label/Name:** `TSH Store - Price List Updates`
- **URL:** `https://erp.tsh.sale/api/tds/webhooks/prices`
- **Method:** `POST`
- **Module:** `Price Lists` or `Pricelist`

**Events to Subscribe:**
- [x] Price List Created
- [x] Price List Updated
- [x] Price List Item Added
- [x] Price List Item Updated

**Click:** "Save" → "Test Webhook"

---

## ✅ Step 3: Test Each Webhook

### Option 1: Use Zoho's Test Button

After saving each webhook:
1. Click the **"Test Webhook"** button in Zoho Books
2. You should see a success response
3. Check webhook health for confirmation

### Option 2: Make a Real Change

1. Update a product in Zoho Books (e.g., change description)
2. Wait 5-10 seconds
3. Check if webhook was received:

```bash
curl http://localhost:8000/api/tds/webhooks/stats
```

### Option 3: Manual Test via Command Line

```bash
# Test products webhook
curl -X POST https://erp.tsh.sale/api/tds/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "TEST123",
    "organization_id": "748369814",
    "event_type": "item.updated",
    "item": {
      "item_id": "TEST123",
      "name": "Test Product",
      "sku": "TEST-SKU",
      "rate": 100.00
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Product webhook processed and queued",
  "event_id": "...",
  "queued": true
}
```

---

## 🔍 Verification Steps

### 1. Check Webhook Health

```bash
ssh root@167.71.39.50
curl http://localhost:8000/api/tds/webhooks/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "webhooks_received_24h": 10,
  "queue_size": 0,
  "system": "tds",
  "timestamp": "2025-11-13T..."
}
```

### 2. Check Webhook Statistics

```bash
curl http://localhost:8000/api/tds/webhooks/stats
```

**Expected Response:**
```json
{
  "period": "last_24_hours",
  "total_received": 15,
  "total_processed": 14,
  "total_failed": 1,
  "success_rate": 93.33,
  "by_entity": {
    "products": 5,
    "customers": 3,
    "invoices": 7
  }
}
```

### 3. Check Database for Webhook Events

```bash
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp -c "
SELECT 
  id,
  entity_type,
  entity_id,
  status,
  created_at
FROM tds_inbox_events
ORDER BY created_at DESC
LIMIT 10;
"
```

### 4. Check Sync Queue

```bash
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp -c "
SELECT 
  entity_type,
  status,
  COUNT(*) as count
FROM tds_sync_queue
GROUP BY entity_type, status
ORDER BY entity_type, status;
"
```

---

## 🐛 Troubleshooting

### Issue 1: Webhook Returns 422 Error

**Symptoms:**
- Zoho shows webhook failed
- Status code 422 (Unprocessable Entity)

**Cause:**
- Payload format doesn't match expected schema

**Solution:**
Check the actual payload Zoho is sending and update webhook handler if needed.

```bash
# Check recent errors
docker compose logs app --tail=100 | grep -i "422\|webhook"
```

---

### Issue 2: Webhook Returns 401 Error

**Symptoms:**
- Unauthorized error

**Cause:**
- Webhook API key mismatch

**Solution:**
Either remove the API key requirement or configure it properly:

```bash
# Option 1: Remove key requirement (development)
# Remove WEBHOOK_API_KEY from .env

# Option 2: Generate and configure key
openssl rand -hex 32
# Add to .env: WEBHOOK_API_KEY=<generated-key>
# Add to Zoho webhook headers: X-Webhook-Key: <generated-key>
```

---

### Issue 3: Webhook Not Received

**Check 1: Network Connectivity**
```bash
curl -I https://erp.tsh.sale/api/tds/webhooks/health
```

**Check 2: Zoho Configuration**
- Verify URL is correct
- Ensure method is POST
- Check events are selected

**Check 3: Application Logs**
```bash
docker compose logs app -f | grep webhook
```

---

### Issue 4: Webhook Received But Not Synced

**Check Queue:**
```sql
SELECT * FROM tds_sync_queue 
WHERE status = 'pending' OR status = 'failed'
LIMIT 10;
```

**Check Workers:**
```bash
# Verify background workers are running
docker compose logs app | grep -i worker
```

**Manual Trigger:**
```bash
# Force reprocessing of failed items
curl -X POST http://localhost:8000/api/tds/sync/retry-failed
```

---

## 📊 Monitoring & Maintenance

### Daily Health Check

Add to cron or monitoring system:

```bash
#!/bin/bash
# Check webhook health daily
HEALTH=$(curl -s http://localhost:8000/api/tds/webhooks/health)
STATUS=$(echo $HEALTH | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
  echo "ALERT: Webhook system unhealthy!"
  # Send notification
fi
```

### Weekly Statistics Review

```bash
# Get weekly webhook statistics
curl http://localhost:8000/api/tds/webhooks/stats | jq .
```

### Monitor Failed Webhooks

```sql
-- Check failed webhooks in last 24 hours
SELECT 
  entity_type,
  entity_id,
  error_message,
  created_at
FROM tds_inbox_events
WHERE status = 'failed'
  AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

## 🎯 Success Criteria Checklist

### Setup Complete When:

- [ ] All 8 webhooks configured in Zoho Books
- [ ] Each webhook tested successfully
- [ ] Health endpoint returns "healthy"
- [ ] Statistics show webhooks being received
- [ ] Database shows events in tds_inbox_events
- [ ] Sync queue processing events successfully
- [ ] No 422 errors in application logs
- [ ] Product updates from Zoho appear in TSH ERP within 1 minute
- [ ] Customer updates synced automatically
- [ ] Invoice updates tracked in real-time

---

## 📞 Quick Reference

### Webhook URLs (Copy & Paste)

```
Products:     https://erp.tsh.sale/api/tds/webhooks/products
Customers:    https://erp.tsh.sale/api/tds/webhooks/customers
Invoices:     https://erp.tsh.sale/api/tds/webhooks/invoices
Orders:       https://erp.tsh.sale/api/tds/webhooks/orders
Bills:        https://erp.tsh.sale/api/tds/webhooks/bills
Credit Notes: https://erp.tsh.sale/api/tds/webhooks/credit-notes
Stock:        https://erp.tsh.sale/api/tds/webhooks/stock
Prices:       https://erp.tsh.sale/api/tds/webhooks/prices
```

### Health Check Commands

```bash
# Local health check
curl http://localhost:8000/api/tds/webhooks/health

# Remote health check
curl https://erp.tsh.sale/api/tds/webhooks/health

# Get statistics
curl http://localhost:8000/api/tds/webhooks/stats | jq .

# Check recent events
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \
  "SELECT * FROM tds_inbox_events ORDER BY created_at DESC LIMIT 5;"
```

---

## 🔗 Related Documentation

- **Main Setup Guide:** `ZOHO_WEBHOOK_SETUP_COMPLETE.md`
- **Sync Rules:** `.claude/ZOHO_SYNC_RULES.md`
- **Data Sync Status:** `ZOHO_DATA_SYNC_STATUS_REPORT.md`
- **Webhook Code:** `app/tds/api/webhooks.py`

---

## 🎉 What Happens After Setup?

Once webhooks are configured:

1. **Automatic Sync** - Any changes in Zoho Books automatically sync to TSH ERP within seconds
2. **Real-time Updates** - Products, prices, customers updated in real-time
3. **No Manual Sync** - No need to run manual sync scripts
4. **Mobile Apps Updated** - All mobile apps see changes immediately
5. **Audit Trail** - Complete history of all changes tracked

---

**Setup Status:** ✅ Endpoints Ready - ⏳ Waiting for Zoho Configuration  
**Last Updated:** November 13, 2025  
**Production URL:** https://erp.tsh.sale

🚀 **Ready to configure webhooks in Zoho Books!**

