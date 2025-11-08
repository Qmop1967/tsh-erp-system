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
├─> activeForm: Present continuous ("Searching for existing code", "Fixing import errors")
└─> status: pending | in_progress | completed
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

1. [Core Development Principles](#core-development-principles) ⭐ **MANDATORY**
2. [Claude Code Operating Instructions](#claude-code-operating-instructions) 🤖 **MANDATORY**
3. [Overview](#overview)
4. [Product Roadmap & Multi-Price List System](#product-roadmap--multi-price-list-system) 🚀 **STRATEGIC**
5. [Architecture Philosophy](#architecture-philosophy)
6. [Deployment Strategy](#deployment-strategy)
7. [Zoho Integration Strategy](#zoho-integration-strategy)
8. [Development Workflow](#development-workflow)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Maintenance & Monitoring](#maintenance--monitoring)
11. [Team Transition Plan](#team-transition-plan)

---

## Overview

### Project Context

**TSH ERP Ecosystem** is a comprehensive ERP system built with:
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Self-Hosted on VPS)
- **Cache**: Redis
- **Web Server**: Nginx (Reverse Proxy)
- **Deployment**: Docker Compose
- **Integration**: Zoho Books & Inventory (Bi-directional Sync)

### 🌟 Why "Ecosystem"? - The Fundamental Architecture Principle

**Understanding the "Ecosystem" Concept:**

The name **"TSH ERP Ecosystem"** is not just a title—it represents a **fundamental architectural philosophy** that governs how ALL components of the system are designed, built, and integrated.

**"Ecosystem" means:**

```
┌─────────────────────────────────────────────────────────────┐
│         THE ECOSYSTEM ARCHITECTURE PRINCIPLES                │
└─────────────────────────────────────────────────────────────┘

🔴 PRINCIPLE 1: ONE CENTRALIZED SELF-HOSTED DATABASE
├─> ALL project components share ONE PostgreSQL database
├─> Self-hosted on VPS (167.71.39.50)
├─> NO external databases (no Supabase, Firebase, etc.)
├─> DRY (Don't Repeat Yourself) - single source of truth
└─> All apps read/write to the SAME unified database

🔴 PRINCIPLE 2: ONE UNIFIED AUTHENTICATION SYSTEM
├─> ALL applications use ONE authentication mechanism
├─> Shared user sessions across all apps
├─> Centralized user management
├─> Single login = access to all authorized apps
└─> Consistent security standards everywhere

🔴 PRINCIPLE 3: ONE UNIFIED AUTHORIZATION SYSTEM
├─> ALL applications use ONE role-based access control (RBAC)
├─> Shared permissions and roles across ecosystem
├─> Centralized authorization rules
├─> User permissions defined once, applied everywhere
└─> Consistent access control policies

🔴 PRINCIPLE 4: UNIFIED & ORGANIZED ARCHITECTURE
├─> ALL components follow the SAME architectural patterns
├─> Consistent code structure across all apps
├─> Shared libraries and services
├─> Standardized API design
├─> Common logging, monitoring, error handling
└─> Same development principles everywhere
```

**What This Means in Practice:**

```
┌─────────────────────────────────────────────────────────────┐
│              ECOSYSTEM COMPONENT INTEGRATION                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ TSH Consumer App │  │ TSH Clients App  │  │ TSH Technical    │
│ (Flutter)        │  │ (Flutter)        │  │ App (Flutter)    │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         └─────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Backend    │
                    │  (Unified API Layer) │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Unified Auth/AuthZ  │
                    │  (Single System)     │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  PostgreSQL Database │
                    │  (ONE SHARED DB)     │
                    │  Self-Hosted VPS     │
                    └──────────────────────┘

✅ ONE Database - All apps share the same data
✅ ONE Authentication - Login once, access all apps
✅ ONE Authorization - Permissions defined centrally
✅ ONE Architecture - Consistent patterns everywhere
```

**Benefits of the Ecosystem Approach:**

1. **Data Consistency**
   - No data synchronization issues between apps
   - Real-time data access for all components
   - Single source of truth for all business data

2. **Development Efficiency**
   - Write authentication logic ONCE
   - Create API endpoints ONCE, use everywhere
   - Shared code libraries reduce duplication

3. **Maintenance Simplicity**
   - Update database schema in ONE place
   - Fix bugs ONCE, benefits all apps
   - Centralized monitoring and logging

4. **User Experience**
   - Seamless experience across all applications
   - Single login for all services
   - Consistent interface and behavior

5. **Security & Compliance**
   - Centralized security controls
   - Easier to audit and maintain
   - Consistent security standards

**Anti-Patterns to AVOID:**

```
❌ WRONG: Multiple Databases
   - Consumer app has its own database
   - Clients app has separate database
   - Result: Data sync nightmares, inconsistencies

❌ WRONG: Multiple Authentication Systems
   - Each app has its own login
   - Different user tables
   - Result: User management chaos

❌ WRONG: Inconsistent Architecture
   - Each app built with different patterns
   - Different API designs
