# Zoho ↔ TSH ERP Data Sync Checker

## Overview

Automated data consistency verification tool that compares data between Zoho Books/Inventory and the local PostgreSQL database to ensure perfect synchronization before deployments.

## Purpose

This tool prevents deployment of code when financial or product data discrepancies exist between Zoho (source of truth) and the local ERP system, ensuring data integrity across the entire ecosystem.

## Features

- ✅ Compares invoices (IDs, numbers, totals, statuses)
- ✅ Compares customers (names, emails, contact info)
- ✅ Compares products (SKUs, names, prices, stock quantities)
- ✅ Returns detailed JSON diff reports
- ✅ Exits with code 1 if any mismatches found (stops CI/CD)
- ✅ Configurable record limits
- ✅ Environment-aware (staging/production modes)

## Usage

### Manual Execution

```bash
# Run in staging mode (default, checks 100 records)
python scripts/run_data_sync_check.py --mode=staging

# Run in production mode with custom limit
python scripts/run_data_sync_check.py --mode=production --limit=50

# Quick check (10 records)
python scripts/run_data_sync_check.py --limit=10
```

### Required Environment Variables

```bash
# Zoho API Credentials
export ZOHO_ORGANIZATION_ID="your_org_id"
export ZOHO_ACCESS_TOKEN="your_access_token"
export ZOHO_REFRESH_TOKEN="your_refresh_token"

# Database Connection
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="tsh_erp"
export DB_USER="postgres"
export DB_PASSWORD="your_db_password"
```

### GitHub Actions Integration

The sync check runs automatically in the CI/CD pipeline:

1. **On every push to `develop` or `staging` branches**
2. **After integration tests pass**
3. **Before deployment proceeds**

See `.github/workflows/staging-fast.yml` for configuration.

## Output Format

### Success (No Differences)

```json
{
  "status": "ok",
  "differences": 0,
  "checked": 300,
  "mode": "staging",
  "timestamp": "2025-11-02T12:00:00.000000"
}
```

Exit code: `0`

### Failure (Differences Found)

```json
{
  "status": "failed",
  "differences": 5,
  "checked": 300,
  "mode": "staging",
  "timestamp": "2025-11-02T12:00:00.000000",
  "details": [
    {
      "category": "invoice_total_mismatch",
      "detail": "Invoice INV-001 total mismatch",
      "zoho_value": "1500.00",
      "db_value": "1450.00",
      "timestamp": "2025-11-02T12:00:01.000000"
    },
    {
      "category": "product_stock_mismatch",
      "detail": "Product Laptop X stock mismatch",
      "zoho_value": "50",
      "db_value": "45",
      "timestamp": "2025-11-02T12:00:02.000000"
    }
  ]
}
```

Exit code: `1`

## Difference Categories

### Invoices
- `missing_invoice_in_db` - Invoice exists in Zoho but not in database
- `invoice_number_mismatch` - Invoice number differs
- `invoice_total_mismatch` - Total amount differs (tolerance: 0.01)
- `invoice_status_mismatch` - Invoice status differs

### Customers
- `missing_customer_in_db` - Customer exists in Zoho but not in database
- `customer_company_mismatch` - Company name differs
- `customer_email_mismatch` - Email address differs

### Products
- `missing_product_in_db` - Product exists in Zoho but not in database
- `product_name_mismatch` - Product name differs
- `product_sku_mismatch` - SKU differs
- `product_rate_mismatch` - Price/rate differs (tolerance: 0.01)
- `product_stock_mismatch` - Stock quantity differs

### Errors
- `database_connection` - Failed to connect to PostgreSQL
- `zoho_api_error` - Zoho API request failed
- `zoho_json_error` - Invalid JSON from Zoho API
- `database_query_error` - Database query failed

## How It Works

### 1. Data Fetching

**From Zoho:**
- Connects to Zoho Books API (`https://books.zoho.com/api/v3`)
- Fetches recent records sorted by date
- Uses organization ID for multi-org support

**From Database:**
- Connects to PostgreSQL using `psycopg2`
- Queries records with `zoho_*_id` foreign keys
- Matches records by Zoho IDs

