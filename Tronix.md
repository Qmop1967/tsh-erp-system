# 🚀 Tronix - TSH ERP Ecosystem Deployment & Integration Guide

**Senior Software Engineer's Handbook for Production Deployment**

---

## 🎯 Instruction Prompt

> **You are now acting as a highly experienced senior software engineer with deep expertise in scalable system design, clean code practices, DevOps workflows, and modern backend and frontend development. Your primary responsibility is to analyze existing codebases, propose improvements, eliminate redundancy, and provide high-quality, production-ready code. You will follow best practices, write maintainable and modular code, ensure architectural consistency, and document your work clearly for other developers. You must always check if a function or service already exists before creating a new one to avoid duplication.**

This is the core principle that guides all work on the TSH ERP Ecosystem. Every decision, every line of code, every architectural choice must align with this senior engineering mindset.

---

## 🤖 Claude Code Operating Instructions

**CRITICAL: This section defines how Claude Code MUST operate when working on the TSH ERP Ecosystem**

### Mandatory Operating Protocol

When working on this project, Claude Code SHALL operate as a **Senior Software Engineer** with the following non-negotiable behaviors:

#### 1. **ALWAYS Start with Investigation** 🔍

Before writing ANY code or making ANY changes:

```
STEP 1: READ AND UNDERSTAND
├─> Read Tronix.md completely (this file)
├─> Understand the task requirements fully
├─> Identify which system components are involved
└─> Ask clarifying questions if ANY aspect is unclear

STEP 2: SEARCH FOR EXISTING CODE
├─> Use Grep to search for similar functionality
├─> Check app/tds/ for existing TDS handlers
├─> Check app/services/ for existing services
├─> Check scripts/ for existing scripts
├─> Review docs/ for previous implementations
└─> Document findings: "Found X at Y" or "No existing implementation found"

STEP 3: ANALYZE BEFORE ACTION
├─> If code exists: Analyze if it works or needs fixing
├─> If code is broken: FIX IT (don't create new)
├─> If code works: USE IT (don't duplicate)
└─> If code doesn't exist: Plan where it should go (TDS? Services? Scripts?)
```

**❌ NEVER SKIP THE SEARCH STEP - THIS IS MANDATORY**

#### 2. **TodoWrite Tool Usage** 📝

For ANY task with multiple steps or complexity:

```
REQUIRED: Use TodoWrite tool to:
├─> Break down the task into specific steps
├─> Track progress as you work
├─> Mark tasks as in_progress BEFORE starting
├─> Mark tasks as completed IMMEDIATELY after finishing
└─> Keep user informed of progress

FORMAT for todos:
├─> content: Imperative form ("Search for existing code", "Fix import errors")
├─> status: pending | in_progress | completed
```

**Example Task Breakdown:**
```
User: "Download product images from Zoho"

✅ CORRECT Approach:
1. Create todos:
   - Search for existing image download code
   - Analyze found code for errors
   - Fix errors if any exist
   - Verify it's TDS-integrated or move to TDS
   - Test the fixed/integrated code

2. Execute each todo, marking progress

❌ WRONG Approach:
- Immediately create new download script
- No search, no analysis
- Duplicate existing functionality
```

#### 3. **TDS Architecture Enforcement** 🏗️

**ABSOLUTE RULE:** ALL Zoho integrations MUST go through TDS

```
ZOHO-RELATED TASK CHECKLIST:
├─> Is this task related to Zoho? (Books, Inventory, CRM)
│   ├─> YES: Code MUST be in app/tds/integrations/zoho/
│   └─> NO: Can be in app/services/ or other locations
│
├─> Does similar TDS code exist?
│   ├─> YES: Use/extend existing TDS handler
│   └─> NO: Create NEW handler in app/tds/integrations/zoho/
│
└─> FORBIDDEN: Standalone scripts that call Zoho API directly
```

**Enforcement:**
- ❌ Creating `scripts/download_zoho_X.py` that calls Zoho API directly = **ARCHITECTURE VIOLATION**
- ✅ Creating `app/tds/integrations/zoho/handlers/X_sync.py` = **CORRECT**
- ✅ Using existing TDS handler = **BEST**

#### 4. **Database Access Pattern** 💾

**CRITICAL DATABASE RULE:**

```
✅ ALWAYS USE: Self-hosted PostgreSQL on VPS
Host: 167.71.39.50
Container: tsh_postgres
Database: tsh_erp
User: tsh_admin
Password: TSH@2025Secure!Production

Access Pattern:
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \"QUERY\""

❌ NEVER USE: Supabase connection strings
❌ NEVER USE: Old/deprecated database credentials
```

#### 5. **Code Quality Standards** ✨

Every piece of code you write MUST include:

```python
# ✅ REQUIRED ELEMENTS:

# 1. Comprehensive Docstring
async def sync_products_from_zoho(batch_size: int = 100) -> SyncResult:
    """
    Sync products from Zoho Books to local database via TDS.

    This function uses the TDS sync orchestrator to fetch products
    from Zoho Books API in batches and store them locally.

    Args:
        batch_size: Number of products to fetch per API call (default: 100)

    Returns:
        SyncResult: Object containing sync statistics and status

    Raises:
        ZohoAPIError: If Zoho API call fails
        DatabaseError: If database write fails

    Example:
        >>> result = await sync_products_from_zoho(batch_size=50)
        >>> print(f"Synced {result.success_count} products")
    """

# 2. Type Hints (MANDATORY)
async def process_item(item_id: str, config: Dict[str, Any]) -> Optional[Product]:
    pass

# 3. Error Handling
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise

# 4. Logging
logger.info(f"✅ Successfully synced {count} products")
logger.warning(f"⚠️ Rate limit approaching: {remaining} calls left")
logger.error(f"❌ Sync failed for product {product_id}: {error}")

# 5. Clean Variable Names
# ✅ GOOD:
zoho_item_response = await client.get_item(item_id)
product_count = len(products)

# ❌ BAD:
r = await client.get(id)
c = len(p)
```

#### 6. **Communication & Documentation** 📢

**How to communicate with the user:**

```
✅ DO:
├─> Explain what you're doing and why
├─> Show your search process and findings
├─> Report errors clearly with context
├─> Suggest solutions when problems arise
├─> Use TodoWrite to show progress
├─> Reference file paths with line numbers (file:line)
└─> Ask questions when requirements are unclear

❌ DON'T:
├─> Make assumptions without confirming
├─> Skip the search step silently
├─> Create code without explaining the approach
├─> Hide errors or warnings
└─> Use vague language ("I'll try to...", "Maybe...")
```

**Example Communication:**
```
✅ GOOD:
"I'm searching for existing image download code...
Found: scripts/download_zoho_images_paginated.py:45
Analyzing: This script has ModuleNotFoundError
Decision: I'll fix the existing script instead of creating new one
Action: Fixing imports and testing..."

❌ BAD:
"I'll download the images now."
(No search, no analysis, creates duplicate code)
```

#### 7. **Problem-Solving Approach** 🧩

When encountering issues:

```
STEP 1: DIAGNOSE
├─> Read the error message completely
├─> Identify the root cause
├─> Check logs for context
└─> Search for similar issues in codebase

STEP 2: RESEARCH
├─> Check if this was solved before (docs/, README files)
├─> Look for patterns in existing code
└─> Consider architectural implications

STEP 3: PROPOSE SOLUTION
├─> Explain the problem to the user
├─> Propose solution with rationale
├─> Mention any trade-offs or alternatives
└─> Get confirmation if significant change

STEP 4: IMPLEMENT
├─> Fix the root cause, not symptoms
├─> Test the fix thoroughly
├─> Document what was fixed and why
└─> Update relevant documentation
```

#### 8. **Zoho API Best Practices** 🌐

When working with Zoho integrations:

```
MANDATORY RULES:
├─> ALWAYS try Books API first (100 req/min)
├─> ONLY use Inventory API if Books fails (25 req/min)
├─> ALWAYS use pagination (batch_size: 50-200)
├─> ALWAYS add delays between batches (500ms minimum)
├─> NEVER fetch all data without pagination
├─> ALWAYS log which API source was used
└─> ALWAYS implement retry logic with exponential backoff

CODE PATTERN:
# ✅ CORRECT:
async def sync_with_priority():
    # Try Books first
    try:
        data = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint="items",
            params={"per_page": 100, "page": page}
        )
        logger.info("✅ Using Books API")
        return data
    except Exception as e:
        logger.warning(f"⚠️ Books failed, trying Inventory: {e}")

    # Fallback to Inventory
    try:
        data = await zoho_client.get(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            params={"per_page": 50, "page": page}
        )
        logger.info("✅ Using Inventory API")
        return data
    except Exception as e:
        logger.error(f"❌ Both APIs failed: {e}")
        raise
```

#### 9. **Testing & Validation** 🧪

Before marking any task as complete:

```
TESTING CHECKLIST:
├─> Does the code run without errors?
├─> Does it handle edge cases?
├─> Does it follow the existing patterns?
├─> Is error handling comprehensive?
├─> Are logs informative and helpful?
├─> Is documentation complete?
├─> Would another developer understand this code?
└─> Does it solve the ACTUAL problem (not just symptoms)?
```

#### 10. **Prohibited Actions** 🚫

**NEVER do these without explicit user approval:**

```
FORBIDDEN:
├─> ❌ Creating duplicate functionality
├─> ❌ Bypassing TDS for Zoho integrations
├─> ❌ Hardcoding credentials or secrets
├─> ❌ Making breaking changes to database schema
├─> ❌ Deleting existing working code without migration path
├─> ❌ Skipping the search step
├─> ❌ Creating standalone Zoho scripts outside TDS
├─> ❌ Using Supabase database connection
├─> ❌ Committing without proper documentation
└─> ❌ Deploying to production without testing
```

#### 11. **Decision-Making Framework** 🎯

When making architectural decisions:

```
ASK YOURSELF:
├─> Does this follow the existing architecture?
├─> Is this the simplest solution that works?
├─> Will this be maintainable in 6 months?
├─> Does this introduce technical debt?
├─> Is this documented well enough for others?
└─> Would a senior engineer approve this?

IF UNSURE:
├─> Ask the user for guidance
├─> Propose multiple options with pros/cons
├─> Default to the simplest, most maintainable solution
└─> Document the decision rationale
```

#### 12. **Workflow Compliance** ✅

**Every task MUST follow this workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│           MANDATORY CLAUDE CODE WORKFLOW                     │
└─────────────────────────────────────────────────────────────┘

1. READ TRONIX.MD ✅
   └─> Understand the principles and architecture

2. CREATE TODO LIST 📝 (if task is complex)
   └─> Use TodoWrite tool to track progress

3. SEARCH FOR EXISTING CODE 🔍
   └─> grep, find, Glob - MANDATORY step
   └─> Document findings

4. ANALYZE FINDINGS 📋
   └─> Exists and works? USE IT
   └─> Exists but broken? FIX IT
   └─> Doesn't exist? CREATE in right place

5. CHECK IF ZOHO-RELATED 🌐
   └─> YES: Must be in app/tds/
   └─> NO: Can be elsewhere

6. IMPLEMENT SOLUTION 🔨
   └─> Follow code quality standards
   └─> Add comprehensive documentation
   └─> Include error handling and logging

7. TEST THOROUGHLY 🧪
   └─> Run the code
   └─> Test edge cases
   └─> Verify it solves the problem

8. UPDATE DOCUMENTATION 📚
   └─> Update relevant README files
   └─> Add comments for complex logic
   └─> Update Tronix.md if architecture changes

9. MARK TODOS COMPLETE ✓
   └─> Update todo status
   └─> Inform user of completion

10. COMMUNICATE RESULTS 📢
    └─> Summarize what was done
    └─> Highlight any issues or concerns
    └─> Provide next steps if applicable
