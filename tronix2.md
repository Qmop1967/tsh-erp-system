   - Result: Maintenance nightmare, steep learning curve

✅ CORRECT: Unified Ecosystem
   - ONE database for all apps
   - ONE auth system for all apps
   - ONE architecture pattern for all apps
   - Result: Clean, maintainable, scalable system
```

**Critical Implementation Rules:**

1. **Database Access**
   - ALWAYS connect to the shared PostgreSQL database
   - NEVER create separate databases per app
   - Use views/schemas for app-specific data isolation if needed

2. **Authentication**
   - ALWAYS use the unified FastAPI authentication endpoints
   - NEVER implement separate auth systems
   - Share JWT tokens across all ecosystem apps

3. **Authorization**
   - ALWAYS check permissions against the central RBAC system
   - NEVER create app-specific permission logic
   - Define roles once, apply everywhere

4. **Architecture**
   - ALWAYS follow TDS-centric integration patterns
   - ALWAYS use shared service layers
   - NEVER duplicate business logic across apps

**The Ecosystem Promise:**

> "Build it once, use it everywhere. One database, one auth, one architecture—unified, organized, and maintainable."

This is WHY we call it an **ECOSYSTEM** and not just "TSH ERP System". Every component is part of a unified, interconnected whole, sharing the same foundation and following the same principles.

---

### Deployment Environment

- **VPS**: DigitalOcean Droplet (167.71.39.50)
- **Domain**: erp.tsh.sale
- **SSL**: Let's Encrypt (Auto-renewal via Certbot)
- **OS**: Ubuntu 22.04 LTS
- **Docker**: Docker Compose v3.8

### 🔴 CRITICAL: Database Access Pattern

**⚠️ ALWAYS USE SELF-HOSTED DATABASE - NEVER USE SUPABASE ⚠️**

**Production Database Configuration:**
- **Host:** 167.71.39.50 (TSH ERP VPS)
- **Container:** `tsh_postgres`
- **Database:** `tsh_erp`
- **User:** `tsh_admin`
- **Password:** `TSH@2025Secure!Production`

**✅ CORRECT Database Access Pattern:**
```bash
# Always use this pattern for database queries
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \"YOUR_SQL_QUERY_HERE\""
```

**❌ WRONG - DO NOT USE:**
```bash
# OLD/DEPRECATED - Supabase connection (NO LONGER ACTIVE)
# NEVER use: psql "postgresql://postgres.trjjglxhteqnzmyakxhe:..."
```

**Why Self-Hosted Only:**
- ✅ Full control over data and infrastructure
- ✅ No external dependencies or third-party services
- ✅ Lower costs and better performance
- ✅ Complete data sovereignty
- ✅ Aligned with institutional approach

**Common Database Operations:**
```bash
# Query products
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \"SELECT COUNT(*) FROM products;\""

# Check active products with stock
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \"SELECT COUNT(*) FROM products WHERE is_active = true AND actual_available_stock > 0;\""

