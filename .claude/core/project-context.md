# TSH ERP Ecosystem - Project Context

**Purpose:** Business context, scale, and migration strategy
**Last Updated:** 2025-11-14
**Load via:** @docs/core/project-context.md

---

## 🎯 Core Business Model

TSH company operates a complete **import-distribution-retail business** in Iraq:

### Supply Chain
```
China Imports → Multi-location Warehouses → Distribution Channels:
                                            ├─ Wholesale (B2B - 500+ clients)
                                            ├─ Retail (B2C - direct consumers)
                                            ├─ Partner Salesmen (100+ social sellers)
                                            └─ Travel Sales (12 field agents, $35K USD/week)
```

### What This System IS
- ✅ **Production system** running real business with real revenue
- ✅ Single company (TSH) - NOT multi-tenant SaaS
- ✅ Iraq-specific (Arabic RTL, IQD currency, local payments)
- ✅ Currently in parallel operation with Zoho Books + Zoho Inventory

### What This System is NOT
- ❌ Multi-tenant SaaS product
- ❌ Open-source demo or template
- ❌ Startup MVP or proof-of-concept
- ❌ Simple CRUD application

---

## 📊 Scale (Always Remember These Numbers)

### Active Users
```
500+ wholesale clients → 30 wholesale orders/day
100+ partner salesmen → Social media sellers across Iraq
12 travel salespersons → $35K USD weekly field sales
30+ daily retail customers → 1M IQD average transaction
Multiple warehouse staff → Multi-location inventory management
Office admin staff → Operations, HR, accounting
```

### Business Volume
- **30 wholesale orders per day**
- **30 retail transactions per day**
- **$35,000 USD weekly** handled by travel salespeople
- **Multi-million IQD daily** transaction volume
- **2,218+ products** in active inventory
- **Multiple warehouse locations** (China + local supply chain)

### Technical Footprint
- **8 specialized mobile applications** (Flutter)
- **3 web applications** (React + Flutter Web)
- **57 database tables** with 127 MB of production data
- **198+ BFF API endpoints**
- **82 utility scripts**
- **Multiple integrations** (Zoho Books, Zoho Inventory, TDS Core, WhatsApp)
- **Real-time GPS tracking** for field teams
- **AWS S3** for database backup and restore

**Impact of Scale:**
- Pagination is **MANDATORY** (not optional)
- Database indexes are **CRITICAL** (not nice-to-have)
- Performance matters (thousands of users affected)
- Security is paramount (real revenue at stake)
- Arabic support is **PRIMARY** (not secondary)

---

## 🔄 Zoho Migration Strategy (CRITICAL Context)

### Current State: Parallel Operation

TSH ERP Ecosystem runs **ALONGSIDE** Zoho Books and Zoho Inventory. We're in a **phased migration**, NOT an immediate replacement.

### Two Zoho Products (Must Understand Both)

#### 📗 Zoho Books (Accounting & Financial)
```yaml
Data Types:
  - Invoices, bills, payments, receipts
  - Customers and vendors
  - Financial transactions, accounts, ledgers
  - Tax calculations, banking transactions
  - Credit notes
  - Purchase orders (financial side)
  - Sales orders (financial side)

API: https://www.zohoapis.com/books/v3/
Organization ID: 748369814
Rate Limit: 100 requests/minute
```

#### 📦 Zoho Inventory (Products & Stock)
```yaml
Data Types:
  - Products (2,218+ items)
  - Stock levels (real-time inventory)
  - Warehouses (multiple locations)
  - Inventory adjustments, stock transfers
  - Composite items, product categories
  - Product images
  - Serial numbers / batch tracking
  - Reorder levels
  - Purchase orders (inventory side)
  - Sales orders (inventory side)

API: https://www.zohoapis.com/inventory/v1/
Organization ID: 748369814
Rate Limit: 100 requests/minute
```

#### Connection Between Both
- Same Zoho organization ID (748369814)
- Data is linked (Invoice in Books references Product from Inventory)
- TDS Core syncs with **BOTH APIs** for complete picture
- Some entities exist in both (Sales Order has financial data in Books, inventory data in Inventory)

---

## 🎯 Migration Phases

### Phase 1: One-Directional Sync (CURRENT)
**Zoho Books + Zoho Inventory → TSH ERP (READ ONLY)**

```
Zoho Books (Master - Financials)
      ↓ (via TDS Core)
Zoho Inventory (Master - Products/Stock)
      ↓ (via TDS Core)
TSH ERP Ecosystem (Slave - Read Only)
```

