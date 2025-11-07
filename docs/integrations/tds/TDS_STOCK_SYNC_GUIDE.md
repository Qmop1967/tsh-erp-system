# TDS Stock Sync - Pagination Batch Processing Guide

## Overview

The TDS (TSH Data Sync) Stock Sync feature enables efficient synchronization of item stock quantities from Zoho Books/Inventory to your local database using **pagination batch processing**. This ensures optimal performance with minimal API calls and efficient database operations.

## Features

- **Pagination Support**: Fetches items in batches of up to 200 items per API call
- **Bulk Database Updates**: Efficient UPSERT operations using PostgreSQL's `ON CONFLICT`
- **TDS Integration**: Fully integrated with TDS event system for monitoring
- **Progress Tracking**: Real-time progress updates and statistics
- **Flexible Filtering**: Sync only active items, items with stock, or all items
- **Error Handling**: Automatic retry with detailed error tracking
- **Dry Run Mode**: Preview sync operations without making changes

## Architecture

```
┌─────────────────┐
│  Zoho Books/    │
│  Inventory API  │
└────────┬────────┘
         │ Pagination (200 items/call)
         ▼
┌─────────────────┐
│  TDS Stock      │
│  Sync Service   │
└────────┬────────┘
         │ Batch Processing
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  Products Table │
└─────────────────┘
```

## API Endpoints

### 1. Trigger Stock Sync

**POST** `/api/bff/tds/sync/stock`

Triggers a full stock synchronization from Zoho.

**Query Parameters:**
- `batch_size` (int, default: 200): Items per Zoho API call (50-200)
- `active_only` (bool, default: true): Only sync active items
- `with_stock_only` (bool, default: false): Only sync items with stock > 0
- `db_batch_size` (int, default: 100): Items per database batch (10-500)

**Example Request:**
```bash
curl -X POST "https://erp.tsh.sale/api/bff/tds/sync/stock?batch_size=200&active_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**
```json
{
  "success": true,
  "stats": {
    "total_items_from_zoho": 1523,
    "api_calls_made": 8,
    "products_updated": 1450,
    "products_created": 73,
    "products_skipped": 0,
    "errors": []
  },
  "duration_seconds": 45.32,
  "sync_run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Get Stock Sync Statistics

**GET** `/api/bff/tds/sync/stock/stats`

Retrieves current stock sync statistics from the database.

**Example Response:**
```json
{
  "total_products": 1523,
  "with_zoho_id": 1523,
  "with_stock": 1245,
  "total_stock_quantity": 45678,
  "last_sync_time": "2025-11-06T10:30:00Z",
  "stale_products": 12
}
```

### 3. Sync Specific Items

**POST** `/api/bff/tds/sync/stock/specific`

Syncs stock for specific Zoho item IDs (useful for targeted updates).

**Query Parameters:**
- `item_ids` (list of strings): Zoho item IDs to sync

**Example Request:**
```bash
curl -X POST "https://erp.tsh.sale/api/bff/tds/sync/stock/specific?item_ids=123456&item_ids=789012" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Command Line Script

### Installation

Make the script executable:
```bash
chmod +x scripts/tds_sync_stock.py
```

### Usage

```bash
python scripts/tds_sync_stock.py [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--batch-size N` | Items per Zoho API call | 200 |
| `--db-batch-size N` | Items per database batch | 100 |
| `--active-only` | Only sync active items | True |
| `--with-stock-only` | Only sync items with stock > 0 | False |
| `--dry-run` | Preview without changes | False |
| `--verbose` | Enable verbose logging | False |

### Examples

**Full sync with default settings:**
```bash
python scripts/tds_sync_stock.py
```

**Sync only items with stock:**
```bash
python scripts/tds_sync_stock.py --with-stock-only
```

**Custom batch sizes:**
```bash
python scripts/tds_sync_stock.py --batch-size 100 --db-batch-size 50
```

**Dry run to preview:**
```bash
python scripts/tds_sync_stock.py --dry-run
```

**Verbose logging:**
```bash
python scripts/tds_sync_stock.py --verbose
```

## Database Schema

The sync updates the `products` table with the following fields:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    zoho_item_id VARCHAR(255) UNIQUE,
    sku VARCHAR(255),
    name VARCHAR(500),
    description TEXT,
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    is_active BOOLEAN,
    last_synced TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Performance Optimization

### API Call Efficiency

- **Maximum batch size**: 200 items per call (Zoho API limit)
- **Average items per call**: ~190-200 items
- **Example**: 1,500 items = 8 API calls (vs 1,500 individual calls)

### Database Efficiency

- **Bulk UPSERT**: Uses PostgreSQL's `ON CONFLICT` for efficient updates
- **Batch processing**: Updates multiple items per transaction
- **Index optimization**: Primary index on `zoho_item_id`

### Performance Metrics

For a typical sync of 1,500 items:
- API Calls: 8
- Database Operations: 15 batches (100 items each)
- Total Duration: 30-60 seconds
- Items/Second: 25-50

## Monitoring & Tracking

### TDS Integration

Stock sync is fully integrated with the TDS (TSH Data Sync) system:

1. **Sync Runs**: Each sync creates a TDS sync run record
2. **Event Bus**: Publishes events for monitoring
3. **Progress Tracking**: Real-time progress updates
4. **Error Tracking**: Detailed error logs and alerts

### View Sync History

**GET** `/api/bff/tds/runs?entity_type=product`

```json
{
  "runs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "zoho",
      "entity_type": "product",
      "status": "completed",
      "progress_percentage": 100,
      "processed": 1523,
      "failed": 0,
      "started_at": "2025-11-06T10:00:00Z",
      "duration": "45s"
    }
  ]
}
```

## Scheduled Sync

### Using Cron

Add to crontab for daily sync at 2 AM:

```bash
crontab -e