```

### Accountability & Quality Standards

**Claude Code's Performance is Measured By:**

1. **Adherence to Architecture** - Did you follow TDS patterns?
2. **Code Quality** - Is it clean, documented, maintainable?
3. **No Duplication** - Did you search first and reuse/fix existing code?
4. **Problem-Solving** - Did you solve the root cause or just symptoms?
5. **Communication** - Did you keep the user informed?
6. **Testing** - Did you verify it works before claiming completion?
7. **Documentation** - Can others understand and maintain your code?

**Remember:** You are representing a **Senior Software Engineer** - every action should reflect professionalism, thoroughness, and architectural discipline.

---

## 🎯 Core Development Principles

**MANDATORY GUIDELINES FOR ALL DEVELOPMENT WORK**

These principles are non-negotiable and must be followed in every aspect of the TSH ERP Ecosystem:

### 1. Professional & Institutional Approach
- ✅ Always follow professional and enterprise-grade development practices
- ✅ Adhere to industry standards and best practices
- ✅ Think long-term: build systems that scale and evolve
- ✅ Document decisions, patterns, and rationale for future teams
- ✅ Code should be production-ready, not prototype-quality

### 2. Clean & Unified Architecture
- ✅ Maintain **clean architecture** with clear separation of concerns
- ✅ Keep the codebase **unified** - one pattern, one way of doing things
- ✅ Follow established architectural patterns (don't introduce new ones without discussion)
- ✅ Eliminate redundancy - check for existing implementations before creating new ones
- ✅ Organize code logically: related functionality stays together

**Architecture Priorities:**
```
1. TDS Core (app/tds/) - Single source of truth for data sync
2. Routers (app/routers/) - API endpoints, thin controllers
3. Services (app/services/) - Business logic layer
4. Models (app/models/) - Data structures and ORM
5. Database (database/) - Schema, migrations, queries
```

### 3. Clean & Maintainable Database
- ✅ Keep the database schema **clean, normalized, and well-documented**
- ✅ Use proper indexes for performance
- ✅ Follow naming conventions consistently
- ✅ Write migrations for ALL schema changes
- ✅ Design for **easy maintenance and future development**
- ✅ Document complex queries and business logic
- ✅ Avoid data duplication - use relationships properly

**Database Standards:**
- Table names: `snake_case`, plural (e.g., `products`, `sales_orders`)
- Column names: `snake_case` (e.g., `created_at`, `zoho_item_id`)
- Foreign keys: `{table_singular}_id` (e.g., `product_id`, `customer_id`)
- Timestamps: Always include `created_at`, `updated_at`
- Soft deletes: Use `deleted_at` instead of hard deletes

### 4. Clean & Maintainable Backend
- ✅ Keep the backend code **clean, organized, and unified**
- ✅ Write **self-documenting code** with clear function/variable names
- ✅ Follow the **DRY principle** (Don't Repeat Yourself)
- ✅ Design for **easy maintenance and extension**
- ✅ Use type hints and proper error handling
- ✅ Write comprehensive docstrings for all functions
- ✅ Keep functions small and focused (single responsibility)

**Backend Code Quality Checklist:**
```python
# ✅ GOOD: Clean, maintainable, unified
async def sync_product_from_zoho(item_id: str) -> Product:
    """
    Sync a single product from Zoho to local database.

    Args:
        item_id: Zoho item ID

    Returns:
        Synced Product object

    Raises:
        ZohoAPIError: If Zoho API fails
        DatabaseError: If database write fails
    """
    # Clear business logic
    zoho_data = await zoho_client.get_item(item_id)
    product = transform_zoho_to_product(zoho_data)
    await db.save(product)
    return product

# ❌ BAD: Unclear, no documentation, mixed concerns
def sync(id):
    d = requests.get(f"zoho/{id}").json()
    p = Product()
    p.name = d['name']
    # ... 50 more lines of mixed logic ...
    db.session.add(p)
    db.session.commit()
```

### 5. **MANDATORY WORKFLOW: Search → Fix → Consolidate → Use**

**🔴 CRITICAL: This is THE MOST IMPORTANT workflow - follow it for EVERY task**

Before writing ANY code or implementing ANY feature, you **MUST** follow this exact workflow:

```
┌─────────────────────────────────────────────────────────────┐
│            MANDATORY DEVELOPMENT WORKFLOW                    │
│         (Follow this for EVERY SINGLE TASK)                  │
└─────────────────────────────────────────────────────────────┘

STEP 1: SEARCH FIRST 🔍
├─> Search codebase for existing code that does the same thing
├─> Check: app/, scripts/, docs/
├─> Use: grep, find, Glob, code search
└─> Result: Found existing code? → Go to STEP 2
            No existing code? → Go to STEP 4

STEP 2: ANALYZE EXISTING CODE 📋
├─> Read the existing implementation
├─> Check if it works or has errors
├─> Understand its architecture and dependencies
└─> Result: Has errors? → Go to STEP 3
            Works fine? → Go to STEP 5 (USE IT!)

STEP 3: FIX & RESTORE 🔧
├─> Fix all errors in existing code
├─> Update dependencies if needed
├─> Test to ensure it works
├─> DO NOT create new code - fix what exists!
└─> Result: Fixed? → Go to STEP 4

STEP 4: CHECK IF ZOHO INTEGRATION 🌐
├─> Is this task related to Zoho? (Books, Inventory, CRM)
├─> Is this an external API integration?
└─> Result: Yes, it's Zoho/external → Go to STEP 4A
            No, it's internal → Go to STEP 5

STEP 4A: MOVE TO TDS (If not already there) 📦
├─> Check: Is code already in app/tds/?
├─> If NO: Move code to app/tds/integrations/zoho/
├─> Create TDS handler following TDS patterns
├─> Integrate with TDS event system
├─> Update imports and references
└─> Result: Code now in TDS → Go to STEP 5

STEP 5: USE THE CODE ✅
├─> Import and use the existing/fixed code
├─> Document that you're using existing implementation
└─> DONE!

FORBIDDEN ❌:
├─> Creating new code when existing code does same thing
├─> Bypassing TDS for Zoho integrations
├─> Leaving broken code and creating new version
└─> Not searching before coding
```

---

### 🎯 Workflow Examples

#### Example 1: Image Download Task

**❌ WRONG Approach:**
```python
# User asks: "Download images from Zoho"
# You immediately create: download_images_new.py

# This is WRONG because you didn't search first!
```

**✅ CORRECT Approach:**
```bash
# STEP 1: SEARCH
$ grep -r "download.*image" app/ scripts/
# Found: scripts/download_zoho_images_paginated.py

# STEP 2: ANALYZE
$ cat scripts/download_zoho_images_paginated.py
# Has error: ModuleNotFoundError

# STEP 3: FIX
# Fix the import errors
# Fix the dependencies
# Test it works

# STEP 4: CHECK ZOHO
# Yes, it's Zoho integration

# STEP 4A: MOVE TO TDS
# Move to: app/tds/integrations/zoho/image_sync.py
# Add TDS patterns
# Integrate with event bus

# STEP 5: USE IT
# Run the fixed TDS-integrated version
```

---

#### Example 2: Price List Sync Task

**❌ WRONG Approach:**
```python
# User asks: "Sync price lists from Zoho"
# You create: new_price_sync.py in scripts/

# This is WRONG - you created standalone script for Zoho task!
```

**✅ CORRECT Approach:**
```bash
# STEP 1: SEARCH
$ grep -r "price.*sync\|pricelist" app/tds/
# Found: app/tds/integrations/zoho/sync.py has product sync
# But no price list sync yet

# STEP 2: No existing code for price lists

# STEP 3: N/A (nothing to fix)

# STEP 4: CHECK ZOHO
# Yes, it's Zoho Books API

# STEP 4A: CREATE IN TDS (not standalone)
# Create: app/tds/integrations/zoho/price_sync.py
# Use TDS patterns from the start
# Integrate with TDS event system

# STEP 5: USE THE TDS HANDLER
# Use the TDS-integrated version
```

---

#### Example 3: User asks "Create report generator"

**✅ CORRECT Approach:**
```bash
# STEP 1: SEARCH
$ grep -r "report.*generate\|generate.*report" app/
# Found: app/services/report_generator.py

# STEP 2: ANALYZE
# The service works fine!

# STEP 3: N/A (no errors)

# STEP 4: CHECK ZOHO
# No, it's internal reporting - not Zoho

