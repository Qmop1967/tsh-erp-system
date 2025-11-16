# AI Monitoring & Alert Guidelines

**Purpose:** Proactive security and performance monitoring patterns
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/ai-guidelines/ai-monitoring.md

---

## 🚨 Automated Security Scanning

### Critical Security Issues (BLOCK IMMEDIATELY)

#### 1. SQL Injection Vulnerabilities
```python
# ❌ VULNERABLE - Alert and fix immediately
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# Alert: "🚨 SECURITY CRITICAL: SQL injection vulnerability at [location]"
# Action: Rewrite with parameterized query

# ✅ SAFE - Use ORM or parameterized queries
query = select(User).filter(User.email == user_input)
```

#### 2. Direct Zoho API Access (Architecture Violation)
```python
# ❌ VIOLATION - Alert immediately
import requests
response = requests.get("https://www.zohoapis.com/books/v3/invoices")

# Alert: "🚨 ARCHITECTURE VIOLATION: Direct Zoho API access at [location]"
# Action: Route through TDS Core

# ✅ CORRECT - Through TDS Core
from app.tds.sync_engine import TDSCore
tds = TDSCore()
invoices = await tds.get_invoices_from_zoho()
```

#### 3. Hardcoded Credentials
```python
# ❌ CRITICAL - Alert immediately
database_url = "postgresql://user:password123@localhost/db"

# Alert: "🚨 SECURITY CRITICAL: Hardcoded credentials at [location]"
# Action: Use environment variables

# ✅ SAFE - Environment variables
database_url = os.getenv("DATABASE_URL")
```

#### 4. Missing Authentication
```python
# ❌ VULNERABLE - Alert immediately
@router.delete("/api/products/{id}")
async def delete_product(id: int):
    db.query(Product).filter(Product.id == id).delete()

# Alert: "🚨 SECURITY CRITICAL: Endpoint lacks authentication"
# Action: Add authentication

# ✅ SECURE - Authentication required
@router.delete("/api/products/{id}")
async def delete_product(
    id: int,
    current_user: User = Depends(get_current_user)
):
    service = ProductService(db, current_user)
    return await service.delete_product(id)
```

#### 5. Missing Authorization (RBAC + ABAC + RLS)
```python
# ❌ INSECURE - Missing all 3 layers
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

# Alert: "🚨 SECURITY CRITICAL: Missing all 3 authorization layers"
# Action: Implement RBAC + ABAC + RLS

# ✅ SECURE - All 3 layers present
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role(["admin", "salesperson"])),  # RBAC
    abac: User = Depends(check_abac_permission("orders.read")),    # ABAC
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS filtering
    return await service.get_orders()
```

---

## ⚡ Performance Monitoring

### Critical Performance Issues (FLAG IMMEDIATELY)

#### 1. Missing Pagination
```python
# ❌ SLOW - Alert for large datasets
@router.get("/products")
async def get_products():
    return db.query(Product).all()  # Returns all 2,218+ products!

# Alert: "⚠️ PERFORMANCE: Returns 2,218+ products without pagination"
# Action: Add pagination

# ✅ FAST - Paginated
@router.get("/products")
async def get_products(skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()
```

#### 2. N+1 Query Problem
```python
# ❌ SLOW - N+1 queries
orders = db.query(Order).all()
for order in orders:
    client = db.query(Client).filter(Client.id == order.client_id).first()

# Alert: "⚠️ PERFORMANCE: N+1 query detected, will make N database calls"
# Action: Use joinedload

# ✅ FAST - Single query with join
orders = db.query(Order).options(joinedload(Order.client)).all()
```

#### 3. Missing Database Indexes
```python
# ⚠️ Flag if querying on unindexed columns
# Check WHERE clauses on:
- Foreign keys (client_id, product_id, etc.)
- Search fields (email, phone, sku)
- Filter fields (status, is_active, category)

# Alert: "⚠️ PERFORMANCE: Querying products.sku without index"
# Suggestion: CREATE INDEX idx_products_sku ON products(sku);
```

#### 4. Sync I/O in Async Context
```python
# ❌ SLOW - Blocking async function
async def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()  # Blocks!

# Alert: "💡 OPTIMIZATION: Blocking I/O in async function"
# Action: Use async database session

# ✅ FAST - Async database query
async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Product).filter(Product.id == product_id)
    )
    return result.scalar_one_or_none()
```

---

## 🎯 Alert Levels & Response Actions

### 🔴 CRITICAL (Stop Immediately)
```yaml
Triggers:
  - SQL injection vulnerability
  - Direct Zoho API access
  - Hardcoded credentials
  - Missing authentication on sensitive endpoint
  - Data corruption risk

Action:
  1. STOP current implementation
  2. Alert: "🚨 CRITICAL: [issue] at [location]"
  3. Explain: What's wrong, why it's dangerous, what could happen
  4. Fix: Implement secure pattern
  5. Verify: Test fix works
  6. Never allow insecure code to proceed
```

### ⚠️ HIGH PRIORITY (Fix Immediately)
```yaml
Triggers:
  - Missing pagination (>100 records)
  - N+1 query pattern
  - Missing input validation
  - Missing RBAC checks
  - Missing Arabic fields

Action:
  1. Alert: "⚠️ [category]: [issue] at [location]"
  2. Automatically fix (don't ask)
  3. Continue execution
  4. Explain what was fixed
```

### 💡 MEDIUM PRIORITY (Suggest Improvement)
```yaml
Triggers:
  - Inefficient algorithm
  - Missing database index
  - Sync I/O in async context
  - Code duplication

Action:
  1. Alert: "💡 OPTIMIZATION: [issue] at [location]"
  2. Suggest fix
  3. Ask if should apply
  4. Continue if user approves
```