# Add this line
0 2 * * * /path/to/python /path/to/scripts/tds_sync_stock.py >> /path/to/logs/stock_sync_cron.log 2>&1
```

### Using Systemd Timer

Create `/etc/systemd/system/tds-stock-sync.service`:

```ini
[Unit]
Description=TDS Stock Sync Service
After=network.target

[Service]
Type=oneshot
User=tsh
WorkingDirectory=/path/to/TSH_ERP_Ecosystem
ExecStart=/usr/bin/python3 scripts/tds_sync_stock.py
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/tds-stock-sync.timer`:

```ini
[Unit]
Description=TDS Stock Sync Timer
Requires=tds-stock-sync.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable tds-stock-sync.timer
sudo systemctl start tds-stock-sync.timer
```

## Error Handling

### Common Errors

**1. Zoho API Rate Limit**
```
Error: Rate limit exceeded (429)
Solution: Increase batch_size to reduce API calls or wait 60 seconds
```

**2. Network Timeout**
```
Error: Connection timeout
Solution: Reduce batch_size or check network connectivity
```

**3. Database Connection**
```
Error: Connection to database failed
Solution: Check database credentials and connectivity
```

### Error Recovery

The sync service includes automatic retry logic:
- Failed items are tracked in error list
- Database rollback on batch failure
- TDS dead letter queue for permanent failures

## Best Practices

### Sync Frequency

- **High-volume stores**: Sync every 4-6 hours
- **Medium-volume stores**: Sync daily
- **Low-volume stores**: Sync weekly
- **After bulk updates**: Manual trigger via API or script

### Batch Size Selection

- **Fast network**: batch_size=200, db_batch_size=100
- **Moderate network**: batch_size=150, db_batch_size=75
- **Slow network**: batch_size=100, db_batch_size=50

### Filtering Strategy

- **Initial sync**: `active_only=true, with_stock_only=false`
- **Daily sync**: `active_only=true, with_stock_only=false`
- **Quick update**: `with_stock_only=true` (faster for large catalogs)

## Troubleshooting

### Check Sync Status

```bash
# View recent syncs
curl "https://erp.tsh.sale/api/bff/tds/runs?entity_type=product" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get current stats
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Logs

```bash
# Script logs
tail -f logs/tds_stock_sync_*.log

# Application logs
tail -f logs/app.log | grep "stock_sync"
```

### Manual Verification

```sql
-- Check last sync time
SELECT MAX(last_synced) as last_sync FROM products;

-- Count synced products
SELECT
    COUNT(*) as total,
    COUNT(CASE WHEN last_synced IS NOT NULL THEN 1 END) as synced,
    COUNT(CASE WHEN stock_quantity > 0 THEN 1 END) as with_stock
FROM products;

-- Find stale products (not synced in 24 hours)
SELECT COUNT(*)
FROM products
WHERE last_synced < NOW() - INTERVAL '24 hours'
   OR last_synced IS NULL;
```

## Integration Examples

### Python Integration

```python
import httpx

async def trigger_stock_sync():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://erp.tsh.sale/api/bff/tds/sync/stock",
            params={
                "batch_size": 200,
                "active_only": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### JavaScript/TypeScript Integration

```typescript
async function triggerStockSync() {
    const response = await fetch(
        'https://erp.tsh.sale/api/bff/tds/sync/stock?batch_size=200&active_only=true',
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }
    );
    return await response.json();
}
```

### Webhook Integration

Trigger sync after Zoho webhook events:

```python
@router.post("/webhooks/zoho/item-updated")
async def handle_item_update(webhook_data: dict):
    item_id = webhook_data.get("item_id")

    # Trigger specific item sync
    await sync_specific_items([item_id])

    return {"status": "synced"}
```

## Support & Resources

- **Documentation**: See project README and architecture docs
- **API Reference**: `/docs` endpoint (Swagger UI)
- **TDS Dashboard**: `/api/bff/tds/dashboard`
- **Health Check**: `/api/bff/tds/health`

## Changelog

### Version 2.0.0 (November 2025)
- Initial release of pagination batch stock sync
- TDS integration
- Bulk database operations
- Command line script
- API endpoints
- Dry run mode
- Comprehensive monitoring

---

**Last Updated**: November 6, 2025
**Author**: TSH Development Team
**Status**: Production Ready
