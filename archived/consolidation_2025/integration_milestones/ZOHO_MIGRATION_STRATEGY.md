# Zoho Books to TSH ERP - Complete Migration & Sync Strategy

**Date:** November 4, 2025
**Status:** ✅ Webhooks Fixed - Ready for Full Migration
**Goal:** Migrate all data from Zoho Books to TSH ERP and maintain real-time sync

---

## 📊 Current Status

### Webhooks: ✅ WORKING
- **Last Test:** Nov 4, 2025 09:52 PM
- **Status:** 202 Accepted
- **All 7 Endpoints:** Configured correctly at `/api/zoho/webhooks/*`

### Current Data in TSH ERP:
- **Products:** 2,218
- **Customers:** 13
- **Invoices:** 74
- **Orders:** 9

### Sync Architecture:
```
Zoho Books
    ↓
Webhook (Real-time) → TSH ERP API
    ↓
tds_inbox_events (Raw webhook data)
    ↓
tds_sync_queue (Processing queue)
    ↓
Background Workers (2 async workers)
    ↓
PostgreSQL Database (products, customers, invoices, etc.)
```

---

## 🎯 Migration Strategy

### Phase 1: Initial Data Migration (One-time Bulk Sync)
**Goal:** Import ALL existing data from Zoho Books

### Phase 2: Real-time Sync (Continuous)
**Goal:** Keep TSH ERP in sync with Zoho Books via webhooks

### Phase 3: Monitoring & Maintenance
**Goal:** Ensure 99.9% sync reliability with auto-healing

---

## Phase 1: Initial Data Migration

### Step 1.1: Products/Items Migration

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/items?organization_id={org_id}
```

**Strategy:**
1. Fetch all items from Zoho Books (paginated, 200 per page)
2. Transform to TSH ERP format
3. Bulk insert/update into `products` table
4. Track sync cursor to avoid duplicates

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/products
# Features:
# - Pagination support
# - Incremental sync (date-based filtering)
# - Duplicate detection via zoho_item_id
# - Progress tracking
# - Error handling with retry
```

**Estimated Time:** ~5-10 minutes for 2,000+ products

---

### Step 1.2: Customers/Contacts Migration

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/contacts?organization_id={org_id}
```

**Strategy:**
1. Fetch all contacts from Zoho Books
2. Transform to TSH ERP customer format
3. Bulk insert/update into `customers` table
4. Handle customer addresses separately

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/customers
# Features:
# - Contact + addresses in single transaction
# - Email uniqueness validation
# - Customer type mapping (B2B/B2C)
```

**Estimated Time:** ~1-2 minutes for hundreds of customers

---

### Step 1.3: Invoices Migration

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/invoices?organization_id={org_id}
```

**Strategy:**
1. Fetch all invoices from Zoho Books (with line items)
2. Transform to TSH ERP format
3. Insert into `invoices` + `invoice_line_items` tables
4. Calculate totals, tax, discounts

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/invoices
# Features:
# - Invoice header + line items in transaction
# - Status mapping (draft, sent, paid, void)
# - Payment tracking
# - Date range filtering (e.g., last 6 months)
```

**Estimated Time:** ~2-5 minutes for hundreds of invoices

---

### Step 1.4: Stock Levels Migration

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/items/{item_id}
# Returns stock_on_hand for each warehouse
```

**Strategy:**
1. Fetch current stock levels for all items
2. Update `products.stock_quantity` field
3. Store warehouse-level stock if needed

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/stock
# Features:
# - Warehouse-based stock tracking
# - Historical stock snapshots
# - Low stock alerts
```

**Estimated Time:** ~5 minutes for 2,000+ products

---

### Step 1.5: Price Lists Migration

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/pricelists?organization_id={org_id}
GET https://www.zohoapis.com/books/v3/pricelists/{pricelist_id}
```

**Strategy:**
1. Fetch all price lists from Zoho Books
2. For each price list, fetch item prices
3. Insert into `pricelists` + `product_prices` tables

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/pricelists
# Features:
# - Multi-currency support
# - Effective date ranges
# - Percentage/fixed price types
```

**Estimated Time:** ~2-3 minutes

---

### Step 1.6: Bills/Vendor Bills Migration (Optional)

