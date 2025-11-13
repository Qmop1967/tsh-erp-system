# TSH ERP Ecosystem - Project Vision & Core Principles

**Last Updated:** 2025-11-12
**Read this FIRST in every new session**

---

## 🎯 THE CORE IDEA

We are building a **complete ERP ecosystem for TSH company's import-distribution-retail business** operating in Iraq. This system handles the ENTIRE supply chain from:
- **China imports** (bulk orders)
- **Local vendor purchases** (supplementary)
- **Multi-location warehousing** (inventory management)
- **Wholesale distribution** (B2B to 500+ clients)
- **Retail sales** (B2C direct to consumers)

**This is NOT:**
- ❌ A generic multi-tenant SaaS product
- ❌ An open-source demo or template
- ❌ A startup MVP or proof-of-concept
- ❌ A simple CRUD application

**This IS:**
- ✅ A **PRODUCTION SYSTEM** running a real business with real revenue
- ✅ Single company (TSH) - not multi-tenant
- ✅ Iraq-specific (Arabic RTL, IQD currency, local payment methods)
- ✅ Currently in **parallel operation with Zoho Books + Zoho Inventory** (transitioning)

---

## 📊 THE SCALE (Never Forget These Numbers)

### Active Users
- **500+ wholesale clients** - Place 30 wholesale orders daily
- **100+ partner salesmen** - Social media sellers across all Iraq cities
- **12 travel salespersons** - Handle $35K USD weekly in field operations
- **30 daily retail customers** - Average 1M IQD per transaction
- **Multiple warehouse staff** - Managing multi-location inventory
- **Office admin staff** - Managing operations, HR, accounting

### Business Volume
- **30 wholesale orders per day**
- **30 retail transactions per day**
- **$35,000 USD weekly** handled by travel salespeople
- **Multi-million IQD daily** transaction volume
- **2,218+ products** in active inventory
- **Multiple warehouse locations** (China + local supply chain)

### Technical Scale
- **8 specialized mobile applications** (Flutter)
- **3 web applications** (React + Flutter Web)
- **57 database tables** with 127 MB of production data
- **Multiple integrations** (Zoho Books, Zoho Inventory, TDS Core, WhatsApp)
- **Real-time GPS tracking** for field teams
- **AWS S3** for database backup and restore

---

## 🏗️ ARCHITECTURE CONSTRAINTS (NON-NEGOTIABLE)

### Technology Stack
```yaml
Backend:
  - Language: Python 3.9+
  - Framework: FastAPI (NO Django, NO Flask)
  - Database: PostgreSQL 12+ (single source of truth)
  - ORM: SQLAlchemy
  - Auth: JWT tokens

Frontend Web:
  - ERP Admin: React 18+ with TypeScript
  - Consumer Shop: Flutter Web
  - TDS Dashboard: React with shadcn/ui

Mobile:
  - Framework: Flutter 3.0+ (ALL 8 apps)
  - Platforms: iOS & Android
  - Native Performance: Required (not hybrid WebView)

Infrastructure:
  - Hosting: VPS (167.71.39.50)
  - Containers: Docker + Docker Compose
  - Reverse Proxy: Nginx
  - Deployment: GitHub Actions → VPS
  - Backup: AWS S3 (database backup and restore)

Integrations:
  - Zoho Books API - Currently in production (accounting, financials)
  - Zoho Inventory API - Currently in production (products, stock)
  - TDS Core - Sync orchestrator (controls ALL Zoho ↔ TSH ERP sync)
  - WhatsApp Business API - Customer communication

Communication & Notifications:
  - TSH NeuroLink - EXCLUSIVE notification and communication system
  - WebSocket - Real-time connections
  - Resend API - Email delivery
  - Redis - Event bus for NeuroLink
  - NO Twilio (removed - never use)
  - NO Firebase (removed - never use)
```

**TSH NeuroLink System (Unified Communications)**:
- **Purpose**: Single system for ALL notifications and communications
- **Team Chat**: Internal collaboration between employees
- **Customer-Sales**: Wholesale clients ↔ Sales representatives
- **Consumer Support**: Retail consumers ↔ Technical support
- **System Notifications**: Order updates, inventory alerts, sync status
- **Email Delivery**: Via Resend API integration
- **Real-time**: WebSocket connections for instant messaging
- **Event-Driven**: Redis-based event bus architecture