# Interactive psql session
ssh root@167.71.39.50 "docker exec -it tsh_postgres psql -U tsh_admin -d tsh_erp"
```

---

## 🚀 Product Roadmap & Multi-Price List System

**Date:** November 7, 2025
**Status:** Strategic Plan - Implementation Roadmap
**Priority:** HIGH - Core Business Logic

### Business Overview

TSH operates with a sophisticated multi-tier pricing system to serve different customer segments with appropriate pricing and currency options.

**خطة المنتجات ونظام قوائم الأسعار المتعددة**

---

### 💰 Price Lists Architecture

TSH maintains **6 distinct price lists** synchronized with Zoho Books:

| Price List | Currency | Target Audience | Access Method |
|------------|----------|-----------------|---------------|
| **Wholesale A** | USD | Bulk buyers (Tier 1) | TSH Clients App |
| **Wholesale B** | USD | Bulk buyers (Tier 2) | TSH Clients App |
| **Retailer** | USD | Retail businesses | TSH Clients App |
| **Technical IQD** | IQD | Technical professionals | TSH Technical App |
| **Technical USD** | USD | Technical professionals | TSH Technical App |
| **Consumer IQD** | IQD | End consumers | TSH Consumer App ✅ |

**Key Principle:** Each customer sees ONLY their assigned price list with the correct currency.

---

### 📱 Flutter Applications Ecosystem

#### 1. TSH Consumer App ✅ **LIVE**

**Status:** Production
**Users:** General public (walk-in customers)
**Price List:** Consumer IQD (IQD currency)
**Location:** `mobile/flutter_apps/10_tsh_consumer_app`

**Features:**
- ✅ Browse products with Consumer IQD prices
- ✅ View stock availability (real-time from Zoho)
- ✅ Place orders
- ✅ Track delivery
- ✅ No login required (public access)

**Current Metrics:**
- 472 active products available
- IQD currency only
- Real-time Zoho inventory sync
- Installed on iOS devices

---

#### 2. TSH Clients App 🔨 **TO BE DEVELOPED**

**Status:** Planning Phase
**Users:** Business customers (Wholesale A/B, Retailers)
**Price Lists:** Wholesale A (USD), Wholesale B (USD), Retailer (USD)
**Proposed Location:** `mobile/flutter_apps/20_tsh_clients_app`

**Core Functionality:**

```
┌─────────────────────────────────────────────┐
│         CLIENT LOGIN FLOW                    │
└─────────────────────────────────────────────┘

1. Client logs in with credentials
   └─> Authenticate against database

2. System checks client record
   └─> Query: SELECT price_list_id, currency
       FROM clients WHERE client_id = ?

3. Load client's assigned price list
   └─> Wholesale A, Wholesale B, or Retailer

4. Display products with client-specific pricing
   └─> Show prices in USD
   └─> Apply client's discount tier (if any)

5. Client can place orders at their price tier
   └─> Order syncs back to Zoho Books
```

**Required Features:**
- 🔐 Secure login/authentication
- 💰 Dynamic price list loading based on client
- 💵 USD currency display
- 📊 Client-specific order history
- 📦 Stock availability (same as consumer app)
- 🔄 Sync orders back to Zoho
- 👤 Client profile management
- 📱 Multi-language support (English/Arabic)

**Database Schema Requirements:**

```sql
-- Clients table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    zoho_contact_id VARCHAR(100) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    price_list_id INTEGER NOT NULL,  -- Links to price_lists table
    currency VARCHAR(3) DEFAULT 'USD',
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (price_list_id) REFERENCES price_lists(id)
);

-- Price lists table
CREATE TABLE price_lists (
    id SERIAL PRIMARY KEY,
    zoho_pricelist_id VARCHAR(100) UNIQUE,
    name VARCHAR(100) NOT NULL,  -- "Wholesale A", "Wholesale B", "Retailer"
    currency VARCHAR(3) NOT NULL,  -- "USD", "IQD"
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product prices per price list
CREATE TABLE product_prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    price_list_id INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    effective_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (price_list_id) REFERENCES price_lists(id),
    UNIQUE(product_id, price_list_id)
);
```

**API Endpoints Needed:**

```python
# Client authentication
POST /api/clients/login
{
    "email": "client@example.com",
    "password": "..."
}

# Get client profile (with price list info)
GET /api/clients/me
Response: {
    "id": 123,
    "name": "ABC Company",
    "price_list": "Wholesale A",
    "currency": "USD",
    "discount": 5.0
}

# Get products with client-specific pricing
GET /api/clients/products?price_list_id=2
Response: [
    {
        "id": 1,
        "name": "Product A",
        "price": 25.00,  // Wholesale A price in USD
        "currency": "USD",
        "stock": 100
    }
]

# Place client order
POST /api/clients/orders
{
    "items": [
        {"product_id": 1, "quantity": 10}
    ],
    "delivery_address": "..."
}
```

---

#### 3. TSH Technical Man App 🔨 **TO BE DEVELOPED**

**Status:** Planning Phase
**Users:** Technical professionals (installers, technicians, engineers)
**Price Lists:** Technical IQD (IQD), Technical USD (USD)
**Proposed Location:** `mobile/flutter_apps/30_tsh_technical_app`

**Core Functionality:**

```
┌─────────────────────────────────────────────┐
│      TECHNICAL USER LOGIN FLOW               │
└─────────────────────────────────────────────┘