**What Happens:**
- ✅ All Zoho Books data syncs TO TSH ERP automatically
- ✅ All Zoho Inventory data syncs TO TSH ERP automatically
- ✅ TSH ERP reads and displays combined data
- ❌ TSH ERP does NOT push data back to Zoho yet
- ✅ TDS Core controls ALL sync operations

**Phase 1 Rules:**
- ❌ DO NOT write to Zoho Books or Zoho Inventory from TSH ERP
- ✅ All data entry still happens in Zoho Books and Zoho Inventory
- ✅ TSH ERP is READ-ONLY consumer
- ✅ Focus on data accuracy and completeness
- ✅ Test sync reliability from both APIs

**Phase 1 Success Criteria (via TDS Core):**
- ✅ All Zoho Inventory products synced (2,218+) - DONE
- ✅ All Zoho Inventory stock levels synced - DONE
- ⚠️ All Zoho Books customers synced (500+) - NEEDS VERIFICATION
- ❌ All Zoho Books vendors synced - TODO
- ❌ All Zoho Books sales orders synced - NOT RELIABLE
- ❌ All Zoho Books invoices synced - TODO
- ❌ All Zoho Books payments synced - TODO
- ❌ Product images (700+) - INCOMPLETE
- 99%+ sync success rate, < 30 second latency

**Timeline:** 1 month to complete Phase 1

---

### Phase 2: Two-Directional Sync (TESTING)
**Zoho Books + Zoho Inventory ↔ TSH ERP (Bidirectional - Small Transactions)**

```
Zoho Books (Still Primary - Financials)
      ↕ (via TDS Core)
Zoho Inventory (Still Primary - Products/Stock)
      ↕ (via TDS Core)
TSH ERP Ecosystem (Testing Writes)
```

**What Happens:**
- ✅ Continue reading from both Zoho products
- ✅ Start pushing SMALL transactions from TSH ERP back
- ✅ Test invoice creation → sync to Zoho Books
- ✅ Test order placement → sync to Books + Inventory
- ✅ Test stock adjustments → sync to Inventory
- ✅ Verify data consistency in BOTH directions
- ⚠️ Start with low-risk transactions only

**Phase 2 Rules:**
- ⚠️ Start with NON-CRITICAL transactions only
- ✅ Test thoroughly before production use
- ✅ Monitor sync errors closely for both APIs
- ✅ Have rollback plan ready
- ✅ Keep both Zoho products as source of truth for conflicts

**Objective:** Prove two-way sync works accurately with both products

---

### Phase 3: Gradual TSH ERP Dependence
**TSH ERP becomes primary, Zoho as backup**

```
TSH ERP Ecosystem (Primary - Most Operations)
      ↕ (via TDS Core)
Zoho Books (Secondary - Backup & Verification)
      ↕ (via TDS Core)
Zoho Inventory (Secondary - Backup & Verification)
```

**What Happens:**
- ✅ Most daily operations happen in TSH ERP
- ✅ TSH ERP pushes transactions to both Zoho products for backup
- ✅ Accounting team still uses Zoho Books for final reports
- ✅ Inventory team can verify in Zoho Inventory if needed
- ✅ Test with real business volume (30+ orders/day)

**Phase 3 Rules:**
- ⚠️ Maintain Zoho sync for financial auditing and backup
- ✅ Train staff on TSH ERP interfaces
- ✅ Monitor business operations closely
- ✅ Verify accounting reports match between TSH ERP and Zoho Books

**Success Criteria:**
- 30+ daily orders processed successfully
- All 500+ wholesale clients can place orders
- Mobile apps used by field teams daily
- Financial reports match Zoho Books
- Stock levels match Zoho Inventory
- Staff prefer TSH ERP over Zoho

---

### Phase 4: Complete Independence (GOAL)
**TSH ERP fully independent, Zoho links cut**

```
TSH ERP Ecosystem (Fully Independent)
      ✂️ (Cut the links)
Zoho Books + Inventory (Historical archive only)
```

**What Happens:**
- ✅ TSH ERP operates completely independently
- ✅ No more sync with Zoho Books or Zoho Inventory
- ✅ All operations in TSH ERP only
- ✅ Zoho kept for historical reference
- ✅ Cancel Zoho subscriptions (cost savings)

**Prerequisites:**
- ✅ Run parallel for minimum 3 months
- ✅ Zero critical bugs in TSH ERP
- ✅ All staff trained and comfortable
- ✅ Complete data migration verified from BOTH products
- ✅ Financial auditor approves
- ✅ Management approval

---

## 🎛️ TDS Core: The Sync Orchestrator

**TDS (TSH Data Sync) Core handles ALL Zoho operations:**

