# TDS Stock Sync - Quick Start Guide

## 🚀 Quick Commands

### Via API

```bash
# Full sync
curl -X POST "https://erp.tsh.sale/api/bff/tds/sync/stock?batch_size=200&active_only=true"

# Get statistics
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats"

# Sync specific items
curl -X POST "https://erp.tsh.sale/api/bff/tds/sync/stock/specific?item_ids=123&item_ids=456"
```

### Via Command Line

```bash
# Full sync
python scripts/tds_sync_stock.py

# Dry run (preview)
python scripts/tds_sync_stock.py --dry-run

# Only items with stock
python scripts/tds_sync_stock.py --with-stock-only

# Verbose mode
python scripts/tds_sync_stock.py --verbose
```

---

## 📊 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/bff/tds/sync/stock` | POST | Trigger stock sync |
| `/api/bff/tds/sync/stock/stats` | GET | Get sync statistics |
| `/api/bff/tds/sync/stock/specific` | POST | Sync specific items |
| `/api/bff/tds/dashboard` | GET | TDS dashboard |
| `/api/bff/tds/runs` | GET | Sync history |

---

## ⚙️ Configuration Options

### API Parameters

```
batch_size       = 50-200    (items per API call, default: 200)
db_batch_size    = 10-500    (items per DB batch, default: 100)
active_only      = true/false (default: true)
with_stock_only  = true/false (default: false)
```

### CLI Arguments

```
--batch-size N        Items per Zoho API call
--db-batch-size N     Items per database batch
--active-only         Only sync active items
--with-stock-only     Only sync items with stock > 0
--dry-run             Preview without changes
--verbose             Enable verbose logging
```

---

## 📈 Performance

| Items | API Calls | Duration | Items/Sec |
|-------|-----------|----------|-----------|
| 500   | 3         | 15-20s   | 25-33     |
| 1,500 | 8         | 30-60s   | 25-50     |
| 5,000 | 25        | 2-4 min  | 20-40     |

---

## 🔍 Monitoring

```bash
# Check last sync
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats"

# View sync history
curl "https://erp.tsh.sale/api/bff/tds/runs?entity_type=product&limit=10"

# Check TDS health
curl "https://erp.tsh.sale/api/bff/tds/health"
```

---

## 📅 Schedule Sync

### Using Cron (Daily at 2 AM)

```bash
crontab -e
# Add this line:
0 2 * * * /usr/bin/python3 /path/to/scripts/tds_sync_stock.py >> /var/log/tds_sync.log 2>&1
```

### Using Systemd Timer

```bash
sudo systemctl enable tds-stock-sync.timer
sudo systemctl start tds-stock-sync.timer
```

---

## 🛠️ Troubleshooting

### Check Sync Status
```bash
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats"
```

### View Logs
```bash
tail -f logs/tds_stock_sync_*.log
```

### Database Check
```sql
SELECT COUNT(*), MAX(last_synced) FROM products;
```

---

## 📚 Full Documentation

- **Complete Guide**: `TDS_STOCK_SYNC_GUIDE.md`
- **Implementation Details**: `TDS_STOCK_SYNC_IMPLEMENTATION_SUMMARY.md`
- **API Docs**: `https://erp.tsh.sale/docs`

---

## ✅ Quick Test

```bash
# 1. Dry run to preview
python scripts/tds_sync_stock.py --dry-run

# 2. Run actual sync
python scripts/tds_sync_stock.py

# 3. Check results
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats"
```

---

**Status**: Production Ready ✅
**Version**: 2.0.0
**Updated**: November 6, 2025