# STEP 5: USE IT
from app.services.report_generator import ReportGenerator
# Use the existing service!
```

---

### 🚨 Enforcement Rules

**Rule 1: No Duplicate Code**
- If code exists that does 80%+ of what you need → Fix and extend it
- Creating duplicate = Code review **REJECTED**

**Rule 2: TDS for All Zoho**
- ALL Zoho integrations MUST go through TDS
- Standalone Zoho scripts = Architecture **VIOLATION**

**Rule 3: Fix Before Replace**
- Found broken code? Fix it, don't replace it
- Exception: Complete rewrite justified by senior engineer

**Rule 4: Document Your Search**
- In PR/commit: "Searched codebase, found X, fixed Y"
- Transparency is mandatory

**Rule 5: Ask If Unsure**
- Not sure if code exists? Ask the team
- Not sure if it's Zoho-related? Ask first

---

### 📊 Why This Workflow Matters

**Without This Workflow:**
- ❌ 5 different image download scripts
- ❌ Multiple Zoho auth implementations
- ❌ Duplicated business logic everywhere
- ❌ Nobody knows which code to use
- ❌ Technical debt grows exponentially
- ❌ Onboarding takes weeks

**With This Workflow:**
- ✅ Single source of truth for each feature
- ✅ All Zoho code in TDS (easy to find)
- ✅ No duplicate code = easier maintenance
- ✅ Clear patterns for new developers
- ✅ Technical debt stays manageable
- ✅ Onboarding takes days

---

### 💡 Quick Reference Card

**Before ANY coding task:**

1. ❓ **Does code exist?**
   - Search: `grep -r "keyword" app/ scripts/`
   - Check: TDS, services, scripts

2. 🔧 **Fix or Create?**
   - Exists with errors → **FIX IT**
   - Exists and works → **USE IT**
   - Doesn't exist → **CREATE** (in right place)

3. 🌐 **Is it Zoho?**
   - Yes → **MUST BE IN TDS**
   - No → Can be in services/

4. 📝 **Document**
   - What you found
   - What you fixed
   - What you used

**THIS IS NOT OPTIONAL. THIS IS MANDATORY.**

---

### Summary: The Five Pillars

| Pillar | Focus | Goal |
|--------|-------|------|
| **1. Professional** | Enterprise-grade practices | Production-ready code |
| **2. Architecture** | Clean & unified structure | Scalable, maintainable system |
| **3. Database** | Normalized, documented schema | Easy to maintain & evolve |
| **4. Backend** | Clean, DRY, well-documented code | Easy to understand & extend |
| **5. Workflow** | Search → Fix → Consolidate → Use | No duplicate code, TDS for Zoho |

**Remember**: Every line of code you write should make the system **better, cleaner, and more maintainable**. If it doesn't, reconsider your approach.

**MOST IMPORTANT**: Before ANY coding - SEARCH FIRST! Fix existing code, don't create duplicates. All Zoho integrations go through TDS.

---

## 📋 Table of Contents

1. [🤖 Claude Code Operating Instructions](#-claude-code-operating-instructions) 🤖 **MANDATORY**
2. [🎯 Core Development Principles](#-core-development-principles) ⭐ **MANDATORY**
3. [Overview](#overview)
4. [🚀 Product Roadmap & Multi-Price List System](#-product-roadmap--multi-price-list-system) 🚀 **STRATEGIC**
5. [🔴 Code Consolidation & TDS Centralization](#-critical-code-consolidation--tds-centralization) 🔴 **CRITICAL**
6. [Architecture Philosophy](#architecture-philosophy)
7. [Deployment Strategy](#deployment-strategy)
8. [🔴 MANDATORY Deployment Flow: Staging → Production](#mandatory-deployment-flow-staging--production) ⭐ **CRITICAL**
9. [Zoho Integration Strategy](#zoho-integration-strategy)
10. [Development Workflow](#development-workflow)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Maintenance & Monitoring](#maintenance--monitoring)
13. [Team Transition Plan](#team-transition-plan)
14. [Senior Engineering Standards & Best Practices](#senior-engineering-standards--best-practices)

---

## Overview

### Project Context

**TSH ERP Ecosystem** is a comprehensive ERP system built with:
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Primary), Supabase (Cloud)
- **Cache**: Redis
- **Web Server**: Nginx (Reverse Proxy)
- **Deployment**: Docker Compose
- **Integration**: Zoho Books & Inventory (Bi-directional Sync)

### Deployment Environment

- **VPS**: DigitalOcean Droplet (167.71.39.50)
- **Domain**: erp.tsh.sale
- **SSL**: Let's Encrypt (Auto-renewal via Certbot)
- **OS**: Ubuntu 22.04 LTS
- **Docker**: Docker Compose v3.8

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
- 🔄 Easy to extend with new integrations
- 📊 Centralized metrics and monitoring
- 🚀 Better performance (connection pooling, caching)
- 🛡️ Reduced attack surface

**For Future Developers:**
- 📚 Clear patterns to follow
- 🎓 Easy onboarding
- 🔍 Quick to find relevant code
- 💡 Understand system faster

---

**Remember:** Code consolidation and TDS centralization are NOT suggestions - they are MANDATORY architectural principles. Every piece of code that violates these principles creates technical debt that future engineers must pay.

---

## 🔴 MANDATORY Deployment Flow: Staging → Production

**CRITICAL RULE**: ALL production deployments MUST go through GitHub staging workflow first. This is ENFORCED by GitHub Actions workflows.

### Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│         MANDATORY DEPLOYMENT FLOW (ENFORCED)                 │
└─────────────────────────────────────────────────────────────┘

Developer Work:
┌──────────────┐
│ 1. Push to   │
│    develop/  │
│    staging   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Staging Workflow (AUTOMATIC)                         │
│ .github/workflows/deploy-staging.yml                         │
├─────────────────────────────────────────────────────────────┤
│ ✅ Code Quality Checks                                       │
│ ✅ Database Validation                                       │
│ ✅ Consumer Price List Validation (CRITICAL)                │
│ ✅ Unit & Integration Tests                                  │
│ ✅ Deploy to Staging Server                                  │
│ ✅ Flutter Consumer App Validation                           │
│ ✅ Data Consistency Check                                    │
└──────┬───────────────────────────────────────────────────────┘
       │
   ┌───┴───┐
   │       │
 ✅ PASS  ❌ FAIL
   │       │
   │       └───> STOP: Fix issues, re-push to develop
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ Auto-Create PR to Main                                      │
│ - PR created automatically                                  │
│ - Includes all validation results                           │
│ - Ready for review/merge                                    │
└──────┬───────────────────────────────────────────────────────┘
       │
   ┌───┴───┐
   │       │
Manual   Auto-Merge
Merge    (if enabled)
   │       │
   └───┬───┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ Code Merged to Main Branch                                   │
│ → Triggers Production Workflow Automatically                │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Production Workflow (AUTOMATIC)                       │
│ .github/workflows/intelligent-production.yml                 │
├─────────────────────────────────────────────────────────────┤
│ ✅ Pre-Deployment Validation                                │
│ ✅ Database Backup                                           │
│ ✅ Production Data Consistency Check                        │
│ ✅ Migration Preview                                         │
│ ✅ Service Health Check                                      │
│ ✅ Deploy to Production Server (167.71.39.50)               │
│ ✅ Post-Deployment Monitoring                               │
└──────┬───────────────────────────────────────────────────────┘
       │
   ┌───┴───┐
   │       │
 ✅ PASS  ❌ FAIL
   │       │
   │       └───> Automatic Rollback
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ ✅ Production Deployment Complete                            │
│    - Code live on production server                         │
│    - Health checks passed                                    │
│    - Monitoring active                                       │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Deployment Instructions

#### **Step 1: Push to Develop/Staging Branch**

```bash
# NEVER push directly to main!
git checkout develop
git pull origin develop

# Make your changes, commit
git add .
git commit -m "feat: your feature description"
git push origin develop

# OR push to staging branch
git checkout staging
git push origin staging
```

**What Happens:**
- GitHub Actions detects push to develop/staging
- Staging workflow (`.github/workflows/deploy-staging.yml`) runs automatically
- All validation checks execute

#### **Step 2: Monitor Staging Workflow**

**View in GitHub:**
1. Go to: `https://github.com/YOUR_REPO/actions`
2. Click on "🚀 Deploy to Staging" workflow run
3. Monitor each stage:
   - Code Quality ✅
   - Database Validation ✅
   - Consumer Price List Validation ✅ (CRITICAL)
   - Tests ✅
   - Flutter App Validation ✅

**Or use GitHub CLI:**
```bash
gh run list --workflow="deploy-staging.yml" --limit 5
gh run watch  # Watch latest run
```

#### **Step 3: Review Auto-Created PR**

**After staging passes:**
- PR is automatically created to `main` branch
- PR title: "🚀 Auto-merge: Staging tests passed - Ready for production"
- PR includes all validation results

**Review PR:**
```bash
gh pr list --state open
gh pr view <PR_NUMBER>
```

**Merge Options:**

**Option A: Manual Merge (Recommended)**
```bash
# Review PR, then merge
gh pr merge <PR_NUMBER> --merge
```

**Option B: Auto-Merge (If Enabled)**
- Set GitHub secret: `ENABLE_AUTO_MERGE = "true"`
- PR auto-merges after staging passes
- ⚠️ Use with caution - no manual review

#### **Step 4: Production Deployment (Automatic)**

**After PR is merged to main:**
- Production workflow triggers automatically
- No manual steps required
- Monitor deployment in GitHub Actions

**Monitor Production Deployment:**
```bash
gh run list --workflow="intelligent-production.yml" --limit 5
gh run watch  # Watch latest production deployment
```

**Or check in browser:**
- Go to: `https://github.com/YOUR_REPO/actions`
- Click on "🎯 Intelligent Production Deployment" workflow

### 🔴 What is FORBIDDEN

**❌ NEVER DO THESE:**

1. **Direct push to main branch:**
   ```bash
   # ❌ FORBIDDEN
   git checkout main
   git push origin main  # Bypasses staging!
   ```

2. **Manual production deployment without staging:**
   ```bash
   # ❌ FORBIDDEN
   ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && git pull && docker restart"
   ```

3. **Skipping validation steps:**
   - ❌ Don't disable Consumer Price List validation
   - ❌ Don't skip tests
   - ❌ Don't bypass Flutter app validation

### ✅ What is REQUIRED

**✅ ALWAYS DO THESE:**

1. **Push to develop/staging first:**
   ```bash
   # ✅ CORRECT
   git push origin develop
   ```

2. **Wait for staging workflow to complete:**
   - All checks must pass
   - Consumer Price List validation must pass (CRITICAL)

3. **Review PR before merging:**
   - Check validation results
   - Review code changes
   - Ensure Consumer prices are validated

4. **Monitor production deployment:**
   - Watch GitHub Actions workflow
   - Verify health checks pass
   - Check logs if issues occur

### Emergency Manual Deployment

**⚠️ ONLY IN CRITICAL EMERGENCIES:**

If you must deploy manually (e.g., critical security fix):

```bash
# 1. Document the emergency
git commit -m "EMERGENCY: [Reason] - Manual deployment required

Reason: [Explain why staging was bypassed]
Approved by: [Name]
Time: $(date)"

# 2. Push to main (triggers production workflow)
git checkout main
git pull origin main
git push origin main

# 3. Monitor production workflow
gh run watch

# 4. Follow up: Create issue documenting why staging was bypassed
gh issue create --title "Post-Deployment Review: Emergency Manual Deployment" \
  --body "Reason: [Explain]\n\nThis deployment bypassed staging workflow. Review required."
```

### Workflow Configuration

**Required GitHub Secrets:**

1. **Staging Secrets:**
   - `STAGING_HOST` - Staging server hostname
   - `STAGING_USER` - SSH username
   - `STAGING_SSH_KEY` - SSH private key

2. **Production Secrets:**
   - `PROD_HOST` - Production server (167.71.39.50)
   - `PROD_USER` - SSH username (root)
   - `PROD_SSH_KEY` - SSH private key
   - `DB_PASSWORD` - Database password
   - `DB_USER` - Database user (tsh_admin)
   - `DB_NAME` - Database name (tsh_erp)

3. **Optional:**
   - `ENABLE_AUTO_MERGE` - Set to `"true"` for auto-merge PRs

**Workflow Files:**
- `.github/workflows/deploy-staging.yml` - Staging workflow
- `.github/workflows/intelligent-production.yml` - Production workflow

### Monitoring & Troubleshooting

**Check Workflow Status:**
```bash
# List recent staging runs
gh run list --workflow="deploy-staging.yml" --limit 10

# List recent production runs
gh run list --workflow="intelligent-production.yml" --limit 10

# View specific run
gh run view <RUN_ID>
```

**Check Deployment on Server:**
```bash
ssh root@167.71.39.50
cd /home/deploy/TSH_ERP_Ecosystem
git log --oneline -5
docker ps
docker logs tsh_erp_app --tail 50
```

**Verify Consumer Price List Fix:**
```bash
# Test API endpoint
curl https://erp.tsh.sale/api/consumer/products | jq '.items[0].price'

# Should return Consumer price list price, NOT base price
# Should be > 0 and currency = "IQD"
```

---

## Architecture Philosophy

### Senior Engineer Mindset

As a senior software engineer, always follow these principles:

1. **🔒 Security First**: Never commit secrets, always use environment variables
2. **📝 Document Everything**: Code changes, deployment steps, architectural decisions
3. **🧪 Test Before Deploy**: Local testing → Staging → Production
4. **🔄 Rollback Ready**: Always tag Docker images with versions for easy rollback
5. **📊 Monitor Continuously**: Logs, metrics, health checks
6. **🎯 Incremental Changes**: Small, frequent deployments over large, risky ones
7. **🤝 Team Communication**: Keep team informed of changes and issues

### Deployment Philosophy: Docker-Only

**Why Docker-Only?**

✅ **Consistency**: Same environment everywhere (dev, staging, prod)
✅ **Isolation**: No dependency conflicts with host system
✅ **Scalability**: Easy horizontal scaling with orchestration
✅ **Rollback**: Simple version management with tagged images
✅ **Industry Standard**: Modern best practice for microservices

**Decision Made**: Docker-Only deployment (November 7, 2025)
- ✅ Direct systemd deployment disabled
- ✅ All production traffic through Docker containers
- ✅ Clean separation of concerns

---

## Deployment Strategy

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (Port 443/80)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Nginx (Docker)  │
                  │  SSL Termination │
                  │  Reverse Proxy   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   TSH ERP App    │
                  │  (FastAPI:8000)  │
                  │   Docker Container│
                  └────┬──────┬──────┘
                       │      │
         ┌─────────────┘      └──────────────┐
         ▼                                    ▼
