# Zoho Synchronization System - Complete Documentation

## Overview

The Zoho Synchronization System provides comprehensive, real-time, one-directional data synchronization from Zoho to TSH ERP System. The system supports three main entity types: **Items**, **Customers**, and **Vendors**.

### Key Features

✅ **One-Directional Sync**: Zoho → TSH ERP (Read-only from Zoho)  
✅ **Real-Time Synchronization**: Immediate updates when changes occur in Zoho  
✅ **Detailed Field Mapping**: Granular control over field transformations  
✅ **Image Synchronization**: Automatic download and storage of product images  
✅ **Data Analysis**: Pre-sync analysis to identify changes and conflicts  
✅ **Comprehensive Logging**: Detailed logs of all sync operations  
✅ **Error Handling**: Automatic retry with configurable thresholds  
✅ **Conflict Resolution**: Configurable strategy (Zoho wins by default)  
✅ **Validation**: Data validation before inserting into TSH ERP  

---

## Architecture

### Components

1. **Sync Mappings**: Define how Zoho fields map to TSH ERP fields
2. **Sync Control**: Configure sync behavior, webhooks, and error handling
3. **Sync Logs**: Track all sync operations with detailed status
4. **Data Analyzer**: Analyze Zoho data before syncing

### Data Flow

```
Zoho API
    ↓
Webhook/Polling
    ↓
Data Analysis
    ↓
Field Transformation
    ↓
Data Validation
    ↓
TSH ERP Database
    ↓
Sync Log
```

---

## Entity Types

### 1. Items (Products/Inventory)

**Zoho Source**: Zoho Inventory Items  
**TSH Destination**: `items` table  
**Sync Mode**: Real-time (15-minute polling fallback)  
**Image Sync**: ✅ Enabled

#### Field Mappings

| Zoho Field | TSH ERP Field | Type | Required | Transformation |
|------------|---------------|------|----------|----------------|
| `item_id` | `zoho_item_id` | text | Yes | None |
| `name` | `name` | text | Yes | None |
| `sku` | `sku` | text | Yes | Uppercase |
| `description` | `description` | text | No | None |
| `rate` | `unit_price` | number | Yes | None |
| `stock_on_hand` | `quantity_on_hand` | number | No | None |
| `category_name` | `category` | text | No | None |
| `unit` | `unit_of_measure` | text | No | None |
| `brand` | `brand` | text | No | None |
| `manufacturer` | `manufacturer` | text | No | None |
| `purchase_rate` | `cost_price` | number | No | None |
| `reorder_level` | `reorder_point` | number | No | None |
| `image_name` | `image_url` | image | No | Download Image |
| `item_type` | `item_type` | text | No | Lowercase |
| `is_taxable` | `is_taxable` | boolean | No | None |
| `tax_id` | `tax_rate_id` | text | No | None |
| `status` | `is_active` | boolean | No | Status to Boolean |

#### Special Features

- **Image Download**: Automatically downloads product images from Zoho and stores them locally
- **SKU Normalization**: Converts SKU to uppercase for consistency
- **Stock Tracking**: Syncs real-time inventory levels
- **Category Mapping**: Maps Zoho categories to TSH categories

---

### 2. Customers (Contacts)

**Zoho Source**: Zoho Books/CRM Contacts  
**TSH Destination**: `customers` table  
**Sync Mode**: Real-time (10-minute polling fallback)  
**Image Sync**: ❌ Disabled

#### Field Mappings

| Zoho Field | TSH ERP Field | Type | Required | Transformation |
|------------|---------------|------|----------|----------------|
| `contact_id` | `zoho_customer_id` | text | Yes | None |
| `contact_name` | `name` | text | Yes | None |
| `company_name` | `company_name` | text | No | None |
| `contact_person` | `contact_person` | text | No | None |
| `email` | `email` | text | No | Lowercase |
| `phone` | `phone` | text | No | None |
| `mobile` | `mobile` | text | No | None |
| `billing_address` | `address` | text | No | Format Address |
| `billing_city` | `city` | text | No | None |
| `billing_country` | `country` | text | No | None |
| `billing_zip` | `postal_code` | text | No | None |
| `tax_id` | `tax_number` | text | No | None |
| `credit_limit` | `credit_limit` | number | No | None |
| `payment_terms` | `payment_terms` | number | No | None |
| `currency_code` | `currency` | text | No | Uppercase |
| `language_code` | `portal_language` | text | No | Lowercase |
| `status` | `is_active` | boolean | No | Status to Boolean |
| `notes` | `notes` | text | No | None |

#### Special Features

- **Email Normalization**: Converts email to lowercase
- **Address Formatting**: Formats address fields into single address string
- **Credit Limit Sync**: Keeps credit limits synchronized
- **Multi-Language Support**: Maps language preferences

---

### 3. Vendors (Suppliers)

**Zoho Source**: Zoho Books Vendors  
**TSH Destination**: `suppliers` table  
**Sync Mode**: Real-time (10-minute polling fallback)  
**Image Sync**: ❌ Disabled