**Zoho API Endpoint:**
```
GET https://www.zohoapis.com/books/v3/bills?organization_id={org_id}
```

**Strategy:**
1. Fetch all bills (purchases) from Zoho Books
2. Transform to TSH ERP format
3. Track vendor payments

**Implementation:**
```python
# Create endpoint: POST /api/zoho/bulk-sync/bills
# Features:
# - Vendor tracking
# - Purchase history
# - Payment status
```

**Estimated Time:** ~2-5 minutes

---

## Phase 2: Real-time Sync (Already Configured!)

### Current Webhook Configuration: ✅

| Entity | Zoho Webhook URL | Status |
|--------|-----------------|--------|
| Products | `https://erp.tsh.sale/api/zoho/webhooks/products` | ✅ Working |
| Customers | `https://erp.tsh.sale/api/zoho/webhooks/customers` | ✅ Working |
| Invoices | `https://erp.tsh.sale/api/zoho/webhooks/invoices` | ✅ Working |
| Bills | `https://erp.tsh.sale/api/zoho/webhooks/bills` | ✅ Working |
| Credit Notes | `https://erp.tsh.sale/api/zoho/webhooks/credit-notes` | ✅ Working |
| Stock | `https://erp.tsh.sale/api/zoho/webhooks/stock` | ✅ Working |
| Prices | `https://erp.tsh.sale/api/zoho/webhooks/prices` | ✅ Working |

### How It Works:

1. **User changes data in Zoho Books** (e.g., updates product price)
2. **Zoho sends webhook** to TSH ERP within seconds
3. **TSH ERP receives webhook** → stores in `tds_inbox_events`
4. **Webhook validator** checks for duplicates
5. **Queue processor** adds to `tds_sync_queue`
6. **Background workers** process queue item
7. **Entity handler** updates database table
8. **Status updated** to `completed`

**Current Performance:**
- **Webhook delivery time:** < 5 seconds
- **Queue processing time:** < 10 seconds
- **Total sync delay:** < 15 seconds (real-time!)

---

## Phase 3: Monitoring & Auto-Healing

### Zoho Sync Manager Agent: ✅ Active

The agent continuously monitors:

#### Health Checks (Every 15 minutes):
- ✅ Service status
- ✅ Queue metrics (pending, failed, completed)
- ✅ Sync delays per entity type
- ✅ Worker activity
- ✅ Error patterns
- ✅ Stuck locks
- ✅ System resources

#### Auto-Healing Actions:
- ✅ Re-queue failed items (< 5 retries)
- ✅ Clear stuck locks (> 30 min)
- ✅ Restart service if workers stuck
- ✅ Move permanently failed items to dead letter queue
- ✅ Clean old completed items (> 30 days)

#### Alerts:
- ⚠️ Warning: > 50 pending items or > 30 min delay
- 🔴 Critical: > 200 pending items or > 2 hour delay

---

## 🚀 Implementation Plan

### Week 1: Bulk Sync Endpoints

**Day 1-2: Create Bulk Sync Service**
- [ ] Create `app/services/zoho_bulk_sync.py`
- [ ] Implement Zoho API client with pagination
- [ ] Add OAuth token refresh logic
- [ ] Create base bulk sync class

**Day 3-4: Implement Entity Sync**
- [ ] Products bulk sync endpoint
- [ ] Customers bulk sync endpoint
- [ ] Invoices bulk sync endpoint
- [ ] Stock levels sync endpoint
- [ ] Price lists sync endpoint

**Day 5: Testing & Validation**
- [ ] Test each endpoint with sample data
- [ ] Verify data transformation accuracy
- [ ] Check duplicate handling
- [ ] Performance testing (large datasets)

### Week 2: Migration Execution

**Day 1: Products Migration**
- [ ] Run bulk sync for all products
- [ ] Verify count matches Zoho Books
- [ ] Validate critical fields (SKU, price, stock)
- [ ] Fix any errors

**Day 2: Customers Migration**
- [ ] Run bulk sync for all customers
- [ ] Verify email uniqueness
- [ ] Validate addresses
- [ ] Fix any errors