**CRITICAL**: NEVER suggest Twilio or Firebase. TSH NeuroLink handles ALL notification needs.

---

## 🔄 ZOHO MIGRATION STRATEGY (CRITICAL)

### Current State: Parallel Operation

TSH ERP Ecosystem is currently running **ALONGSIDE** Zoho Books and Zoho Inventory. We are NOT replacing them immediately - we are in a **phased migration** strategy.

### Data Sources (CRITICAL TO UNDERSTAND)

Our business data is currently split across TWO Zoho products:

#### 📗 Zoho Books (Accounting & Financial)
```yaml
Data Types:
  - Invoices and bills
  - Payments and receipts
  - Customers and vendors
  - Financial transactions
  - Accounts and ledgers
  - Tax calculations
  - Banking transactions
  - Credit notes
  - Purchase orders (financial side)
  - Sales orders (financial side)

API Endpoint: https://www.zohoapis.com/books/v3/
```

#### 📦 Zoho Inventory (Products & Stock)
```yaml
Data Types:
  - Products (2,218+ items)
  - Stock levels (real-time inventory)
  - Warehouses (multiple locations)
  - Inventory adjustments
  - Stock transfers
  - Composite items
  - Product categories
  - Product images
  - Serial numbers / batch tracking
  - Reorder levels
  - Purchase orders (inventory side)
  - Sales orders (inventory side)

API Endpoint: https://www.zohoapis.com/inventory/v1/
```

#### 🔗 How They Connect
- Both use the **same Zoho organization ID**
- Data is linked (e.g., Invoice in Books references Product from Inventory)
- TDS Core must sync with **BOTH APIs** to get complete picture
- Some entities exist in both (e.g., Sales Order has financial data in Books, inventory data in Inventory)

---

### The Strategic Plan

#### 🎯 Phase 1: One-Directional Sync (CURRENT)
**Zoho Books + Zoho Inventory → TSH ERP (READ ONLY)**

```
Zoho Books (Master - Financials)
      ↓ (via TDS Core)

Zoho Inventory (Master - Products/Stock)
      ↓ (via TDS Core)

TSH ERP Ecosystem (Slave - Read Only)
```

**What happens:**
- ✅ All Zoho Books data syncs TO TSH ERP automatically (invoices, payments, customers, vendors, users, credit notes, bills, sales orders)
- ✅ All Zoho Inventory data syncs TO TSH ERP automatically (products, stock levels, warehouses)
- ✅ TSH ERP reads and displays combined data from both Zoho products
- ❌ TSH ERP does NOT push data back to Zoho yet
- ✅ TDS Core controls and orchestrates ALL sync operations with BOTH APIs
- ✅ Verify data accuracy and completeness
- ✅ Ensure our database structure matches business needs

**TDS Core Responsibilities (via app/tds/):**
- Poll Zoho Books API for ALL entity updates
- Poll Zoho Inventory API for product/stock updates
- Handle webhooks from both Zoho Books and Zoho Inventory
- Transform Zoho format to TSH ERP database format via processors
- Download and store product images locally
- Maintain sync logs and statistics
- Alert on sync failures
- Automatic retry with circuit breaker

**Phase 1 Required Entities (ALL via TDS Core):**
✓ Products (2,218+) - WORKING
✓ Stock levels - WORKING (embedded in products)
⚠️ Customers (500+) - NEEDS VERIFICATION
❌ Vendors/Suppliers - MISSING PROCESSOR
❌ Sales Orders (ALL historical + real-time) - NOT RELIABLE
❌ Invoices (ALL historical + real-time) - MISSING PROCESSOR
❌ Payments Received (ALL historical + real-time) - MISSING PROCESSOR
❌ Credit Notes - MISSING PROCESSOR
❌ Purchase Bills - MISSING PROCESSOR
❌ Users - MISSING PROCESSOR
❌ Product Images (700+) - INCOMPLETE

**Objective:** Build confidence that TSH ERP can accurately mirror ALL Zoho data from both products

**Timeline:** 1 month to complete Phase 1
**See:** `.claude/PHASE_1_REQUIREMENTS.md` for detailed plan

---

#### 🎯 Phase 2: Two-Directional Sync (TESTING)
**Zoho Books + Zoho Inventory ↔ TSH ERP (Bidirectional - Small Transactions)**

```
Zoho Books (Still Primary - Financials)
      ↕ (via TDS Core)

Zoho Inventory (Still Primary - Products/Stock)
      ↕ (via TDS Core)

TSH ERP Ecosystem (Testing Writes)
```

