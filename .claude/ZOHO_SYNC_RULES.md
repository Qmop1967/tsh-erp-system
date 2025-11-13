# Zoho Sync Rules - Mandatory Procedures

**Created:** November 13, 2025  
**Authority Level:** CRITICAL - NEVER VIOLATE  
**Last Updated:** November 13, 2025

---

## 🚨 ABSOLUTE RULES - NEVER VIOLATE

### Rule #1: ALL Zoho Sync MUST Go Through TDS

```yaml
MANDATORY:
  - ALL Zoho Books sync operations → TDS Core
  - ALL Zoho Inventory sync operations → TDS Core
  - ALL data fetching from Zoho → TDS Core
  - ALL webhook processing → TDS Core

FORBIDDEN:
  ❌ Direct Zoho Books API calls
  ❌ Direct Zoho Inventory API calls
  ❌ Bypassing TDS for "quick" sync
  ❌ Creating separate sync scripts outside TDS
```

**Why:**
- TDS (TSH Datasync) is the ONLY authorized sync orchestrator
- Ensures data consistency and audit trail
- Handles authentication, rate limiting, and error recovery
- Provides unified interface for both Zoho products

---

## 📦 TDS Architecture Components

### Core TDS Components

```
app/tds/
├── integrations/
│   └── zoho/
│       ├── client.py          # UnifiedZohoClient (ONLY way to access Zoho)
│       ├── auth.py             # ZohoAuthManager (handles tokens)
│       ├── processors/         # Data transformers
│       │   ├── products.py     # ProductProcessor (with safe_decimal)
│       │   ├── customers.py    # CustomerProcessor
│       │   ├── pricelists.py   # PriceListProcessor
│       │   └── invoices.py     # InvoiceProcessor
│       └── sync.py             # Sync orchestration
├── api/
│   └── webhooks.py             # Webhook endpoints
└── models/
    └── inbox.py                # TDS inbox and queue models
```

### TDS Sync Flow

```
Zoho Books/Inventory
       ↓
UnifiedZohoClient (authentication + API calls)
       ↓
Processor (transform data + validate)
       ↓
TDSSyncQueue (queue for processing)
       ↓
Background Workers (2 workers)
       ↓
PostgreSQL Database (products, customers, etc.)
```

---

## 🔄 How to Sync Data from Zoho

### Method 1: Manual Sync Script (Preferred for Bulk)

**Use:** `run_tds_zoho_sync.py` in project root

```bash
# On Production VPS
cd /home/deploy/TSH_ERP_Ecosystem
DATABASE_URL='postgresql://tsh_admin:changeme@localhost:5432/tsh_erp' \
  python3 run_tds_zoho_sync.py
```

**What it syncs:**
- ✅ Products (2,221+ items)
- ✅ Stock levels (embedded in products)
- ✅ Categories and attributes
- ✅ Status and pricing

**Features:**
- Uses UnifiedZohoClient (proper authentication)
- Applies ProductProcessor (data transformation)
- Handles errors gracefully (continues on failure)
- Provides detailed progress and statistics
- 100% success rate with safe_decimal fix

### Method 2: API Endpoints (For Real-time)

**Webhook Endpoints** (for automatic sync from Zoho):

```yaml
Products: POST https://erp.tsh.sale/api/tds/webhooks/products
Customers: POST https://erp.tsh.sale/api/tds/webhooks/customers
Invoices: POST https://erp.tsh.sale/api/tds/webhooks/invoices
Orders: POST https://erp.tsh.sale/api/tds/webhooks/orders
Stock: POST https://erp.tsh.sale/api/tds/webhooks/stock
Prices: POST https://erp.tsh.sale/api/tds/webhooks/prices
```

**How to configure in Zoho Books:**
1. Go to Settings → Automation → Webhooks
2. Create webhook for each entity type
3. Set URL to appropriate endpoint above
4. Select events (Created, Updated, Deleted)

### Method 3: Scheduled Cron Jobs (For Periodic Sync)

```bash
# Every 4 hours - Stock sync
15 */4 * * * cd /home/deploy/TSH_ERP_Ecosystem && \
  DATABASE_URL='...' python3 run_tds_zoho_sync.py

# Daily at 2 AM - Price list sync
0 2 * * * cd /home/deploy/TSH_ERP_Ecosystem && \
  DATABASE_URL='...' python3 scripts/sync_pricelists_from_zoho.py
```

