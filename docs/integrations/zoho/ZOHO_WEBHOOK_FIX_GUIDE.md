# Zoho Webhook Configuration Fix Guide

**Date:** November 4, 2025
**Issue:** Zoho webhooks are configured with incorrect URLs causing "Bad Gateway" errors
**Status:** 🔴 CRITICAL - No webhooks received in 3+ days

---

## Problem Identified

Your screenshot shows Zoho is sending webhooks to:
- **Current (WRONG):** `https://erp.tsh.sale/api/tds/webhooks/products`
- **Correct:** `https://erp.tsh.sale/api/zoho/webhooks/products`

**Impact:**
- All Zoho webhooks are failing with "Bad Gateway" (502) errors
- No sync activity for 3+ days
- Data is stale and out of sync

---

## Correct Webhook URLs

Based on the production codebase (`/home/deploy/TSH_ERP_Ecosystem/app/routers/zoho_webhooks.py`), the correct URLs are:

### 1. Products/Items
```
https://erp.tsh.sale/api/zoho/webhooks/products
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 2. Customers/Contacts
```
https://erp.tsh.sale/api/zoho/webhooks/customers
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 3. Invoices
```
https://erp.tsh.sale/api/zoho/webhooks/invoices
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 4. Bills
```
https://erp.tsh.sale/api/zoho/webhooks/bills
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 5. Credit Notes
```
https://erp.tsh.sale/api/zoho/webhooks/credit-notes
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 6. Stock Adjustments
```
https://erp.tsh.sale/api/zoho/webhooks/stock
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

### 7. Price Lists
```
https://erp.tsh.sale/api/zoho/webhooks/prices
```
**Method:** POST
**Headers:** `X-Webhook-Key: [your-webhook-key]` (optional)

---

## How to Fix in Zoho Books

### Step 1: Access Zoho Books Webhooks Settings

1. Log in to **Zoho Books**: https://books.zoho.com
2. Click on **Settings** (gear icon) in top right
3. Navigate to **Automation** → **Webhooks**
4. You should see a list of configured webhooks

### Step 2: Update Each Webhook URL

For **each webhook** in the list:

1. Click on the webhook name to edit
2. Find the **URL** field
3. **Change from:**
   ```
   https://erp.tsh.sale/api/tds/webhooks/[entity]
   ```
   **Change to:**
   ```
   https://erp.tsh.sale/api/zoho/webhooks/[entity]
   ```

4. Click **Save**

### Step 3: Update All 7 Webhooks

Make sure to update URLs for:
- ✅ Products (items)
- ✅ Customers (contacts)
- ✅ Invoices
- ✅ Bills
- ✅ Credit Notes
- ✅ Stock Adjustments
- ✅ Price Lists

---

## Testing After Configuration

### Option 1: Manual Test via Zoho UI

1. In Zoho Books, go to the webhook settings
2. Click **Test Webhook** button next to each webhook
3. Verify you see:
   - ✅ **Status:** Success (202 Accepted)
   - ✅ **Response:** `{"success": true, "message": "... webhook processed and queued"}`

### Option 2: Trigger Real Event

1. Make a small change to a product in Zoho Books (e.g., update description)
2. Wait 10-30 seconds
3. Check if webhook was received:

```bash
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c \"SELECT id, entity_type, entity_id, status, created_at FROM tds_sync_queue ORDER BY created_at DESC LIMIT 10;\""
```

You should see a new `product` entry with status `pending` or `processing`.

### Option 3: Monitor Service Logs

```bash
ssh root@167.71.39.50 "journalctl -u tsh-erp -f | grep -i webhook"
```

Watch for log messages like:
```
Product webhook received: 2646610000XXXXXXX
```

---

## Verification Checklist

After updating all webhook URLs, verify:

- [ ] All 7 webhooks updated in Zoho Books settings
- [ ] Test webhook button shows success (202 Accepted)
- [ ] Make a test change in Zoho Books
- [ ] Verify webhook appears in `tds_sync_queue` table
- [ ] Check service logs show webhook received
- [ ] Verify sync delay drops from 3+ days to < 5 minutes

---

## Common Issues

### Issue 1: Still Getting "Bad Gateway"

**Cause:** URL not updated correctly
**Fix:** Double-check URL format - must be `/api/zoho/webhooks/` not `/api/tds/webhooks/`

### Issue 2: Getting 401 Unauthorized

**Cause:** Webhook API key mismatch
**Fix:**
1. Check `app/core/config.py` for `WEBHOOK_API_KEY` setting
2. Update `X-Webhook-Key` header in Zoho webhook configuration
3. Or disable authentication by removing the key requirement

### Issue 3: Webhooks Not Appearing in Queue

**Cause:** Service might be down or duplicate event
**Fix:**
1. Check service status: `systemctl status tsh-erp`
2. Check logs: `journalctl -u tsh-erp -n 50`
3. Verify database connection

### Issue 4: "Duplicate Event" Response

**Status:** ✅ This is NORMAL!
**Explanation:** System returns success for duplicates to prevent Zoho from retrying indefinitely

---

## Expected Results

After fixing the webhook URLs, you should see:

### Immediate (within 1 minute):
- ✅ Test webhooks return 202 Accepted
- ✅ No more "Bad Gateway" errors in Zoho logs

### Within 5 minutes:
- ✅ New items appear in `tds_sync_queue`
- ✅ Workers process the queue
- ✅ Items move from `pending` → `processing` → `completed`

### Within 1 hour:
- ✅ Sync delay drops from 3+ days to < 5 minutes
- ✅ All recent Zoho changes synced to TSH ERP
- ✅ No failed items in queue

---

## Monitoring Going Forward

Use the Zoho Sync Manager agent to monitor health:

```
Check Zoho sync health
```

The agent will:
- ✅ Check queue status
- ✅ Monitor sync delays
- ✅ Detect and fix failed items
- ✅ Alert if delays exceed thresholds
- ✅ Auto-heal common issues

---

## Quick Reference: URL Mapping

| Entity | Old (WRONG) URL | New (CORRECT) URL |
|--------|----------------|-------------------|
| Products | `/api/tds/webhooks/products` | `/api/zoho/webhooks/products` |
| Customers | `/api/tds/webhooks/customers` | `/api/zoho/webhooks/customers` |
| Invoices | `/api/tds/webhooks/invoices` | `/api/zoho/webhooks/invoices` |
| Bills | `/api/tds/webhooks/bills` | `/api/zoho/webhooks/bills` |
| Credit Notes | `/api/tds/webhooks/credit-notes` | `/api/zoho/webhooks/credit-notes` |
| Stock | `/api/tds/webhooks/stock` | `/api/zoho/webhooks/stock` |
| Prices | `/api/tds/webhooks/prices` | `/api/zoho/webhooks/prices` |

**Key Change:** `/api/tds/` → `/api/zoho/`

---

## Need Help?

If you encounter issues after following this guide:

1. **Check service logs:**
   ```bash
   ssh root@167.71.39.50 "journalctl -u tsh-erp -n 100"
   ```

2. **Run health check:**
   ```bash
   .claude/agents/zoho-sync-manager/tools/sync_health_check.sh
   ```

3. **Ask the Zoho Sync Manager agent:**
   ```
   I updated the webhook URLs but still seeing issues. Please investigate.
   ```

---

**Status:** ✅ Ready to implement
**Estimated Time:** 10-15 minutes
**Risk Level:** Low (non-destructive change)
**Rollback:** Change URLs back if needed

**Next Step:** Update the 7 webhook URLs in Zoho Books settings now!