1. Technical person logs in
   └─> Authenticate against database

2. System checks technical user record
   └─> Query: SELECT price_list_id, currency,
       preferred_language FROM technical_users
       WHERE user_id = ?

3. Load technical price list
   └─> Technical IQD OR Technical USD
   └─> Based on user preference/region

4. Display products with technical pricing
   └─> Typically wholesale-level or below
   └─> May include installation kits/bundles

5. Technical user can:
   └─> Browse products
   └─> Place orders for job sites
   └─> Access technical specifications
   └─> View installation manuals
```

**Unique Features for Technical App:**
- 📋 Technical product specifications
- 🔧 Installation guides and manuals
- 📦 Bundle/kit recommendations
- 🎯 Product compatibility checker
- 📍 Job site management
- 💳 Dual currency support (IQD + USD toggle)
- 📊 Purchase history by job site
- 🔔 Product availability notifications

**Database Schema Requirements:**

```sql
-- Technical users table
CREATE TABLE technical_users (
    id SERIAL PRIMARY KEY,
    zoho_contact_id VARCHAR(100) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    price_list_id INTEGER NOT NULL,  -- Technical IQD or Technical USD
    preferred_currency VARCHAR(3) DEFAULT 'IQD',
    specialization VARCHAR(100),  -- CCTV, Networking, etc.
    certification_level VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (price_list_id) REFERENCES price_lists(id)
);

-- Job sites (for technical users)
CREATE TABLE job_sites (
    id SERIAL PRIMARY KEY,
    technical_user_id INTEGER NOT NULL,
    site_name VARCHAR(255),
    site_address TEXT,
    customer_name VARCHAR(255),
    project_type VARCHAR(100),  -- Installation, Maintenance, Upgrade
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, cancelled
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (technical_user_id) REFERENCES technical_users(id)
);
```

---

### 🏗️ Implementation Roadmap

#### Phase 1: Data Model & Sync (2 weeks)

**Goal:** Set up price lists and client linking in database

**Tasks:**
- [ ] Create `price_lists` table
- [ ] Create `product_prices` table
- [ ] Create `clients` table
- [ ] Create `technical_users` table
- [ ] Sync price lists from Zoho Books
- [ ] Sync product prices for all 6 price lists
- [ ] Link existing clients to their Zoho price lists
- [ ] Create TDS handler for price list sync

**Deliverables:**
- Database schema with all price lists
- TDS integration for price sync
- Admin panel to manage price list assignments

---

#### Phase 2: TSH Clients App Development (4-6 weeks)

**Goal:** Build and deploy clients app with dynamic pricing

**Week 1-2: Backend API**
- [ ] Create client authentication system
- [ ] Build client profile API
- [ ] Create dynamic pricing API (filters by price list)
- [ ] Implement order placement API
- [ ] Add order history API
- [ ] TDS integration for order sync to Zoho

**Week 3-4: Flutter App**
- [ ] Set up Flutter project structure
- [ ] Implement login/authentication UI
- [ ] Build product catalog with dynamic pricing
- [ ] Create shopping cart
- [ ] Implement order placement flow
- [ ] Add order history screen
- [ ] Profile management screen

**Week 5-6: Testing & Deployment**
- [ ] Test with real client data
- [ ] Verify pricing accuracy across price lists
- [ ] Test order sync to Zoho
- [ ] Deploy to App Store / Play Store
- [ ] User acceptance testing with clients
- [ ] Training materials for clients

**Deliverables:**
- Live TSH Clients App (iOS + Android)
- Client onboarding process
- User documentation

---

#### Phase 3: TSH Technical App Development (4-6 weeks)

**Goal:** Build technical professionals app with specialized features

**Similar timeline to Clients App but with additional features:**
- [ ] Technical specifications database
- [ ] Installation guide integration
- [ ] Job site management
- [ ] Product compatibility checker
- [ ] Dual currency toggle

**Deliverables:**
- Live TSH Technical App (iOS + Android)
- Technical user onboarding
- Installation guides library

---

#### Phase 4: Maintenance & Optimization (Ongoing)

**Tasks:**
- [ ] Monitor price sync accuracy
- [ ] Collect user feedback from all apps
- [ ] Optimize performance
- [ ] Add new features based on requests
- [ ] Regular security audits
- [ ] Update product catalogs

---

### 🎯 Success Criteria

**For TSH Clients App:**
- ✅ 100% price accuracy across all price lists
- ✅ <2s load time for product catalog
- ✅ 99.9% uptime
- ✅ Successful Zoho order sync
- ✅ 80%+ client adoption rate

**For TSH Technical App:**
- ✅ All technical specifications available
- ✅ Dual currency support working
- ✅ Job site management functional
- ✅ 70%+ technical user adoption

**For Overall System:**
- ✅ Real-time price sync from Zoho
- ✅ Zero pricing errors
- ✅ Unified authentication system
- ✅ Centralized monitoring dashboard

---

### 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-APP ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ TSH Consumer    │  │ TSH Clients     │  │ TSH Technical   │
│ App ✅          │  │ App 🔨          │  │ App 🔨          │
│                 │  │                 │  │                 │
│ Consumer IQD    │  │ Wholesale A/B   │  │ Technical IQD   │
│ Public Access   │  │ Retailer (USD)  │  │ Technical USD   │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                              v
                ┌─────────────────────────────┐
                │     FastAPI Backend         │
                │  (Unified API Layer)        │
                │                             │
                │  /api/consumer/*            │
                │  /api/clients/*             │
                │  /api/technical/*           │
                │                             │
                │  - Authentication           │
                │  - Dynamic Pricing          │
                │  - Order Management         │
                │  - Stock Sync               │
                └──────────┬──────────────────┘
                           │
                           v
                ┌─────────────────────────────┐
                │      PostgreSQL DB          │
                │  (Self-Hosted)              │
                │                             │
                │  - products                 │
                │  - price_lists              │
                │  - product_prices           │
                │  - clients                  │
                │  - technical_users          │
                │  - orders                   │
                └──────────┬──────────────────┘
                           │
                           v
                ┌─────────────────────────────┐
                │         TDS CORE            │
                │  (Sync Management)          │
                │                             │
                │  - Price Sync               │
                │  - Product Sync             │
                │  - Order Sync               │
                │  - Client Sync              │
                └──────────┬──────────────────┘
                           │
                           v
                ┌─────────────────────────────┐
                │      Zoho Books API         │
                │                             │
                │  - 6 Price Lists            │
                │  - Products                 │
                │  - Customers/Contacts       │
                │  - Sales Orders             │
                └─────────────────────────────┘
```

