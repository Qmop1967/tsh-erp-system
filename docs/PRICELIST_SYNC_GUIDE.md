# Price List Sync from Zoho Books - Complete Guide

**Author:** Claude Code (Senior Software Engineer AI)
**Date:** November 7, 2025
**Version:** 1.0.0
**Status:** ✅ Ready for Testing

---

## 📋 Overview

This guide documents the **complete price list synchronization system** from Zoho Books to TSH ERP, following TDS architecture principles and senior engineering standards.

### Business Context

TSH operates with **6 distinct price lists** synchronized from Zoho Books:

| Price List | Currency | Target Audience | Zoho Books Name |
|------------|----------|-----------------|-----------------|
| **Wholesale A** | USD | Bulk buyers (Tier 1) | Wholesale A |
| **Wholesale B** | USD | Bulk buyers (Tier 2) | Wholesale B |
| **Retailer** | USD | Retail businesses | Retailer |
| **Technical IQD** | IQD | Technical professionals | Technical IQD |
| **Technical USD** | USD | Technical professionals | Technical USD |
| **Consumer IQD** | IQD | End consumers | Consumer IQD |

---

## 🏗️ Architecture

### Components Created

#### 1. **TDS Price List Processor**
**Location:** `app/tds/integrations/zoho/processors/pricelists.py`

**Responsibilities:**
- Validates Zoho Books price list data
- Transforms Zoho format to TSH ERP format
- Maps English names to Arabic equivalents
- Determines price list codes (wholesale_a, retailer, etc.)

**Key Methods:**
```python
- validate(pricelist_data) → bool
- transform(pricelist_data) → Dict
- transform_price_item(item_data, pricelist_id, product_id) → Dict
- batch_transform_pricelists(pricelists) → List[Dict]
```

#### 2. **Price List Sync Script**
**Location:** `scripts/sync_pricelists_from_zoho.py`

**Features:**
- Uses UnifiedZohoClient (TDS component)
- Implements Books API priority pattern
- Proper error handling and logging
- Upsert logic (insert new, update existing)
- Comprehensive statistics reporting

**Workflow:**
```
1. Fetch price lists from Zoho Books API
2. Validate and transform data using PriceListProcessor
3. Upsert to price_lists table
4. Log statistics and results
```

---

## 🚀 Usage

### Prerequisites

1. **Database tables** exist (already created):
   - `price_lists`
   - `product_prices`
   - `price_list_items`

2. **Environment variables** configured:
   - `ZOHO_CLIENT_ID`
   - `ZOHO_CLIENT_SECRET`
   - `ZOHO_REFRESH_TOKEN`
   - `ZOHO_ORGANIZATION_ID`

3. **Dependencies** installed:
   - All packages in `requirements.txt`

### Running the Sync

#### Option 1: Direct Execution (Local)

```bash
# Navigate to project root
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Activate virtual environment (if applicable)
source .venv/bin/activate

# Run the sync script
python scripts/sync_pricelists_from_zoho.py
```

#### Option 2: Production Server

```bash
# SSH to production server
ssh root@167.71.39.50

# Navigate to project directory
cd /home/deploy/TSH_ERP_Ecosystem

# Run sync in Docker container
docker exec -it tsh_erp_app python scripts/sync_pricelists_from_zoho.py
```

#### Option 3: Via API Endpoint (Future Integration)

Once integrated into TDS orchestrator:

```bash
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/pricelists \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Expected Output

### Successful Sync

```
======================================================================
🚀 Starting Price List Sync from Zoho Books
======================================================================
📘 Fetching price lists from Zoho Books...
✅ Found 6 price lists in Zoho Books
🔄 Transforming price list data...
✅ Batch transformed 6/6 price lists
💾 Saving price lists to database...
✅ Created new price list: Wholesale A (wholesale_a)
✅ Created new price list: Wholesale B (wholesale_b)
✅ Created new price list: Retailer (retailer)
✅ Created new price list: Technical IQD (technical_iqd)
✅ Created new price list: Technical USD (technical_usd)
✅ Created new price list: Consumer IQD (consumer_iqd)
======================================================================
✅ Price List Sync Complete
   Total: 6
   Successful: 6
   Failed: 0
   Duration: 3.45 seconds
======================================================================

======================================================================
📊 SYNC STATISTICS
======================================================================
Total Price Lists: 6
Successfully Synced: 6
Failed: 0
Duration: 3.45 seconds
======================================================================
```

---

## 🔍 Verification

### Step 1: Check Database

```bash
# SSH to production
ssh root@167.71.39.50

# Query price lists
docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c "
SELECT
    id,
    code,
    name_en,
    name_ar,
    currency,
    is_active,
    zoho_price_list_id,
    zoho_last_sync
FROM price_lists
ORDER BY code;
"
```

**Expected Result:**
```
 id |      code      |    name_en    |   name_ar  | currency | is_active | zoho_price_list_id |   zoho_last_sync
