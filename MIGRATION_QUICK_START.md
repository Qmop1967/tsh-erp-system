# Zoho Migration - Quick Start Guide

## ✅ What's Working Now

1. **Webhooks:** All 7 webhooks configured and working at `/api/zoho/webhooks/*`
2. **Real-time Sync:** New changes in Zoho Books sync to TSH ERP within 15 seconds
3. **Auto-Healing:** Zoho Sync Manager agent monitors and fixes issues automatically

**Test Confirmed:** Nov 4, 2025 09:52 PM - Product webhook received successfully!

---

## 🎯 Your Goal

Migrate ALL data from Zoho Books to TSH ERP:
- ✅ Products (2,000+ items)
- ✅ Customers (contacts)
- ✅ Invoices (historical + current)
- ✅ Stock levels
- ✅ Price lists
- ✅ Bills (optional)
- ✅ Credit notes (optional)

---

## 📋 What We Need to Build

### 1. Bulk Sync Service (`app/services/zoho_bulk_sync.py`)
**Purpose:** Fetch large amounts of data from Zoho Books API

**Features:**
- OAuth authentication with auto-refresh
- Pagination support (200 items per request)
- Rate limiting (100 requests/minute)
- Error handling and retry logic
- Progress tracking

### 2. Bulk Sync Endpoints
**Purpose:** HTTP endpoints to trigger bulk sync operations

**Endpoints:**
- `POST /api/zoho/bulk-sync/products` - Sync all products
- `POST /api/zoho/bulk-sync/customers` - Sync all customers
- `POST /api/zoho/bulk-sync/invoices` - Sync invoices (with date filter)
- `POST /api/zoho/bulk-sync/stock` - Sync current stock levels
- `POST /api/zoho/bulk-sync/pricelists` - Sync all price lists

### 3. Data Transformers
**Purpose:** Convert Zoho format to TSH ERP format

**Transformers:**
- `ZohoItemTransformer` → Product
- `ZohoContactTransformer` → Customer
- `ZohoInvoiceTransformer` → Invoice + InvoiceLineItems
- `ZohoStockTransformer` → Product stock update
- `ZohoPriceListTransformer` → PriceList + ProductPrices

---

## 🚀 Implementation Steps

### Step 1: Zoho API Configuration

**What you need:**
1. Zoho Books **Organization ID**
2. Zoho OAuth **Client ID** and **Client Secret**
3. Zoho OAuth **Refresh Token**

**Where to get them:**
1. Go to https://api-console.zoho.com
2. Create new "Self Client" application
3. Generate refresh token with scope: `ZohoBooks.fullaccess.all`
4. Store in environment variables:
   ```bash
   ZOHO_CLIENT_ID=your_client_id
   ZOHO_CLIENT_SECRET=your_client_secret
   ZOHO_REFRESH_TOKEN=your_refresh_token
   ZOHO_ORGANIZATION_ID=your_org_id
   ```

**I can help you with this!**

---

### Step 2: Create Bulk Sync Service (Day 1)

**File:** `app/services/zoho_bulk_sync.py`

**What it does:**
```python
class ZohoBulkSyncService:
    async def sync_products(self, incremental=False, modified_since=None):
        """Fetch all products from Zoho Books and insert into TSH ERP"""

    async def sync_customers(self, incremental=False, modified_since=None):
        """Fetch all customers from Zoho Books and insert into TSH ERP"""

    async def sync_invoices(self, incremental=False, modified_since=None):
        """Fetch all invoices from Zoho Books and insert into TSH ERP"""

    # ... etc
```

**Estimated Time:** 4-6 hours

---

### Step 3: Create Bulk Sync Endpoints (Day 2)

**File:** `app/routers/zoho_bulk_sync.py`

