# 🚀 Price List Sync - Complete Deployment Guide

**Date:** November 7, 2025
**Version:** 1.0.0 - Production Ready
**Status:** ✅ Ready for Deployment

---

## 📋 Executive Summary

This deployment package enables **complete integration of Zoho Books price lists** into the TSH ERP Ecosystem using the TDS (TSH Data Sync) architecture.

### What's Included:

- ✅ Fixed processor for Zoho Books API field mapping
- ✅ Complete TDS orchestrator integration
- ✅ Automated deployment script
- ✅ Database sync capability
- ✅ Production-ready code

### Expected Outcome:

After deployment, all **6 active price lists** from Zoho Books will be synced to the local database:

1. **Consumer** (IQD) - مستهلك
2. **Retailor** (USD) - قطاعي
3. **Technical IQD** (IQD) - فني - دينار
4. **Technical USD** (USD) - فني - دولار
5. **Wholesale A** (USD) - جملة أ
6. **Wholesale B** (USD) - جملة ب

---

## 🔧 What Was Fixed

### Issue #1: Field Name Mismatch

**Problem:**
Processor was looking for `pricebook_name` field, but Zoho Books API returns `name`.

**Files Affected:**
- `app/tds/integrations/zoho/processors/pricelists.py`
- `app/tds/integrations/zoho/sync.py`

**Solution:**
```python
# ❌ BEFORE (Incorrect)
required_fields = ['pricebook_id', 'pricebook_name']

# ✅ AFTER (Correct)
required_fields = ['pricebook_id', 'name']
```

**Changes Made:**
- Line 73-74 (pricelists.py): Updated validation logic
- Line 105 (pricelists.py): Updated transform logic
- Line 497-498 (sync.py): Updated entity validation
- Lines 767-776 (sync.py): Updated _save_pricelist method

### Issue #2: Production Integration Missing

**Problem:**
Production server didn't have the price list integration in TDS.

**Solution:**
Added complete TDS integration:
- `EntityType.PRICELISTS` enum
- `ENTITY_ENDPOINTS` mapping to Zoho Books `/pricebooks`
- `_save_pricelist()` method with upsert logic
- Validation and transformation pipeline

---

## 📦 Files Changed

### 1. app/tds/integrations/zoho/processors/pricelists.py

**Status:** ✅ FIXED
**Lines Changed:** 73-74, 91-106
**Changes:**
- Updated field names from `pricebook_name` → `name`
- Added comments explaining API structure
- Fixed validation logic

**Key Methods:**
- `validate()` - Validates Zoho price list data
- `transform()` - Transforms to local database format
- `batch_transform_pricelists()` - Batch processing utility

### 2. app/tds/integrations/zoho/sync.py

**Status:** ✅ FIXED
**Lines Changed:** 71, 137, 497-498, 767-776, 861
**Changes:**
- Added `EntityType.PRICELISTS` enum member (line 71)
- Added ENTITY_ENDPOINTS mapping (line 137)
- Fixed validation logic (lines 497-498)
- Fixed _save_pricelist field names (lines 767-776, 861)

**Key Additions:**
```python
# EntityType enum
PRICELISTS = "pricelists"  # Line 71

# ENTITY_ENDPOINTS mapping
EntityType.PRICELISTS: (ZohoAPI.BOOKS, "pricebooks"),  # Line 137

# _save_pricelist method
async def _save_pricelist(self, entity: Dict[str, Any]):
    # Complete upsert logic for price lists
    # Lines 747-865
```

### 3. app/tds/integrations/zoho/processors/__init__.py

**Status:** ✅ COMPLETE
**Changes:** None needed (already correct)
**Exports:**
```python
from .pricelists import PriceListProcessor, batch_transform_pricelists

__all__ = [
    'ProductProcessor',
    'InventoryProcessor',
    'CustomerProcessor',
    'PriceListProcessor',  # ✅ Already exported
    'batch_transform_pricelists',  # ✅ Already exported
]
```

---

## 🚀 Deployment Instructions

### Option 1: Automated Deployment (Recommended)

**Prerequisites:**
- SSH access to production server (root@167.71.39.50)
- Local changes committed and ready

**Steps:**

```bash
# Navigate to project root
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Run deployment script
./scripts/deploy_pricelist_sync.sh
```

