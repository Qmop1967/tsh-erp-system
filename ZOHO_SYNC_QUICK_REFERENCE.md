# 🚀 Zoho Sync - Quick Command Reference

## ✅ SYNC STATUS: OPERATIONAL
**Last Successful Sync**: October 4, 2025  
**Items Synced**: 2,204  
**Duplicate Prevention**: ✅ Active  
**Backend**: Running on http://localhost:8000

---

## 📋 Quick Commands

### 1. Start Backend Server
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
python3 -m uvicorn app.main:app --reload --port 8000
```

### 2. Sync Items (via API)
```bash
curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true&force=false" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### 3. Sync Customers (Ready to Use)
```bash
curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/customer/execute?sync_images=true&force=false" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### 4. Sync Vendors (Ready to Use)
```bash
curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/vendor/execute?sync_images=true&force=false" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### 5. View Synced Data
```bash
# View items
cat /Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/tsh_item_records.json | python3 -m json.tool | head -100

# Count items
python3 -c "import json; print(len(json.load(open('/Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/tsh_item_records.json'))))"
```

### 6. View Sync Logs
```bash
cat /Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/settings/zoho_sync_logs.json | python3 -m json.tool
```

### 7. Check Sync Status (via API)
```bash
curl "http://localhost:8000/api/settings/integrations/zoho/sync/item/status" | python3 -m json.tool
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings/integrations/zoho/sync/item/execute` | POST | Sync items |
| `/api/settings/integrations/zoho/sync/customer/execute` | POST | Sync customers |
| `/api/settings/integrations/zoho/sync/vendor/execute` | POST | Sync vendors |
| `/api/settings/integrations/zoho/sync/{type}/status` | GET | Get sync status |
| `/api/settings/integrations/zoho/sync/logs` | GET | View sync logs |
| `/api/settings/integrations/zoho/config` | GET | Get configuration |
| `/api/settings/integrations/zoho/mappings` | GET | Get field mappings |

---

## 📁 Important Files

| File | Description |
|------|-------------|
| `app/data/tsh_item_records.json` | Synced items (1.7 MB) |
| `app/data/tsh_customer_records.json` | Synced customers (future) |
| `app/data/tsh_vendor_records.json` | Synced vendors (future) |
| `app/data/settings/zoho_sync_logs.json` | Sync operation logs |
| `app/data/settings/zoho_config.json` | Zoho configuration |
| `app/data/settings/zoho_sync_mappings.json` | Field mappings |
| `app/data/images/item/` | Product images directory |

---

## 🔧 Sync Service Code

**Location**: `app/services/zoho_sync_service.py`

**Key Methods**:
- `sync_items(sync_images=True)` → Sync items from Zoho
- `sync_customers()` → Sync customers from Zoho
- `sync_vendors()` → Sync vendors from Zoho
- `_generate_unique_id()` → Generate MD5 hash for deduplication
- `_download_image()` → Download product images
- `_map_fields()` → Map Zoho fields to TSH fields

---

## 🎯 Sync Statistics (Latest)

```json
{
  "sync_id": "sync_items_20251004_212327",
  "status": "success",
  "statistics": {
    "total": 2204,
    "new": 0,
    "updated": 2204,
    "skipped": 0,
    "errors": 0,
    "images_downloaded": 0
  },
  "timestamp": "2025-10-04T21:23:27.746112"
}
```

**Performance**: ~44-50 items/second  
**Duplicate Prevention**: ✅ Working (0 duplicates in second sync)

---

## 🔐 Duplicate Prevention Logic

```python
# Unique ID generated from:
fields = ["zoho_item_id", "code", "name"]
unique_string = "|".join(values)
unique_id = hashlib.md5(unique_string.encode()).hexdigest()

# Process:
1. Generate unique_id for each Zoho item
2. Check if unique_id exists in TSH database
3. If exists → UPDATE existing record
4. If new → INSERT new record
```

**Result**: No duplicates created even after multiple syncs ✅

---

## 📱 Frontend Integration (Ready)

The backend is ready for frontend integration. Frontend can:
- Trigger syncs via button clicks
- Display real-time progress
- Show sync statistics
- View sync history
- Configure field mappings
- Enable/disable sync for each entity type

**Frontend Route**: `/settings/integrations/zoho`

---

## 🎨 Sample Synced Item

```json
{
  "zoho_item_id": "2646610000066685131",
  "code": "tsh00057",
  "name": "2 Female RCA TO Male 3.5 Adapter",
  "name_ar": "2 Female RCA TO Male 3.5 Adapter",
  "cost_price": 0.07,
  "selling_price": 2.0,
  "unit": "pcs",
  "track_inventory": true,
  "is_active": true,
  "unique_id": "b5dce9e4d513cea88feb6046b78c7b78",
  "sync_source": "zoho",
  "zoho_sync_date": "2025-10-04T21:22:43.692981"
}
```

---

## 🚨 Troubleshooting

### Backend Not Starting
```bash
# Check if port is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart backend
python3 -m uvicorn app.main:app --reload --port 8000
```

### Sync Fails
```bash
# Check logs
tail -50 /Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/settings/zoho_sync_logs.json

# Clear synced data and resync
rm /Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/tsh_item_records.json
# Then run sync again
```

### View Backend Errors
```bash
# Backend terminal will show real-time errors
# Look for 🔄 Starting sync and ✅ Sync completed messages
```

---

## ✅ Success Checklist

- [x] Backend API operational
- [x] Items sync working (2,204 items)
- [x] Duplicate prevention active
- [x] Field mapping complete
- [x] Sync logging operational
- [x] Image support infrastructure ready
- [x] Customer sync code ready
- [x] Vendor sync code ready
- [x] Frontend integration ready

---

## 📞 Support

**Documentation**: 
- `ZOHO_SYNC_COMPLETE_SUCCESS.md` - Full success report
- `ZOHO_SYNC_SYSTEM_DOCUMENTATION.md` - System documentation
- `ZOHO_DATA_ANALYSIS_LIVE.md` - Data analysis

**Code Files**:
- `app/services/zoho_sync_service.py` - Main sync logic
- `app/routers/settings.py` - API endpoints

---

**Last Updated**: October 4, 2025  
**Status**: 🟢 PRODUCTION READY