#### Field Mappings

| Zoho Field | TSH ERP Field | Type | Required | Transformation |
|------------|---------------|------|----------|----------------|
| `vendor_id` | `zoho_vendor_id` | text | Yes | None |
| `vendor_name` | `name` | text | Yes | None |
| `company_name` | `company_name` | text | No | None |
| `contact_name` | `contact_person` | text | No | None |
| `email` | `email` | text | No | Lowercase |
| `phone` | `phone` | text | No | None |
| `mobile` | `mobile` | text | No | None |
| `billing_address` | `address` | text | No | Format Address |
| `billing_city` | `city` | text | No | None |
| `billing_country` | `country` | text | No | None |
| `billing_zip` | `postal_code` | text | No | None |
| `tax_id` | `tax_number` | text | No | None |
| `payment_terms` | `payment_terms` | number | No | None |
| `currency_code` | `currency` | text | No | Uppercase |
| `status` | `is_active` | boolean | No | Status to Boolean |
| `notes` | `notes` | text | No | None |

---

## API Endpoints

### Configuration Endpoints

#### Get All Sync Mappings
```http
GET /api/settings/integrations/zoho/sync/mappings
```

**Response:**
```json
{
  "status": "success",
  "mappings": {
    "item": {...},
    "customer": {...},
    "vendor": {...}
  }
}
```

#### Get Entity Mapping
```http
GET /api/settings/integrations/zoho/sync/mappings/{entity_type}
```

**Parameters:**
- `entity_type`: `item`, `customer`, or `vendor`

#### Update Entity Mapping
```http
POST /api/settings/integrations/zoho/sync/mappings/{entity_type}
```

**Body:**
```json
{
  "entity_type": "item",
  "enabled": true,
  "sync_direction": "zoho_to_tsh",
  "sync_mode": "real_time",
  "field_mappings": [...],
  "sync_images": true,
  "auto_create": true,
  "auto_update": true
}
```

#### Reset Entity Mapping
```http
POST /api/settings/integrations/zoho/sync/mappings/{entity_type}/reset
```

Resets mapping to default configuration.

---

### Control Endpoints

#### Get Sync Control Settings
```http
GET /api/settings/integrations/zoho/sync/control
```

#### Update Sync Control Settings
```http
POST /api/settings/integrations/zoho/sync/control
```

**Body:**
```json
{
  "webhook_enabled": true,
  "webhook_url": "https://your-domain.com/api/webhooks/zoho",
  "webhook_secret": "your-secret-key",
  "batch_size": 100,
  "retry_attempts": 3,
  "retry_delay": 60,
  "error_threshold": 10,
  "validate_data": true,
  "backup_before_sync": true
}
```

---

### Operation Endpoints

#### Analyze Zoho Data
```http
POST /api/settings/integrations/zoho/sync/{entity_type}/analyze
```