**What the script does:**
1. ✅ Verifies local files exist
2. ✅ Backs up production files
3. ✅ Deploys updated files to production
4. ✅ Restarts Docker container
5. ✅ Waits for health check
6. ✅ Runs price list sync
7. ✅ Verifies database has price lists

**Expected Output:**
```
===============================================================================
TSH ERP - Price List Sync Deployment
===============================================================================

Step 1: Verifying local files...
✅ Found: app/tds/integrations/zoho/processors/pricelists.py
✅ Found: app/tds/integrations/zoho/processors/__init__.py
✅ Found: app/tds/integrations/zoho/sync.py

Step 2: Backing up production files...
✅ Backup created at: /home/deploy/backups/pricelist_sync_20251107_200000

Step 3: Deploying files to production...
✅ All files deployed successfully

Step 4: Restarting Docker container...
✅ Container restarted

Step 5: Waiting for application to be healthy...
✅ Application is healthy

Step 6: Running price list sync...
✅ Sync completed successfully

Step 7: Verifying price lists in database...
✅ Found 6 price lists in database

===============================================================================
✨ Deployment Complete!
===============================================================================
```

---

### Option 2: Manual Deployment

If automated script fails, deploy manually:

#### Step 1: Deploy Files

```bash
# From local machine
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Deploy processor
scp app/tds/integrations/zoho/processors/pricelists.py \
    root@167.71.39.50:/home/deploy/TSH_ERP_Ecosystem/app/tds/integrations/zoho/processors/

# Deploy sync orchestrator
scp app/tds/integrations/zoho/sync.py \
    root@167.71.39.50:/home/deploy/TSH_ERP_Ecosystem/app/tds/integrations/zoho/

# Deploy __init__.py (if changed)
scp app/tds/integrations/zoho/processors/__init__.py \
    root@167.71.39.50:/home/deploy/TSH_ERP_Ecosystem/app/tds/integrations/zoho/processors/
```

#### Step 2: Restart Container

```bash
ssh root@167.71.39.50 "docker restart tsh_erp_app"

# Wait for container to be healthy
sleep 20
```

#### Step 3: Run Sync

```bash
# Via API endpoint
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/pricelists \
  -H "Content-Type: application/json" \
  -s | python3 -m json.tool
```

#### Step 4: Verify Database

```bash
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \
  \"SELECT code, name_en, currency, is_active FROM price_lists ORDER BY code;\""
```

---

## ✅ Verification Checklist

After deployment, verify the following:

### 1. Container Health

```bash
ssh root@167.71.39.50 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

**Expected:**
```
NAMES          STATUS
tsh_erp_app    Up X hours (healthy)
```

### 2. Price Lists in Database

```bash
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \
  \"SELECT COUNT(*) as total, COUNT(CASE WHEN is_active THEN 1 END) as active FROM price_lists;\""
```

**Expected:**
```
 total | active
-------+--------
    11 |      6
```

### 3. Price List Details

```bash
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \
  \"SELECT code, name_en, currency, is_active FROM price_lists WHERE is_active = true ORDER BY code;\""
```

**Expected Output:**
```
     code      |    name_en     | currency | is_active
---------------+----------------+----------+-----------
 consumer_iqd  | Consumer       | IQD      | t
 retailer      | Retailor       | USD      | t
 technical_iqd | Technical IQD  | IQD      | t
 technical_usd | Technical USD  | USD      | t
 wholesale_a   | Wholesale A    | USD      | t
 wholesale_b   | Wholesale B    | USD      | t
```

### 4. API Endpoint Test

```bash
# Test sync endpoint
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/pricelists \
  -H "Content-Type: application/json" \
  -s -w "\nHTTP_CODE:%{http_code}\n"
```

**Expected:** HTTP_CODE:200

### 5. Application Logs

```bash
ssh root@167.71.39.50 "docker logs tsh_erp_app --tail 50 | grep -i price"
```

**Look for:**
- ✅ "Synced X price lists"
- ✅ "Created new price list: Consumer"
- ❌ No errors or exceptions

---

## 🔄 Sync Options

### Manual Sync

```bash
# Sync all price lists
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/pricelists \
  -H "Content-Type: application/json"
```

### Programmatic Sync

```python
from app.tds.integrations.zoho.sync import (
    ZohoSyncOrchestrator,
    EntityType,
    SyncConfig,
    SyncMode
)

# Initialize orchestrator
orchestrator = ZohoSyncOrchestrator(zoho_client)