### Responsibilities
```yaml
Sync Operations:
  - ALL sync between Zoho Books and TSH ERP
  - ALL sync between Zoho Inventory and TSH ERP
  - Webhook handling from both products
  - Data transformation (Zoho format ↔ TSH ERP format)
  - Conflict resolution
  - Error handling and retry logic
  - Sync monitoring and logging
  - Manual sync triggers when needed

API Management:
  - OAuth 2.0 token refresh for both APIs
  - Rate limit management (100 req/min per API)
  - Circuit breaker pattern
  - Retry with exponential backoff
```

### Architecture
```
Zoho Books API ──────┐
                     ↓
Zoho Inventory API ──┼──→ TDS Core Worker
                     ↓     (process & transform)
                     ↓
              PostgreSQL Database
                     ↓
              TSH ERP Backend API
```

### TDS Dashboard Provides
- Real-time sync status for BOTH Zoho products
- Sync statistics (success/failure rates)
- Error logs and alerts
- Manual sync controls
- Data consistency checks
- API rate limit monitoring

**Critical Rule:** NEVER bypass TDS Core to access Zoho APIs directly

---

## ⏰ Deployment Constraints

### During Development Phase (CURRENT)
```yaml
Freedom: Deploy anytime (24/7)
Reason: Business still runs on Zoho Books + Zoho Inventory
Staging: Use freely for testing
Restrictions: None
```

### During Production Transition (Phase 3+)
```yaml
Caution: Schedule during low-activity hours
Avoid: Peak business hours (9 AM - 5 PM Iraq time)
Method: Zero-downtime blue-green deployments
Always: Test thoroughly in staging first
Always: Have rollback plan ready
Reason: Business operations depend on TSH ERP
```

---

## 💡 Development Principles

### 1. Enhance Before Creating
- **ALWAYS search** existing code first
- Check `/scripts/`, `/mobile/`, `/app/` directories
- Reuse and enhance existing functionality
- Avoid duplicate code or features

### 2. Real Data Matters
- 500+ clients depend on accurate data
- Inventory errors have real financial impact
- Performance issues affect daily operations
- Test with production-scale data (2,218+ products)

### 3. Arabic-First Design
- RTL layout is NOT optional
- Arabic is primary language (not translation afterthought)
- Most users don't speak English
- All user-facing text must support Arabic

### 4. Mobile-First for Field Teams
- Salespeople work primarily on mobile
- GPS tracking critical for travel sales
- Offline capability needed (Iraq connectivity issues)
- Mobile apps are PRIMARY interface for 100+ users

### 5. Performance is Critical
- 30+ orders/day can't wait for slow responses
- Mobile users on potentially slow networks
- Pagination required for 2,218+ products
- Indexes critical for large tables

### 6. Security is Paramount
- Real money transactions
- Customer data protection (GDPR-equivalent)
- Role-based access control (RBAC + ABAC + RLS)
- Financial audit trails

---

## 🌍 Iraq Market Context

### Language & Culture
- **Arabic** is primary language (English secondary)
- **RTL (Right-to-Left)** layout required
- **Iraqi dialect** influences UX copy
- **Cultural considerations** for communication

### Currency & Payments
- **IQD (Iraqi Dinar)** primary currency
- **USD** used for international transactions
- **Cash** still dominant (digital payments growing)
- **Credit terms** common for wholesale (30-90 days)

### Infrastructure Challenges
- **Internet connectivity** can be unreliable
- **Mobile-first** infrastructure (mobile data more reliable)
- **Power outages** common (UPS/backup required)
- **GPS accuracy** varies by region

### Business Practices
- **Relationships matter** in B2B sales
- **Personal service** expected from sales teams
- **Haggling/negotiation** common in retail
- **Family businesses** often have unique requirements

---

## 🎯 Success Metrics

### System Health
- **99.9% uptime** for production
- **< 500ms** API response time average
- **< 30 seconds** Zoho sync latency
- **Zero** data loss incidents

### Business Impact
- **30+ orders/day** processed successfully
- **500+ clients** actively using system
- **12 travel salespersons** completing daily routes
- **100% data accuracy** (match with Zoho)

### User Satisfaction
- **Staff prefer TSH ERP** over Zoho
- **Mobile app adoption** by field teams
- **Reduced support tickets** over time
- **Positive feedback** from clients

---

**For More Details:**
- Technical rules: @docs/core/architecture.md
- Workflows: @docs/core/workflows.md
- Authorization: @docs/AUTHORIZATION_FRAMEWORK.md
- TDS Architecture: @docs/TDS_MASTER_ARCHITECTURE.md
