# Zoho Integration Testing Guide

**Created**: November 2, 2025
**Workflow**: `.github/workflows/zoho-integration-test.yml`

---

## Overview

Comprehensive GitHub Actions workflow to test Zoho Books/Inventory API connections, webhooks, and database synchronization with real production data.

---

## Features

### 1. Zoho API Connection Tests ✅
- Tests all major Zoho Books endpoints
- Tests Zoho Inventory endpoints
- Validates authentication and token refresh
- Retrieves sample data from each endpoint

### 2. Database Sync Tests ✅
- Creates test database schema
- Syncs data from Zoho → PostgreSQL
- Verifies data integrity
- Tests UPSERT operations (INSERT ... ON CONFLICT UPDATE)

### 3. Webhook Handling Tests ✅
- Simulates incoming Zoho webhooks
- Tests payload processing
- Validates database storage
- Tests different event types

### 4. Automated Reporting ✅
- Generates detailed test reports
- Shows pass/fail status for each suite
- Provides deployment recommendations

---

## Required GitHub Secrets

Before running the workflow, configure these secrets in your GitHub repository:

### Zoho API Credentials

1. **ZOHO_CLIENT_ID**
   ```
   Your Zoho OAuth2 Client ID
   ```

2. **ZOHO_CLIENT_SECRET**
   ```
   Your Zoho OAuth2 Client Secret
   ```

3. **ZOHO_REFRESH_TOKEN**
   ```
   Your Zoho OAuth2 Refresh Token
   ```

4. **ZOHO_ORGANIZATION_ID**
   ```
   Your Zoho Organization ID (found in Zoho Books settings)
   ```

### How to Get Zoho Credentials

#### Step 1: Create Zoho OAuth2 Client

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Click "Add Client"
3. Select "Server-based Applications"
4. Fill in:
   - **Client Name**: TSH ERP Integration
   - **Homepage URL**: https://erp.tsh.sale
   - **Authorized Redirect URIs**: https://erp.tsh.sale/zoho/callback
5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

#### Step 2: Generate Refresh Token

1. Build authorization URL:
   ```
   https://accounts.zoho.com/oauth/v2/auth?
     scope=ZohoBooks.fullaccess.all,ZohoInventory.fullaccess.all&
     client_id=YOUR_CLIENT_ID&
     response_type=code&
     redirect_uri=https://erp.tsh.sale/zoho/callback&
     access_type=offline
   ```

2. Visit the URL in your browser
3. Authorize the application
4. Copy the `code` parameter from the redirect URL

5. Exchange code for refresh token:
   ```bash
   curl -X POST \
     'https://accounts.zoho.com/oauth/v2/token' \
     -d 'code=YOUR_AUTH_CODE' \
     -d 'client_id=YOUR_CLIENT_ID' \
     -d 'client_secret=YOUR_CLIENT_SECRET' \
     -d 'redirect_uri=https://erp.tsh.sale/zoho/callback' \
     -d 'grant_type=authorization_code'
   ```

6. Copy the `refresh_token` from the response

#### Step 3: Find Organization ID

