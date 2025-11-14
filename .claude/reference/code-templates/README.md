# Code Templates - TSH ERP Patterns

**Purpose:** Production-ready, reusable code templates organized by category
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/[category].md

---

## 📂 Template Categories

### 🔐 Authentication & Authorization
**File:** `authentication.md`
**Load:** `@docs/reference/code-templates/authentication.md`

Templates for:
- Protected API endpoints (Template 1.1)
- RBAC (Role-Based Access Control) endpoints (Template 1.2)
- Login & JWT token generation (Template 1.3)

**When to Use:**
- Implementing new secured endpoints
- Adding authentication to existing endpoints
- Setting up login/logout functionality
- Role-based access requirements

---

### 📊 CRUD Operations
**File:** `crud-operations.md`
**Load:** `@docs/reference/code-templates/crud-operations.md`

Templates for:
- Create resource with Arabic fields (Template 2.1)
- List resources with pagination (Template 2.2)
- Update resource (partial update) (Template 2.3)
- Delete resource (soft delete) (Template 2.4)

**When to Use:**
- Creating new resource endpoints (products, clients, orders)
- Adding list/search functionality
- Implementing update operations
- Adding delete/archive functionality

---

### 🔄 Zoho Sync Operations
**File:** `zoho-sync.md`
**Load:** `@docs/reference/code-templates/zoho-sync.md`

Templates for:
- Sync products from Zoho via TDS Core (Template 3.1)
- Scheduled sync jobs
- Error handling for Zoho operations

**When to Use:**
- Implementing Zoho data sync
- Creating scheduled sync jobs
- Handling Zoho API errors
- Building TDS Core integrations

---

### 🌍 Arabic Bilingual Support
**File:** `arabic-bilingual.md`
**Load:** `@docs/reference/code-templates/arabic-bilingual.md`

Templates for:
- Bilingual model mixin (Template 4.1)
- Arabic field patterns
- RTL support patterns

**When to Use:**
- Creating new user-facing models
- Adding Arabic support to existing models
- Implementing bilingual schemas

---

### 📄 Pagination Patterns
**File:** `pagination.md`
**Load:** `@docs/reference/code-templates/pagination.md`

Templates for:
- Web pagination (max 100 items)
- Mobile-optimized pagination (Template 5.1)
- Infinite scroll support

**When to Use:**
- List endpoints with >100 records
- Mobile app endpoints
- Infinite scroll implementations
- Search result pagination

---

### ❌ Error Handling
**File:** `error-handling.md`
**Load:** `@docs/reference/code-templates/error-handling.md`

Templates for:
- Standardized error responses (Template 6.1)
- Validation error handling
- Business logic errors
- Bilingual error messages

**When to Use:**
- Implementing error responses
- Custom exception handlers
- Validation error formatting
- Arabic error messages

---

### 🗄️ Database Optimization
**File:** `database-optimization.md`
**Load:** `@docs/reference/code-templates/database-optimization.md`

Templates for:
- Query with proper indexing (Template 7.1)
- Prevent N+1 query problem (Template 7.2)
- Eager loading with joinedload/selectinload

**When to Use:**
- Optimizing slow queries
- Adding indexes to tables
- Preventing N+1 queries
- Loading related data efficiently

---

### 🧪 Testing Patterns
**File:** `testing.md`
**Load:** `@docs/reference/code-templates/testing.md`

Templates for:
- Integration tests for API endpoints (Template 9.1)
- Test fixtures and helpers
- Database testing patterns

**When to Use:**
- Writing tests for new endpoints
- Testing CRUD operations
- Integration testing
- Bug fix verification

---

## 🎯 Quick Selection Guide

**I need to...**

| Task | Load This Template |
|------|-------------------|
| Secure an endpoint | `authentication.md` → Template 1.1 |
| Add role-based access | `authentication.md` → Template 1.2 |
| Create user login | `authentication.md` → Template 1.3 |
| Create new resource | `crud-operations.md` → Template 2.1 |
| List with pagination | `crud-operations.md` → Template 2.2 |
| Update a resource | `crud-operations.md` → Template 2.3 |
| Delete (soft delete) | `crud-operations.md` → Template 2.4 |
| Sync from Zoho | `zoho-sync.md` → Template 3.1 |
| Add Arabic fields | `arabic-bilingual.md` → Template 4.1 |
| Paginate for mobile | `pagination.md` → Template 5.1 |
| Handle errors | `error-handling.md` → Template 6.1 |
| Optimize query | `database-optimization.md` → Template 7.1 |
| Fix N+1 queries | `database-optimization.md` → Template 7.2 |
| Write tests | `testing.md` → Template 9.1 |