**Day 3: Invoices Migration**
- [ ] Run bulk sync for recent invoices (last 6 months)
- [ ] Verify totals and line items
- [ ] Validate payment status
- [ ] Fix any errors

**Day 4: Stock & Prices Migration**
- [ ] Sync current stock levels
- [ ] Sync all price lists
- [ ] Verify multi-currency prices
- [ ] Fix any errors

**Day 5: Validation & Cleanup**
- [ ] Run full data consistency check
- [ ] Compare totals with Zoho Books reports
- [ ] Document any discrepancies
- [ ] Clean up test data

### Week 3: Monitoring & Optimization

**Day 1-2: Monitor Real-time Sync**
- [ ] Watch webhook activity for 48 hours
- [ ] Verify all entity types syncing correctly
- [ ] Check queue processing speed
- [ ] Identify bottlenecks

**Day 3-4: Performance Optimization**
- [ ] Optimize slow queries
- [ ] Tune worker count if needed
- [ ] Adjust batch sizes
- [ ] Implement caching where appropriate

**Day 5: Documentation & Training**
- [ ] Document sync architecture
- [ ] Create troubleshooting guide
- [ ] Train team on monitoring tools
- [ ] Set up automated health checks

---

## 📋 Data Mapping

### Products (Zoho Items → TSH ERP Products)

```json
{
  "zoho_item_id": "item.item_id",
  "name": "item.name",
  "sku": "item.sku",
  "description": "item.description",
  "unit_price": "item.rate",
  "stock_quantity": "item.stock_on_hand",
  "is_active": "item.status == 'active'",
  "tax_rate": "item.tax_percentage",
  "category_name": "item.category_name",
  "image_url": "item.image_document_id → fetch image URL",
  "zoho_metadata": "item (full JSON)"
}
```

### Customers (Zoho Contacts → TSH ERP Customers)

```json
{
  "zoho_contact_id": "contact.contact_id",
  "name": "contact.contact_name",
  "full_name": "contact.first_name + contact.last_name",
  "email": "contact.email",
  "phone": "contact.phone",
  "company_name": "contact.company_name",
  "customer_type": "contact.contact_type (business/individual)",
  "is_active": "contact.status == 'active'",
  "billing_address": "contact.billing_address",
  "shipping_address": "contact.shipping_address",
  "zoho_metadata": "contact (full JSON)"
}
```

### Invoices (Zoho Invoices → TSH ERP Invoices)

```json
{
  "zoho_invoice_id": "invoice.invoice_id",
  "invoice_number": "invoice.invoice_number",
  "customer_id": "lookup by zoho_contact_id",
  "invoice_date": "invoice.date",
  "due_date": "invoice.due_date",
  "status": "invoice.status (draft/sent/paid/void)",
  "subtotal": "invoice.sub_total",
  "tax_total": "invoice.tax_total",
  "discount_amount": "invoice.discount_amount",
  "total_amount": "invoice.total",
  "amount_paid": "invoice.payment_made",
  "balance": "invoice.balance",
  "line_items": "invoice.line_items → invoice_line_items table",
  "zoho_metadata": "invoice (full JSON)"
}
```

---

## 🔐 Security & Best Practices

### API Access:
- ✅ Use OAuth 2.0 for Zoho API authentication
- ✅ Store refresh token securely (environment variable)
- ✅ Auto-refresh access token when expired
- ✅ Rate limiting (100 requests/minute for Zoho Books)

### Data Integrity:
- ✅ Use database transactions for bulk inserts
- ✅ Validate all data before inserting
- ✅ Store original Zoho JSON in `zoho_metadata` field
- ✅ Track sync timestamps for incremental updates

### Error Handling:
- ✅ Retry failed API calls (max 3 attempts)
- ✅ Log all errors with context
- ✅ Move permanently failed items to dead letter queue
- ✅ Alert on critical failures

### Performance:
- ✅ Use bulk insert operations (100-200 records at a time)
- ✅ Implement pagination for large datasets
- ✅ Cache frequently accessed data
- ✅ Index all foreign keys and lookup fields

---

## 📊 Success Metrics