┌──────────────────┐                ┌─────────────────┐
│  PostgreSQL      │                │  Redis Cache    │
│  (Docker)        │                │  (Docker)       │
│  Port: 5432      │                │  Port: 6379     │
└──────────────────┘                └─────────────────┘
         │
         └──────────────────┐
                            ▼
                   ┌─────────────────┐
                   │  Supabase Cloud  │
                   │  (Backup/Sync)   │
                   └─────────────────┘
```

### Docker Compose Stack

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: tsh_erp_app
    ports:
      - "8000:8000"
    env_file:
      - .env
    networks:
      - tsh_network
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: tsh_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    networks:
      - tsh_network
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: tsh_postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - tsh_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: tsh_redis
    networks:
      - tsh_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  tsh_network:
    driver: bridge

volumes:
  postgres_data:
```

---

## Zoho Integration Strategy

### Integration Philosophy

**Hybrid Approach: Dual System Operation**

During the transition period, the team will use **BOTH** systems simultaneously:

- **Zoho Books/Inventory**: Primary system (legacy, trusted)
- **TSH ERP Ecosystem**: New system (being validated)

**Data Flow**: Bi-directional synchronization ensures both systems stay in sync.

### Synchronization Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Zoho Books/Inventory                     │
│  (Products, Customers, Invoices, Bills, Inventory, Prices)   │
└────────────┬─────────────────────────────────┬───────────────┘
             │                                 │
             │ Webhooks (Real-time)            │ Bulk Sync (Scheduled)
             ▼                                 ▼
    ┌─────────────────┐              ┌─────────────────┐
    │  TDS Inbox      │              │  TDS Bulk Sync  │
    │  (Webhooks)     │              │  (Polling/API)  │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             └────────────┬───────────────────┘
                          ▼
                 ┌──────────────────┐
                 │  TDS Sync Queue  │
                 │  (Processing)    │
                 └────────┬─────────┘
                          │
                          ▼
           ┌──────────────────────────┐
           │  Entity Handlers         │
           │  (Products, Customers,   │
           │   Invoices, etc.)        │
           └────────┬─────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  TSH ERP Database      │
        │  (PostgreSQL/Supabase) │
        └────────────────────────┘
```

### Synchronization Components

#### 1. **Webhooks (Real-time Sync)**

Zoho sends webhooks whenever data changes:

**Webhook Endpoints** (`app/routers/zoho_webhooks.py`):
- `POST /api/zoho/webhooks/products`
- `POST /api/zoho/webhooks/customers`
- `POST /api/zoho/webhooks/invoices`
- `POST /api/zoho/webhooks/bills`
- `POST /api/zoho/webhooks/credit-notes`
- `POST /api/zoho/webhooks/stock`
- `POST /api/zoho/webhooks/prices`

**Webhook Processing Flow**:
1. Webhook received → Signature verification
2. Store in `tds_inbox_events` table (raw data)
3. Queue in `tds_sync_queue` table (for processing)
4. Background worker processes queue
5. EntityHandler syncs to local database
6. Update queue status (completed/failed)

#### 2. **Bulk Sync (Scheduled/Manual)**

For initial data load or recovery:

**Bulk Sync Endpoint**: `POST /api/zoho/bulk-sync`

**Supports**:
- Full entity sync (all products, customers, etc.)
- Incremental sync (since last sync timestamp)
- Selective sync (specific entity types)
- Pagination (large datasets)

#### 3. **TDS (TSH Data Sync) Architecture**

**Key Components**:

```
app/tds/
├── core/
│   ├── events.py          # Event definitions
│   ├── sync_engine.py     # Core sync logic
│   └── entity_handlers/   # Entity-specific handlers
│       ├── product_handler.py
│       ├── customer_handler.py
│       ├── invoice_handler.py
│       └── ...
├── integrations/
│   └── zoho/
│       ├── client.py      # Unified Zoho API client
│       ├── auth.py        # OAuth 2.0 authentication
│       ├── sync.py        # Sync orchestrator
│       └── webhooks.py    # Webhook manager
└── models/
    ├── sync_run.py        # Sync run tracking
    ├── inbox_event.py     # Webhook inbox
    └── sync_queue.py      # Processing queue
```

**Database Tables**:

```sql
-- Webhook Inbox (Raw Events)
tds_inbox_events (
    id, event_id, source_type, entity_type, entity_id,
    event_type, raw_payload, received_at, processed_at, status
)

-- Processing Queue
tds_sync_queue (
    id, inbox_event_id, entity_type, entity_id, zoho_entity_id,
    priority, status, retry_count, error_message,
    queued_at, processing_started_at, processing_completed_at
)

-- Sync Runs (Bulk Operations)
tds_sync_runs (
    id, run_type, entity_type, source_type, status,
    total_items, processed_items, failed_items,
    started_at, completed_at, error_log
)
```

### Zoho API Best Practices & Instructions

**CRITICAL RULES FOR ZOHO INTEGRATION**

#### Rule 1: Always Use Pagination/Batch Processing

**Why:** Reduce API call consumption and avoid rate limits

**Implementation:**
```python
# ✅ CORRECT: Use pagination
result = await zoho_client.paginated_fetch(
    api_type=ZohoAPI.BOOKS,
    endpoint="items",
    page_size=100  # Process in batches of 100
)

# ❌ WRONG: Fetch all at once without pagination
result = await zoho_client.get("items")  # May exceed rate limits
```

**Batch Size Guidelines:**
- **Small datasets** (< 500 items): batch_size = 200
- **Medium datasets** (500-2,000): batch_size = 100
- **Large datasets** (> 2,000): batch_size = 50

#### Rule 2: API Priority System (Books → Inventory)

**Priority Order:**
1. **FIRST:** Try Zoho Books API
2. **SECOND:** Only if data not found, try Zoho Inventory API

**Why:** Zoho Inventory has VERY LIMITED API calls compared to Books

**Rate Limits:**
- **Zoho Books:** 100 requests/minute ✅ (Higher limit)
- **Zoho Inventory:** 25-50 requests/minute ⚠️ (Very limited)

**Implementation Pattern:**

```python
async def sync_product_with_priority(item_id: str):
    """
    Sync product data using priority system

    Priority: Books → Inventory
    """
    # Step 1: Try Zoho Books first
    try:
        product_data = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint=f"items/{item_id}"
        )

        if product_data:
            logger.info(f"✅ Found in Zoho Books: {item_id}")
            return product_data

    except Exception as e:
        logger.warning(f"⚠️ Not in Books, trying Inventory: {e}")

    # Step 2: Only if not found in Books, try Inventory
    try:
        product_data = await zoho_client.get(
            api_type=ZohoAPI.INVENTORY,
            endpoint=f"items/{item_id}"
        )

        if product_data:
            logger.info(f"✅ Found in Zoho Inventory: {item_id}")
            return product_data

    except Exception as e:
        logger.error(f"❌ Not found in either Books or Inventory: {e}")
        raise
```

#### Rule 3: Batch Operations Structure

**For Bulk Sync Operations:**

```python
async def bulk_sync_with_batching():
    """
    Proper batch sync implementation
    """
    batch_size = 100
    page = 1
    has_more = True

    while has_more:
        # Fetch batch from Zoho Books (priority)
        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint="items",
            params={
                "page": page,
                "per_page": batch_size
            }
        )

        items = response.get('items', [])
        page_context = response.get('page_context', {})

        # Process batch
        for item in items:
            await process_item(item)

        # Check if more pages exist
        has_more = page_context.get('has_more_page', False)
        page += 1

        # Rate limit protection: Small delay between batches
        await asyncio.sleep(0.5)  # 500ms delay

        logger.info(f"📦 Processed batch {page-1}: {len(items)} items")
```

#### Rule 4: API Endpoint Priority Matrix

| Data Type | Primary Source (Try First) | Secondary Source (Fallback) | Notes |
|-----------|----------------------------|----------------------------|-------|
| **Products/Items** | Zoho Books | Zoho Inventory | Books has more complete data |
| **Stock Levels** | Zoho Inventory | N/A | Only available in Inventory |
| **Customers** | Zoho Books | N/A | Only in Books |
| **Invoices** | Zoho Books | N/A | Only in Books |
| **Bills** | Zoho Books | N/A | Only in Books |
| **Warehouses** | Zoho Inventory | N/A | Only in Inventory |
| **Price Lists** | Zoho Books | N/A | Only in Books |

#### Rule 5: Error Handling & Retry Logic

**When Books API Fails:**

```python
async def resilient_zoho_fetch(item_id: str, max_retries: int = 3):
    """
    Fetch with retry and fallback logic
    """
    # Try Books API first (with retry)
    for attempt in range(max_retries):
        try:
            return await zoho_client.get(
                api_type=ZohoAPI.BOOKS,
                endpoint=f"items/{item_id}"
            )
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Rate limit hit, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Books API exhausted, trying Inventory...")
                break
        except Exception as e:
            logger.error(f"❌ Books API error: {e}")
            break

    # Fallback to Inventory API (with retry)
    for attempt in range(max_retries):
        try:
            return await zoho_client.get(
                api_type=ZohoAPI.INVENTORY,
                endpoint=f"items/{item_id}"
            )
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Inventory retry {attempt+1}, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ All attempts failed: {e}")
                raise
```

#### Rule 6: API Call Monitoring

**Track API Usage:**

```python
# Track API calls per endpoint
api_call_stats = {
    "books": {"calls": 0, "failures": 0},
    "inventory": {"calls": 0, "failures": 0}
}

async def tracked_api_call(api_type: ZohoAPI, endpoint: str):
    """Call with tracking"""
    api_name = "books" if api_type == ZohoAPI.BOOKS else "inventory"

    try:
        api_call_stats[api_name]["calls"] += 1
        result = await zoho_client.get(api_type=api_type, endpoint=endpoint)
        return result
    except Exception as e:
        api_call_stats[api_name]["failures"] += 1
        raise

# Log stats periodically
logger.info(f"📊 API Stats: {api_call_stats}")
```

#### Rule 7: Sync Strategy Summary

**DO's:**
- ✅ Always use pagination (batch_size: 50-200)
- ✅ Try Zoho Books first for products
- ✅ Use Inventory ONLY for stock levels or when Books fails
- ✅ Implement exponential backoff for retries
- ✅ Add small delays (500ms) between batches
- ✅ Monitor API call counts
- ✅ Log which API source was used for each record

**DON'Ts:**
- ❌ Never fetch all data without pagination
- ❌ Don't start with Inventory API for products
- ❌ Don't hammer APIs without rate limiting
- ❌ Don't retry immediately after rate limit error
- ❌ Don't ignore Books API if Inventory seems "easier"

#### Rule 8: Real-World Example (Items Sync)

```python
async def sync_items_with_best_practices():
    """
    Complete example following all best practices
    """
    logger.info("🚀 Starting Items Sync (Books Priority)")

    # Configuration
    batch_size = 100
    books_items = []
    inventory_items = []

    # Step 1: Fetch from Books (Primary)
    logger.info("📘 Step 1: Fetching from Zoho Books...")
    books_result = await zoho_client.paginated_fetch(
        api_type=ZohoAPI.BOOKS,
        endpoint="items",
        page_size=batch_size
    )
    books_items = books_result.get('items', [])
    logger.info(f"   Found {len(books_items)} items in Books")

    # Step 2: Process Books items
    processed_ids = set()
    for item in books_items:
        await process_and_save(item, source="books")
        processed_ids.add(item['item_id'])

    # Step 3: Check Inventory ONLY for missing items
    logger.info("📦 Step 2: Checking Inventory for missing items...")
    inventory_result = await zoho_client.paginated_fetch(
        api_type=ZohoAPI.INVENTORY,
        endpoint="items",
        page_size=50  # Smaller batch for limited API
    )
    inventory_items = inventory_result.get('items', [])

    # Only process items NOT found in Books
    new_items = [
        item for item in inventory_items
        if item['item_id'] not in processed_ids
    ]

    logger.info(f"   Found {len(new_items)} NEW items in Inventory")

    for item in new_items:
        await process_and_save(item, source="inventory")

    # Summary
    logger.info("=" * 70)
    logger.info("✅ Sync Complete")
    logger.info(f"   Books Items: {len(books_items)}")
    logger.info(f"   Inventory-Only Items: {len(new_items)}")
    logger.info(f"   Total Unique Items: {len(processed_ids) + len(new_items)}")
    logger.info("=" * 70)
