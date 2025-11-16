# Phase 1 Requirements - Complete Zoho Sync via TDS Core

**Created:** November 13, 2025
**Authority Level:** CRITICAL - PHASE 1 COMPLETION
**Timeline:** 1 Month
**Last Updated:** November 13, 2025

---

## 🎯 Phase 1 Goal

**Achieve reliable and stable real-time sync from Zoho → TSH ERP for ALL business entities**

**Status:** IN PROGRESS (Month 1 of 1)

---

## 🚨 CRITICAL RULE: ALL SYNC VIA TDS CORE

```yaml
MANDATORY:
  ✅ ALL sync operations MUST go through TDS Core
  ✅ TDS Core is located at: app/tds/
  ✅ NEVER bypass TDS Core for direct Zoho API access
  ✅ NEVER create separate sync scripts outside TDS

TDS Core Responsibilities:
  ✅ Zoho Books API integration
  ✅ Zoho Inventory API integration
  ✅ Data transformation via processors
  ✅ Webhook handling
  ✅ Retry logic and error handling
  ✅ Monitoring and statistics
```

---

## 📋 Current TDS Core Status

### ✅ Existing Processors (Working)
```yaml
Products: app/tds/integrations/zoho/processors/products.py
  - Syncs 2,218+ products
  - Includes stock levels
  - Status: ✅ Working (100% success rate)

Customers: app/tds/integrations/zoho/processors/customers.py
  - Syncs customer data
  - Status: ⚠️ Needs verification

Inventory: app/tds/integrations/zoho/processors/inventory.py
  - Syncs inventory data
  - Status: ⚠️ Needs verification

Orders: app/tds/integrations/zoho/processors/orders.py
  - Syncs orders
  - Status: ❌ NOT RELIABLE

Pricelists: app/tds/integrations/zoho/processors/pricelists.py
  - Syncs price lists
  - Status: ⚠️ Needs verification

Price List Items: app/tds/integrations/zoho/processors/price_list_items.py
  - Syncs price list items
  - Status: ⚠️ Needs verification
```

### ❌ Missing Processors (Need to Build)
```yaml
Invoices Processor: MISSING
  - Need: Sync all invoices from Zoho Books
  - Priority: HIGH

Payments Processor: MISSING
  - Need: Sync all payment received from Zoho Books
  - Priority: HIGH

Credit Notes Processor: MISSING
  - Need: Sync all credit notes from Zoho Books
  - Priority: HIGH

Bills Processor: MISSING
  - Need: Sync all purchase bills from Zoho Books
  - Priority: HIGH

Vendors Processor: MISSING
  - Need: Sync all vendors/suppliers from Zoho Books
  - Priority: HIGH

Users Processor: MISSING
  - Need: Sync all users from Zoho Books
  - Priority: MEDIUM

Sales Orders Processor: MISSING or BROKEN
  - Need: Verify/fix sales orders sync
  - Priority: HIGH
```

### ⚠️ Other Issues
```yaml
Product Images: INCOMPLETE
  - Need: Download all 700+ product images
  - Via: app/tds/integrations/zoho/image_sync.py
  - Status: ❌ NOT COMPLETE

Webhooks: CONFIGURED but NOT VERIFIED
  - Status: ⚠️ Need to verify receiving data
  - Location: app/tds/api/webhooks.py
```

---

## 📊 Phase 1 Requirements Checklist

### Week 1: TDS Core Audit & Verification

#### Task 1.1: Verify TDS Core Health
```yaml
□ Check TDS Core is running
  - Service status
  - No crashes or errors
  - Logs are clean

□ Check TDS Core components:
  - Webhook endpoints responding
  - Queue system working
  - Retry mechanism working
  - Monitoring dashboard accessible
```