---

## 🖼️ Image Download Requirements

### Rule #2: ALL Product Images Must Be Downloaded

```yaml
MANDATORY:
  - Download ALL product images from Zoho
  - Store images locally (uploads/ directory)
  - Update product.image_url to local path
  - Sync images with products data
  
IMAGE STORAGE:
  Location: /home/deploy/TSH_ERP_Ecosystem/uploads/products/
  Format: [product_sku]_[timestamp].[extension]
  Example: ABC123_20251113.jpg
```

### Image Download Scripts Available

**1. Primary Image Download Script:**

```bash
# Downloads all product images from Zoho
cd /home/deploy/TSH_ERP_Ecosystem
python3 sync_zoho_images.py
```

**Features:**
- Fetches product images from Zoho Books
- Downloads to local storage
- Updates database with local paths
- Handles missing images gracefully
- Supports resume (if interrupted)

**2. Resume Script (if download interrupted):**

```bash
python3 sync_zoho_images_resume.py
```

**3. TDS Image Download (integrated):**

```bash
python3 tds_download_images.py
```

### Image Download Process

```yaml
1. Fetch Products with Images:
   - Query Zoho Books API for products
   - Extract image_url from each product
   - Filter products with valid image URLs

2. Download Images:
   - Create uploads/products/ directory if not exists
   - Download each image (with retry on failure)
   - Generate unique filename (SKU + timestamp)
   - Save to local filesystem

3. Update Database:
   - Update products.image_url with local path
   - Format: /uploads/products/[filename]
   - Mark image as downloaded
   - Log any failures

4. Verification:
   - Check all images downloaded successfully
   - Verify file sizes > 0
   - Test image accessibility via web server
```

### Image Storage Structure

```
/home/deploy/TSH_ERP_Ecosystem/
└── uploads/
    └── products/
        ├── ABC123_20251113_120000.jpg
        ├── DEF456_20251113_120001.png
        ├── GHI789_20251113_120002.webp
        └── ...
```

### Image URL Format in Database

**Before Download:**
```
image_url: https://books.zoho.com/api/v3/items/123456/image
```

**After Download:**
```
image_url: /uploads/products/ABC123_20251113_120000.jpg
```

**Accessed via Web:**
```
https://erp.tsh.sale/uploads/products/ABC123_20251113_120000.jpg
```

---

## 📊 Stock Data Sync

### Rule #3: Stock Data is Embedded in Products

```yaml
IMPORTANT:
  - Stock levels come WITH product data
  - No separate stock API needed
  - Updated on every product sync
  
STOCK FIELDS IN PRODUCTS:
  - stock_on_hand: Current physical inventory
  - available_stock: Stock available for sale
  - actual_available_stock: Zoho's calculation
  - reorder_level: Minimum stock trigger
```

### Stock Sync Process

**Stock data syncs automatically when syncing products:**

```bash
# This syncs products INCLUDING stock data
python3 run_tds_zoho_sync.py
```

**Stock Fields Retrieved:**

```python
{
    'stock_on_hand': Decimal('50.00'),           # Physical inventory
    'available_stock': Decimal('45.00'),         # Available to sell
    'actual_available_stock': Decimal('45.00'),  # Zoho calculation
    'reorder_level': Decimal('10.00')            # Reorder trigger
}
```

**How Stock is Processed:**

```python
# In ProductProcessor.transform()
'stock_on_hand': safe_decimal(product_data.get('actual_available_stock')),
'available_stock': safe_decimal(product_data.get('available_stock')),
'actual_available_stock': safe_decimal(product_data.get('actual_available_stock')),
'reorder_level': safe_decimal(product_data.get('reorder_level')),
```

**Important:** Uses `safe_decimal()` function to handle invalid values:
- Handles None, empty strings, "None" text
- Returns Decimal('0') for invalid values
- Prevents sync failures from bad data

---

## 🔧 Data Processor Rules

### Safe Decimal Conversion (CRITICAL)

**Problem:** Zoho sometimes returns invalid values for decimal fields

**Solution:** Use `safe_decimal()` helper function