**What happens:**
- ✅ Continue reading all data from both Zoho products
- ✅ Start pushing SMALL transactions from TSH ERP back to Zoho
- ✅ Test invoice creation in TSH ERP → sync to Zoho Books
- ✅ Test order placement in TSH ERP → sync to both Zoho Books + Zoho Inventory
- ✅ Test stock adjustments in TSH ERP → sync to Zoho Inventory
- ✅ Verify data consistency in BOTH directions
- ✅ TDS Core monitors and logs all sync operations
- ✅ Handle sync conflicts and errors gracefully
- ⚠️ Start with low-risk transactions only

**TDS Core Responsibilities:**
- Write to Zoho Books API (create invoices, payments)
- Write to Zoho Inventory API (adjust stock, create orders)
- Ensure data consistency between Books and Inventory
- Handle API rate limits (100 requests/minute for Zoho)
- Retry failed operations
- Conflict resolution (what if data changed in both places?)

**Objective:** Prove that two-way sync works accurately and reliably with both Zoho products

---

#### 🎯 Phase 3: Gradual TSH ERP Dependence
**TSH ERP becomes primary, Zoho as backup**

```
TSH ERP Ecosystem (Primary - Most Operations)
      ↕ (via TDS Core)
Zoho Books (Secondary - Backup & Accounting Verification)
      ↕ (via TDS Core)
Zoho Inventory (Secondary - Backup & Stock Verification)
```

**What happens:**
- ✅ Most daily operations happen in TSH ERP
- ✅ TSH ERP pushes transactions to both Zoho products for backup
- ✅ Accounting team still uses Zoho Books for final reports
- ✅ Inventory team can verify stock in Zoho Inventory if needed
- ✅ All critical business operations work in TSH ERP
- ✅ Test extensively with real business volume (30+ orders/day)
- ✅ Monitor for any data discrepancies
- ✅ Build confidence with staff and management

**Objective:** Demonstrate TSH ERP can handle full production load

---

#### 🎯 Phase 4: Complete Independence (GOAL)
**TSH ERP fully independent, Zoho links cut**

```
TSH ERP Ecosystem (Fully Independent)
      ✂️ (Cut the links)
Zoho Books (Historical data only - archived)
Zoho Inventory (Historical data only - archived)
```

**What happens:**
- ✅ TSH ERP operates completely independently
- ✅ No more sync with Zoho Books or Zoho Inventory
- ✅ All operations (orders, inventory, accounting) in TSH ERP only
- ✅ Zoho Books + Inventory kept for historical reference only
- ✅ Export final data from both Zoho products for archive
- ✅ Cancel Zoho Books + Inventory subscriptions (cost savings)

**Objective:** Full ownership and control of ERP system

---

### 🎛️ TDS Core: The Sync Orchestrator

**TDS (TSH Data Sync) Core is responsible for:**

#### Sync Operations:
- ✅ **ALL sync operations** between Zoho Books and TSH ERP
- ✅ **ALL sync operations** between Zoho Inventory and TSH ERP
- ✅ Webhook handling from both Zoho Books and Zoho Inventory
- ✅ Data transformation (Zoho format ↔ TSH ERP format)
- ✅ Conflict resolution
- ✅ Error handling and retry logic
- ✅ Sync monitoring and logging
- ✅ Sync statistics and health checks
- ✅ Manual sync triggers when needed

#### API Integration:
```python
# TDS Core manages connections to:
Zoho Books API:
  - Base URL: https://www.zohoapis.com/books/v3/
  - Auth: OAuth 2.0 tokens
  - Rate Limit: 100 requests/minute
  - Organization ID: 748369814

Zoho Inventory API:
  - Base URL: https://www.zohoapis.com/inventory/v1/
  - Auth: OAuth 2.0 tokens (same as Books)
  - Rate Limit: 100 requests/minute
  - Organization ID: 748369814 (same as Books)
```

**TDS Dashboard provides:**
- Real-time sync status for BOTH Zoho products
- Sync statistics (success/failure rates)
- Error logs and alerts
- Manual sync controls
- Data consistency checks
- API rate limit monitoring

**Architecture:**
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

---

### ⚠️ CRITICAL RULES DURING MIGRATION