Analyzes Zoho data before syncing:
- Counts total records
- Identifies new records
- Detects updated records
- Finds duplicates
- Validates field completeness

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "entity_type": "item",
    "total_records": 500,
    "new_records": 50,
    "updated_records": 25,
    "matched_records": 425,
    "error_records": 0,
    "field_statistics": {...}
  }
}
```

#### Execute Sync
```http
POST /api/settings/integrations/zoho/sync/{entity_type}/execute
```

**Query Parameters:**
- `force`: Boolean (optional) - Force sync even if recently synced

**Response:**
```json
{
  "status": "success",
  "sync_id": "sync_item_20251004_143022",
  "message": "Sync initiated for item",
  "timestamp": "2025-10-04T14:30:22.123Z"
}
```

#### Get Sync Status
```http
GET /api/settings/integrations/zoho/sync/{entity_type}/status
```

#### Toggle Sync
```http
POST /api/settings/integrations/zoho/sync/{entity_type}/toggle
```

**Body:**
```json
{
  "enabled": true
}
```

#### Get Sync Statistics
```http
GET /api/settings/integrations/zoho/sync/statistics
```

Returns overall statistics for all entity types.

---

### Log Endpoints

#### Get Sync Logs
```http
GET /api/settings/integrations/zoho/sync/logs
```

**Query Parameters:**
- `entity_type`: Filter by entity type (optional)
- `status`: Filter by status (optional)
- `limit`: Number of logs to return (default: 100)

#### Clear Sync Logs
```http
DELETE /api/settings/integrations/zoho/sync/logs
```

---

## Sync Control Configuration

### Webhook Settings

Configure real-time webhooks from Zoho:

```json
{
  "webhook_enabled": true,
  "webhook_url": "https://your-domain.com/api/webhooks/zoho",
  "webhook_secret": "your-secret-key"
}
```

### Batch Processing

Control how many records to process at once:

```json
{
  "batch_size": 100
}
```

Larger batches = faster sync, but more memory usage.

### Error Handling

Configure retry and error behavior:

```json
{
  "retry_attempts": 3,
  "retry_delay": 60,
  "error_threshold": 10,
  "notification_email": "admin@company.com"
}
```

### Data Validation

Enable/disable data validation before inserting:

```json
{
  "validate_data": true,
  "backup_before_sync": true
}
```

---

## Transformation Rules

### Available Transformations

1. **uppercase**: Convert text to uppercase
2. **lowercase**: Convert text to lowercase
3. **format_address**: Combine address fields into single string
4. **status_to_boolean**: Convert status text to boolean (active/inactive)
5. **download_image**: Download and store image from URL
6. **date_format**: Format date strings

### Custom Transformations

You can add custom transformation rules by extending the transformation engine in the backend.

---

## Conflict Resolution

### Strategies

1. **zoho_wins** (Default): Zoho data always overwrites TSH data
2. **tsh_wins**: Keep TSH data, skip Zoho updates
3. **manual**: Flag conflicts for manual review

### Configuration

```json
{
  "conflict_resolution": "zoho_wins",
  "auto_create": true,
  "auto_update": true,
  "delete_sync": false
}
```

---

## Sync Modes

### Real-Time Sync

- Uses Zoho webhooks
- Immediate updates when data changes in Zoho
- Recommended for production

### Scheduled Sync

- Polls Zoho API at regular intervals
- Configured via `sync_frequency` (minutes)
- Fallback when webhooks unavailable

### Manual Sync

- Triggered by user action
- Full sync of all records
- Use for initial setup or troubleshooting

---

## Monitoring and Logging

### Log Structure

```json
{
  "sync_id": "sync_item_20251004_143022",
  "entity_type": "item",
  "entity_id": "tsh_item_123",
  "zoho_id": "zoho_item_456",
  "operation": "update",
  "status": "success",
  "error_message": null,
  "synced_fields": ["name", "price", "quantity"],
  "timestamp": "2025-10-04T14:30:22.123Z"
}
```

### Status Values

- `success`: Sync completed successfully
- `error`: Sync failed with error
- `skipped`: Record skipped (no changes)
- `in_progress`: Sync currently running

---

## Best Practices

### 1. Initial Setup

1. Configure Zoho credentials
2. Test connection
3. Analyze data for each entity type
4. Review and adjust field mappings
5. Enable one entity at a time
6. Monitor logs closely

### 2. Production Use

1. Enable webhooks for real-time sync
2. Set appropriate batch sizes
3. Configure error notifications
4. Enable backup before sync
5. Monitor sync statistics daily
6. Review error logs weekly

### 3. Troubleshooting

1. Check Zoho connection status
2. Review sync logs for errors
3. Verify field mappings are correct
4. Test with single record first
5. Check webhook configuration
6. Validate data in both systems

---

## Security Considerations

### Credentials Storage

- Zoho credentials stored in encrypted config files
- Use environment variables for production
- Rotate secrets regularly

### Webhook Security

- Always use HTTPS
- Implement webhook secret validation
- Rate limit webhook endpoints
- Log all webhook requests

### Data Validation

- Validate all incoming data
- Sanitize text fields
- Check for SQL injection
- Verify data types

---

## Performance Optimization

### Database Optimization

- Index Zoho ID fields
- Use bulk inserts for batches
- Optimize image storage
- Regular database maintenance

### API Optimization

- Use pagination for large datasets
- Cache frequently accessed data
- Implement request throttling
- Monitor API rate limits

### Image Optimization

- Compress images before storing
- Use CDN for image delivery
- Lazy load images in UI
- Clean up old images periodically

---

## File Structure

```
app/
├── data/
│   └── settings/
│       ├── zoho_config.json          # Main Zoho credentials
│       ├── zoho_sync_mappings.json   # Field mapping configs
│       ├── zoho_sync_control.json    # Sync control settings
│       └── zoho_sync_logs.json       # Sync operation logs
└── routers/
    └── settings.py                    # API endpoints
```

---

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 400 | Invalid entity type | Use 'item', 'customer', or 'vendor' |
| 404 | Mapping not found | Create mapping first |
| 500 | Sync failed | Check logs for details |
| 503 | Zoho API unavailable | Retry later |

---

## Support and Maintenance

### Regular Tasks

- **Daily**: Review sync statistics
- **Weekly**: Check error logs
- **Monthly**: Analyze sync performance
- **Quarterly**: Update field mappings

### Backup Strategy

- Automatic backup before sync (if enabled)
- Manual backups before major changes
- Test restore procedures regularly

---

## Future Enhancements

### Planned Features

- [ ] Bi-directional sync (TSH → Zoho)
- [ ] Advanced conflict resolution UI
- [ ] Custom transformation rules builder
- [ ] Real-time sync dashboard
- [ ] Mobile app sync status
- [ ] Email notifications for errors
- [ ] Automated sync scheduling UI
- [ ] Data quality reports
- [ ] Sync performance analytics
- [ ] Multi-organization support

---

## Conclusion

The Zoho Synchronization System provides enterprise-grade data synchronization with comprehensive control, monitoring, and error handling. Follow best practices and monitor regularly for optimal performance.

For support, contact: support@tsh-erp.com