```python
from decimal import Decimal, InvalidOperation

def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Safely convert value to Decimal, handling invalid values"""
    if value is None or value == '' or value == 'None':
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default
```

**Where to Use:**
- ✅ All pricing fields (rate, purchase_rate, cost_price)
- ✅ All stock fields (stock_on_hand, reorder_level)
- ✅ All percentage fields (tax_percentage, discount)
- ✅ Any numeric field from Zoho

**DO NOT use direct Decimal() conversion:**

```python
# ❌ WRONG - Will fail on invalid values
'reorder_level': Decimal(str(product_data.get('reorder_level', 0)))

# ✅ CORRECT - Handles invalid values gracefully
'reorder_level': safe_decimal(product_data.get('reorder_level'))
```

---

## 📝 Sync Script Examples

### Complete Product Sync (with stock)

```python
"""
Location: /home/deploy/TSH_ERP_Ecosystem/run_tds_zoho_sync.py
Purpose: Sync all products + stock from Zoho Books
"""

# Run on production
ssh root@167.71.39.50
cd /home/deploy/TSH_ERP_Ecosystem
DATABASE_URL='postgresql://tsh_admin:changeme@localhost:5432/tsh_erp' \
  python3 run_tds_zoho_sync.py

# Expected output:
# Processed: 2,221
# Success: 2,221
# Failed: 0
# Duration: ~12 seconds
```

### Price List Sync

```python
"""
Location: scripts/sync_pricelists_from_zoho.py
Purpose: Sync price lists and product prices
"""

# Run inside Docker container (has network access)
docker compose exec app python scripts/sync_pricelists_from_zoho.py

# Or with proper DATABASE_URL
DATABASE_URL='postgresql+asyncpg://tsh_admin:changeme@tsh_postgres:5432/tsh_erp' \
  python3 scripts/sync_pricelists_from_zoho.py
```

### Image Download

```python
"""
Location: sync_zoho_images.py
Purpose: Download all product images locally
"""

# Run on production
python3 sync_zoho_images.py

# Check progress
ls -lh uploads/products/ | wc -l  # Count downloaded images
```

---

## 🚫 What NOT to Do

### NEVER Do These:

```python
# ❌ FORBIDDEN - Direct API access
import requests
response = requests.get(
    "https://www.zohoapis.com/books/v3/items",
    headers={"Authorization": f"Zoho-oauthtoken {token}"}
)

# ❌ FORBIDDEN - Bypassing TDS for sync
def sync_products_directly():
    items = zoho_books_api.get_items()
    for item in items:
        db.add(Product(**item))

# ❌ FORBIDDEN - Using wrong decimal conversion
'price': Decimal(str(data.get('price', 0)))  # Will fail on invalid values

# ❌ FORBIDDEN - Skipping image download
# "I'll just use Zoho URLs directly" - NO, download locally

# ❌ FORBIDDEN - Separate stock sync script
# Stock comes with products, don't create separate script
```

### ALWAYS Do These:

```python
# ✅ CORRECT - Use UnifiedZohoClient
from app.tds.integrations.zoho.client import UnifiedZohoClient

async with UnifiedZohoClient() as client:
    items = await client.get_items()

# ✅ CORRECT - Use safe_decimal for numbers
'price': safe_decimal(data.get('price'))

# ✅ CORRECT - Download images during sync
download_product_images(products)

# ✅ CORRECT - Stock syncs with products
# Just run product sync, stock comes automatically
```

---

## 📊 Sync Verification Checklist

After running any sync operation:

```yaml
Database Verification:
□ Check product count: SELECT COUNT(*) FROM products;
□ Check active products: SELECT COUNT(*) FROM products WHERE status = 'active';
□ Check products with stock: SELECT COUNT(*) FROM products WHERE stock_on_hand > 0;
□ Check price lists: SELECT COUNT(*) FROM price_lists;
□ Check customers: SELECT COUNT(*) FROM customers;

Image Verification:
□ Count downloaded images: ls uploads/products/ | wc -l
□ Check image paths in DB: SELECT COUNT(*) FROM products WHERE image_url LIKE '/uploads/%';
□ Test image accessibility: curl https://erp.tsh.sale/uploads/products/[sample_image]

Stock Verification:
□ Products have stock values: SELECT COUNT(*) FROM products WHERE stock_on_hand IS NOT NULL;
□ No NULL reorder levels: SELECT COUNT(*) FROM products WHERE reorder_level IS NULL;
□ Stock values are valid: SELECT MIN(stock_on_hand), MAX(stock_on_hand) FROM products;

Sync Health:
□ Check TDS logs: docker compose logs app --tail 100
□ Check for errors: grep -i error /var/log/tsh_erp/*.log
□ Verify webhook health: curl https://erp.tsh.sale/api/tds/webhooks/health
```