---

## 🔍 Monitoring Triggers

### When to Scan for Security Issues

**Automatic Scanning:**
```yaml
Scan during:
  - Writing new endpoints
  - Modifying database queries
  - Handling user input
  - Implementing authentication/authorization
  - Before deployment (pre-commit check)
```

**Scan Checklist:**
```yaml
□ No SQL injection vulnerabilities
□ No direct Zoho API access
□ No hardcoded credentials
□ All sensitive endpoints authenticated
□ All restricted operations have RBAC + ABAC + RLS
□ All user input validated (Pydantic)
□ No sensitive data exposed in responses
□ XSS protection in place
```

### When to Scan for Performance Issues

**Automatic Scanning:**
```yaml
Scan during:
  - Creating list endpoints
  - Writing database queries
  - Implementing loops with queries
  - Working with large datasets
```

**Scan Checklist:**
```yaml
□ Pagination on all list endpoints (max 100)
□ No N+1 queries (use joinedload)
□ Indexes on foreign keys and search fields
□ Async I/O used correctly
□ Large files processed in streams
□ Appropriate caching (if applicable)
```

---

## 📊 Scale-Based Thresholds

Given TSH ERP scale (500+ clients, 2,218+ products, 30+ orders/day):

### Performance Thresholds
```yaml
Database Queries:
  > 100 records → MUST paginate
  > 1,000 rows → MUST have indexes
  > 1 second query time → Flag for optimization

API Response:
  < 500ms → Good ✅
  500ms - 2s → Investigate ⚠️
  > 2s → Optimize immediately 🚨

Background Jobs:
  > 5 seconds → Move to background job (Celery)
```

### Security Thresholds
```yaml
Data Operations:
  Any endpoint modifying data → MUST have authentication
  Any admin operation → MUST have RBAC (role check)
  Any financial data → MUST exclude from logs
  Any Zoho operation → MUST go through TDS Core
```

---

## 🛡️ Context-Aware Monitoring

### TSH ERP Specific Checks

#### 1. Arabic Support Check
```python
# When creating user-facing model:
class Product(Base):
    name = Column(String, nullable=False)
    # ⚠️ ALERT: Missing name_ar field!

# Alert: "⚠️ BUSINESS RULE: Product model lacks Arabic fields"
# Action: Add name_ar and description_ar automatically
```

#### 2. TDS Core Routing Check
```python
# When seeing Zoho API access:
import requests
requests.get("https://www.zohoapis.com/books/v3/...")

# 🚨 CRITICAL ALERT: Direct Zoho API access!
# Action: Rewrite to use TDS Core
```

#### 3. Authorization Layer Check
```python
# When creating endpoint:
@router.get("/sensitive-data")
async def get_data(db: Session = Depends(get_db)):
    # ⚠️ Check authorization layers:
    # Missing: RBAC (no role check)
    # Missing: ABAC (no attribute check)
    # Missing: RLS (direct DB query)

# Alert: "🚨 SECURITY: Missing all 3 authorization layers"
```

---

## 📋 Pre-Deployment Security Scan

Before ANY deployment, verify:

```yaml
Security Checklist:
□ No SQL injection vulnerabilities
□ No direct Zoho API access (all through TDS Core)
□ No hardcoded credentials
□ All sensitive endpoints authenticated
□ All restricted operations have RBAC + ABAC + RLS
□ All user input validated (Pydantic)
□ No sensitive data in logs
□ XSS protection in place
□ Arabic fields present on user-facing data

Performance Checklist:
□ Pagination on all list endpoints
□ No N+1 queries
□ Indexes on large tables
□ Async I/O used correctly
□ No blocking operations in async functions
□ Response times < 500ms
```

---

## 🎯 Alert Message Format

When detecting an issue:

```markdown
**[EMOJI] [LEVEL] [CATEGORY]: Brief Description**

Location: [file:line]
Issue: [What was detected]
Impact: [What could go wrong / why this matters]
Action: [What I'm doing OR asking user]

[Code example if relevant]
```

**Example:**
```
🚨 CRITICAL SECURITY: SQL Injection Vulnerability

Location: app/routers/products.py:45
Issue: User input directly concatenated into SQL query
Impact: Attackers could read, modify, or delete any database data
Action: Replacing with parameterized query using SQLAlchemy ORM

Before:
query = f"SELECT * FROM products WHERE sku = '{user_sku}'"

After:
products = db.query(Product).filter(Product.sku == user_sku).all()
```

---

## 💡 Proactive Monitoring Best Practices

### During Code Review
```yaml
1. Read code with security mindset
2. Check against known vulnerability patterns
3. Verify performance patterns for scale
4. Flag issues immediately (don't wait)
5. Fix critical issues automatically
6. Suggest improvements for medium issues
```

### During Implementation
```yaml
1. Think "security first" not "security later"
2. Apply performance patterns from start
3. Don't create technical debt
4. Test security assumptions
5. Verify at scale (500+ clients, 2,218+ products)
```

### Before Committing
```yaml
1. Final security scan
2. Final performance check
3. Verify all 3 authorization layers
4. Verify Arabic support
5. Test with production-scale data
6. Check for hardcoded values
```

---

**Related Guidelines:**
- Core interpretation: @docs/reference/ai-guidelines/ai-context-core.md
- Session recovery: @docs/reference/ai-guidelines/ai-session-recovery.md
- Operation modes: @docs/reference/ai-guidelines/ai-operation-modes.md