**What it does:**
```python
@router.post("/bulk-sync/products")
async def bulk_sync_products(
    incremental: bool = False,
    modified_since: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Trigger bulk product sync from Zoho Books"""

    service = ZohoBulkSyncService(db)
    result = await service.sync_products(incremental, modified_since)

    return {
        "success": True,
        "items_synced": result["count"],
        "duration_seconds": result["duration"],
        "errors": result["errors"]
    }
```

**Estimated Time:** 2-3 hours

---

### Step 4: Test with Sample Data (Day 3)

**Test Checklist:**
- [ ] Sync 10 products from Zoho
- [ ] Verify data transformation is correct
- [ ] Check duplicates are handled
- [ ] Test error handling (invalid data)
- [ ] Verify performance (< 1 second per item)

**Estimated Time:** 3-4 hours

---

### Step 5: Execute Full Migration (Day 4-5)

**Order of operations:**

```bash
# 1. Products (most important)
POST /api/zoho/bulk-sync/products
# Expected: ~2,000 products in 5-10 minutes

# 2. Customers
POST /api/zoho/bulk-sync/customers
# Expected: ~hundreds of customers in 1-2 minutes

# 3. Stock Levels
POST /api/zoho/bulk-sync/stock
# Expected: Update 2,000 products in 3-5 minutes

# 4. Price Lists
POST /api/zoho/bulk-sync/pricelists
# Expected: All price lists in 2-3 minutes

# 5. Invoices (last 6 months)
POST /api/zoho/bulk-sync/invoices
Body: {"modified_since": "2025-05-01"}
# Expected: ~hundreds of invoices in 3-5 minutes
```

**Total Migration Time:** 15-30 minutes for all data!

---

## 📊 Validation After Migration

### Data Count Comparison:

```bash
# Check TSH ERP counts
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c \"
SELECT
  (SELECT COUNT(*) FROM products) as products,
  (SELECT COUNT(*) FROM customers) as customers,
  (SELECT COUNT(*) FROM invoices) as invoices,
  (SELECT COUNT(*) FROM product_prices) as prices;
\""

# Compare with Zoho Books reports:
# Go to Zoho Books → Reports → Item Summary
# Compare total counts
```

### Data Quality Checks:

```bash
# Check for products without SKU
SELECT COUNT(*) FROM products WHERE sku IS NULL;

# Check for customers without email
SELECT COUNT(*) FROM customers WHERE email IS NULL;

# Check for invoices with $0 total
SELECT COUNT(*) FROM invoices WHERE total_amount = 0;

# Check for missing Zoho IDs (data integrity)
SELECT COUNT(*) FROM products WHERE zoho_item_id IS NULL;
```

---

## 🔍 Monitoring During Migration

### Real-time Progress:

```bash
# Watch queue activity
watch -n 2 "ssh root@167.71.39.50 'sudo -u postgres psql tsh_erp -c \"SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;\"'"

# Watch service logs
ssh root@167.71.39.50 "journalctl -u tsh-erp -f | grep -i 'product\|customer\|invoice'"
```

### Performance Metrics:

```bash
# Check processing speed
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c \"
SELECT
  entity_type,
  COUNT(*) as total,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_seconds
FROM tds_sync_queue
WHERE status = 'completed'
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY entity_type;
\""
```

---

## 🚨 Troubleshooting

### Issue 1: Zoho API Rate Limit Exceeded

**Error:** `Rate limit exceeded (100 requests/minute)`

**Fix:**
```python
# Add rate limiting in bulk sync service
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=90, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        self.requests = [r for r in self.requests if now - r < timedelta(seconds=self.window_seconds)]

        if len(self.requests) >= self.max_requests:
            sleep_time = self.window_seconds - (now - self.requests[0]).total_seconds()
            await asyncio.sleep(sleep_time)

        self.requests.append(now)
```

### Issue 2: OAuth Token Expired

**Error:** `Invalid or expired access token`