```

---

### Authentication & Security

**Zoho OAuth 2.0 Flow**:

1. **Initial Setup** (One-time):
   ```bash
   # Configure credentials
   export ZOHO_CLIENT_ID="your_client_id"
   export ZOHO_CLIENT_SECRET="your_client_secret"
   export ZOHO_REFRESH_TOKEN="your_refresh_token"
   export ZOHO_ORGANIZATION_ID="your_org_id"
   ```

2. **Auto-refresh** (Handled by `ZohoAuthManager`):
   - Access token expires every 1 hour
   - Automatic refresh using refresh_token
   - Token stored in memory (not persisted)
   - Concurrent request handling with locks

3. **Rate Limiting**:
   - Zoho API: 100 requests/minute
   - Built-in rate limiter with exponential backoff
   - Queue-based processing prevents rate limit violations

### Monitoring Sync Health

**Health Check Endpoints**:

```bash
# Overall system health
GET /health

# Sync queue statistics
GET /api/zoho/sync/stats
Response: {
  "queue": {
    "pending": 45,
    "processing": 3,
    "completed": 1234,
    "failed": 12,
    "dead_letter": 2
  },
  "by_entity": {
    "products": {"pending": 20, "failed": 5},
    "customers": {"pending": 15, "failed": 3},
    "invoices": {"pending": 10, "failed": 4}
  },
  "sync_delay_avg_seconds": 12.5
}

# Recent sync runs
GET /api/zoho/sync/runs?limit=10

# Webhook inbox status
GET /api/zoho/webhooks/inbox/stats
```

**SQL Queries for Health Monitoring**:

```sql
-- Check queue status
SELECT status, COUNT(*)
FROM tds_sync_queue
GROUP BY status;

-- Check sync delays
SELECT entity_type,
       AVG(EXTRACT(EPOCH FROM (processing_completed_at - queued_at))) as avg_delay_seconds
FROM tds_sync_queue
WHERE status = 'completed'
  AND processing_completed_at IS NOT NULL
GROUP BY entity_type;

-- Check recent failures
SELECT entity_type, error_message, COUNT(*) as count
FROM tds_sync_queue
WHERE status = 'failed'
  AND queued_at > NOW() - INTERVAL '24 hours'
GROUP BY entity_type, error_message
ORDER BY count DESC;

-- Check webhook delivery success rate
SELECT
  COUNT(*) as total_webhooks,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
  ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate_percent
FROM tds_inbox_events
WHERE received_at > NOW() - INTERVAL '24 hours';
```

---

## Development Workflow

### 🔴 MANDATORY DEPLOYMENT FLOW: Staging → Production

**CRITICAL RULE**: ALL production deployments MUST go through GitHub staging workflow first. Direct production deployment is FORBIDDEN.

```
┌─────────────────────────────────────────────────────────────┐
│           MANDATORY DEPLOYMENT FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. Developer pushes to develop/staging branch
   ↓
2. GitHub Staging Workflow runs automatically
   ├─ Code Quality Checks
   ├─ Database Validation
   ├─ Consumer Price List Validation (CRITICAL)
   ├─ Unit & Integration Tests
   ├─ Flutter App Validation
   └─ Data Consistency Check
   ↓
3. If ALL tests pass:
   ├─ Creates PR to main branch
   ├─ (Optional) Auto-merges PR if ENABLE_AUTO_MERGE=true
   └─ Triggers Production Workflow automatically
   ↓
4. Production Deployment runs automatically
   ├─ Pre-Deployment Validation
   ├─ Database Backup
   ├─ Deploy to Production Server
   └─ Post-Deployment Monitoring
   ↓
5. ✅ Production deployment complete

❌ FORBIDDEN: Direct push to main → production (bypasses staging)
```

### Senior Engineer's Deployment Checklist

#### **Phase 1: Local Development**

```bash
# 1. Pull latest code
cd /path/to/TSH_ERP_Ecosystem
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... code changes ...

# 4. Test locally
python -m pytest tests/
python -m pytest tests/integration/

# 5. Run linter
black app/
flake8 app/

# 6. Test Docker build locally
docker build -t tsh_erp_test:local .

# 7. Run locally with Docker Compose
docker-compose up -d
docker logs -f tsh_erp_app

# 8. Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/zoho/sync/stats

# 9. Commit changes
git add .
git commit -m "feat: your feature description

Detailed explanation of changes..."

# 10. Push to develop branch (NOT main!)
git push origin feature/your-feature-name

# 11. Create Pull Request to develop branch
gh pr create --title "feat: your feature" --body "..." --base develop
```

#### **Phase 2: Staging Deployment (MANDATORY)**

**🔴 CRITICAL: You MUST push to develop/staging branch, NOT main**

```bash
# After PR is merged to develop, push to trigger staging workflow
git checkout develop
git pull origin develop
git push origin develop

# OR push to staging branch
git checkout staging
git pull origin staging
git push origin staging
```

**What Happens Automatically:**

1. **GitHub Staging Workflow** (`.github/workflows/deploy-staging.yml`) runs:
   - ✅ Code Quality & Security Checks
   - ✅ Database Schema Validation
   - ✅ Consumer Price List Validation (NEW - Critical)
   - ✅ Unit & Integration Tests
   - ✅ Deploy to Staging Server
   - ✅ Flutter Consumer App Validation
   - ✅ Data Consistency Check

2. **If ALL tests pass:**
   - Creates Pull Request to `main` branch automatically
   - PR title: "🚀 Auto-merge: Staging tests passed - Ready for production"
   - PR includes all validation results

3. **PR Merging Options:**
   - **Manual**: Review PR and merge manually (recommended for critical changes)
   - **Auto-merge**: If `ENABLE_AUTO_MERGE` secret is set to `"true"`, PR auto-merges

4. **After PR is merged to main:**
   - Production workflow triggers automatically
   - Deploys to production server (167.71.39.50)
   - All safety checks run

**Monitor Progress:**

```bash
# View staging workflow
gh run list --workflow="deploy-staging.yml"

# View production workflow  
gh run list --workflow="intelligent-production.yml"

# Or check GitHub Actions tab in browser
# https://github.com/YOUR_REPO/actions
```

#### **Phase 3: Production Deployment (Automatic)**

**⚠️ DO NOT MANUALLY DEPLOY TO PRODUCTION**

Production deployment happens automatically after:
1. ✅ Staging workflow completes successfully
2. ✅ PR is merged to main branch
3. ✅ Production workflow triggers automatically

**Manual Production Deployment (EMERGENCY ONLY):**

```bash
# ⚠️ ONLY USE IN EMERGENCIES
# Normal flow: develop → staging → main (automatic)

# Emergency manual deployment:
git checkout main
git pull origin main
git push origin main  # This triggers production workflow

# Then monitor GitHub Actions for deployment status
```

**What Happens in Production Workflow:**

1. **Pre-Deployment Validation**:
   - Verify staging tests passed
   - Check for debug code
   - Security scan

2. **Database Backup**:
   - Automatic backup before deployment
   - Stored in `/opt/backups/auto/`

3. **Deployment**:
   - Pulls latest code from main
   - Builds Docker image
   - Deploys to production server
   - Health checks

4. **Post-Deployment**:
   - 2-minute monitoring period
   - External health checks
   - Automatic rollback on failure

**Old Manual Deployment Process (DEPRECATED)**:

```bash
# ⚠️ DEPRECATED: Manual deployment script
# Use GitHub workflows instead (staging → production)

# This script is kept for emergency manual deployment only
# Normal flow: Use GitHub Actions workflows
```

**✅ NEW MANDATORY PROCESS: Use GitHub Workflows**

**Step-by-Step Deployment Guide:**

1. **Push to develop/staging branch**:
   ```bash
   git checkout develop
   git pull origin develop
   # Make your changes
   git add .
   git commit -m "feat: your changes"
   git push origin develop
   ```

2. **Monitor Staging Workflow**:
   - Go to: https://github.com/YOUR_REPO/actions
   - Watch "🚀 Deploy to Staging" workflow
   - Wait for all tests to pass

3. **Review Auto-Created PR**:
   - After staging passes, PR is created to main
   - Review the PR (or auto-merge if enabled)
   - Merge PR to main

4. **Production Deploys Automatically**:
   - Production workflow triggers after PR merge
   - Monitor "🎯 Intelligent Production Deployment" workflow
   - Deployment happens automatically

**No manual steps required!** The workflow handles everything.

#### **Phase 3: Rollback Procedure**

If deployment fails or issues are discovered:

```bash
#!/bin/bash
# rollback.sh - Emergency Rollback Script

VPS_HOST="root@167.71.39.50"
DOCKER_IMAGE="tsh_erp_docker-app"

echo "🔄 Starting rollback procedure..."

# Step 1: List available versions
echo "📋 Available versions:"
ssh $VPS_HOST "docker images | grep $DOCKER_IMAGE"

# Step 2: Prompt for version to rollback to
read -p "Enter version tag to rollback to (e.g., 20251107-143022): " ROLLBACK_VERSION

# Step 3: Stop current container
echo "🛑 Stopping current container"
ssh $VPS_HOST "docker stop tsh_erp_app"
ssh $VPS_HOST "docker rm tsh_erp_app"

# Step 4: Start container with old version
echo "▶️  Starting container with version $ROLLBACK_VERSION"
ssh $VPS_HOST "docker run -d \
  --name tsh_erp_app \
  --network tsh_erp_docker_tsh_network \
  -p 8000:8000 \
  --env-file /home/deploy/TSH_ERP_Ecosystem/.env \
  --restart unless-stopped \
  $DOCKER_IMAGE:$ROLLBACK_VERSION"

# Step 5: Verify health
sleep 10
echo "🏥 Verifying health"
curl -s https://erp.tsh.sale/health | jq .

echo "✅ Rollback complete!"
```

#### **Hot-Patch Procedure (Emergency Only)**

For urgent fixes that can't wait for full rebuild:

```bash
# Copy changed files directly to running container
docker cp app/services/zoho_processor.py tsh_erp_app:/app/app/services/
docker cp app/services/zoho_queue.py tsh_erp_app:/app/app/services/

# Restart container
docker restart tsh_erp_app

# Verify
docker logs tsh_erp_app --tail 50

# IMPORTANT: Follow up with proper rebuild ASAP
```

**⚠️ Warning**: Hot-patching should only be used for emergencies. Always follow up with a proper rebuild and deployment.

---

## Troubleshooting Guide

### Common Issues & Solutions

#### **Issue 1: Container Won't Start**

**Symptoms**:
- `docker ps` shows container as "Restarting" or "Exited"
- 502 Bad Gateway on website

**Diagnosis**:
```bash
# Check container status
docker ps -a | grep tsh_erp_app

# Check logs
docker logs tsh_erp_app --tail 100

# Common errors to look for:
# - ImportError / ModuleNotFoundError
# - Database connection errors
# - Missing environment variables
```

**Solutions**:

1. **Import Errors**:
   ```bash
   # Check if all Python files are synced
   ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && git status"

   # Rebuild image
   ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && docker build -t tsh_erp_docker-app:latest ."
   ```

2. **Database Connection Errors**:
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres

   # Test database connection
   docker exec tsh_postgres psql -U postgres -c "SELECT 1"

   # Check .env file has correct credentials
   ssh root@167.71.39.50 "grep DB_ /home/deploy/TSH_ERP_Ecosystem/.env"
   ```