#### During Phase 1 (One-Directional):
- ❌ DO NOT write to Zoho Books or Zoho Inventory from TSH ERP
- ✅ All data entry still happens in Zoho Books and Zoho Inventory
- ✅ TSH ERP is READ-ONLY consumer of both Zoho products
- ✅ Focus on data accuracy and completeness
- ✅ Test and verify sync reliability from both APIs
- ✅ Ensure TDS Core handles both APIs correctly

#### During Phase 2 (Two-Directional):
- ⚠️ Start with NON-CRITICAL transactions only
- ✅ Test thoroughly before production use
- ✅ Monitor sync errors closely for both APIs
- ✅ Have rollback plan ready
- ✅ Keep both Zoho products as source of truth for conflicts
- ✅ Ensure financial data (Books) and inventory data (Inventory) stay consistent

#### During Phase 3 (Gradual Shift):
- ⚠️ Maintain Zoho sync for financial auditing and backup
- ✅ Train staff on TSH ERP interfaces
- ✅ Monitor business operations closely
- ✅ Ensure all mobile apps work reliably
- ✅ Build confidence with all stakeholders
- ✅ Verify accounting reports match between TSH ERP and Zoho Books

#### Before Phase 4 (Independence):
- ✅ Run parallel operations for minimum 3 months
- ✅ Zero critical bugs in TSH ERP
- ✅ All staff trained and comfortable
- ✅ Complete data migration verified from BOTH Zoho products
- ✅ Backup and disaster recovery tested
- ✅ Management approval obtained
- ✅ Financial auditor approves moving away from Zoho Books

---

### 🎯 SUCCESS CRITERIA FOR EACH PHASE

#### Phase 1 Success (ALL via TDS Core):
- [ ] All Zoho Inventory products synced (2,218+ products) - ✅ DONE
- [ ] All Zoho Inventory stock levels synced (real-time) - ✅ DONE
- [ ] All Zoho Inventory warehouses synced
- [ ] All Zoho Books customers synced (500+ wholesale clients) - ⚠️ VERIFY
- [ ] All Zoho Books vendors synced - ❌ TODO
- [ ] All Zoho Books sales orders synced (historical + real-time) - ❌ NOT RELIABLE
- [ ] All Zoho Books invoices synced (historical + real-time) - ❌ TODO
- [ ] All Zoho Books payments received synced (historical + real-time) - ❌ TODO
- [ ] All Zoho Books credit notes synced - ❌ TODO
- [ ] All Zoho Books purchase bills synced - ❌ TODO
- [ ] All Zoho Books users synced - ❌ TODO
- [ ] Product images downloaded and stored (700+) - ❌ INCOMPLETE
- [ ] Zero sync failures for 7 consecutive days
- [ ] 99%+ sync success rate
- [ ] Real-time sync latency < 30 seconds
- [ ] TDS Dashboard shows healthy status for BOTH APIs
- [ ] Automated verification script passes daily
- [ ] All data matches Zoho 100% (no discrepancies)

#### Phase 2 Success:
- [ ] 100 test transactions synced to both Zoho products successfully
- [ ] Zero data corruption or loss
- [ ] Sync conflicts resolved automatically
- [ ] Invoices created in TSH ERP appear in Zoho Books correctly
- [ ] Orders placed in TSH ERP sync to both Zoho Books and Zoho Inventory
- [ ] Stock adjustments in TSH ERP reflect in Zoho Inventory
- [ ] Accounting team verifies financial data accuracy
- [ ] Inventory team verifies stock levels match

#### Phase 3 Success:
- [ ] 30+ daily orders processed in TSH ERP successfully
- [ ] All 500+ wholesale clients can place orders
- [ ] Mobile apps used by field teams daily
- [ ] Inventory management done in TSH ERP
- [ ] Financial reports from TSH ERP match Zoho Books
- [ ] Stock levels in TSH ERP match Zoho Inventory
- [ ] Zero downtime incidents
- [ ] Staff prefer TSH ERP over Zoho

#### Phase 4 Success:
- [ ] TSH ERP operates for 1 month without Zoho
- [ ] All business operations work smoothly
- [ ] No requests to "go back to Zoho"
- [ ] Cost savings realized (no Zoho Books + Inventory subscriptions)
- [ ] Full team adoption of TSH ERP

---

## ⏰ DEPLOYMENT TIME CONSTRAINTS