---

### 📊 Price List Management Strategy

**Zoho Books → TSH ERP Sync:**

1. **Daily Price Sync (Automated)**
   - TDS runs every 6 hours
   - Syncs all 6 price lists
   - Updates `product_prices` table
   - Logs all changes

2. **Client Assignment (Manual + Auto)**
   - New clients get default price list (Retailer)
   - Admin can change assignment
   - Synced from Zoho contact custom field

3. **Currency Handling**
   - Store prices in original currency
   - No conversion (display as-is)
   - Each app shows its currency only

4. **Fallback Strategy**
   - If price not found for price list → use Consumer IQD
   - Log missing prices
   - Alert admin

---

### 🔐 Security Considerations

**Client App:**
- ✅ JWT authentication
- ✅ Role-based access (client can only see their own orders)
- ✅ API rate limiting
- ✅ HTTPS only
- ✅ Password hashing (bcrypt)

**Technical App:**
- ✅ Same security as Client App
- ✅ Additional: Job site access control
- ✅ Document access permissions

**Backend:**
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuration
- ✅ Regular security audits

---

### 📈 Monitoring & Analytics

**Track for Each App:**
- Daily active users
- Most viewed products
- Average order value
- Price list usage distribution
- Sync success rates
- API response times
- Error rates

**Business Metrics:**
- Revenue by price list
- Client conversion rate
- Technical user engagement
- Order accuracy (vs manual)
- Customer satisfaction scores

---

**Status:** This roadmap is ACTIVE and guides all future development.
**Owner:** TSH ERP Team
**Review:** Monthly (first Monday of each month)
**Updates:** Document all changes in this section

