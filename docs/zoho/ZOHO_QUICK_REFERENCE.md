# 🎯 ZOHO MAPPING CONTROL - QUICK REFERENCE CARD

## 🚀 INSTANT ACCESS

**Frontend**: http://localhost:5173/settings/integrations/zoho  
**Backend**: http://localhost:8000/api/settings  
**API Docs**: http://localhost:8000/docs

---

## 📊 VIEW ALL MAPPINGS

### Browser (UI)
```
http://localhost:5173/settings/integrations/zoho
```

### Command Line (API)
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings | python3 -m json.tool
```

### Python
```python
import requests
response = requests.get('http://localhost:8000/api/settings/integrations/zoho/sync/mappings')
mappings = response.json()['mappings']
```

---

## 🔍 VIEW SPECIFIC ENTITY MAPPING

### Items (Products/Inventory)
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings/item | python3 -m json.tool
```

### Customers (Contacts)
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings/customer | python3 -m json.tool
```

### Vendors (Suppliers)
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings/vendor | python3 -m json.tool
```

---

## ⚙️ CONTROL SYNC OPERATIONS

### Enable/Disable Entity Sync
```bash
# Enable customer sync
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/mappings/customer \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Disable vendor sync
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/mappings/vendor \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Execute Sync
```bash
# Sync items
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/item/execute

# Sync customers
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/customer/execute

# Full sync all entities
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/all
```

---

## 📈 MONITOR OPERATIONS

### View Statistics
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/statistics | python3 -m json.tool
```

### View Logs
```bash
# Get last 20 logs
curl http://localhost:8000/api/settings/integrations/zoho/sync/logs?limit=20 | python3 -m json.tool

# Filter by status
curl "http://localhost:8000/api/settings/integrations/zoho/sync/logs?status=error&limit=10" | python3 -m json.tool
```

### Check Entity Status
```bash
curl http://localhost:8000/api/settings/integrations/zoho/sync/item/status | python3 -m json.tool
```

---

## 🗺️ CURRENT MAPPINGS

### Items (8 fields)
- item_id → zoho_item_id
- name → name
- sku → sku (uppercase)
- description → description
- rate → unit_price
- purchase_rate → cost_price
- stock_on_hand → quantity_on_hand
- status → status

### Customers (5 fields)
- contact_id → zoho_contact_id
- contact_name → name
- email → email
- phone → phone
- status → status

### Vendors (4 fields)
- vendor_id → zoho_vendor_id
- vendor_name → name
- email → email
- phone → phone

---

## 🧪 TEST THE SYSTEM

```bash
python test_zoho_sync_system.py
```

Tests all:
- Configuration endpoints
- Mapping endpoints  
- Sync control
- Operations
- Monitoring

---

## 📁 CONFIGURATION FILES

```
app/data/settings/
├── zoho_config.json          # OAuth credentials
├── zoho_sync_mappings.json   # Field mappings
├── zoho_sync_control.json    # Sync settings
└── zoho_sync_logs.json       # Operation logs
```

---

## 🎛️ FRONTEND CONTROLS

### On Zoho Integration Page:
- ✅ Enable/Disable toggle for Zoho integration
- ✅ OAuth credentials form (Client ID, Secret, Token, Org ID)
- ✅ Module toggles (CRM, Books, Inventory, Invoice)
- ✅ "Sync Now" button for each module
- ✅ Last sync timestamps
- ✅ "Export All Zoho Data" button
- ✅ "Full Sync All Modules" button

---

## 📖 DOCUMENTATION

- `ZOHO_MAPPING_CONTROL_COMPLETE.md` - Detailed reference
- `ZOHO_MAPPING_CONTROL_SUMMARY.md` - This guide
- `ZOHO_SYNC_SYSTEM_DOCUMENTATION.md` - Full system docs
- `ZOHO_SYNC_QUICK_START.md` - Quick start guide

---

## ✅ QUICK VERIFICATION

```bash
# 1. Check if backend is running
curl http://localhost:8000/health

# 2. View all mappings
curl http://localhost:8000/api/settings/integrations/zoho/sync/mappings

# 3. Check configuration
curl http://localhost:8000/api/settings/integrations/zoho

# 4. Open frontend
open http://localhost:5173/settings/integrations/zoho
```

---

## 🎯 ONE-LINE COMMANDS

```bash
# View everything
curl -s http://localhost:8000/api/settings/integrations/zoho/sync/mappings | python3 -m json.tool

# Sync everything
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/all

# View all logs
curl -s http://localhost:8000/api/settings/integrations/zoho/sync/logs | python3 -m json.tool

# View stats
curl -s http://localhost:8000/api/settings/integrations/zoho/sync/statistics | python3 -m json.tool
```

---

## 🚨 TROUBLESHOOTING

### Backend not responding?
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
uvicorn app.main:app --reload
```

### Frontend not loading?
```bash
cd frontend
npm run dev
```

### Clear logs?
```bash
curl -X POST http://localhost:8000/api/settings/integrations/zoho/sync/logs/clear
```

---

**Status**: ✅ OPERATIONAL  
**Last Updated**: October 4, 2025  
**Quick Link**: http://localhost:5173/settings/integrations/zoho