---

## 📋 Template Structure

Each template file includes:

```yaml
Template Components:
  1. Reasoning Context - WHY this pattern exists
  2. When to Use - Specific scenarios
  3. Code Template - Copy-paste-adapt implementation
  4. Customization Points - What to change for your use case
  5. Related Patterns - Links to other relevant templates
  6. Real Examples - TSH ERP specific code
```

---

## 💡 Usage Philosophy

**Templates are GUIDES, not rigid rules:**

- ✅ Understand the reasoning behind each pattern
- ✅ Adapt to specific requirements
- ✅ Combine multiple templates when needed
- ✅ Use as learning resources
- ❌ Don't blindly copy-paste without understanding
- ❌ Don't ignore context-specific needs

---

## 🔄 Loading Strategy

**When to load templates:**

```yaml
During Planning:
  - Load relevant template to understand pattern
  - Review reasoning and when-to-use sections
  - Plan adaptations needed

During Implementation:
  - Load specific template file
  - Copy template code
  - Customize for specific use case
  - Test implementation

Don't Load:
  - Don't load all templates at once (too much context)
  - Load only what's needed for current task
  - Use this README to identify which template to load
```

---

## 🎯 Template Coverage

```yaml
Current Templates: 14 templates across 8 categories

Coverage by Layer:
  Authentication/Security: 3 templates
  Data Operations: 4 templates
  Integration: 1 template
  Localization: 1 template
  Performance: 3 templates
  Error Handling: 1 template
  Testing: 1 template

TSH ERP Specific:
  ✅ Arabic bilingual support (mandatory)
  ✅ RBAC + ABAC + RLS authorization (3 layers)
  ✅ TDS Core integration (Zoho sync)
  ✅ Pagination (2,218+ products, 500+ clients)
  ✅ Mobile optimization (8 Flutter apps)
  ✅ Performance patterns (production scale)
```

---

## 📊 Template Maturity

```yaml
Production-Ready (Battle-Tested):
  ✅ Authentication & Authorization
  ✅ CRUD Operations
  ✅ Zoho Sync (via TDS Core)
  ✅ Arabic Bilingual Support
  ✅ Pagination
  ✅ Database Optimization

Mature (Well-Tested):
  ✅ Error Handling
  ✅ Testing Patterns

In Development:
  ⏸️ Mobile-specific patterns (future)
  ⏸️ Real-time updates (future)
  ⏸️ File upload patterns (future)
```

---

## 🚀 Common Workflows

### Workflow 1: Create New CRUD Resource

```yaml
1. Load authentication.md → Template 1.1 (secure endpoint)
2. Load crud-operations.md → Template 2.1 (create)
3. Load crud-operations.md → Template 2.2 (list with pagination)
4. Load arabic-bilingual.md → Template 4.1 (Arabic fields)
5. Load testing.md → Template 9.1 (write tests)
```

### Workflow 2: Optimize Slow Endpoint

```yaml
1. Load database-optimization.md → Template 7.1 (indexing)
2. Load database-optimization.md → Template 7.2 (N+1 queries)
3. Load pagination.md → Template 5.1 (if not paginated)
4. Load testing.md → Template 9.1 (verify performance)
```

### Workflow 3: Add Zoho Sync

```yaml
1. Load zoho-sync.md → Template 3.1 (sync pattern)
2. Load error-handling.md → Template 6.1 (error responses)
3. Load database-optimization.md → Template 7.1 (indexing for sync)
4. Load testing.md → Template 9.1 (sync tests)
```

---

## 🎓 Learning Resources

**New to TSH ERP patterns?**

Start with:
1. `authentication.md` - Understand security framework
2. `arabic-bilingual.md` - Understand localization requirements
3. `crud-operations.md` - Learn basic CRUD patterns
4. `pagination.md` - Understand scale requirements
5. `database-optimization.md` - Learn performance patterns

**Working on Zoho integration?**
1. `zoho-sync.md` - TDS Core integration patterns
2. `error-handling.md` - Handle API errors properly

**Building mobile endpoints?**
1. `pagination.md` - Mobile-optimized pagination
2. `error-handling.md` - Mobile-friendly errors
3. `authentication.md` - Mobile authentication

---

**Related Documentation:**
- Core patterns: @docs/core/architecture.md
- Authorization framework: @docs/AUTHORIZATION_FRAMEWORK.md
- TDS Core architecture: @docs/TDS_MASTER_ARCHITECTURE.md
- Deployment workflows: @docs/core/workflows.md