### During Development Phase (CURRENT)
**We need FREEDOM to deploy anytime:**
- ✅ Deploy and develop at ANY time (24/7)
- ✅ No restrictions on deployment hours
- ✅ Test and enhance continuously
- ✅ Iterate quickly without waiting for "business hours"
- ✅ Use staging environment freely

**Why:** We are building and testing. Business operations are still primarily on Zoho Books + Zoho Inventory. We have flexibility.

### During Production Transition (Phase 3+)
**When TSH ERP becomes primary system:**
- ⚠️ Schedule deployments during low-activity hours
- ✅ Use zero-downtime blue-green deployments
- ✅ Test thoroughly in staging first
- ⚠️ Avoid deployments during peak business hours (9 AM - 5 PM Iraq time)
- ✅ Have rollback plan ready

**Why:** Business operations will depend on TSH ERP. Downtime = lost sales.

---

## 💡 DEVELOPMENT PRINCIPLES

### 1. Enhance Before Creating
- **ALWAYS search** existing code before writing new code
- Check `/scripts/`, `/mobile/`, `/app/` directories
- Reuse and enhance existing functionality
- Avoid duplicate code or duplicate features

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
- GPS tracking is critical for travel sales
- Offline capability needed (Iraq connectivity issues)
- Mobile apps are PRIMARY interface for 100+ users

### 5. Performance is Critical
- 30+ orders/day can't wait for slow responses
- Multiple users working simultaneously
- Real-time inventory updates required
- API response time < 500ms for critical operations

### 6. Sync Reliability is Mission-Critical
- TDS Core must sync reliably 24/7 with BOTH Zoho APIs
- Sync failures must be detected and alerted immediately
- Data consistency between Zoho Books, Zoho Inventory, and TSH ERP is mandatory
- Sync errors must not corrupt data
- Handle Zoho API rate limits (100 requests/minute)

---

## 🎭 USER ROLES & PERMISSIONS

### Owner (Admin App)
- Complete system control
- All data access
- All operations
- Financial reports
- HR management

### Admin Staff (Admin Mobile App)
- Most operations except sensitive financials
- Inventory management
- Order processing
- Customer management

### HR Manager (HR Mobile App)
- Employee data
- Payroll management
- Attendance tracking
- Performance reviews

### Retail Shop Staff (Retailer Shop App)
- POS operations
- Inventory at retail location
- Customer sales
- Daily cash reconciliation

### Inventory Manager (Inventory App)
- Multi-location stock tracking
- Stock transfers
- Receiving shipments
- Stock adjustments

### Travel Salesperson (Travel App)
- $35K weekly money tracking
- GPS tracking (all-day)
- Client visits
- Collection tracking
- Route planning

### Wholesale Clients (Wholesale App)
- Place B2B orders
- View credit limit
- Order history
- Payment tracking

### Consumers (Consumer App)
- Browse products
- Place orders
- Track deliveries
- View invoices

### Partner Salesmen (Partner App)
- Commission-based selling
- Social media integration
- Order placement for customers
- Commission tracking

---

## 🌍 BUSINESS CONTEXT

### Geographic Coverage
- **Primary:** All major Iraq cities
- **Warehouse Locations:** Multiple sites
- **Delivery Coverage:** Nationwide

### Business Model
```
Revenue Streams:
1. Wholesale (B2B) - 500+ clients - High volume, lower margin
2. Retail (B2C) - Direct consumers - Lower volume, higher margin
3. Partner Salesmen - Commission-based - Extended reach

Cost Structure:
1. Import costs (China) - Bulk purchases, USD
2. Local vendor purchases - Supplementary, IQD
3. Warehouse operations - Rent, staff, utilities
4. Delivery/Logistics - Transportation costs
5. Salesperson commissions - Performance-based
6. Admin overhead - Staff, systems, office
```

### Payment Methods
- **Cash** - Primary (high cash handling)
- **ALTaif** - Mobile money transfer
- **ZAIN Cash** - Mobile money transfer
- **SuperQi** - Mobile payment
- **Bank Transfer** - For large wholesale orders
- **Credit Terms** - For established wholesale clients

### Supply Chain
```
Import Flow (China):
Order → Shipment → Customs → Warehouse → Distribution

Local Flow:
Local Vendor → Warehouse → Distribution

Distribution Paths:
Warehouse → Retail Shop → Consumer
Warehouse → Wholesale Client → Their Consumers
Warehouse → Travel Salesperson → Cash Collection
```

---