# Sync price lists
config = SyncConfig(
    entity_type=EntityType.PRICELISTS,
    mode=SyncMode.FULL,
    batch_size=200
)

result = await orchestrator.sync_entity(config)
print(f"Synced {result.total_success}/{result.total_processed} price lists")
```

---

## 📊 Expected Results

### Sync Statistics

```json
{
  "success": true,
  "message": "Price lists sync via TDS completed",
  "stats": {
    "total_processed": 11,
    "successful": 6,
    "failed": 0,
    "skipped": 5
  },
  "duration_seconds": 2.5
}
```

**Note:** 5 price lists are skipped because they have `status: "inactive"` in Zoho Books.

### Database Schema

Price lists are stored in the `price_lists` table:

```sql
TABLE price_lists (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    currency currencyenum NOT NULL,  -- USD, IQD, EUR, GBP
    is_default BOOLEAN,
    is_active BOOLEAN NOT NULL,
    zoho_price_list_id VARCHAR(100),
    zoho_last_sync TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);
```

---

## 🚨 Troubleshooting

### Issue: Sync returns 0 price lists

**Diagnosis:**
```bash
# Check Zoho API connectivity
ssh root@167.71.39.50 "docker exec tsh_erp_app python3 -c \"
import os
print('ZOHO_CLIENT_ID:', os.getenv('ZOHO_CLIENT_ID')[:10] + '...')
print('ZOHO_ORG_ID:', os.getenv('ZOHO_ORGANIZATION_ID'))
\""
```

**Solution:**
- Verify Zoho credentials in production `.env` file
- Check Zoho API rate limits

### Issue: Field name errors in logs

**Diagnosis:**
```bash
ssh root@167.71.39.50 "docker logs tsh_erp_app --tail 100 | grep -i 'pricebook_name'"
```

**Solution:**
- Ensure updated `pricelists.py` and `sync.py` are deployed
- Restart container after deployment

### Issue: Database connection errors

**Diagnosis:**
```bash
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c 'SELECT 1;'"
```

**Solution:**
- Verify PostgreSQL container is running
- Check database credentials in application

### Issue: Container won't restart

**Diagnosis:**
```bash
ssh root@167.71.39.50 "docker logs tsh_erp_app --tail 50"
```

**Solution:**
- Check for syntax errors in deployed files
- Restore from backup: `cp $BACKUP_DIR/* $DEPLOY_DIR/`

---

## 🔙 Rollback Procedure

If deployment fails:

### Step 1: Stop Current Container

```bash
ssh root@167.71.39.50 "docker stop tsh_erp_app"
```

### Step 2: Restore Backup

```bash
# Get latest backup directory
LATEST_BACKUP=$(ssh root@167.71.39.50 "ls -td /home/deploy/backups/pricelist_sync_* | head -1")

# Restore files
ssh root@167.71.39.50 "cp $LATEST_BACKUP/* /home/deploy/TSH_ERP_Ecosystem/app/tds/integrations/zoho/"
```

### Step 3: Restart Container

```bash
ssh root@167.71.39.50 "docker start tsh_erp_app"
```

---

## 📚 Related Documentation

- **Main Guide**: `docs/TDS_PRICELIST_INTEGRATION.md`
- **Tronix Manual**: `Tronix.md` (Architecture principles)
- **Product Roadmap**: `Tronix.md` (Multi-Price List System section)
- **Deployment Strategy**: `Tronix.md` (Deployment Strategy section)

---

## ✨ Summary

### What's Ready:

1. ✅ **Code Fixed** - All field name mismatches corrected
2. ✅ **TDS Integration** - Complete orchestrator integration
3. ✅ **Deployment Script** - Automated deployment ready
4. ✅ **Documentation** - Comprehensive guides
5. ✅ **Testing** - Local validation complete

### Deployment Time: ~5 minutes

### Success Criteria:

- ✅ 6 active price lists in database
- ✅ All price lists have correct names and currencies
- ✅ Container remains healthy after deployment
- ✅ Sync API endpoint returns HTTP 200

### Next Phase:

After price list deployment, you can proceed with:
1. **Product Prices Sync** - Sync product-specific prices for each price list
2. **Client App Development** - Build TSH Clients App (Wholesale A/B, Retailer)
3. **Technical App Development** - Build TSH Technical App (Technical IQD/USD)

---

**🚀 Ready to Deploy!**

Run: `./scripts/deploy_pricelist_sync.sh`

---

*End of Deployment Guide*
