# 📋 Scripts Migration Guide - TDS Architecture

**Date:** January 2025  
**Status:** Active Migration  
**Priority:** HIGH - Architectural Compliance

---

## 🎯 Overview

This guide documents the migration of standalone scripts to use TDS (TSH Data Sync) architecture for centralized monitoring, event tracking, and unified integration patterns.

---

## ✅ Migrated Scripts (Use These)

### Image Download

**✅ NEW: `download_zoho_images_tds.py`**
- Uses: `TDSImageSyncHandler`
- Features: Event tracking, monitoring, TDS integration
- Status: **PRODUCTION READY**

**Usage:**
```bash
# Download all images for active products
python3 scripts/download_zoho_images_tds.py

# Only products with stock
python3 scripts/download_zoho_images_tds.py --with-stock

# Force re-download all images
python3 scripts/download_zoho_images_tds.py --force

# Test with limited images
python3 scripts/download_zoho_images_tds.py --limit 10
```

### Stock Sync

**✅ NEW: `unified_stock_sync.py`**
- Uses: `UnifiedStockSyncService`
- Features: Event tracking, monitoring, TDS integration
- Status: **PRODUCTION READY**

**Usage:**
```bash
# Full sync
python3 scripts/unified_stock_sync.py --mode full

# Incremental sync
python3 scripts/unified_stock_sync.py --mode incremental

# Active items only
python3 scripts/unified_stock_sync.py --active-only

# Show statistics
python3 scripts/unified_stock_sync.py --stats
```

---

## ⚠️ Deprecated Scripts (DO NOT USE)

### Image Download Scripts

#### ❌ `download_zoho_images_paginated.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `zoho_token_manager` instead of TDS
- **Migration:** Use `download_zoho_images_tds.py`
- **Action:** Archive after migration complete

#### ❌ `download_zoho_images.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `zoho_token_manager` instead of TDS
- **Migration:** Use `download_zoho_images_tds.py`
- **Action:** Archive after migration complete

#### ❌ `import_zoho_images.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `zoho_service` instead of TDS
- **Migration:** Use `download_zoho_images_tds.py`
- **Action:** Archive after migration complete

### Stock Sync Scripts

#### ❌ `sync_stock_from_zoho_inventory.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `zoho_token_manager` and `zoho_rate_limiter`
- **Migration:** Use `unified_stock_sync.py`
- **Action:** Archive after migration complete

#### ❌ `sync_zoho_stock.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `ZohoStockSyncService`
- **Migration:** Use `unified_stock_sync.py`
- **Action:** Archive after migration complete

#### ❌ `tds_sync_stock.py`
- **Status:** DEPRECATED
- **Reason:** Uses old `ZohoStockSyncService` (despite TDS name)
- **Migration:** Use `unified_stock_sync.py`
- **Action:** Archive after migration complete

---

## 📝 Migration Checklist

### For Image Download:
- [x] Created `download_zoho_images_tds.py` ✅
- [ ] Updated cron jobs to use new script
- [ ] Tested new script in production
- [ ] Archived old scripts
- [ ] Updated documentation

### For Stock Sync:
- [x] Created `unified_stock_sync.py` ✅
- [ ] Updated cron jobs to use new script
- [ ] Tested new script in production
- [ ] Archived old scripts
- [ ] Updated documentation

---

## 🔄 Migration Steps

### Step 1: Update Cron Jobs

**Before:**
```bash
# Old cron job
0 3 * * * cd /home/deploy/TSH_ERP_Ecosystem && python3 scripts/download_zoho_images_paginated.py
```

**After:**
```bash
# New cron job using TDS
0 3 * * * cd /home/deploy/TSH_ERP_Ecosystem && python3 scripts/download_zoho_images_tds.py
```

### Step 2: Test New Scripts

```bash
# Test image download (limited)
python3 scripts/download_zoho_images_tds.py --limit 10

# Test stock sync
python3 scripts/unified_stock_sync.py --mode incremental --stats
```

### Step 3: Archive Old Scripts

```bash
# Move to archive
mkdir -p scripts/archived/deprecated_$(date +%Y%m%d)
mv scripts/download_zoho_images_paginated.py scripts/archived/deprecated_$(date +%Y%m%d)/
mv scripts/download_zoho_images.py scripts/archived/deprecated_$(date +%Y%m%d)/
mv scripts/sync_stock_from_zoho_inventory.py scripts/archived/deprecated_$(date +%Y%m%d)/
mv scripts/sync_zoho_stock.py scripts/archived/deprecated_$(date +%Y%m%d)/
mv scripts/tds_sync_stock.py scripts/archived/deprecated_$(date +%Y%m%d)/
```

### Step 4: Update Documentation

- Update this README
- Update deployment scripts
- Update monitoring dashboards
- Update team documentation

---

## 🎯 Benefits of TDS Migration

### Before (Old Scripts):
- ❌ No event tracking
- ❌ No centralized monitoring
- ❌ Manual error handling
- ❌ Duplicate authentication logic
- ❌ Hard to debug
- ❌ No statistics tracking

### After (TDS Scripts):
- ✅ Event tracking for all operations
- ✅ Centralized monitoring dashboard
- ✅ Automatic error handling and retries
- ✅ Unified authentication
- ✅ Easy debugging with event logs
- ✅ Comprehensive statistics

---

## 📊 Script Comparison

| Feature | Old Scripts | TDS Scripts |
|---------|-------------|-------------|
| **Event Tracking** | ❌ No | ✅ Yes |
| **Monitoring** | ❌ Manual | ✅ Automatic |
| **Error Handling** | ⚠️ Basic | ✅ Comprehensive |
| **Statistics** | ⚠️ Limited | ✅ Detailed |
| **Authentication** | ⚠️ Manual | ✅ Automatic |
| **Rate Limiting** | ⚠️ Manual | ✅ Automatic |
| **Retry Logic** | ❌ No | ✅ Yes |
| **Logging** | ⚠️ Basic | ✅ Structured |

---

## 🚀 Quick Start

### Image Download

```bash
# Basic usage
python3 scripts/download_zoho_images_tds.py

# With options
python3 scripts/download_zoho_images_tds.py \
    --active-only \
    --with-stock \
    --limit 100
```

### Stock Sync

```bash
# Incremental sync (recommended)
python3 scripts/unified_stock_sync.py --mode incremental

# Full sync
python3 scripts/unified_stock_sync.py --mode full

# With options
python3 scripts/unified_stock_sync.py \
    --mode incremental \
    --active-only \
    --batch-size 200
```

---

## 📚 References

- **TDS Architecture:** `app/tds/`
- **TDS Image Sync:** `app/tds/integrations/zoho/image_sync.py`
- **TDS Stock Sync:** `app/tds/integrations/zoho/stock_sync.py`
- **Tronix Guide:** `Tronix.md`
- **Enhancement Analysis:** `CODEBASE_ENHANCEMENT_ANALYSIS.md`

---

## ❓ FAQ

### Q: Can I still use old scripts?
**A:** No, they are deprecated and will be removed. Use TDS scripts instead.

### Q: What if I need the old functionality?
**A:** All functionality is available in TDS scripts with better features.

### Q: How do I migrate my cron jobs?
**A:** Update cron jobs to use new script names (see Migration Steps above).

### Q: Will old scripts be removed?
**A:** Yes, after migration is complete and tested, old scripts will be archived.

---

**Last Updated:** January 2025  
**Status:** Active Migration  
**Owner:** TSH ERP Team