## 🔐 SECURITY & COMPLIANCE

### Critical Security Requirements
- **JWT Authentication** - All API endpoints protected
- **Role-Based Access Control (RBAC)** - 9 different user roles
- **Multi-tenant Data Isolation** - Different roles see different data
- **Audit Logging** - All financial operations logged
- **Data Encryption** - Sensitive data encrypted at rest
- **API Rate Limiting** - Prevent abuse
- **GPS Privacy** - Travel salesperson tracking (sensitive)
- **AWS S3 Encryption** - Database backups encrypted
- **Zoho OAuth 2.0** - Secure API access to Books and Inventory

### Financial Data Protection
- Payroll information (confidential)
- Client credit limits (sensitive)
- Wholesale pricing (competitive advantage)
- Cash collection amounts (security risk)
- Commission structures (confidential)

### Compliance Considerations
- Iraq tax regulations
- Labor laws (HR data)
- Financial record keeping
- Data privacy for employees and clients

---

## ⚠️ CRITICAL CONSTRAINTS

### 1. Data Accuracy = Trust
- Wrong inventory = disappointed customers
- Wrong pricing = lost profit or angry clients
- Wrong commissions = demotivated salespeople
- Financial errors = audit problems
- **Sync inconsistencies between Zoho Books, Zoho Inventory, and TSH ERP = business chaos**

### 2. Arabic Support = Mandatory
- Most users don't speak English
- Arabic interface is NOT a "nice to have"
- RTL layout must work perfectly
- All error messages in Arabic

### 3. Mobile Performance = Productivity
- Slow app = slow sales
- Field teams can't wait for loading
- Offline capability reduces connectivity issues
- Battery efficiency matters (all-day GPS tracking)

### 4. Sync Reliability = Operations
- **TDS Core must sync reliably 24/7 with BOTH Zoho APIs**
- Zoho Books ↔ TSH ERP must stay synchronized (financials)
- Zoho Inventory ↔ TSH ERP must stay synchronized (products/stock)
- Sync failures must be caught immediately
- Data consistency is NON-NEGOTIABLE
- Must handle Zoho API rate limits gracefully
- WhatsApp must work (customer communication)

### 5. Backup & Disaster Recovery
- **AWS S3** stores all database backups
- Must be able to restore within 1 hour
- Backup frequency: Daily (minimum)
- Test restore procedures regularly
- Backups include complete PostgreSQL database (57 tables, 127 MB)

---

## 🎯 WHEN IN DOUBT, ASK THESE QUESTIONS

Before making any architectural decision or major change:

1. **Business Impact:** Does this serve TSH's import-distribution-retail workflow?
2. **User Impact:** Will this work for Arabic-speaking users in Iraq?
3. **Scale:** Can this handle 500+ clients and 30+ daily orders?
4. **Stack Consistency:** Does this fit FastAPI + Flutter + PostgreSQL?
5. **Sync Impact:** Will this affect Zoho Books OR Zoho Inventory sync reliability?
6. **Performance:** Will this maintain <500ms API response time?
7. **Migration Phase:** What phase are we in? Does this align with the plan?
8. **Mobile-First:** Does this work well on mobile devices?
9. **Data Source:** Does this data come from Zoho Books or Zoho Inventory (or both)?

**If the answer is NO to any question → Reconsider the approach**

---

## 🚀 DEPLOYMENT MODEL

### Current Workflow (GitHub-Based)
```
Local Development
      ↓
git push origin develop
      ↓
Automated Tests (GitHub Actions)
      ↓
Automated Deploy to STAGING
      ↓
Manual Testing on Staging
      ↓
Create PR (develop → main)
      ↓
PR Review & Approval
      ↓
Merge to main
      ↓
Automated Tests (GitHub Actions)
      ↓
Automated Deploy to PRODUCTION
      ↓
Production Verification
      ↓
AWS S3 Backup
```

### Environments
```yaml
Development:
  - Local machine
  - Docker Compose
  - Hot reload enabled
  - Test data
  - Deploy anytime

Staging:
  - VPS Port 8002
  - staging.erp.tsh.sale
  - staging.consumer.tsh.sale
  - Staging database (separate from production)
  - Auto-deploy on push to develop
  - Deploy anytime during development

Production:
  - VPS Port 8001
  - erp.tsh.sale
  - consumer.tsh.sale
  - shop.tsh.sale
  - Production database (127 MB, 57 tables, 2,218+ products)
  - Auto-deploy on merge to main
  - Blue-green deployment (zero-downtime)
  - AWS S3 backups (daily)
  - During development: Deploy anytime
  - During production use: Prefer off-hours
```