#### Task 1.2: Audit Current Sync Coverage
```yaml
□ Verify Products sync:
  - Count: Should be 2,218+
  - Stock levels included
  - All fields populated
  - No NULL critical fields

□ Verify Customers sync:
  - Count: Should be 500+
  - All fields populated
  - Contact persons included

□ Test Orders sync:
  - Is it syncing at all?
  - Historical orders included?
  - Real-time updates working?

□ Test Pricelists sync:
  - All price lists synced
  - Price list items synced
  - Consumer prices correct
```

#### Task 1.3: Document Missing Entities
```yaml
□ List ALL entities in Zoho Books that are NOT syncing
□ List ALL entities in Zoho Inventory that are NOT syncing
□ Prioritize by business criticality
□ Create implementation plan
```

---

### Week 2: Build Missing Processors

#### Task 2.1: Invoices Processor
```yaml
Location: app/tds/integrations/zoho/processors/invoices.py

Requirements:
□ Sync all historical invoices
□ Sync new invoices in real-time (webhook)
□ Include invoice line items
□ Include tax calculations
□ Include payment status
□ Map to TSH ERP invoices table

Fields Required:
  - invoice_id (Zoho ID)
  - invoice_number
  - customer_id
  - invoice_date
  - due_date
  - line_items (JSON)
  - subtotal
  - tax_total
  - total
  - balance (unpaid amount)
  - status (draft, sent, paid, overdue, void)
  - currency
```

#### Task 2.2: Payments Processor
```yaml
Location: app/tds/integrations/zoho/processors/payments.py

Requirements:
□ Sync all payment received from Zoho Books
□ Sync new payments in real-time (webhook)
□ Link payments to invoices
□ Include payment method
□ Include payment date

Fields Required:
  - payment_id (Zoho ID)
  - payment_number
  - customer_id
  - invoice_id (or multiple invoices)
  - payment_date
  - amount
  - payment_mode (cash, bank, card, etc.)
  - reference_number
  - notes
```

#### Task 2.3: Credit Notes Processor
```yaml
Location: app/tds/integrations/zoho/processors/credit_notes.py

Requirements:
□ Sync all credit notes from Zoho Books
□ Sync new credit notes in real-time (webhook)
□ Link to original invoice
□ Include refund status

Fields Required:
  - creditnote_id (Zoho ID)
  - creditnote_number
  - customer_id
  - invoice_id (if linked)
  - date
  - line_items (JSON)
  - total
  - balance (unused amount)
  - status
  - refund_mode
```

#### Task 2.4: Bills Processor
```yaml
Location: app/tds/integrations/zoho/processors/bills.py

Requirements:
□ Sync all purchase bills from Zoho Books
□ Sync new bills in real-time (webhook)
□ Include vendor information
□ Include payment status

Fields Required:
  - bill_id (Zoho ID)
  - bill_number
  - vendor_id
  - bill_date
  - due_date
  - line_items (JSON)
  - subtotal
  - tax_total
  - total
  - balance (unpaid amount)
  - status
```

#### Task 2.5: Vendors Processor
```yaml
Location: app/tds/integrations/zoho/processors/vendors.py

Requirements:
□ Sync all vendors/suppliers from Zoho Books
□ Sync new vendors in real-time (webhook)
□ Include contact details
□ Include payment terms

Fields Required:
  - vendor_id (Zoho ID)
  - vendor_name
  - vendor_name_ar (if available)
  - contact_persons (JSON)
  - email
  - phone
  - address
  - payment_terms
  - currency
  - status
```

#### Task 2.6: Users Processor
```yaml
Location: app/tds/integrations/zoho/processors/users.py

Requirements:
□ Sync all users from Zoho Books
□ Include role information
□ Include permissions

Fields Required:
  - user_id (Zoho ID)
  - name
  - email
  - role
  - status (active, inactive)
  - permissions (JSON)
```

#### Task 2.7: Sales Orders Processor (Fix/Verify)
```yaml
Location: app/tds/integrations/zoho/processors/orders.py (exists but broken)

Requirements:
□ Verify existing processor
□ Fix reliability issues
□ Sync all historical sales orders
□ Sync new orders in real-time (webhook)
□ Include order line items
□ Include shipment status

Fields Required:
  - salesorder_id (Zoho ID)
  - salesorder_number
  - customer_id
  - date
  - shipment_date
  - line_items (JSON)
  - subtotal
  - tax_total
  - total
  - status (draft, open, invoiced, void)
```

