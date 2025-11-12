# Zoho Items Comparison and Sync Script

## Overview

This script compares the count of items in Zoho Inventory with items in TSH ERP Ecosystem database and automatically syncs any missing items.

## Features

- ✅ **Count Comparison**: Compares Zoho items count with TSH ERP items count
- ✅ **Missing Items Detection**: Identifies items that exist in Zoho but not in TSH ERP
- ✅ **Automatic Sync**: Syncs missing items from Zoho to TSH ERP database
- ✅ **Uses Zoho MCP Infrastructure**: Leverages the unified Zoho client with proper authentication
- ✅ **Comprehensive Reporting**: Provides detailed statistics and progress updates

## Prerequisites

### Environment Variables

The script requires the following environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Zoho Credentials
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=748369814
```

## Usage

### Run the Script

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
python3 scripts/compare_and_sync_zoho_items_mcp.py
```

### What It Does

1. **Step 1: Fetch Zoho Items**
   - Connects to Zoho Inventory API using unified client
   - Fetches all items with pagination
   - Counts total items and extracts unique item IDs

2. **Step 2: Fetch TSH ERP Items**
   - Connects to PostgreSQL database
   - Queries products table for items with `zoho_item_id`
   - Counts synced items

3. **Step 3: Compare Counts**
   - Identifies items missing in TSH ERP
   - Identifies items that exist in TSH ERP but not in Zoho
   - Calculates differences

4. **Step 4: Sync Missing Items**
   - For each missing item:
     - Fetches detailed item information from Zoho
     - Inserts or updates the item in TSH ERP database
     - Handles categories, prices, stock, and images
   - Provides progress updates and error handling

## Output Example

```
======================================================================
🔄 ZOHO ITEMS COMPARISON AND SYNC
======================================================================

📋 Configuration:
   Organization ID: 748369814
   Database: Connected

----------------------------------------------------------------------
STEP 1: Fetching items from Zoho
----------------------------------------------------------------------
  📥 Fetching items from Zoho (page 1)...
     ✅ Fetched 200 items (total: 200)
     ✅ Fetched 150 items (total: 350)

✅ Zoho Items:
   Total Count: 350
   Unique Item IDs: 350

----------------------------------------------------------------------
STEP 2: Fetching items from TSH ERP Database
----------------------------------------------------------------------

✅ TSH ERP Items:
   Total Count: 320
   Unique Zoho Item IDs: 320

----------------------------------------------------------------------
STEP 3: Comparing Counts
----------------------------------------------------------------------

📊 Comparison Results:
   Zoho Items: 350
   TSH ERP Items: 320
   Difference: 30

   Missing in TSH ERP: 30 items
   Extra in TSH ERP: 0 items

   Missing Item IDs (first 10): ['12345', '12346', ...]

----------------------------------------------------------------------
STEP 4: Syncing Missing Items
----------------------------------------------------------------------

🔄 Syncing 30 missing items...
   ✅ [1/30] Inserted: ZOHO_12345
   ✅ [2/30] Inserted: ZOHO_12346
   ...

✅ Sync Completed!
   📊 Statistics:
      - Inserted: 28
      - Updated: 2
      - Errors: 0

======================================================================
📊 FINAL SUMMARY
======================================================================
   Zoho Items: 350
   TSH ERP Items: 348
   Missing Items: 0
   Extra Items: 0
   Sync Status: ✅ Complete
======================================================================
```

## Technical Details

### Architecture

- **ZohoMCPClient**: Wrapper around UnifiedZohoClient for Zoho API interactions
- **TSHERPItemsCounter**: Database query handler for TSH ERP items
- **ZohoItemSyncer**: Syncs individual items from Zoho to TSH ERP

### Database Schema

The script works with the `products` table which should have:
- `zoho_item_id`: Zoho item identifier (used for matching)
- `sku`: Product SKU
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `actual_available_stock`: Stock quantity
- `image_url`: Product image URL
- `category_id`: Foreign key to categories table

### Error Handling

- Network errors: Retries with exponential backoff
- Authentication errors: Automatic token refresh
- Database errors: Transaction rollback and error reporting
- Rate limiting: Built-in rate limiter (100 requests/minute)

## Integration with Zoho MCP

This script uses the TSH ERP Ecosystem's unified Zoho client infrastructure, which is MCP-ready. The client:

- Handles OAuth 2.0 authentication automatically
- Manages token refresh and rotation
- Implements rate limiting
- Provides retry logic with exponential backoff
- Publishes events for monitoring

## Scheduling

You can schedule this script to run periodically using cron:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/TSH_ERP_Ecosystem && python3 scripts/compare_and_sync_zoho_items_mcp.py >> logs/zoho_sync.log 2>&1
```

## Troubleshooting

### Common Issues

1. **Missing Credentials**
   - Ensure all Zoho environment variables are set
   - Check `.env` file or system environment

2. **Database Connection Errors**
   - Verify DATABASE_URL is correct
   - Check database server is running
   - Ensure URL-encoded passwords are properly formatted

3. **Zoho API Errors**
   - Check refresh token is valid
   - Verify organization ID is correct
   - Check API rate limits

4. **Missing Categories**
   - Script automatically creates "Uncategorized" category if needed
   - Ensure categories table exists

## Related Scripts

- `scripts/unified_stock_sync.py`: Stock synchronization
- `scripts/sync_zoho_to_postgres.py`: General Zoho to PostgreSQL sync
- `scripts/sync_pricelists_from_zoho.py`: Price list synchronization

## Author

TSH ERP Team  
Date: November 8, 2025