---

## 🔴 CRITICAL: Code Consolidation & TDS Centralization

**⚠️ ALWAYS CHECK FOR EXISTING CODE BEFORE CREATING NEW FUNCTIONALITY ⚠️**

### The Golden Rule: Search First, Code Second

Before creating ANY new functionality, script, service, or feature:

1. **🔍 SEARCH THE CODEBASE** for existing implementations
2. **📋 CHECK TDS** for related sync/integration functionality
3. **📚 REVIEW DOCUMENTATION** in `/docs` for previous implementations
4. **🗂️ EXAMINE SCRIPTS** in `/scripts` for similar tools

**Why This Matters:**
- ✅ Prevents code duplication (DRY principle)
- ✅ Maintains unified architecture
- ✅ Reduces maintenance burden
- ✅ Ensures consistency across the system
- ✅ Faster development (reuse > rewrite)

### TDS (TSH Data Sync) - The Single Source of Truth

**PRINCIPLE:** All external integrations and data synchronization MUST go through TDS.

**What belongs in TDS:**
- ✅ ALL Zoho API interactions (Books, Inventory, CRM)
- ✅ Product synchronization
- ✅ Order synchronization
- ✅ Customer data sync
- ✅ Image downloads from Zoho
- ✅ Stock updates
- ✅ Price updates
- ✅ Any external API integration

**What does NOT belong in TDS:**
- ❌ Internal business logic
- ❌ Direct database queries (use services)
- ❌ UI/frontend code
- ❌ Authentication/authorization

### Architecture Pattern: TDS-Centric

```
┌─────────────────────────────────────────────────────────┐
│                   TSH ERP ECOSYSTEM                      │
└─────────────────────────────────────────────────────────┘

WRONG ❌ - Standalone Scripts:
┌──────────────┐        ┌──────────────┐
│ Script 1     │───────>│  Zoho API    │
└──────────────┘        └──────────────┘
┌──────────────┐              │
│ Script 2     │──────────────┤
└──────────────┘              │
┌──────────────┐              │
│ Script 3     │──────────────┘
└──────────────┘

Problems:
- Multiple auth implementations
- No centralized monitoring
- Difficult to maintain
- No event tracking
- No unified error handling


CORRECT ✅ - TDS-Centric:
┌──────────────┐
│   Script     │
└──────┬───────┘
       │
       v
┌─────────────────────────────────┐
│            TDS CORE             │
│  (Single Source of Truth)       │
│                                 │
│  - OAuth Management             │
│  - Event Bus                    │
│  - Queue System                 │
│  - Error Handling               │
│  - Logging & Monitoring         │
│  - Rate Limiting                │
└────────────┬────────────────────┘
             │
             v
      ┌──────────────┐
      │  Zoho API    │
      └──────────────┘

Benefits:
✅ Centralized auth & token refresh
✅ All events tracked & logged
✅ Easy monitoring & debugging
✅ Single configuration point
✅ Consistent error handling
```

### Workflow: Integrating Standalone Code into TDS

**When you find standalone code outside TDS:**

1. **STOP** - Don't run the standalone code
2. **ANALYZE** - Understand what it does
3. **PLAN** - Design TDS integration
4. **INTEGRATE** - Move functionality into TDS
5. **DEPRECATE** - Mark old code as archived
6. **DOCUMENT** - Update this file and TDS docs

**Example: Integrating Image Download**

```python
# ❌ WRONG - Standalone Script
# File: scripts/download_images.py
async def download_images():
    """Download images directly from Zoho"""
    token = get_token()  # Separate auth
    for item in items:
        image = download_image(item, token)
        save_to_disk(image)
        update_db(item.id, image_url)

# ✅ CORRECT - TDS Integration
# File: app/tds/integrations/zoho/handlers/image_sync.py
from app.tds.core.service import TDSService
from app.tds.core.events import event_bus

class ImageSyncHandler(BaseSyncHandler):
    """TDS handler for Zoho image synchronization"""

    async def sync_images(self, items: List[Dict]) -> SyncResult:
        """Download images through TDS"""

        # Create TDS sync run
        sync_run = await self.tds.create_sync_run(
            run_type=SourceType.ZOHO,
            entity_type=EntityType.PRODUCT,
            configuration={"task": "image_download"}
        )

        for item in items:
            # TDS handles auth automatically
            image = await self.zoho_client.download_image(item['item_id'])

            # TDS handles storage
            result = await self.image_service.store(image)

            # TDS handles database updates
            await self.record_entity_sync(
                entity_type=EntityType.PRODUCT,
                entity_id=item['id'],
                operation=OperationType.UPDATE,
                changes={"image_url": result.public_url}
            )

            # TDS publishes events
            # (automatic through record_entity_sync)

        return sync_run
```