**Fix:**
```python
async def refresh_access_token(self):
    """Refresh Zoho OAuth access token using refresh token"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": settings.zoho_refresh_token,
        "client_id": settings.zoho_client_id,
        "client_secret": settings.zoho_client_secret,
        "grant_type": "refresh_token"
    }

    response = await httpx.post(url, data=data)
    response.raise_for_status()

    token_data = response.json()
    self.access_token = token_data["access_token"]
    return self.access_token
```

### Issue 3: Data Transformation Errors

**Error:** `Invalid product data: missing required field 'sku'`

**Fix:**
```python
# Add default values for missing fields
def transform_zoho_item(zoho_item: dict) -> dict:
    return {
        "zoho_item_id": zoho_item.get("item_id"),
        "name": zoho_item.get("name", "Unnamed Product"),
        "sku": zoho_item.get("sku") or f"AUTO-{zoho_item.get('item_id')}",
        "description": zoho_item.get("description", ""),
        "unit_price": Decimal(zoho_item.get("rate", 0)),
        # ... etc
    }
```

---

## ✅ Success Checklist

After migration is complete, verify:

- [ ] **Product count matches** Zoho Books item count
- [ ] **All products have SKU** (no NULL SKUs)
- [ ] **Stock levels are accurate** (spot-check 10 products)
- [ ] **Customer emails are unique** (no duplicates)
- [ ] **Invoice totals are correct** (spot-check 10 invoices)
- [ ] **Price lists are complete** (all currencies synced)
- [ ] **Webhooks still working** (test by editing item in Zoho)
- [ ] **Queue is empty** (all items processed)
- [ ] **No errors in logs** (check last 100 log lines)
- [ ] **Real-time sync works** (edit item in Zoho, verify it syncs within 15 seconds)

---

## 📅 Recommended Timeline

### Week 1: Development
- **Monday:** Set up Zoho API credentials and test connectivity
- **Tuesday:** Create bulk sync service with products endpoint
- **Wednesday:** Add customers and invoices endpoints
- **Thursday:** Add stock and price lists endpoints
- **Friday:** Testing and bug fixes

### Week 2: Migration
- **Monday:** Migrate products (2,000+ items)
- **Tuesday:** Migrate customers and addresses
- **Wednesday:** Migrate invoices (last 6 months)
- **Thursday:** Migrate stock levels and price lists
- **Friday:** Validation and cleanup

### Week 3: Monitoring
- **Monday-Friday:** Monitor sync health, optimize performance, document

---

## 🎯 Expected Results

### After Full Migration:

**TSH ERP Database:**
- ✅ **2,000+ products** with complete details
- ✅ **Hundreds of customers** with addresses
- ✅ **6 months of invoices** with line items
- ✅ **Current stock levels** for all products
- ✅ **All price lists** with multi-currency support

**Real-time Sync:**
- ✅ **Any change in Zoho** syncs to TSH ERP within 15 seconds
- ✅ **99.9% sync reliability** with auto-healing
- ✅ **Zero manual intervention** needed

**Business Benefits:**
- ✅ **Single source of truth** - TSH ERP has all Zoho data
- ✅ **Offline capability** - ERP works even if Zoho is down
- ✅ **Fast queries** - No need to call Zoho API for reports
- ✅ **Custom features** - Can build features not available in Zoho

---

## 🚀 Ready to Start?

**I can help you with:**

1. **Zoho API Setup** - Get OAuth credentials and test connection
2. **Build Bulk Sync Service** - Create the core service and endpoints
3. **Execute Migration** - Run the migration and validate results
4. **Monitor & Optimize** - Ensure sync health and performance

**What would you like to do first?**

Options:
- A) Set up Zoho API credentials and test connectivity
- B) Start building the bulk sync service
- C) Review and customize the migration plan
- D) Something else?

---

**Current Status:**
- ✅ Webhooks working (real-time sync active)
- ✅ Auto-healing enabled (Zoho Sync Manager agent running)
- ✅ Migration strategy documented
- ⏳ Bulk sync service (waiting to implement)

**Next Step:** Tell me which option you'd like to proceed with!