---

## 🔄 Sync Frequency Recommendations

```yaml
Products:
  Manual: On-demand when bulk changes needed
  Webhook: Real-time (configure in Zoho Books)
  Cron: Every 4 hours as backup
  
Stock:
  Included: Syncs with products automatically
  No separate sync needed
  
Images:
  Initial: Download all images once
  Ongoing: Download new product images weekly
  Webhook: Download image on new product creation
  
Price Lists:
  Manual: When creating new price lists
  Webhook: On price changes
  Cron: Daily at 2 AM
  
Customers:
  Webhook: Real-time (best for new customers)
  Cron: Daily for bulk updates
```

---

## 🚨 Emergency Procedures

### If Sync Fails

```yaml
1. Check TDS Logs:
   docker compose logs app --tail 100
   
2. Verify Zoho Authentication:
   python3 regenerate_zoho_token.py
   
3. Check Database Connection:
   docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp -c "SELECT 1;"
   
4. Re-run Sync:
   DATABASE_URL='...' python3 run_tds_zoho_sync.py
   
5. Check Results:
   # Should show: Success: X, Failed: 0
```

### If Images Won't Download

```yaml
1. Check uploads directory permissions:
   ls -la uploads/products/
   chmod 755 uploads/products/
   
2. Test Zoho image URL access:
   curl -I [zoho_image_url]
   
3. Check disk space:
   df -h
   
4. Retry download:
   python3 sync_zoho_images_resume.py
```

### If Stock Data Missing

```yaml
Stock is embedded in products, so:
1. Re-run product sync:
   python3 run_tds_zoho_sync.py
   
2. Verify stock fields populated:
   SELECT COUNT(*) FROM products WHERE stock_on_hand IS NOT NULL;
   
3. Check for NULL reorder levels:
   SELECT COUNT(*) FROM products WHERE reorder_level IS NULL;
   # Should be 0 with safe_decimal fix
```

---

## 📚 Related Documentation

- `DEPLOYMENT_SUCCESS_NOV13_2025.md` - Latest deployment with sync
- `ZOHO_DATA_SYNC_COMPLETE_NOV13_2025.md` - Complete sync results
- `DEPLOYMENT_COMPLETE_2025-11-10.md` - TDS webhook setup
- `TDS_MASTER_ARCHITECTURE.md` - TDS architecture details

---

## ✅ Quick Reference

```yaml
Sync Products + Stock:
  Command: python3 run_tds_zoho_sync.py
  Location: Project root
  Via: TDS Core → UnifiedZohoClient → ProductProcessor
  
Download Images:
  Command: python3 sync_zoho_images.py
  Location: Project root
  Stores: uploads/products/
  
Sync Price Lists:
  Command: python3 scripts/sync_pricelists_from_zoho.py
  Location: scripts/
  Via: TDS Core → PriceListProcessor
  
Verify Sync:
  Health: curl https://erp.tsh.sale/api/tds/webhooks/health
  Stats: curl https://erp.tsh.sale/api/tds/webhooks/stats
  Database: docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp

REMEMBER:
✅ ALL sync through TDS Core
✅ Download ALL images
✅ Stock comes with products
✅ Use safe_decimal for numbers
❌ NEVER bypass TDS
❌ NEVER use direct Zoho API
```

---

**Last Sync:** November 13, 2025  
**Products Synced:** 2,221 (100% success)  
**Stock Data:** Included with products  
**Images Status:** Ready to download  
**System:** Production at https://erp.tsh.sale

---

**END OF ZOHO SYNC RULES**

These rules are MANDATORY and must be followed in ALL future AI sessions.