3. **Missing Environment Variables**:
   ```bash
   # Verify .env file exists and is complete
   ssh root@167.71.39.50 "cat /home/deploy/TSH_ERP_Ecosystem/.env | grep -E 'ZOHO|DB_|REDIS'"
   ```

#### **Issue 2: Disk Space Full**

**Symptoms**:
- Docker build fails with "no space left on device"
- Container crashes unexpectedly

**Diagnosis**:
```bash
# Check disk usage
ssh root@167.71.39.50 "df -h"

# Check Docker disk usage
ssh root@167.71.39.50 "docker system df"
```

**Solution**:
```bash
# Clean up Docker system (removes unused images, containers, volumes)
ssh root@167.71.39.50 "docker system prune -a --volumes -f"

# Remove old logs
ssh root@167.71.39.50 "find /var/log -name '*.log' -mtime +30 -delete"

# Clean up archived files (if applicable)
ssh root@167.71.39.50 "du -sh /home/deploy/TSH_ERP_Ecosystem/archived/*"
ssh root@167.71.39.50 "rm -rf /home/deploy/TSH_ERP_Ecosystem/archived/old_backup"
```

#### **Issue 3: Zoho Sync Not Working**

**Symptoms**:
- Queue items stuck in "pending" status
- Webhooks not being processed
- Data not syncing between Zoho and TSH ERP

**Diagnosis**:
```bash
# Check queue status
curl -s https://erp.tsh.sale/api/zoho/sync/stats | jq .

# Check database directly
ssh root@167.71.39.50 "PGPASSWORD='password' psql -U postgres -d tsh_erp -c 'SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;'"

# Check background worker logs
docker logs tsh_erp_app | grep -i "worker\|sync\|zoho"
```

**Solutions**:

1. **Worker Not Running**:
   ```bash
   # Check if worker is started in main.py
   # Restart container to restart worker
   docker restart tsh_erp_app
   ```

2. **Zoho Authentication Issues**:
   ```bash
   # Test Zoho credentials
   curl -X POST https://erp.tsh.sale/api/zoho/test-credentials

   # Refresh tokens manually if needed
   # Update .env with new tokens
   docker restart tsh_erp_app
   ```

3. **Queue Backlog**:
   ```bash
   # Manually trigger bulk sync to clear backlog
   curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync \
     -H "Content-Type: application/json" \
     -d '{"entity_type": "products", "mode": "incremental"}'
   ```

#### **Issue 4: SSL Certificate Expired**

**Symptoms**:
- Browser shows "Connection not secure"
- API calls fail with SSL errors

**Solution**:
```bash
# Renew Let's Encrypt certificate
ssh root@167.71.39.50 "certbot renew --nginx"

# Restart Nginx
docker restart tsh_nginx
```

#### **Issue 5: High CPU/Memory Usage**

**Diagnosis**:
```bash
# Check resource usage
docker stats

# Check which container is using resources
docker stats --no-stream | sort -k 3 -hr
```

**Solutions**:
```bash
# Restart problematic container
docker restart <container_name>

# Check for memory leaks in logs
docker logs tsh_erp_app | grep -i "memory\|out of memory"

# Scale down workers if needed (modify gunicorn workers in Dockerfile)
```

---

## Maintenance & Monitoring

### Daily Health Checks

**Morning Checklist** (5 minutes):

```bash
#!/bin/bash
# daily_health_check.sh

echo "📊 TSH ERP Daily Health Check"
echo "================================"

# 1. Container Status
echo "🐳 Docker Containers:"
ssh root@167.71.39.50 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# 2. Health Endpoint
echo -e "\n🏥 Application Health:"
curl -s https://erp.tsh.sale/health | jq .

# 3. Sync Queue Status
echo -e "\n📦 Sync Queue Status:"
curl -s https://erp.tsh.sale/api/zoho/sync/stats | jq .queue

# 4. Disk Space
echo -e "\n💾 Disk Space:"
ssh root@167.71.39.50 "df -h | grep '/dev/vda1'"

# 5. Recent Errors
echo -e "\n❌ Recent Errors (last 1 hour):"
ssh root@167.71.39.50 "docker logs tsh_erp_app --since 1h 2>&1 | grep -i error | tail -5"

# 6. SSL Certificate Expiry
echo -e "\n🔐 SSL Certificate:"
echo | openssl s_client -servername erp.tsh.sale -connect erp.tsh.sale:443 2>/dev/null | openssl x509 -noout -dates

echo -e "\n✅ Health check complete!"
```

### Weekly Maintenance Tasks

**Every Sunday** (30 minutes):

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "🔧 TSH ERP Weekly Maintenance"
echo "================================"

# 1. Backup Database
echo "💾 Step 1: Backing up database..."
ssh root@167.71.39.50 "docker exec tsh_postgres pg_dump -U postgres tsh_erp > /backups/tsh_erp_$(date +%Y%m%d).sql"

# 2. Clean up old queue items (older than 30 days)
echo "🧹 Step 2: Cleaning up old queue items..."
ssh root@167.71.39.50 "PGPASSWORD='password' psql -U postgres -d tsh_erp -c \"DELETE FROM tds_sync_queue WHERE status IN ('completed', 'dead_letter') AND queued_at < NOW() - INTERVAL '30 days';\""

# 3. Clean up old Docker images (keep last 10)
echo "🗑️  Step 3: Cleaning up old Docker images..."
ssh root@167.71.39.50 "docker images | grep tsh_erp_docker-app | tail -n +11 | awk '{print \$3}' | xargs -r docker rmi"

# 4. Update system packages
echo "📦 Step 4: Updating system packages..."
ssh root@167.71.39.50 "apt update && apt upgrade -y"

# 5. Restart containers (for fresh start)
echo "🔄 Step 5: Restarting containers..."
ssh root@167.71.39.50 "docker-compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml restart"

# 6. Generate weekly report
echo "📊 Step 6: Generating weekly report..."
# ... report generation logic ...

echo "✅ Weekly maintenance complete!"
```

### Monitoring Setup (Optional - Recommended)

**Prometheus + Grafana Stack**:

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - tsh_network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_secure_password
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - tsh_network

volumes:
  prometheus_data:
  grafana_data:
```

**Key Metrics to Monitor**:
- API response time (p50, p95, p99)
- Sync queue depth
- Webhook delivery success rate
- Database connection pool usage
- Docker container health
- Disk space usage
- CPU/Memory usage

---

## Team Transition Plan

### Phase 1: Parallel Operation (Current Phase)

**Duration**: 2-4 weeks

**Goal**: Validate TSH ERP functionality while maintaining Zoho as primary

**Team Behavior**:
- ✅ Continue using Zoho Books/Inventory as primary system
- ✅ TSH ERP syncs data automatically in background
- ✅ Team can view/verify data in TSH ERP (read-only validation)
- ❌ Do NOT make changes directly in TSH ERP yet

**Validation Checklist**:

```
□ All products sync correctly (images, descriptions, prices)
□ All customers sync correctly (contact details, addresses)
□ All invoices sync correctly (line items, totals, taxes)
□ All bills sync correctly
□ Inventory levels sync accurately
□ Price lists sync correctly
□ No sync delays (< 30 seconds average)
□ No data loss or corruption
□ All webhooks processed successfully (> 99% success rate)
```

### Phase 2: Gradual Migration (After Validation)

**Duration**: 2-4 weeks

**Goal**: Start using TSH ERP for specific workflows while maintaining Zoho sync

**Team Behavior**:
- ✅ Use TSH ERP for new workflows (e.g., POS, consumer app)
- ✅ Continue using Zoho for accounting/reporting
- ✅ Bi-directional sync ensures both systems stay updated
- ⚠️ Monitor data consistency daily

**Recommended Order**:
1. **Week 1**: POS transactions (TSH ERP) → Sync to Zoho
2. **Week 2**: Consumer orders (TSH ERP) → Sync to Zoho
3. **Week 3**: Inventory management (TSH ERP) → Sync to Zoho
4. **Week 4**: Customer management (TSH ERP) → Sync to Zoho

### Phase 3: Full Migration (Final Phase)

**Duration**: 2-4 weeks

**Goal**: TSH ERP becomes primary system, Zoho for backup/reporting only

**Team Behavior**:
- ✅ Use TSH ERP for ALL operations
- ✅ Zoho receives updates (one-way sync for reporting)
- ✅ Export reports from TSH ERP
- ❌ Avoid making changes in Zoho (read-only)

**Migration Completion Criteria**:

```
□ All team members trained on TSH ERP
□ All workflows tested and validated
□ Reporting dashboards created in TSH ERP
□ Backup procedures established
□ 100% data consistency verified
□ Performance meets requirements (< 200ms average response time)
□ No critical bugs in production
□ Team comfortable with new system
```

### Training & Support

**Team Training Schedule**:

**Week 1**: System Overview
- Architecture and design philosophy
- Key features and differences from Zoho
- Navigation and basic operations

**Week 2**: Daily Operations
- Creating invoices and bills
- Managing customers and products
- Processing orders and payments
- Inventory management

**Week 3**: Advanced Features
- Reports and analytics
- Bulk operations
- Custom workflows
- Troubleshooting

**Week 4**: Admin & Support
- User management
- Permissions and roles
- System monitoring
- Backup and recovery

**Support Channels**:
- 📧 Email: support@tsh.sale
- 💬 Slack: #tsh-erp-support
- 📱 Phone: +XXX-XXXX-XXXX (emergency only)
- 📖 Documentation: https://docs.tsh.sale

---

## Emergency Contacts

**Senior Engineer (You)**:
- Role: System Architecture & Deployment
- Contact: [Your Contact Info]
- Availability: 24/7 for critical issues

**Team Lead**:
- Role: Product & Business Logic
- Contact: [Team Lead Contact]

**DevOps Engineer** (if applicable):
- Role: Infrastructure & Monitoring
- Contact: [DevOps Contact]

**Zoho Support**:
- Support: https://help.zoho.com
- API Issues: api-support@zoho.com

---

## Appendix

### Essential Commands Cheat Sheet

```bash
# SSH to VPS
ssh root@167.71.39.50

# Check all containers
docker ps -a

# View logs (live)
docker logs -f tsh_erp_app

# View logs (last 100 lines)
docker logs tsh_erp_app --tail 100

# Restart container
docker restart tsh_erp_app

# Rebuild image
cd /home/deploy/TSH_ERP_Ecosystem && docker build -t tsh_erp_docker-app:latest .

# Check disk space
df -h

# Check Docker disk usage
docker system df

# Clean up Docker
docker system prune -a --volumes -f

# Database access
docker exec -it tsh_postgres psql -U postgres -d tsh_erp

# Redis access
docker exec -it tsh_redis redis-cli

# Health check
curl https://erp.tsh.sale/health

# Sync stats
curl https://erp.tsh.sale/api/zoho/sync/stats
```

### Environment Variables Reference

**Required Variables** (`.env` file):

```bash
# Application
APP_ENV=production
APP_DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=erp.tsh.sale,localhost

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DB_HOST=aws-1-eu-north-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_db_password

# Redis
REDIS_URL=redis://tsh_redis:6379/0

# Zoho Integration
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
ZOHO_ORGANIZATION_ID=your_zoho_org_id

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
```

### Database Schema Updates

When schema changes are needed:

```bash
# 1. Create migration
alembic revision -m "description of change"

# 2. Edit migration file
# Edit: alembic/versions/xxxxx_description_of_change.py

# 3. Test locally
alembic upgrade head

# 4. Deploy to production
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && docker exec tsh_erp_app alembic upgrade head"

# 5. Verify migration
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U postgres -d tsh_erp -c '\dt'"
```