### 2. Comparison Logic

For each entity type:
1. Create lookup dictionaries by Zoho ID
2. Check if each Zoho record exists in database
3. Compare key fields with appropriate tolerances:
   - **Decimals/Floats**: 0.01 tolerance (1 cent)
   - **Strings**: Exact match
   - **Integers**: Exact match

### 3. Result Reporting

- Collects all differences in a list
- Returns structured JSON with categories
- Exits with code 1 if any differences found
- GitHub Actions interprets exit code to fail workflow

## CI/CD Integration Flow

```
┌─────────────────────────────────────────────┐
│  Push to develop/staging                    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Quick Tests (linting, security)            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Integration Tests                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  ⭐ Zoho ↔ TSH ERP Data Sync Check ⭐       │
│                                             │
│  1. Copy script to staging server           │
│  2. Install dependencies                    │
│  3. Run: python run_data_sync_check.py      │
│  4. Check exit code                         │
└────────────────┬────────────────────────────┘
                 │
                 ├─── Exit 0 (Success) ───────┐
                 │                            │
                 │                            ▼
                 │              ┌─────────────────────────┐
                 │              │  Deploy to Staging      │
                 │              └─────────────────────────┘
                 │
                 └─── Exit 1 (Failed) ────────┐
                                              │
                                              ▼
                                ┌──────────────────────────┐
                                │  ❌ STOP DEPLOYMENT      │
                                │  Show diff details       │
                                │  Notify team             │
                                └──────────────────────────┘
```

## Troubleshooting

### "Missing required dependency" Error

```bash
pip install requests psycopg2-binary
```

### "Failed to connect to database" Error

Check environment variables:
```bash
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME
```

### "Zoho API request failed" Error

1. Check token expiration
2. Verify organization ID
3. Check network connectivity
4. Review Zoho API rate limits

### False Positives

If legitimate differences exist (e.g., during manual data entry):
1. Review the diff details
2. Sync the data manually
3. Re-run the check
4. Only proceed when sync is confirmed

## Database Schema Requirements

The database must have these tables with Zoho ID columns:

```sql
-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    zoho_invoice_id VARCHAR(255) UNIQUE,
    invoice_number VARCHAR(255),
    customer_name VARCHAR(255),
    total DECIMAL(10,2),
    status VARCHAR(50),
    invoice_date DATE
);

-- Customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    zoho_contact_id VARCHAR(255) UNIQUE,
    company_name VARCHAR(255),
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    zoho_item_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    sku VARCHAR(100),
    rate DECIMAL(10,2),
    stock_quantity INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

## Security Considerations

- **Never commit credentials** to version control
- Use GitHub Secrets for CI/CD environment variables
- Encrypt sensitive data at rest
- Use read-only database user for checks
- Limit API token permissions to read-only

## Performance

- **Default limit**: 100 records per entity (300 total)
- **Typical runtime**: 10-30 seconds
- **Network overhead**: ~3-5 API calls to Zoho
- **Database overhead**: 3 SELECT queries

For production use with thousands of records, consider:
- Running checks off-peak
- Implementing pagination
- Caching Zoho responses
- Using database indexes on `zoho_*_id` columns

## Maintenance

### Adding New Entity Types

1. Add comparison method (e.g., `compare_orders()`)
2. Update `run_check()` to call new method
3. Add database query for new entity
4. Add Zoho API endpoint
5. Define comparison fields
6. Update documentation

### Customizing Tolerances

Edit comparison logic in script:
```python
# Current: 0.01 tolerance for decimals
if abs(zoho_total - db_total) > 0.01:
    # Report difference

# Increase to 0.10 for higher tolerance
if abs(zoho_total - db_total) > 0.10:
    # Report difference
```

## Support

For issues or questions:
1. Check logs: `python run_data_sync_check.py --mode=staging`
2. Review GitHub Actions output
3. Verify credentials and database connectivity
4. Contact system administrator

## License

Part of TSH ERP Ecosystem - Internal Use Only