### Search Patterns for Existing Code

**Before implementing ANY feature, run these searches:**

```bash
# Search for existing functionality
grep -r "function_name" app/ scripts/

# Search for Zoho integrations
grep -r "zoho.*api\|zoho.*client" app/

# Search for image handling
grep -r "image.*download\|download.*image" app/ scripts/

# Check TDS handlers
ls -la app/tds/integrations/zoho/handlers/

# Check existing scripts
ls -la scripts/ | grep -i "keyword"

# Check documentation
find docs/ -name "*.md" | xargs grep -i "keyword"
```

### Code Consolidation Checklist

Before writing new code:

- [ ] Searched codebase for existing implementation
- [ ] Checked TDS for related handlers
- [ ] Reviewed `/scripts` directory
- [ ] Examined `/docs` for previous work
- [ ] Verified no duplicate functionality exists
- [ ] If found outside TDS: plan integration
- [ ] If not found: implement in TDS (not standalone)

### TDS Directory Structure

```
app/tds/
├── core/
│   ├── service.py           # TDS core service
│   ├── events.py            # Event bus & events
│   ├── queue.py             # Sync queue management
│   └── handlers.py          # Base handler classes
├── integrations/
│   └── zoho/
│       ├── client.py        # Zoho API client
│       ├── auth.py          # OAuth management
│       ├── sync.py          # Main sync orchestrator
│       ├── processors/      # Data transformers
│       │   ├── products.py
│       │   ├── customers.py
│       │   └── orders.py
│       └── handlers/        # Entity-specific handlers
│           ├── product_sync.py
│           ├── order_sync.py
│           ├── customer_sync.py
│           └── image_sync.py    # ← Image downloads go here
└── models/                  # TDS database models
```

### When to Create Standalone vs TDS-Integrated

**Standalone Script (Rare):**
- One-time data migration
- Emergency hotfix (integrate into TDS later)
- Development/testing utilities
- System administration tasks

**TDS-Integrated (Default):**
- Any Zoho interaction
- Recurring synchronization
- Data imports/exports
- External API calls
- Image/file downloads
- Webhook handlers

### Example: Finding Existing Image Download Code

```bash
# Step 1: Search for image download
$ grep -r "download.*image\|image.*download" app/ scripts/
app/services/image_service.py:    async def download_and_store_image(...)
scripts/download_zoho_images_paginated.py:async def download_images_batch(...)

# Step 2: Check if TDS-integrated
$ ls app/tds/integrations/zoho/handlers/ | grep image
# (empty - not integrated)

# Step 3: Decision
# ✅ Code exists but NOT in TDS
# ❌ Creating new standalone script = WRONG
# ✅ Integrate existing into TDS = CORRECT
```

### Enforcement

**This is NOT optional.** Every engineer on this project:

1. ✅ MUST search for existing code before creating new
2. ✅ MUST integrate Zoho interactions through TDS
3. ✅ MUST document when moving code into TDS
4. ✅ MUST update Tronix.md with new patterns

**Violations:**
- Creating duplicate functionality = Code review rejection
- Bypassing TDS for Zoho = Architecture violation
- Not documenting integration = Incomplete work

### Benefits of This Approach

**For the Team:**
- 🎯 Single place to find all Zoho integration code
- 📊 Easy monitoring of all external API calls
- 🐛 Faster debugging (centralized logging)
- 📈 Better performance tracking
- 🔒 Consistent security patterns

**For the System:**
- 🏗️ Clean, maintainable architecture