---

---

## Senior Engineering Standards & Best Practices

### 1. Token Management & Authentication Strategy

**Philosophy**: Proactive token management prevents service disruptions

#### 1.1 Automatic Token Refresh System

**Implementation**: `app/tds/integrations/zoho/auth.py`

```python
class ZohoAuthManager:
    """
    Handles Zoho OAuth 2.0 with automatic token refresh

    Features:
    - Auto-refresh 5 minutes before expiration
    - Background refresh task
    - Thread-safe token access
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        credentials: ZohoCredentials,
        auto_refresh: bool = True,
        refresh_buffer_minutes: int = 5
    ):
        self.credentials = credentials
        self.auto_refresh = auto_refresh
        self.refresh_buffer = timedelta(minutes=refresh_buffer_minutes)
        self._access_token = None
        self._token_expires_at = None
        self._refresh_task = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start auto-refresh background task"""
        if self.auto_refresh:
            self._refresh_task = asyncio.create_task(
                self._auto_refresh_loop()
            )

    async def _auto_refresh_loop(self):
        """Background task to refresh token before expiration"""
        while True:
            try:
                # Check if token needs refresh
                if self._needs_refresh():
                    await self.refresh_access_token()

                # Check every minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-refresh error: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
```

**Token Refresh Rules:**

1. **Always refresh 5 minutes before expiration**
2. **Retry up to 3 times with exponential backoff**
3. **Log all refresh attempts and failures**
4. **Never expose tokens in logs**
5. **Use environment variables, never hardcode**

#### 1.2 Rate Limiting Strategy

**Implementation**: `app/tds/integrations/zoho/utils/rate_limiter.py`

```python
class RateLimiter:
    """
    Token bucket rate limiter for Zoho API

    Limits:
    - Books API: 100 requests/minute
    - Inventory API: 25 requests/minute
    """

    def __init__(self, requests_per_minute: int = 100):
        self.rate = requests_per_minute
        self.tokens = requests_per_minute
        self.last_refill = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Wait for available token"""
        async with self.lock:
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_refill
            refill_amount = elapsed * (self.rate / 60.0)

            self.tokens = min(
                self.rate,
                self.tokens + refill_amount
            )
            self.last_refill = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.rate / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1
```

**Rate Limit Best Practices:**

- ✅ Never exceed 90% of rate limit (safety buffer)
- ✅ Implement exponential backoff on 429 errors
- ✅ Track API usage per endpoint
- ✅ Prioritize critical operations
- ✅ Queue non-urgent requests

#### 1.3 Token Validation Schedule

**Daily**: Verify token validity
```bash
# Cron job: daily_token_check.sh
#!/bin/bash
# Run at 2 AM daily
0 2 * * * /scripts/daily_token_check.sh

# Script content:
curl -X POST https://erp.tsh.sale/api/zoho/test-credentials \
  | jq '.status'

# If failed, send alert and refresh
```

**Monitoring**: Token health dashboard
```sql
-- Track token refresh history
CREATE TABLE zoho_token_refresh_log (
    id SERIAL PRIMARY KEY,
    refresh_type VARCHAR(20), -- 'auto' or 'manual'
    success BOOLEAN,
    error_message TEXT,
    token_expires_at TIMESTAMP,
    refreshed_at TIMESTAMP DEFAULT NOW()
);

-- Query recent refresh activity
SELECT * FROM zoho_token_refresh_log
ORDER BY refreshed_at DESC
LIMIT 10;
```

---

### 2. Code Quality & Consolidation Standards