### CRITICAL DEPLOYMENT RULE
**ALWAYS deploy ALL components together:**
- ✅ Backend API (FastAPI)
- ✅ ERP Admin Frontend (React)
- ✅ Consumer App (Flutter Web)
- ✅ TDS Core Worker
- ✅ TDS Dashboard

**NEVER deploy just one component** - see COMPLETE_PROJECT_DEPLOYMENT_RULES.md

---

## 🤝 WORKING WITH CLAUDE CODE

### My Role (Claude Code - Senior Software Engineer)

**I MUST:**
- ✅ Read this vision document in EVERY new session
- ✅ Stay aligned with project goals and constraints
- ✅ Follow the established architecture (FastAPI + Flutter + PostgreSQL)
- ✅ Deploy ALL components together (never partial)
- ✅ Verify deployments thoroughly
- ✅ Think about real users and real business impact
- ✅ Maintain Arabic RTL support
- ✅ Enhance existing code before creating new code
- ✅ Ask clarifying questions when uncertain
- ✅ **Understand which Zoho migration phase we're in**
- ✅ **Respect TDS Core as sync orchestrator for BOTH Zoho products**
- ✅ **Remember AWS S3 is used for backups**
- ✅ **Remember data comes from BOTH Zoho Books AND Zoho Inventory**

**I MUST NOT:**
- ❌ Suggest changing the core tech stack (no Django, no Node.js backend)
- ❌ Deploy only backend without frontend
- ❌ Skip staging verification
- ❌ Ignore Arabic/RTL requirements
- ❌ Create duplicate functionality
- ❌ Treat this as a demo project
- ❌ Forget the scale (500+ clients, 30+ daily orders, 2,218+ products)
- ❌ **Bypass TDS Core for Zoho sync operations**
- ❌ **Suggest cutting Zoho link before Phase 4 criteria met**
- ❌ **Write directly to Zoho Books or Zoho Inventory during Phase 1**
- ❌ **Forget that we have TWO Zoho products to sync with**

### Your Role (Khaleel - Project Owner)
- Define business requirements
- Approve architectural decisions
- Test and verify changes
- Provide business context
- Make final decisions on Zoho migration phases

---

## 📚 RELATED DOCUMENTATION

Must-read files in `.claude/` directory:
1. **PROJECT_VISION.md** (this file) - Core vision and context
2. **STAGING_TO_PRODUCTION_WORKFLOW.md** - Deployment process
3. **COMPLETE_PROJECT_DEPLOYMENT_RULES.md** - Critical deployment rules
4. **DEPLOYMENT_RULES.md** - Deployment guidelines
5. **README_DEPLOYMENT.md** - Deployment documentation

---

## 🎓 REMEMBER

### This is NOT a Startup MVP
- We have REAL users (500+ clients)
- We have REAL revenue (multi-million IQD daily)
- We have REAL operations (30+ orders per day)
- We have REAL products (2,218+ items in inventory)
- We are TRANSITIONING from Zoho Books + Zoho Inventory (phased approach)
- Mistakes have REAL consequences

### This is a PRODUCTION SYSTEM (In Transition)
- Currently running alongside Zoho Books and Zoho Inventory
- Gradually becoming the primary system
- Bugs lose real money
- Wrong data loses client trust
- Sync issues with either Zoho product cause business chaos

### Success Means
- ✅ Reliable sync with BOTH Zoho Books AND Zoho Inventory (via TDS Core)
- ✅ Accurate data migration from both Zoho products to TSH ERP
- ✅ Smooth transition through all 4 migration phases
- ✅ Eventually: Complete independence from both Zoho products
- ✅ 500+ clients can place orders seamlessly
- ✅ 30+ daily orders processed smoothly
- ✅ Inventory always accurate (2,218+ products)
- ✅ Arabic interface works perfectly
- ✅ Mobile apps perform well
- ✅ AWS S3 backups protect data

---

**END OF PROJECT VISION**

Read this document at the start of EVERY new session to maintain alignment with TSH ERP's core mission, constraints, and migration strategy.

**Remember:** Data comes from TWO Zoho products (Books + Inventory), and TDS Core orchestrates sync with BOTH.