----+----------------+---------------+------------+----------+-----------+--------------------+--------------------
  1 | consumer_iqd   | Consumer IQD  | مستهلك    | IQD      | t         | 123456789          | 2025-11-07 14:30:00
  2 | retailer       | Retailer      | قطاعي     | USD      | t         | 123456790          | 2025-11-07 14:30:00
  3 | technical_iqd  | Technical IQD | فني       | IQD      | t         | 123456791          | 2025-11-07 14:30:00
  4 | technical_usd  | Technical USD | فني       | USD      | t         | 123456792          | 2025-11-07 14:30:00
  5 | wholesale_a    | Wholesale A   | جملة أ    | USD      | t         | 123456793          | 2025-11-07 14:30:00
  6 | wholesale_b    | Wholesale B   | جملة ب    | USD      | t         | 123456794          | 2025-11-07 14:30:00
```

### Step 2: Check Logs

```bash
# View sync logs
tail -f logs/pricelist_sync.log
```

### Step 3: Test API (If Available)

```bash
# Get all price lists
curl https://erp.tsh.sale/api/multi-price-system/price-lists

# Expected: Should return the synced price lists
```

---

## 🔧 Troubleshooting

### Issue: No price lists found in Zoho

**Symptom:**
```
⚠️ No price lists found in Zoho Books
```

**Solution:**
1. Verify price lists exist in Zoho Books web interface
2. Check if API endpoint is correct (`pricebooks`)
3. Verify Zoho credentials have proper permissions

### Issue: Authentication failed

**Symptom:**
```
❌ Failed to fetch price lists from Zoho: 401 Unauthorized
```

**Solution:**
1. Check environment variables are set correctly
2. Refresh Zoho OAuth tokens
3. Verify organization ID is correct

### Issue: Database connection error

**Symptom:**
```
❌ Failed to save price list: connection refused
```

**Solution:**
1. Verify database is running: `docker ps | grep postgres`
2. Check database credentials in .env file
3. Ensure database exists: `SELECT datname FROM pg_database;`

### Issue: Duplicate key error

**Symptom:**
```
ERROR: duplicate key value violates unique constraint "ix_price_lists_code"
```

**Solution:**
1. This indicates price list already exists with same code
2. The script will update existing records (upsert logic)
3. If problem persists, check for data inconsistency

---

## 📈 Next Steps

### Phase 1: Complete (✅)
- ✅ Created TDS price list processor
- ✅ Created sync script with TDS components
- ✅ Implemented upsert logic
- ✅ Added comprehensive logging

### Phase 2: Testing (In Progress)
- [ ] Run sync on production server
- [ ] Verify all 6 price lists synced correctly
- [ ] Check data accuracy (names, currencies, codes)
- [ ] Validate zoho_price_list_id mappings

### Phase 3: Integration (Planned)
- [ ] Integrate into TDS orchestrator (`app/tds/integrations/zoho/sync.py`)
- [ ] Add to bulk sync endpoint (`/api/zoho/bulk-sync/pricelists`)
- [ ] Implement webhook support for real-time updates
- [ ] Add to scheduled sync jobs

### Phase 4: Product Prices (Planned)
- [ ] Fetch product-specific prices from each price list
- [ ] Sync to `product_prices` table
- [ ] Link prices to existing products
- [ ] Handle price updates and history

---

## 📝 Technical Notes

### Zoho Books API

**Endpoint:** `GET https://www.zohoapis.com/books/v3/pricebooks`

**Rate Limit:** 100 requests/minute

**Response Structure:**
```json
{
  "code": 0,
  "message": "success",
  "pricebooks": [
    {
      "pricebook_id": "123456789",
      "pricebook_name": "Wholesale A",
      "description": "High volume clients",
      "currency_code": "USD",
      "currency_symbol": "$",
      "is_default": false,
      "status": "active"
    }
  ]
}
```

### Database Schema

**Table:** `price_lists`

**Key Columns:**
- `id` - Primary key (auto-increment)
- `code` - Unique code (wholesale_a, retailer, etc.)
- `zoho_price_list_id` - Zoho Books pricebook ID
- `zoho_last_sync` - Last sync timestamp
- `name_en` / `name_ar` - Bilingual names
- `currency` - USD or IQD
- `is_active` - Status flag

### Code Quality

✅ **Follows Tronix.md principles:**
- Uses TDS architecture (all Zoho code in app/tds/)
- Comprehensive docstrings and type hints
- Proper error handling and logging
- Clean, maintainable code
- Arabic language support

---

## 👥 Support

**For issues or questions:**
1. Check logs: `logs/pricelist_sync.log`
2. Review Tronix.md: Section on TDS integration
3. Contact: TSH ERP Team

---

**🚀 Ready to sync price lists from Zoho Books to TSH ERP!**

*End of Price List Sync Guide*