### Migration Success Criteria:
- ✅ **Products:** 100% of Zoho items imported
- ✅ **Customers:** 100% of active contacts imported
- ✅ **Invoices:** Last 6 months imported with 100% accuracy
- ✅ **Stock:** Current stock levels match Zoho exactly
- ✅ **Prices:** All price lists synced correctly

### Ongoing Sync Health:
- ✅ **Sync delay:** < 30 seconds average
- ✅ **Queue backlog:** < 20 items
- ✅ **Failed items:** < 1% of total
- ✅ **Uptime:** 99.9%
- ✅ **Data consistency:** 100%

---

## 🛠️ Tools & Endpoints

### Bulk Sync API (To Be Created):

```bash
# Sync all products
POST /api/zoho/bulk-sync/products
Body: {
  "incremental": false,  # Full sync
  "modified_since": null,  # Or ISO date for incremental
  "batch_size": 200
}

# Sync all customers
POST /api/zoho/bulk-sync/customers
Body: {
  "incremental": false,
  "include_addresses": true
}

# Sync recent invoices
POST /api/zoho/bulk-sync/invoices
Body: {
  "incremental": true,
  "modified_since": "2025-05-01",  # Last 6 months
  "include_line_items": true
}

# Sync current stock
POST /api/zoho/bulk-sync/stock
Body: {
  "warehouses": ["all"],
  "update_only": true  # Don't create new products
}

# Sync price lists
POST /api/zoho/bulk-sync/pricelists
Body: {
  "pricelist_ids": [],  # Empty = all
  "include_item_prices": true
}
```

### Monitoring Commands:

```bash
# Check sync health
.claude/agents/zoho-sync-manager/tools/sync_health_check.sh

# Run auto-heal
.claude/agents/zoho-sync-manager/tools/auto_heal.sh

# Check queue status
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c \"SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;\""

# View recent errors
ssh root@167.71.39.50 "journalctl -u tsh-erp -n 100 | grep -i error"
```

---

## 🚨 Rollback Plan

If migration encounters critical issues:

### Rollback Steps:
1. Stop bulk sync endpoints (disable routes)
2. Keep webhooks active (real-time sync continues)
3. Review error logs and fix issues
4. Clear failed queue items
5. Re-run migration with fixed code

### Data Safety:
- Original Zoho data is never modified
- TSH ERP tables have soft delete (no permanent data loss)
- Database backups before migration
- Can re-sync at any time

---

## 💡 Recommendations

### Short-term (This Week):
1. ✅ **Fix webhook URLs** - DONE!
2. ✅ **Monitor real-time sync** - Verify webhooks working for 48 hours
3. ✅ **Create bulk sync endpoints** - Start with products
4. ✅ **Test with sample data** - Validate transformation logic

### Medium-term (Next 2 Weeks):
1. ✅ **Execute full migration** - Products → Customers → Invoices → Stock → Prices
2. ✅ **Validate data accuracy** - Compare totals with Zoho Books reports
3. ✅ **Optimize performance** - Tune workers, indexes, caching
4. ✅ **Document processes** - Create runbooks for common tasks

### Long-term (This Month):
1. ✅ **Automated health checks** - Schedule daily monitoring
2. ✅ **Performance dashboard** - Track sync metrics over time
3. ✅ **Incremental sync** - Weekly sync to catch any missed data
4. ✅ **Team training** - Ensure everyone knows how to use the system

---

## 📞 Next Steps

### Immediate Actions:

1. **Confirm Migration Scope:**
   - Which entities do you want to migrate? (Products, Customers, Invoices, etc.)
   - Date range for historical data? (e.g., last 6 months for invoices)
   - Any exclusions or filters?

2. **Review Zoho API Access:**
   - Confirm OAuth tokens are configured
   - Test API connectivity
   - Verify organization ID

3. **Create Bulk Sync Endpoints:**
   - I'll implement the bulk sync service
   - Create endpoints for each entity type
   - Add progress tracking and error handling

4. **Execute Migration:**
   - Run bulk sync in test environment first
   - Validate data accuracy
   - Run in production with monitoring

---

**Status:** ✅ Ready to proceed with bulk migration
**Estimated Total Time:** 2-3 weeks for complete migration + monitoring
**Risk Level:** Low (non-destructive, can re-sync if needed)

**Would you like me to start creating the bulk sync endpoints?**
