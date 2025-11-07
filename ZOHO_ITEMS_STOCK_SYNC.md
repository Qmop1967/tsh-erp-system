# 📦 Zoho Items with Stock Synchronization Guide

**Complete guide for syncing Zoho Books/Inventory items with stock levels to TSH ERP**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Endpoint](#api-endpoint)
3. [Request Parameters](#request-parameters)
4. [Response Format](#response-format)
5. [Usage Examples](#usage-examples)
6. [Stock Data Structure](#stock-data-structure)
7. [Sync Modes](#sync-modes)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Monitoring & Health Checks](#monitoring--health-checks)

---

## Overview

### What is Items with Stock Sync?

The **Items with Stock Sync** endpoint synchronizes product data AND inventory stock levels from Zoho Books/Inventory to the TSH ERP database in a single operation. This ensures complete inventory visibility across both systems.

### What Gets Synced?

**Product Data:**
- Product name (English & Arabic)
- SKU (Stock Keeping Unit)
- Descriptions
- Unit prices
- Cost prices
- Images (primary & gallery)
- Categories
- Barcodes
- Unit of measure
- Brand, color, size, weight, dimensions

**Stock Data:**
- Stock on hand (current physical inventory)
- Available stock (stock available for sale)
- Warehouse information
- Min/max stock levels
- Reorder points
- Last modified timestamps

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Zoho Books/Inventory API                    │
│           (Items endpoint with stock information)             │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │ HTTPS REST API
                             │ OAuth 2.0 Authentication
                             │ Rate Limited (100 req/min)
                             │
                             ▼
                ┌──────────────────────────┐
                │   TSH ERP API Endpoint   │
                │  /api/zoho/bulk-sync/    │
                │    items-with-stock      │
                └────────────┬─────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │ UnifiedStockSyncService     │
              │ (TDS Architecture)          │
              │                             │
              │ - Batch Processing          │
              │ - Pagination                │
              │ - Error Handling            │
              │ - Progress Tracking         │
              └────────────┬────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  TSH ERP Database    │
                │  (PostgreSQL)        │
                │                      │
                │  Tables:             │
                │  - products          │
                │  - inventory_items   │
                │  - warehouses        │
                └──────────────────────┘
```

---

## API Endpoint

### Endpoint URL

```
POST /api/zoho/bulk-sync/items-with-stock
```

### Authentication

Requires valid Zoho OAuth 2.0 credentials configured in environment variables:

```bash
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id
```

### Rate Limiting

- Zoho API: 100 requests per minute
- Built-in rate limiter with exponential backoff
- Automatic retry on rate limit errors

---

## Request Parameters

### Request Body Schema

```json
{
  "incremental": false,
  "modified_since": "2025-01-01",
  "batch_size": 100,
  "active_only": true,
  "with_stock_only": true,
  "sync_images": true
}
```

### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `incremental` | boolean | `false` | If true, only sync items modified since `modified_since` date |
| `modified_since` | string | `null` | ISO date string (YYYY-MM-DD) for incremental sync |
| `batch_size` | integer | `100` | Number of items to process in each batch (10-200) |
| `active_only` | boolean | `true` | If true, only sync active items (not archived/inactive) |
| `with_stock_only` | boolean | `true` | If true, only sync items with stock on hand > 0 |
| `sync_images` | boolean | `true` | If true, download and sync product images from Zoho |

### Parameter Validation

- `batch_size`: Must be between 10 and 200
- `modified_since`: Must be valid ISO date format (YYYY-MM-DD)
- All boolean parameters default to their specified values if omitted

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Items with stock bulk sync completed",
  "stats": {
    "total_processed": 2543,
    "successful": 2540,
    "failed": 3,
    "skipped": 127,
    "stock_updated": 2540
  },
  "duration_seconds": 342.56,
  "error": null
}
```

### Error Response

```json
{
  "success": false,
  "message": "Items with stock bulk sync failed",
  "stats": {
    "total_processed": 145,
    "successful": 140,
    "failed": 5,
    "skipped": 0,
    "stock_updated": 140
  },
  "duration_seconds": 67.23,
  "error": "Rate limit exceeded. Retry after 60 seconds."
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Overall sync operation success status |
| `message` | string | Human-readable status message |
| `stats.total_processed` | integer | Total items attempted to sync |
| `stats.successful` | integer | Successfully synced items |
| `stats.failed` | integer | Failed items (see logs for details) |
| `stats.skipped` | integer | Skipped items (e.g., duplicates, unchanged) |
| `stats.stock_updated` | integer | Items with stock levels updated |
| `duration_seconds` | float | Total sync duration in seconds |
| `error` | string\|null | Error message if sync failed |

---

## Usage Examples

### Example 1: Full Sync (All Items)

**Use Case:** Initial data migration or complete refresh

```bash
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "incremental": false,
    "batch_size": 100,
    "active_only": true,
    "with_stock_only": false,
    "sync_images": true
  }'
```

**Expected Duration:** 5-10 minutes for 2,000+ items

### Example 2: Incremental Sync (Recent Changes)

**Use Case:** Daily updates to capture recent changes

```bash
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "incremental": true,
    "modified_since": "2025-01-01",
    "batch_size": 200,
    "active_only": true,
    "with_stock_only": false,
    "sync_images": true
  }'
```

**Expected Duration:** 1-3 minutes for typical daily changes

### Example 3: Active Items with Stock Only

**Use Case:** Sync only sellable products with available inventory

```bash
curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "incremental": false,
    "batch_size": 150,
    "active_only": true,
    "with_stock_only": true,
    "sync_images": true
  }'
```

**Expected Duration:** 3-6 minutes depending on available stock count

### Example 4: Python Script

```python
import requests
import json

def sync_items_with_stock(incremental=False, modified_since=None):
    """Sync Zoho items with stock to TSH ERP"""

    url = "https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock"

    payload = {
        "incremental": incremental,
        "batch_size": 100,
        "active_only": True,
        "with_stock_only": False,
        "sync_images": True
    }

    if modified_since:
        payload["modified_since"] = modified_since

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {YOUR_TOKEN}"
    }

    print(f"🔄 Starting sync (incremental={incremental})...")

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result["success"]:
        stats = result["stats"]
        print(f"✅ Sync completed!")
        print(f"   Total: {stats['total_processed']}")
        print(f"   Success: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Stock Updated: {stats['stock_updated']}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
    else:
        print(f"❌ Sync failed: {result.get('error', 'Unknown error')}")

    return result

# Usage examples
if __name__ == "__main__":
    # Full sync
    result = sync_items_with_stock(incremental=False)

    # Incremental sync (last 7 days)
    from datetime import datetime, timedelta
    since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = sync_items_with_stock(incremental=True, modified_since=since_date)
```

### Example 5: JavaScript/Node.js

```javascript
const axios = require('axios');

async function syncItemsWithStock(options = {}) {
    const {
        incremental = false,
        modifiedSince = null,
        batchSize = 100,
        activeOnly = true,
        withStockOnly = false,
        syncImages = true
    } = options;

    const url = 'https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock';

    const payload = {
        incremental,
        batch_size: batchSize,
        active_only: activeOnly,
        with_stock_only: withStockOnly,
        sync_images: syncImages
    };

    if (modifiedSince) {
        payload.modified_since = modifiedSince;
    }

    try {
        console.log('🔄 Starting sync...');

        const response = await axios.post(url, payload, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${YOUR_TOKEN}`
            }
        });

        const result = response.data;

        if (result.success) {
            console.log('✅ Sync completed!');
            console.log(`   Total: ${result.stats.total_processed}`);
            console.log(`   Success: ${result.stats.successful}`);
            console.log(`   Failed: ${result.stats.failed}`);
            console.log(`   Stock Updated: ${result.stats.stock_updated}`);
            console.log(`   Duration: ${result.duration_seconds.toFixed(2)}s`);
        } else {
            console.error(`❌ Sync failed: ${result.error || 'Unknown error'}`);
        }

        return result;

    } catch (error) {
        console.error('❌ Request failed:', error.message);
        throw error;
    }
}

// Usage examples
(async () => {
    // Full sync
    await syncItemsWithStock({ incremental: false });

    // Incremental sync (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const sinceDate = sevenDaysAgo.toISOString().split('T')[0];

    await syncItemsWithStock({
        incremental: true,
        modifiedSince: sinceDate
    });
})();
```

---

## Stock Data Structure

### Zoho Stock Fields (API Response)

```json
{
  "item_id": "2646610000000029001",
  "sku": "PROD-001",
  "name": "Sample Product",
  "stock_on_hand": 150,
  "available_stock": 145,
  "committed_stock": 5,
  "actual_available_stock": 145,
  "warehouses": [
    {
      "warehouse_id": "2646610000000123001",
      "warehouse_name": "Main Warehouse",
      "warehouse_stock_on_hand": 100,
      "warehouse_available_stock": 95
    },
    {
      "warehouse_id": "2646610000000123002",
      "warehouse_name": "Secondary Warehouse",
      "warehouse_stock_on_hand": 50,
      "warehouse_available_stock": 50
    }
  ],
  "last_modified_time": "2025-01-07T10:30:00Z"
}
```

### TSH ERP Database Schema

**products table:**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    description TEXT,
    unit_price NUMERIC(10,2) NOT NULL,
    cost_price NUMERIC(10,2),
    min_stock_level INTEGER DEFAULT 0,
    max_stock_level INTEGER,
    reorder_point INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_trackable BOOLEAN DEFAULT TRUE,
    zoho_item_id VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**inventory_items table:**
```sql
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    warehouse_id INTEGER REFERENCES warehouses(id),
    stock_on_hand INTEGER DEFAULT 0,
    available_stock INTEGER DEFAULT 0,
    committed_stock INTEGER DEFAULT 0,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Field Mapping

| Zoho Field | TSH ERP Field | Table | Notes |
|------------|---------------|-------|-------|
| `item_id` | `zoho_item_id` | products | Unique identifier |
| `sku` | `sku` | products | Stock Keeping Unit |
| `name` | `name` | products | English name |
| `stock_on_hand` | `stock_on_hand` | inventory_items | Total physical stock |
| `available_stock` | `available_stock` | inventory_items | Stock available for sale |
| `committed_stock` | `committed_stock` | inventory_items | Stock in pending orders |
| `warehouse_id` | `zoho_warehouse_id` | warehouses | Warehouse reference |
| `last_modified_time` | `last_sync_at` | inventory_items | Sync timestamp |

---

## Sync Modes

### 1. Full Sync

**When to use:**
- Initial data migration
- Complete database refresh
- After major Zoho changes
- Recovery from data corruption

**Characteristics:**
- Syncs ALL items from Zoho
- Ignores `modified_since` parameter
- Longest duration (5-10 minutes)
- Most thorough and complete

**Configuration:**
```json
{
  "incremental": false,
  "batch_size": 100
}
```

### 2. Incremental Sync

**When to use:**
- Daily/hourly updates
- Capturing recent changes
- Scheduled cron jobs
- Continuous synchronization

**Characteristics:**
- Only syncs items modified after `modified_since` date
- Fastest sync mode (1-3 minutes)
- Requires valid date parameter
- Most efficient for regular updates

**Configuration:**
```json
{
  "incremental": true,
  "modified_since": "2025-01-01"
}
```

### 3. Filtered Sync (Active Only)

**When to use:**
- Syncing sellable products only
- Excluding archived/discontinued items
- Production/live inventory

**Characteristics:**
- Uses `filter_by=Status.Active` in Zoho API
- Excludes inactive items
- Reduces sync time
- Focuses on relevant products

**Configuration:**
```json
{
  "active_only": true
}
```

### 4. Stock-Available Sync

**When to use:**
- Syncing in-stock products only
- E-commerce product feeds
- Avoiding out-of-stock items

**Characteristics:**
- Only syncs items with `stock_on_hand > 0`
- Client-side filtering (Zoho API limitation)
- Longer API calls but fewer database writes
- Ideal for customer-facing systems

**Configuration:**
```json
{
  "with_stock_only": true
}
```

---

## Best Practices

### 1. Scheduling Strategy

**Recommended Schedule:**

```
Daily Full Sync:      03:00 AM (low traffic time)
Hourly Incremental:   Every hour on the hour
Real-time Updates:    Via webhooks (separate system)
```

**Cron Example:**
```bash
# Full sync at 3 AM daily
0 3 * * * curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock \
  -H "Content-Type: application/json" \
  -d '{"incremental": false, "batch_size": 100}'

# Incremental sync every hour
0 * * * * curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/items-with-stock \
  -H "Content-Type: application/json" \
  -d '{"incremental": true, "modified_since": "$(date -d '1 hour ago' +%Y-%m-%d)"}'
```

### 2. Batch Size Optimization

**Recommendations:**
- **Small catalogs** (< 500 items): `batch_size: 200`
- **Medium catalogs** (500-2,000 items): `batch_size: 100`
- **Large catalogs** (> 2,000 items): `batch_size: 50`

**Why?**
- Larger batches = Fewer API calls but longer per-batch processing
- Smaller batches = More API calls but faster failure recovery
- Balance between API rate limits and processing efficiency

### 3. Error Handling

**Retry Strategy:**
```python
import time

def sync_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            result = sync_items_with_stock()
            if result["success"]:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️  Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ All {max_retries} attempts failed")
                raise
```

### 4. Monitoring Best Practices

**Metrics to Track:**
- Sync success rate (target: > 99%)
- Average sync duration (baseline for comparison)
- Failed items count (investigate if > 1%)
- Stock discrepancies (TSH ERP vs Zoho)
- API rate limit hits

**Alerting Thresholds:**
- Success rate < 95%: Warning
- Success rate < 90%: Critical
- Duration > 2x baseline: Warning
- Failed items > 5%: Critical

### 5. Data Validation

**Post-Sync Checks:**
```sql
-- Check for missing stock data
SELECT p.id, p.sku, p.name, COUNT(ii.id) as inventory_count
FROM products p
LEFT JOIN inventory_items ii ON p.id = ii.product_id
WHERE p.is_trackable = TRUE
  AND p.is_active = TRUE
GROUP BY p.id
HAVING COUNT(ii.id) = 0;

-- Check for negative stock (data quality issue)
SELECT p.sku, p.name, ii.stock_on_hand, ii.available_stock
FROM products p
JOIN inventory_items ii ON p.id = ii.product_id
WHERE ii.stock_on_hand < 0 OR ii.available_stock < 0;

-- Check for stock without products (orphaned records)
SELECT ii.id, ii.stock_on_hand
FROM inventory_items ii
LEFT JOIN products p ON ii.product_id = p.id
WHERE p.id IS NULL;
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Sync Takes Too Long

**Symptoms:**
- Sync duration > 15 minutes
- Timeouts
- High server load

**Solutions:**
1. Reduce `batch_size` to 50
2. Enable `with_stock_only: true` to reduce items
3. Use incremental sync instead of full sync
4. Schedule during low-traffic periods
5. Check Zoho API performance status

#### Issue 2: Authentication Failures

**Symptoms:**
- HTTP 401 Unauthorized
- "Invalid access token" errors

**Solutions:**
1. Verify environment variables are set correctly
2. Check if refresh token is expired
3. Generate new OAuth tokens from Zoho
4. Verify organization_id matches credentials
5. Check API access permissions in Zoho

```bash
# Test authentication
curl -X GET https://erp.tsh.sale/api/zoho/bulk-sync/status
```

#### Issue 3: Missing Stock Data

**Symptoms:**
- Products synced but no inventory_items records
- Stock levels showing as 0

**Root Causes:**
- `is_trackable` = FALSE in products table
- Warehouse not configured in TSH ERP
- Zoho API not returning stock data

**Solutions:**
1. Check product `is_trackable` flag:
```sql
UPDATE products SET is_trackable = TRUE WHERE zoho_item_id IS NOT NULL;
```

2. Verify warehouses exist:
```sql
SELECT * FROM warehouses;
```

3. Check Zoho API response in logs:
```bash
docker logs tsh_erp_app | grep "stock_on_hand"
```

#### Issue 4: Duplicate Items

**Symptoms:**
- Same product appearing multiple times
- SKU uniqueness violations

**Root Causes:**
- `zoho_item_id` not properly set
- SKU format changes in Zoho
- Duplicate entries in Zoho

**Solutions:**
1. Run deduplication script:
```sql
-- Find duplicates
SELECT sku, COUNT(*) as count
FROM products
GROUP BY sku
HAVING COUNT(*) > 1;

-- Keep latest, delete older duplicates
DELETE FROM products p1
USING products p2
WHERE p1.id < p2.id
  AND p1.sku = p2.sku;
```

2. Enable strict zoho_item_id validation in sync config

#### Issue 5: Rate Limit Exceeded

**Symptoms:**
- HTTP 429 Too Many Requests
- "Rate limit exceeded" errors

**Solutions:**
1. Reduce `batch_size`
2. Increase delay between batches (handled automatically)
3. Check if other services are using Zoho API
4. Upgrade Zoho API plan if consistently hitting limits
5. Use webhook for real-time updates instead of frequent polls

---

## Monitoring & Health Checks

### Health Check Endpoints

#### 1. Service Status

```bash
GET /api/zoho/bulk-sync/status
```

**Response:**
```json
{
  "service": "Zoho Bulk Sync",
  "status": "healthy",
  "available_operations": [
    "POST /api/zoho/bulk-sync/items-with-stock",
    "POST /api/zoho/bulk-sync/products",
    "POST /api/zoho/bulk-sync/customers"
  ],
  "features": [
    "Pagination support",
    "Incremental sync",
    "Batch processing",
    "Stock level synchronization"
  ]
}
```

#### 2. Sync Queue Stats

```bash
GET /api/zoho/sync/stats
```

**Response:**
```json
{
  "queue": {
    "pending": 0,
    "processing": 0,
    "completed": 2543,
    "failed": 3,
    "dead_letter": 0
  },
  "by_entity": {
    "products": {"pending": 0, "failed": 2},
    "inventory": {"pending": 0, "failed": 1}
  },
  "sync_delay_avg_seconds": 8.5
}
```

### Database Monitoring Queries

#### Check Sync Freshness

```sql
-- Items not synced in last 24 hours
SELECT
    COUNT(*) as outdated_count,
    MAX(ii.last_sync_at) as last_sync
FROM inventory_items ii
WHERE ii.last_sync_at < NOW() - INTERVAL '24 hours'
  OR ii.last_sync_at IS NULL;
```

#### Stock Level Summary

```sql
-- Stock summary by status
SELECT
    CASE
        WHEN ii.stock_on_hand = 0 THEN 'Out of Stock'
        WHEN ii.stock_on_hand <= p.min_stock_level THEN 'Low Stock'
        WHEN ii.stock_on_hand <= p.reorder_point THEN 'Reorder Level'
        ELSE 'In Stock'
    END as stock_status,
    COUNT(*) as count,
    SUM(ii.stock_on_hand) as total_units
FROM inventory_items ii
JOIN products p ON ii.product_id = p.id
WHERE p.is_active = TRUE
GROUP BY stock_status
ORDER BY stock_status;
```

#### Sync Performance Metrics

```sql
-- Average sync duration over last 7 days
SELECT
    DATE(last_sync_at) as sync_date,
    COUNT(*) as items_synced,
    AVG(EXTRACT(EPOCH FROM (updated_at - last_sync_at))) as avg_seconds
FROM inventory_items
WHERE last_sync_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(last_sync_at)
ORDER BY sync_date DESC;
```

### Grafana Dashboard Queries

**Panel 1: Stock Sync Success Rate**
```sql
SELECT
    time_bucket('1 hour', last_sync_at) AS time,
    COUNT(*) FILTER (WHERE stock_on_hand >= 0) as successful,
    COUNT(*) as total,
    (COUNT(*) FILTER (WHERE stock_on_hand >= 0) * 100.0 / COUNT(*)) as success_rate
FROM inventory_items
WHERE last_sync_at > NOW() - INTERVAL '24 hours'
GROUP BY time_bucket('1 hour', last_sync_at)
ORDER BY time;
```

**Panel 2: Items by Stock Status**
```sql
SELECT
    CASE
        WHEN stock_on_hand = 0 THEN 'Out of Stock'
        WHEN stock_on_hand <= min_stock_level THEN 'Low Stock'
        ELSE 'In Stock'
    END as status,
    COUNT(*) as count
FROM inventory_items ii
JOIN products p ON ii.product_id = p.id
WHERE p.is_active = TRUE
GROUP BY status;
```

---

## Summary

### Quick Reference

**Endpoint:** `POST /api/zoho/bulk-sync/items-with-stock`

**Key Features:**
- ✅ Syncs products + stock in one operation
- ✅ Multi-warehouse support
- ✅ Incremental & full sync modes
- ✅ Batch processing (10-200 items)
- ✅ Automatic deduplication
- ✅ Comprehensive error handling
- ✅ Real-time progress tracking

**Performance:**
- Full sync: 5-10 minutes (2,000+ items)
- Incremental: 1-3 minutes (typical daily changes)
- Batch size: 100-200 items per API call

**Best Practices:**
- Schedule full sync daily at 3 AM
- Run incremental sync hourly
- Monitor success rate (target > 99%)
- Validate stock data post-sync
- Use webhooks for real-time updates

---

**Document Version:** 1.0.0
**Last Updated:** November 7, 2025
**Author:** TSH ERP Team

For questions or issues, contact: support@tsh.sale