1. Log into [Zoho Books](https://books.zoho.com/)
2. Go to **Settings** → **Organization Profile**
3. Copy the **Organization ID** from the URL:
   ```
   https://books.zoho.com/app/748369814#/...
                              ^^^^^^^^^ This is your Organization ID
   ```

#### Step 4: Add Secrets to GitHub

```bash
gh secret set ZOHO_CLIENT_ID --body "YOUR_CLIENT_ID"
gh secret set ZOHO_CLIENT_SECRET --body "YOUR_CLIENT_SECRET"
gh secret set ZOHO_REFRESH_TOKEN --body "YOUR_REFRESH_TOKEN"
gh secret set ZOHO_ORGANIZATION_ID --body "748369814"
```

---

## Usage

### Manual Trigger (Recommended for First Run)

1. Go to **Actions** tab in GitHub
2. Select "Zoho Integration Tests (Real API & DB)"
3. Click "Run workflow"
4. Select test scope:
   - **all**: Run all tests (API + Database + Webhooks)
   - **api-only**: Test only Zoho API connections
   - **database-only**: Test only database sync
   - **webhooks-only**: Test only webhook handling
5. Click "Run workflow"

### Automatic Triggers

The workflow also runs automatically when:
- Push to `develop` branch with changes to:
  - `zoho/**` files
  - `webhooks/**` files
  - `scripts/zoho_*.py` files

---

## Test Scenarios Covered

### 1. Zoho Books API Tests

Tests these endpoints:
```
✅ GET /books/v3/invoices
✅ GET /books/v3/contacts (customers)
✅ GET /books/v3/items (products)
✅ GET /books/v3/salesorders
✅ GET /books/v3/organizations/{org_id}
```

**Validates**:
- Authentication (access token retrieval)
- API response status codes
- Data structure and fields
- Record counts

### 2. Zoho Inventory API Tests

Tests these endpoints:
```
✅ GET /inventory/v1/items
```

**Validates**:
- Inventory-specific authentication
- Stock quantity data
- SKU information

### 3. Database Sync Tests

**Creates schema**:
- `customers` table (with zoho_contact_id)
- `products` table (with zoho_item_id)
- `invoices` table (with zoho_invoice_id)

**Tests**:
- Fetch 10 customers from Zoho → Insert into DB
- Fetch 10 products from Zoho → Insert into DB
- UPSERT operations (INSERT ... ON CONFLICT UPDATE)
- Data integrity verification

### 4. Webhook Tests

**Simulates webhooks for**:
- `invoice.created`
- `customer.updated`
- `product.stock_updated`

**Validates**:
- Webhook payload storage
- JSON parsing
- Event type categorization
- Timestamp tracking

---

## Expected Output

### Successful Run

```
🧪 Zoho Integration Test Results

Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Zoho API Connections: PASSED
✅ Database Sync: PASSED
✅ Webhook Handling: PASSED

Test Scope: all
Branch: develop
Timestamp: 2025-11-02 08:00:00 UTC

✅ All tests passed! Safe to deploy.
```

### Detailed API Test Output

```
══════════════════════════════════════════════════════════
ZOHO API CONNECTION TESTS
══════════════════════════════════════════════════════════
Timestamp: 2025-11-02T08:00:01.000000

🔑 Authenticating with Zoho...

📡 Testing API Endpoints:
──────────────────────────────────────────────────────────
✅ Invoices API: SUCCESS
   → Found 5 invoices

✅ Customers API: SUCCESS
   → Found 5 contacts

✅ Products API: SUCCESS
   → Found 5 items

✅ Sales Orders API: SUCCESS
   → Found 5 salesorders

✅ Organization Info: SUCCESS

══════════════════════════════════════════════════════════
RESULTS: 5/5 tests passed
══════════════════════════════════════════════════════════
```

### Database Sync Output

```
══════════════════════════════════════════════════════════
ZOHO → DATABASE SYNC TEST
══════════════════════════════════════════════════════════

📥 Syncing customers from Zoho...
✅ Synced 10 customers

📥 Syncing products from Zoho...
✅ Synced 10 products

🔍 Verifying synced data:
──────────────────────────────────────────────────────────
   Customers in DB: 10
   Products in DB: 10
   Invoices in DB: 0

══════════════════════════════════════════════════════════
✅ SYNC COMPLETE: 20 records synced
══════════════════════════════════════════════════════════
```

---

## Troubleshooting

### Error: "Zoho authentication failed"

**Cause**: Expired or invalid refresh token

**Solution**:
1. Generate a new refresh token (see Step 2 above)
2. Update the GitHub secret:
   ```bash
   gh secret set ZOHO_REFRESH_TOKEN --body "NEW_REFRESH_TOKEN"
   ```

### Error: "Missing Zoho credentials"

**Cause**: GitHub secrets not configured

**Solution**:
1. Verify secrets are set:
   ```bash
   gh secret list | grep ZOHO
   ```
2. Add missing secrets (see "Required GitHub Secrets" section)

### Error: "Database connection failed"

**Cause**: PostgreSQL service not running or configuration issue

**Solution**:
- This should not happen in GitHub Actions (uses Docker service)
- If testing locally, ensure PostgreSQL is running:
  ```bash
  sudo systemctl status postgresql
  ```

### Error: "API rate limit exceeded"

**Cause**: Too many API requests to Zoho

**Solution**:
- Wait 1-2 minutes before re-running
- Reduce test data limits in workflow file:
  ```yaml
  per_page=5  # Reduce from 10 to 5
  ```

---

## Performance

### Typical Run Times

| Job | Duration |
|-----|----------|
| Setup Test Environment | 15-20s |
| Test Zoho API | 30-45s |
| Test Database Sync | 40-60s |
| Test Webhooks | 20-30s |
| Generate Report | 5-10s |
| **Total** | **2-3 minutes** |

---

## Advanced Configuration

### Running Specific Test Suites

**API Tests Only**:
```bash
gh workflow run zoho-integration-test.yml \
  -f test_scope=api-only
```

**Database Tests Only**:
```bash
gh workflow run zoho-integration-test.yml \
  -f test_scope=database-only
```

**Webhooks Only**:
```bash
gh workflow run zoho-integration-test.yml \
  -f test_scope=webhooks-only
```

### Using Production Zoho Account

```bash
gh workflow run zoho-integration-test.yml \
  -f test_scope=all \
  -f use_production=true
```

**Note**: The `use_production` flag is for future implementation where you might have separate test/production Zoho accounts.

---

## Integration with CI/CD

### Adding to Staging Workflow

To run Zoho tests before deployment, add to `.github/workflows/staging-fast.yml`:

```yaml
jobs:
  # ... existing jobs ...

  zoho-integration-check:
    name: Verify Zoho Integration
    runs-on: ubuntu-latest
    needs: [backend-tests]
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Zoho tests
        run: gh workflow run zoho-integration-test.yml -f test_scope=all
```

---

## Security Considerations

1. **Never commit credentials** to version control
2. **Use GitHub Secrets** for all sensitive data
3. **Limit API permissions** in Zoho OAuth2 scope
4. **Rotate tokens** regularly (every 90 days)
5. **Monitor API usage** in Zoho Developer Console

---

## Monitoring

### Check Recent Test Runs

```bash
gh run list --workflow=zoho-integration-test.yml --limit 5
```

### View Specific Test Run

```bash
gh run view <RUN_ID>
```

### Watch Live Test Run

```bash
gh run watch <RUN_ID>
```

---

## Next Steps

After successful testing:

1. ✅ Verify all tests pass
2. ✅ Check test report in GitHub Actions summary
3. ✅ Review API response data
4. ✅ Confirm database sync accuracy
5. ✅ Deploy to staging with confidence

---

## Related Documentation

- **Zoho API Docs**: https://www.zoho.com/books/api/v3/
- **Zoho Inventory API**: https://www.zoho.com/inventory/api/v1/
- **OAuth2 Guide**: https://www.zoho.com/accounts/protocol/oauth.html
- **Webhook Setup**: https://www.zoho.com/books/api/v3/webhooks/

---

*Created: November 2, 2025*
*Workflow: `.github/workflows/zoho-integration-test.yml`*
*Status: Ready for testing*