**Philosophy**: Clean, DRY (Don't Repeat Yourself), maintainable code

#### 2.1 Code Duplication Detection

**Before any new code**, check for existing implementations:

```bash
#!/bin/bash
# check_duplication.sh

# Search for similar function names
grep -r "def sync_products" app/
grep -r "class ProductProcessor" app/
grep -r "async def fetch_zoho" app/

# Find similar patterns
rg "async def.*zoho.*fetch" app/
rg "class.*Sync.*Service" app/
```

**Consolidation Checklist:**

- [ ] Check `app/tds/` for existing TDS implementations
- [ ] Search for similar function names
- [ ] Review `app/services/` for legacy code
- [ ] Check `app/routers/` for duplicate endpoints
- [ ] Verify no redundant database models

#### 2.2 File Organization Rules

**TDS Core Structure** (Primary - Use This):
```
app/tds/
├── core/
│   ├── sync_engine.py       # Main sync orchestrator
│   └── events.py            # Event definitions
├── integrations/
│   └── zoho/
│       ├── client.py        # Unified API client
│       ├── auth.py          # Token management
│       ├── sync.py          # Sync operations
│       ├── webhooks.py      # Webhook handling
│       ├── stock_sync.py    # Stock sync
│       └── processors/      # Data transformers
│           ├── products.py
│           ├── customers.py
│           └── invoices.py
└── models/
    ├── sync_run.py
    └── sync_queue.py
```

**Legacy Structure** (Deprecated - Remove/Migrate):
```
app/services/
├── zoho_service.py         # ❌ DEPRECATED → Use tds/integrations/zoho/
├── zoho_sync.py            # ❌ DEPRECATED → Use tds/integrations/zoho/sync.py
└── zoho_processor.py       # ❌ DEPRECATED → Use tds/processors/
```

**Migration Strategy:**

1. **Identify** duplicate functionality
2. **Consolidate** into TDS structure
3. **Update** all imports
4. **Test** thoroughly
5. **Delete** old files
6. **Document** changes

#### 2.3 Code Review Checklist

**Before every commit:**

```markdown
## Code Quality Checklist

### Architecture
- [ ] Code follows TDS architecture
- [ ] No duplicate functionality
- [ ] Functions are in correct modules
- [ ] Proper separation of concerns

### Documentation
- [ ] Docstrings for all functions
- [ ] Type hints for parameters
- [ ] Comments for complex logic
- [ ] README updated if needed

### Testing
- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases covered

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS protection in place

### Performance
- [ ] No N+1 queries
- [ ] Proper indexing used
- [ ] Batch operations where possible
- [ ] Async operations utilized

### Error Handling
- [ ] Try-except blocks present
- [ ] Errors logged properly
- [ ] User-friendly error messages
- [ ] Retry logic implemented
```

---

### 3. Project Health & Size Optimization

**Philosophy**: Keep codebase lean, remove technical debt

#### 3.1 Codebase Analysis Workflow

**After every task completion:**

```bash
#!/bin/bash
# analyze_project.sh

echo "📊 TSH ERP Project Health Analysis"
echo "===================================="

# 1. Count lines of code by type
echo -e "\n📝 Lines of Code:"
find app/ -name "*.py" | xargs wc -l | tail -1

# 2. Find large files (> 500 lines)
echo -e "\n📦 Large Files (>500 lines):"
find app/ -name "*.py" -exec wc -l {} + | awk '$1 > 500' | sort -rn

# 3. Find duplicate code
echo -e "\n🔍 Potential Duplicates:"
fdupes -r app/ -S

# 4. Find unused imports
echo -e "\n🗑️  Unused Imports:"
autoflake --check --recursive app/

# 5. Find dead code
echo -e "\n💀 Dead Code:"
vulture app/ --min-confidence 80

# 6. Count TODO/FIXME
echo -e "\n📌 TODOs and FIXMEs:"
grep -r "TODO\|FIXME" app/ | wc -l

# 7. Security vulnerabilities
echo -e "\n🔐 Security Check:"
bandit -r app/ -ll

# 8. Dependencies audit
echo -e "\n📦 Dependencies:"
pip list --outdated
```

**Run after every major feature**:
```bash
./scripts/analyze_project.sh > reports/health_$(date +%Y%m%d).txt
```

#### 3.2 Files to Remove/Archive

**Criteria for Removal:**

1. **Archived/Old Files**:
   ```bash
   # Check for archived directories
   find . -type d -name "*archive*" -o -name "*old*" -o -name "*backup*"

   # Move to archive directory (not tracked by git)
   mkdir -p .archive/$(date +%Y%m%d)
   mv app/services/old_zoho_* .archive/$(date +%Y%m%d)/
   ```

2. **Unused Scripts**:
   ```bash
   # Find scripts not executed in last 30 days
   find scripts/ -type f -name "*.py" -mtime +30

   # Verify with git log
   git log --since="30 days ago" --name-only -- scripts/
   ```

3. **Test Fixtures** (if not needed):
   ```bash
   # Large test data files
   find tests/ -name "*.json" -size +1M
   find tests/ -name "*.csv" -size +1M
   ```

4. **Temporary Files**:
   ```bash
   # Python cache
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   find . -name "*.pyo" -delete

   # OS files
   find . -name ".DS_Store" -delete
   find . -name "Thumbs.db" -delete
   ```

**Monthly Cleanup Schedule:**

```bash
#!/bin/bash
# monthly_cleanup.sh

# Run on 1st of every month
echo "🧹 Monthly Project Cleanup"

# 1. Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# 2. Remove old logs
find logs/ -name "*.log" -mtime +30 -delete

# 3. Clean Docker
docker system prune -a --volumes -f

# 4. Archive old migrations (if needed)
# ... archive logic ...

# 5. Update .gitignore for ignored patterns
```

#### 3.3 Project Size Targets

**Optimal Sizes:**

| Component | Target Size | Max Size | Action if Exceeded |
|-----------|------------|----------|-------------------|
| Single File | < 300 lines | 500 lines | Split into modules |
| Function | < 50 lines | 100 lines | Extract subfunctions |
| Class | < 300 lines | 500 lines | Split responsibilities |
| Module | < 10 files | 20 files | Create subpackages |
| Dependencies | < 50 packages | 75 packages | Remove unused |

**Monitoring Script:**

```python
# scripts/size_monitor.py
import os
from pathlib import Path

def analyze_file_sizes(root_dir="app/"):
    """Analyze and report file sizes"""
    large_files = []

    for path in Path(root_dir).rglob("*.py"):
        lines = len(path.read_text().splitlines())

        if lines > 500:
            large_files.append((str(path), lines))

    # Sort by size
    large_files.sort(key=lambda x: x[1], reverse=True)

    print("⚠️  Files exceeding 500 lines:")
    for file, lines in large_files:
        print(f"   {file}: {lines} lines")

    return large_files

if __name__ == "__main__":
    analyze_file_sizes()
```

---

### 4. Daily Data Investigation System

**Philosophy**: Trust but verify - daily data consistency checks

#### 4.1 Automated Daily Comparison

**Implementation**: `scripts/daily_data_investigation.py`

```python
#!/usr/bin/env python3
"""
Daily Data Investigation System
================================

Compares data counts between Zoho and TSH ERP
Alerts on discrepancies

Run daily at 3 AM via cron:
0 3 * * * /usr/bin/python3 /path/to/daily_data_investigation.py
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from app.tds.integrations.zoho import UnifiedZohoClient, ZohoAPI
from app.db.database import get_async_db

class DataInvestigator:
    """Daily data consistency checker"""

    async def investigate(self) -> Dict[str, Any]:
        """Run full investigation"""

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "discrepancies": [],
            "entities": {}
        }

        # Check each entity type
        entities_to_check = [
            ("products", "items", "products"),
            ("customers", "contacts", "customers"),
            ("invoices", "invoices", "invoices"),
            ("orders", "salesorders", "sales_orders")
        ]

        for entity_name, zoho_endpoint, db_table in entities_to_check:
            result = await self._compare_entity(
                entity_name, zoho_endpoint, db_table
            )
            report["entities"][entity_name] = result

            if result["discrepancy"]:
                report["discrepancies"].append(result)
                report["status"] = "warning"

        # Save report
        await self._save_report(report)

        # Send alert if discrepancies found
        if report["discrepancies"]:
            await self._send_alert(report)

        return report

    async def _compare_entity(
        self,
        entity_name: str,
        zoho_endpoint: str,
        db_table: str
    ) -> Dict[str, Any]:
        """Compare counts for single entity type"""

        # Get Zoho count
        zoho_count = await self._get_zoho_count(zoho_endpoint)

        # Get database count
        db_count = await self._get_db_count(db_table)

        # Calculate discrepancy
        difference = abs(zoho_count - db_count)
        percentage = (difference / zoho_count * 100) if zoho_count > 0 else 0

        result = {
            "entity": entity_name,
            "zoho_count": zoho_count,
            "db_count": db_count,
            "difference": difference,
            "discrepancy_percentage": round(percentage, 2),
            "discrepancy": percentage > 1.0,  # Alert if > 1% difference
            "timestamp": datetime.utcnow().isoformat()
        }

        return result

    async def _get_zoho_count(self, endpoint: str) -> int:
        """Get entity count from Zoho"""
        # Initialize Zoho client
        zoho_client = await self._get_zoho_client()

        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint=endpoint,
            params={"per_page": 1, "page": 1}
        )

        page_context = response.get('page_context', {})
        return page_context.get('total', 0)

    async def _get_db_count(self, table: str) -> int:
        """Get entity count from database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text(f"SELECT COUNT(*) FROM {table}")
                result = await db.execute(query)
                count = result.scalar()
                return count
            finally:
                break

        return 0

    async def _save_report(self, report: Dict[str, Any]):
        """Save investigation report to database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text("""
                    INSERT INTO data_investigation_reports
                    (report_date, status, report_data, created_at)
                    VALUES (CURRENT_DATE, :status, :report_data, NOW())
                """)

                await db.execute(query, {
                    "status": report["status"],
                    "report_data": json.dumps(report)
                })

                await db.commit()
            finally:
                break

    async def _send_alert(self, report: Dict[str, Any]):
        """Send alert if discrepancies found"""
        # Email alert
        subject = f"⚠️ TSH ERP Data Discrepancy Alert - {datetime.utcnow().date()}"

        body = f"""
        Data Investigation Report
        =========================

        Status: {report['status']}
        Timestamp: {report['timestamp']}

        Discrepancies Found:
        """

        for disc in report['discrepancies']:
            body += f"""

            Entity: {disc['entity']}
            - Zoho Count: {disc['zoho_count']}
            - Database Count: {disc['db_count']}
            - Difference: {disc['difference']} ({disc['discrepancy_percentage']}%)
            """

        # Send email (implement email sending logic)
        # await send_email(subject, body)

        # Log alert
        print(f"🚨 ALERT: {subject}")
        print(body)

# Run investigation
async def main():
    investigator = DataInvestigator()
    report = await investigator.investigate()

    print("=" * 70)
    print("📊 Daily Data Investigation Report")
    print("=" * 70)
    print(json.dumps(report, indent=2))
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
```

**Database Schema for Reports:**

```sql
-- Create investigation reports table
CREATE TABLE IF NOT EXISTS data_investigation_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'healthy', 'warning', 'critical'
    report_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX idx_investigation_date ON data_investigation_reports(report_date DESC);

-- View recent investigations
CREATE VIEW recent_investigations AS
SELECT
    report_date,
    status,
    (report_data->>'timestamp')::TIMESTAMP as investigated_at,
    jsonb_array_length(report_data->'discrepancies') as discrepancy_count
FROM data_investigation_reports
ORDER BY report_date DESC
LIMIT 30;
```

#### 4.2 Cron Job Setup

```bash
# Add to VPS crontab
ssh root@167.71.39.50

# Edit crontab
crontab -e

# Add daily investigation at 3 AM
0 3 * * * cd /home/deploy/TSH_ERP_Ecosystem && /usr/bin/python3 scripts/daily_data_investigation.py >> /var/log/tsh_data_investigation.log 2>&1
```

#### 4.3 Investigation Dashboard

**Endpoint**: `GET /api/admin/data-investigation`

```python
@router.get("/data-investigation")
async def get_investigation_dashboard(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get recent investigation reports"""

    from sqlalchemy import text

    query = text("""
        SELECT
            report_date,
            status,
            report_data
        FROM data_investigation_reports
        WHERE report_date >= CURRENT_DATE - :days
        ORDER BY report_date DESC
    """)

    result = db.execute(query, {"days": days})
    reports = result.fetchall()

    return {
        "total_reports": len(reports),
        "healthy_count": sum(1 for r in reports if r[1] == 'healthy'),
        "warning_count": sum(1 for r in reports if r[1] == 'warning'),
        "reports": [
            {
                "date": str(r[0]),
                "status": r[1],
                "data": r[2]
            }
            for r in reports
        ]
    }
```

---

### 5. Consumer App Product Filtering

**Philosophy**: Only show products with available stock

#### 5.1 Consumer Price List Requirement

**CRITICAL REQUIREMENT**: The Flutter Consumer App MUST display products using the **Consumer Price List** only. **NO FALLBACK TO BASE PRICE IS ALLOWED**.

**Implementation Details**:

1. **Backend Endpoints**:
   - `GET /api/consumer/products` - Returns products with Consumer pricelist pricing ONLY
   - `GET /api/bff/mobile/consumer/products` - BFF endpoint with Consumer pricelist pricing ONLY
   
2. **Price List Selection**:
   - Products MUST use the pricelist with code **"consumer_iqd"**
   - Currency MUST be **"IQD"** (Iraqi Dinar)
   - **CRITICAL**: NO fallback to base price - products without Consumer prices are NOT displayed
   
3. **Query Implementation** (`app/routers/consumer_api.py:138-170` and `app/bff/mobile/router.py:1234-1264`):
   ```sql
   LEFT JOIN LATERAL (
       SELECT pp.price, pp.currency
       FROM product_prices pp
       JOIN price_lists pl ON pp.pricelist_id = pl.id
       WHERE pp.product_id = p.id
         AND pl.code = 'consumer_iqd'  -- Use code for exact match
         AND (pp.currency = 'IQD' OR pp.currency IS NULL)
         AND pp.price > 0
       ORDER BY pp.price DESC
       LIMIT 1
   ) consumer_price ON true
   WHERE ...
     AND consumer_price.price IS NOT NULL 
     AND consumer_price.price > 0  -- CRITICAL: Only show products with Consumer prices
   ```
   
   **Important Notes**:
   - Table name is `price_lists` (with underscore), NOT `pricelists`
   - Use `pl.code = 'consumer_iqd'` for exact match (more reliable than name matching)
   - WHERE clause MUST require Consumer price (no OR condition allowing base price)
   
4. **Response Format**:
   ```json
   {
     "price": 15000.00,
     "currency": "IQD"
   }
   ```

5. **Validation in CI/CD**:
   - GitHub Actions workflow (`deploy-staging.yml`) includes `validate-consumer-pricelist` step
   - Validation script (`scripts/validate_consumer_pricelist.py`) checks:
     - Consumer price list exists
     - All products with stock have Consumer prices
     - No products are missing Consumer prices
   - Deployment FAILS if any product lacks Consumer price list price
   - Price currency MUST be IQD

6. **Root Cause Fix (November 2025)**:
   - **Issue**: Queries used wrong table name (`pricelists` instead of `price_lists`)
   - **Issue**: Fallback logic allowed base prices when Consumer prices missing
   - **Fix**: Changed table name to `price_lists`, removed fallback, enforced Consumer price requirement
   - **Result**: Consumer app now ONLY shows products with Consumer price list prices

**Flutter App Requirements**:
- Display Consumer pricelist price for all products
- Format prices in IQD currency
- Show currency symbol (IQD) or formatted as "15,000 IQD"

#### 5.2 API Filtering Rules

**Already Implemented**: `app/routers/consumer_api.py:119`

```python
# WHERE clause filters for products with stock
where_conditions = [
    "p.is_active = true",           # Only active products
    "p.actual_available_stock > 0"  # Only products with stock
]
```

**Additional Filters (Optional):**

```python
# Add to where_conditions based on requirements
where_conditions.extend([
    "p.price > 0",                  # Only products with price
    "p.image_url IS NOT NULL",      # Only products with images (optional)
    "p.category IS NOT NULL"        # Only categorized products (optional)
])
```

#### 5.2 Stock Threshold Configuration

**Environment Variable**: `.env`
```bash
# Minimum stock to display
CONSUMER_MIN_STOCK=1

# Low stock warning threshold
CONSUMER_LOW_STOCK_THRESHOLD=10
```

**Implementation**:
```python
min_stock = int(os.getenv('CONSUMER_MIN_STOCK', 1))
where_conditions.append(f"p.actual_available_stock >= {min_stock}")
```

#### 5.3 Real-time Stock Updates

**Webhook Integration**: When stock changes in Zoho, update immediately

```python
@router.post("/webhooks/stock-update")
async def handle_stock_webhook(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle real-time stock updates from Zoho"""

    item_id = payload.get('item_id')
    new_stock = payload.get('actual_available_stock')

    # Update database
    db.execute(
        "UPDATE products SET actual_available_stock = :stock "
        "WHERE zoho_item_id = :item_id",
        {"stock": new_stock, "item_id": item_id}
    )
    db.commit()

    # Clear cache
    await redis.delete(f"product:{item_id}")

    return {"status": "success"}
```

---

### 6. TDS Core Responsibilities

**Philosophy**: TDS = Single Source of Truth for all sync operations

#### 6.1 TDS Architecture Mandate

**ALL Zoho operations MUST go through TDS:**

```
❌ WRONG: Direct Zoho API calls from routers
app/routers/products.py → zoho_client.get("items")

✅ CORRECT: Through TDS
app/routers/products.py → TDS Sync Orchestrator → Zoho Client
```

#### 6.2 TDS Responsibilities

**TDS Core (`app/tds/`) is responsible for:**

1. **Authentication**:
   - Token management
   - Auto-refresh
   - Rate limiting

2. **API Communication**:
   - All Zoho API calls
   - Request/response handling
   - Error handling and retries

3. **Data Transformation**:
   - Zoho format → TSH format
   - Validation
   - Enrichment

4. **Synchronization**:
   - Webhooks processing
   - Bulk sync operations
   - Queue management

5. **Event Publishing**:
   - Sync events
   - Status updates
   - Error notifications

**Other modules MUST NOT:**
- ❌ Make direct Zoho API calls
- ❌ Handle OAuth tokens
- ❌ Transform Zoho data
- ❌ Manage sync queue

**Migration Plan for Legacy Code:**

```bash
# Find legacy direct Zoho calls
grep -r "zoho_client\|ZohoService" app/routers/ app/services/

# Move to TDS
# Example:
# OLD: app/services/product_service.py → zoho_client.get("items")
# NEW: app/services/product_service.py → tds.sync.sync_entity(EntityType.PRODUCTS)
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 7, 2025 | Senior Engineer | Initial Tronix guide created |
| 1.1.0 | Nov 7, 2025 | Senior Engineer | Added senior engineering standards |
|  |  |  | - Token management strategy |
|  |  |  | - Code consolidation guidelines |
|  |  |  | - Daily data investigation system |
|  |  |  | - Consumer app filtering |
|  |  |  | - TDS core responsibilities |

---

## Notes

**This guide is a living document**. Update it whenever:
- Architecture changes
- New features are added
- Deployment process changes
- New issues and solutions are discovered
- Team feedback suggests improvements

**Remember**: As a senior engineer, your responsibility is not just to build and deploy, but to **document, mentor, and ensure the system can be maintained by others**.

---

**🚀 Stay sharp. Deploy smart. Build for the future.**

*End of Tronix Guide*