---

### Week 3: Complete Images & Test Webhooks

#### Task 3.1: Complete Product Images Download
```yaml
Via: app/tds/integrations/zoho/image_sync.py

Requirements:
□ Download ALL 700+ product images
□ Store in: /home/deploy/TSH_ERP_Ecosystem/uploads/products/
□ Update products.image_url with local paths
□ Verify all images accessible via web

Process:
1. Query products with Zoho image URLs
2. Download each image with retry logic
3. Save with format: {zoho_item_id}.jpg
4. Update database: image_url = '/uploads/products/{zoho_item_id}.jpg'
5. Create symlinks if needed
6. Verify via: curl https://erp.tsh.sale/product-images/{zoho_item_id}.jpg
```

#### Task 3.2: Verify Webhook Configuration
```yaml
Webhook Endpoints: app/tds/api/webhooks.py

Verify webhooks configured in Zoho Books for:
□ Products (create, update, delete)
□ Customers (create, update)
□ Sales Orders (create, update)
□ Invoices (create, update)
□ Payments (create)
□ Credit Notes (create, update)
□ Bills (create, update)
□ Vendors (create, update)

Verify webhooks configured in Zoho Inventory for:
□ Products (create, update)
□ Stock adjustments

Test Process:
1. Create test entity in Zoho
2. Verify webhook received in TDS logs
3. Verify data synced to database
4. Verify within 30 seconds
```

---

### Week 4: Testing & Stabilization

#### Task 4.1: Data Verification Script
```yaml
Create: scripts/verify_phase1_sync.sh

Verify ALL entities synced:
□ Products count: Zoho vs TSH ERP (should match 2,218+)
□ Customers count: Zoho vs TSH ERP (should match 500+)
□ Sales Orders count: Zoho vs TSH ERP
□ Invoices count: Zoho vs TSH ERP
□ Payments count: Zoho vs TSH ERP
□ Credit Notes count: Zoho vs TSH ERP
□ Bills count: Zoho vs TSH ERP
□ Vendors count: Zoho vs TSH ERP
□ Users count: Zoho vs TSH ERP
□ Images count: Database vs file system (should be 700+)

Alert if ANY mismatch > 1%
```

#### Task 4.2: Load Testing
```yaml
Test TDS Core Performance:
□ Simulate 100 webhook calls in 1 minute
□ Simulate bulk sync of 1,000+ records
□ Measure sync latency (should be < 30 seconds)
□ Verify no memory leaks
□ Verify no database locks
```

#### Task 4.3: 7-Day Stability Test
```yaml
Monitor TDS Core for 7 consecutive days:
□ Zero crashes
□ 99%+ sync success rate
□ All webhooks processed within 30 seconds
□ No manual intervention needed
□ All data matches Zoho
```

---

## ✅ Phase 1 Success Criteria

### Data Completeness
```yaml
✓ Products: 2,218+ synced with stock levels
✓ Customers: 500+ synced with contacts
✓ Sales Orders: ALL historical + real-time
✓ Invoices: ALL historical + real-time
✓ Payments: ALL historical + real-time
✓ Credit Notes: ALL historical + real-time
✓ Bills: ALL historical + real-time
✓ Vendors: ALL synced
✓ Users: ALL synced
✓ Images: 700+ downloaded and accessible
```

### Sync Reliability
```yaml
✓ 99%+ sync success rate
✓ Real-time sync latency < 30 seconds
✓ Zero sync failures for 7 consecutive days
✓ Automatic retry working for failures
✓ Circuit breaker working for Zoho API issues
✓ No manual intervention needed
```

### Data Accuracy
```yaml
✓ ALL entities match Zoho 100%
✓ Stock levels match Zoho (±0 tolerance)
✓ Invoice totals match Zoho exactly
✓ Payment amounts match Zoho exactly
✓ No NULL values in critical fields
```

### System Health
```yaml
✓ TDS Core runs 24/7 without crashes
✓ TDS Dashboard shows green status
✓ All webhook endpoints responding < 500ms
✓ Monitoring and alerts working
✓ Logs are clean (no critical errors)
```

### Team Confidence
```yaml
✓ Khaleel trusts the sync is working
✓ Staff can view all data in TSH ERP
✓ No data discrepancies reported
✓ Ready to attempt Phase 2 testing
```

---

## 🔧 Implementation Notes

### TDS Core Architecture
```
app/tds/
├── api/
│   └── webhooks.py           # Webhook endpoints
├── core/
│   ├── events.py             # Event system
│   ├── queue.py              # Sync queue
│   └── service.py            # Core service
├── integrations/
│   └── zoho/
│       ├── client.py         # UnifiedZohoClient (ONLY Zoho access)
│       ├── auth.py           # Authentication
│       ├── processors/       # Entity processors
│       │   ├── products.py
│       │   ├── customers.py
│       │   ├── orders.py
│       │   ├── invoices.py   # ← CREATE THIS
│       │   ├── payments.py   # ← CREATE THIS
│       │   ├── credit_notes.py  # ← CREATE THIS
│       │   ├── bills.py      # ← CREATE THIS
│       │   ├── vendors.py    # ← CREATE THIS
│       │   └── users.py      # ← CREATE THIS
│       ├── image_sync.py     # Image download
│       └── webhooks.py       # Webhook handlers
├── services/
│   ├── monitoring.py         # Monitoring
│   ├── alerts.py             # Alerting
│   └── auto_healing.py       # Auto-recovery
└── utils/
    ├── retry.py              # Retry logic
    ├── rate_limiter.py       # Rate limiting
    └── circuit_breaker.py    # Circuit breaker
```

### Processor Pattern
```python
# Each processor follows this pattern:
class EntityProcessor:
    def __init__(self, db_session):
        self.db = db_session

    async def transform(self, zoho_data: dict) -> dict:
        """Transform Zoho format to TSH ERP format"""
        return {
            # Map Zoho fields to TSH ERP fields
        }

    async def validate(self, data: dict) -> bool:
        """Validate data before saving"""
        # Check required fields
        # Validate data types
        # Check business rules
        return True

    async def save(self, data: dict):
        """Save to database"""
        # Create or update record
        # Handle relationships
        # Commit transaction
```

---

## 🚨 Critical Reminders

### ❌ NEVER Do This:
```python
# ❌ WRONG - Direct Zoho API access
import requests
response = requests.get("https://www.zohoapis.com/books/v3/invoices")

# ❌ WRONG - Separate sync script outside TDS
def sync_invoices():
    invoices = zoho.get_invoices()
    for inv in invoices:
        db.save(inv)
```

### ✅ ALWAYS Do This:
```python
# ✅ CORRECT - Use TDS Core
from app.tds.integrations.zoho.client import UnifiedZohoClient
from app.tds.integrations.zoho.processors.invoices import InvoiceProcessor

async with UnifiedZohoClient() as client:
    invoices = await client.get_invoices()
    processor = InvoiceProcessor(db_session)
    for invoice in invoices:
        data = await processor.transform(invoice)
        if await processor.validate(data):
            await processor.save(data)
```

---

## 📊 Progress Tracking

Use todo list to track:
- [ ] Week 1: TDS Core audit complete
- [ ] Week 2: All processors built and tested
- [ ] Week 3: Images complete, webhooks verified
- [ ] Week 4: 7-day stability test passed
- [ ] Phase 1: SUCCESS CRITERIA MET

---

**Last Updated:** November 13, 2025
**Status:** IN PROGRESS
**Next Milestone:** Week 1 Audit Complete
**Estimated Completion:** December 13, 2025

---

**END OF PHASE 1 REQUIREMENTS**
