# Quality Enhancement Framework for Multi-Agent System

**Version:** 1.0.0
**Created:** 2025-11-15
**Purpose:** Comprehensive framework to ensure all agents deliver stable, secure, reliable, scalable, maintainable code with consistency and harmony

---

## 🎯 The 7 Pillars of Quality

Every agent must enforce these 7 pillars in all code they produce:

1. **Stability** - Code works reliably without crashes
2. **Security** - Code protects against vulnerabilities
3. **Reliability** - Code handles failures gracefully
4. **Scalability** - Code performs well under load
5. **Maintainability** - Code is easy to understand and modify
6. **Consistency** - Code follows established patterns
7. **Harmony** - Code integrates seamlessly with existing system

---

## 1️⃣ STABILITY

### Definition
Code that works reliably without crashes, handles edge cases, and provides clear error messages.

### Requirements Checklist
- [ ] All functions have error handling (try/except blocks)
- [ ] All errors logged with context (logger.error with details)
- [ ] All functions have docstrings explaining purpose and parameters
- [ ] All edge cases handled (None, empty lists, zero values)
- [ ] All user inputs validated before processing
- [ ] All external dependencies have fallback behavior
- [ ] All async operations have timeout limits
- [ ] All database sessions properly closed (use context managers)

### Code Examples

#### ❌ UNSTABLE CODE
```python
def get_product_price(product_id):
    product = db.query(Product).filter(Product.id == product_id).first()
    return product.price * 1.15  # Crashes if product is None
```

#### ✅ STABLE CODE
```python
def get_product_price(product_id: int) -> Optional[Decimal]:
    """
    Calculate product price with tax (15% IQD tax rate).

    Args:
        product_id: Unique identifier of the product

    Returns:
        Decimal: Price with tax, or None if product not found

    Raises:
        ValueError: If product_id is invalid
    """
    try:
        # Validate input
        if not product_id or product_id <= 0:
            raise ValueError(f"Invalid product_id: {product_id}")

        # Query with proper error handling
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_deleted == False
        ).first()

        if not product:
            logger.warning(f"Product not found: {product_id}")
            return None

        if product.price is None or product.price < 0:
            logger.error(f"Invalid price for product {product_id}: {product.price}")
            return None

        # Calculate with tax
        tax_rate = Decimal("1.15")
        return product.price * tax_rate

    except ValueError as e:
        logger.error(f"Validation error in get_product_price: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_product_price: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_product_price: {e}")
        return None
```

---

## 2️⃣ SECURITY

### Definition
Code that protects against vulnerabilities, enforces authentication/authorization, and follows security best practices.

### Requirements Checklist
- [ ] All endpoints require authentication (Depends(get_current_user))
- [ ] All sensitive operations require authorization (RoleChecker)
- [ ] All database queries use parameterized queries (NO f-strings in SQL)
- [ ] All user inputs validated and sanitized
- [ ] All secrets in environment variables (never hardcoded)
- [ ] All passwords hashed with bcrypt
- [ ] All tokens use secure random generation
- [ ] All uploads validated (file type, size, content)
- [ ] All responses sanitized (no sensitive data leaks)
- [ ] All SQL operations implement RLS (Row-Level Security)

### The 3 Authorization Layers (NON-NEGOTIABLE)

**EVERY endpoint must implement ALL 3 layers:**

#### Layer 1: RBAC (Role-Based Access Control)
```python
@router.get("/admin/users")
async def list_users(
    current_user: User = Depends(get_current_user),  # Authenticated user
    _role_check: bool = Depends(RoleChecker(["admin", "manager"])),  # Role check
    db: Session = Depends(get_db_with_rls)
):
    # Only admin and manager can access
```

#### Layer 2: ABAC (Attribute-Based Access Control)
```python
@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_with_rls)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    # ABAC: Check attributes
    if order.customer_id not in current_user.assigned_customer_ids:
        raise HTTPException(status_code=403, detail="Not authorized for this customer")

    if order.created_at < current_user.access_start_date:
        raise HTTPException(status_code=403, detail="No access to historical orders")

    return order
```

#### Layer 3: RLS (Row-Level Security)
```python
# Set RLS context before all queries
def get_db_with_rls():
    db = SessionLocal()
    try:
        # Set user context for RLS policies
        db.execute(text(
            "SET LOCAL app.current_user_id = :user_id;"
        ), {"user_id": current_user.id})

        # Set role context
        db.execute(text(
            "SET LOCAL app.current_role = :role;"
        ), {"role": current_user.role.name})

        yield db
    finally:
        db.close()
```

### SQL Injection Prevention

#### ❌ VULNERABLE (SQL Injection)
```python
user_id = request.query_params.get("user_id")
db.execute(f"DELETE FROM users WHERE id = {user_id}")  # CRITICAL VULNERABILITY
```

#### ✅ SECURE (Parameterized Query)
```python
from sqlalchemy import text

user_id = request.query_params.get("user_id")
db.execute(
    text("DELETE FROM users WHERE id = :user_id"),
    {"user_id": user_id}
)
```

---

## 3️⃣ RELIABILITY

### Definition
Code that handles failures gracefully, implements retry logic, and ensures data integrity.

### Requirements Checklist
- [ ] All external API calls have retry logic (max 3 retries)
- [ ] All retries use exponential backoff (1s, 2s, 4s)
- [ ] All database operations use transactions
- [ ] All transactions have rollback on error
- [ ] All critical operations are idempotent
- [ ] All background jobs have dead letter queue
- [ ] All state changes are atomic
- [ ] All file operations check disk space first

### Retry Pattern with Exponential Backoff
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def sync_zoho_product(product_id: int):
    """
    Sync product from Zoho with automatic retry.

    Retries up to 3 times with exponential backoff:
    - Attempt 1: immediate
    - Attempt 2: wait 1 second
    - Attempt 3: wait 2 seconds
    """
    try:
        response = await zoho_client.get_product(product_id)
        return response
    except ZohoAPIError as e:
        logger.warning(f"Zoho API error, will retry: {e}")
        raise  # Trigger retry
    except Exception as e:
        logger.error(f"Fatal error, no retry: {e}")
        raise  # No retry for unexpected errors
```

### Transaction Pattern
```python
from sqlalchemy.orm import Session

def create_order_with_items(order_data: dict, items_data: list, db: Session):
    """
    Create order with items in a single transaction.

    All changes committed together or rolled back on error.
    """
    try:
        # Begin transaction (automatically managed by context)
        db.begin_nested()  # Savepoint for rollback

        # Create order
        order = Order(**order_data)
        db.add(order)
        db.flush()  # Get order.id without committing

        # Create items
        for item_data in items_data:
            item = OrderItem(order_id=order.id, **item_data)
            db.add(item)

        # Update product stock
        for item_data in items_data:
            product = db.query(Product).filter(
                Product.id == item_data["product_id"]
            ).with_for_update().first()  # Lock row for update

            if product.stock < item_data["quantity"]:
                raise ValueError(f"Insufficient stock for product {product.id}")

            product.stock -= item_data["quantity"]

        # Commit transaction
        db.commit()
        logger.info(f"Order created successfully: {order.id}")
        return order

    except Exception as e:
        # Rollback all changes
        db.rollback()
        logger.error(f"Order creation failed, rolled back: {e}")
        raise
```

---

## 4️⃣ SCALABILITY

### Definition
Code that performs well under load, supports growth, and optimizes resource usage.

### Requirements Checklist
- [ ] All lists paginated (max 100 items per page)
- [ ] All foreign keys indexed in database
- [ ] All search fields indexed in database
- [ ] All read-heavy queries cached (Redis)
- [ ] All N+1 query patterns eliminated (use joinedload)
- [ ] All long operations moved to background jobs
- [ ] All database connections use connection pooling
- [ ] All response payloads optimized (only needed fields)

### Pagination (MANDATORY for lists > 100 items)
```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int

@router.get("/products", response_model=PaginatedResponse[ProductSchema])
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),  # Max 100
    db: Session = Depends(get_db)
):
    """List products with pagination"""

    # Count total items
    total = db.query(Product).filter(Product.is_deleted == False).count()

    # Calculate pagination
    skip = (page - 1) * per_page
    pages = (total + per_page - 1) // per_page

    # Query with limit and offset
    products = db.query(Product).filter(
        Product.is_deleted == False
    ).order_by(
        Product.created_at.desc()
    ).limit(per_page).offset(skip).all()

    return PaginatedResponse(
        items=products,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )
```

### N+1 Query Elimination
```python
from sqlalchemy.orm import joinedload

# ❌ BAD: N+1 queries (1 + N additional queries)
orders = db.query(Order).all()  # 1 query
for order in orders:
    print(order.customer.name)  # N queries (one per order)
    for item in order.items:
        print(item.product.name)  # N*M queries

# ✅ GOOD: Single optimized query with eager loading
orders = db.query(Order).options(
    joinedload(Order.customer),  # Load customer in same query
    joinedload(Order.items).joinedload(OrderItem.product)  # Load items and products
).all()  # Single query with joins

for order in orders:
    print(order.customer.name)  # No additional query
    for item in order.items:
        print(item.product.name)  # No additional query
```

### Caching Strategy
```python
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def get_product_catalog(category: str = None) -> List[Product]:
    """
    Get product catalog with Redis caching.

    Cache hit: ~5ms response time
    Cache miss: ~200ms response time
    """
    # Build cache key
    cache_key = f"product_catalog:{category or 'all'}"

    # Try cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit: {cache_key}")
        return json.loads(cached_data)

    # Cache miss - query database
    logger.info(f"Cache miss: {cache_key}")
    query = db.query(Product).filter(Product.is_active == True)

    if category:
        query = query.filter(Product.category == category)

    products = query.all()

    # Cache for 1 hour
    redis_client.setex(
        cache_key,
        3600,  # TTL: 1 hour
        json.dumps([p.to_dict() for p in products])
    )

    return products

# Invalidate cache on product update
async def update_product(product_id: int, updates: dict):
    """Update product and invalidate relevant caches"""
    product = db.query(Product).filter(Product.id == product_id).first()

    for key, value in updates.items():
        setattr(product, key, value)

    db.commit()

    # Invalidate caches
    redis_client.delete(f"product_catalog:all")
    redis_client.delete(f"product_catalog:{product.category}")
    redis_client.delete(f"product:{product_id}")
```

---

## 5️⃣ MAINTAINABILITY

### Definition
Code that is easy to understand, modify, and extend by other developers.

### Requirements Checklist
- [ ] All code follows style guide (PEP 8 for Python, Dart guide for Flutter)
- [ ] All functions < 50 lines (break down complex functions)
- [ ] All files < 500 lines (split large files)
- [ ] All magic numbers replaced with named constants
- [ ] All duplicated code extracted to utility functions
- [ ] All complex logic has explanatory comments
- [ ] All public APIs documented with examples
- [ ] All code passes linting (Ruff, MyPy)

### Code Organization
```python
# ❌ BAD: Magic numbers, unclear logic
def calculate_commission(sales):
    if sales > 10000000:
        return sales * 0.15
    elif sales > 5000000:
        return sales * 0.10
    else:
        return sales * 0.05

# ✅ GOOD: Named constants, clear structure
# constants.py
COMMISSION_TIER_1_THRESHOLD = 10_000_000  # 10M IQD
COMMISSION_TIER_2_THRESHOLD = 5_000_000   # 5M IQD
COMMISSION_TIER_1_RATE = Decimal("0.15")  # 15%
COMMISSION_TIER_2_RATE = Decimal("0.10")  # 10%
COMMISSION_BASE_RATE = Decimal("0.05")    # 5%

def calculate_commission(sales_amount: Decimal) -> Decimal:
    """
    Calculate sales commission based on tiered rates.

    Commission Tiers:
    - Sales > 10M IQD: 15% commission
    - Sales 5M-10M IQD: 10% commission
    - Sales < 5M IQD: 5% commission

    Args:
        sales_amount: Total sales in IQD

    Returns:
        Decimal: Commission amount in IQD

    Example:
        >>> calculate_commission(Decimal("12000000"))
        Decimal("1800000")  # 15% of 12M
    """
    if sales_amount >= COMMISSION_TIER_1_THRESHOLD:
        return sales_amount * COMMISSION_TIER_1_RATE
    elif sales_amount >= COMMISSION_TIER_2_THRESHOLD:
        return sales_amount * COMMISSION_TIER_2_RATE
    else:
        return sales_amount * COMMISSION_BASE_RATE
```

### Function Size Limit
```python
# ❌ BAD: Function too long (>50 lines), doing too much
def process_order(order_data):
    # 100+ lines of mixed responsibilities
    # - Validation
    # - Customer lookup
    # - Inventory check
    # - Payment processing
    # - Email sending
    # - Logging
    # Hard to understand and test

# ✅ GOOD: Break into focused functions
def process_order(order_data: dict) -> Order:
    """
    Process customer order through complete workflow.

    Returns:
        Order: Created order object
    """
    # Each step is a separate, testable function
    validate_order_data(order_data)
    customer = get_or_create_customer(order_data["customer_id"])
    check_inventory_availability(order_data["items"])
    payment = process_payment(order_data["payment"])
    order = create_order(order_data, payment)
    send_order_confirmation(order)
    log_order_created(order)
    return order
```

---

## 6️⃣ CONSISTENCY

### Definition
Code that follows established patterns, conventions, and architectural standards across the entire system.

### Requirements Checklist
- [ ] All models have Arabic fields (name_ar, description_ar)
- [ ] All models have timestamps (created_at, updated_at)
- [ ] All models have soft delete (is_deleted, deleted_at)
- [ ] All API responses follow standard format
- [ ] All error responses follow standard format
- [ ] All database tables use snake_case naming
- [ ] All Python classes use PascalCase naming
- [ ] All functions use snake_case naming
- [ ] All constants use UPPER_SNAKE_CASE naming

### Standard Model Template
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric
from datetime import datetime

class Product(Base):
    """
    Standard model with ALL required fields.

    This is the template ALL models must follow.
    """
    __tablename__ = "products"

    # Primary key (required)
    id = Column(Integer, primary_key=True, index=True)

    # Bilingual fields (required for user-facing content)
    name = Column(String(255), nullable=False)  # English
    name_ar = Column(String(255), nullable=False)  # Arabic
    description = Column(Text)  # English
    description_ar = Column(Text)  # Arabic

    # Business fields (domain-specific)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, default=0)

    # Audit fields (required for all models)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Soft delete (required for all models)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey("users.id"))

    # Active status (business logic)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"
```

### Standard API Response Format
```python
# Success response
{
    "success": true,
    "data": {
        "id": 123,
        "name": "Laptop",
        "name_ar": "لابتوب"
    },
    "message": "Product retrieved successfully",
    "timestamp": "2025-11-15T12:00:00Z"
}

# Error response
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid product data",
        "details": {
            "field": "price",
            "issue": "Price must be positive"
        }
    },
    "timestamp": "2025-11-15T12:00:00Z"
}

# Paginated response
{
    "success": true,
    "data": {
        "items": [...],
        "total": 2218,
        "page": 1,
        "per_page": 50,
        "pages": 45
    },
    "message": "Products retrieved successfully",
    "timestamp": "2025-11-15T12:00:00Z"
}
```

---

## 7️⃣ HARMONY

### Definition
Code that integrates seamlessly with existing system, respects established architecture, and works well with other agents.

### Requirements Checklist
- [ ] All new code follows existing patterns (search before creating)
- [ ] All dependencies match project requirements.txt
- [ ] All imports organized (stdlib, third-party, local)
- [ ] All new features integrate with existing features
- [ ] All breaking changes discussed and approved
- [ ] All agents coordinate on shared components
- [ ] All code reviews include cross-agent perspective
- [ ] All architectural decisions documented

### Integration Pattern
```python
# When adding a new feature, integrate with existing systems

# 1. Search for existing similar functionality
# Before: Creating new customer service
# Do: Search for existing customer code
result = subprocess.run(
    ["grep", "-r", "class CustomerService", "app/services/"],
    capture_output=True
)

# 2. Extend existing service rather than create new
from app.services.customer_service import CustomerService

# ❌ BAD: Create duplicate service
class NewCustomerService:
    def get_customer(self, id):
        # Duplicates existing functionality
        pass

# ✅ GOOD: Extend existing service
class CustomerService:
    # Existing methods
    def get_customer(self, id):
        pass

    # Add new method to existing service
    def get_customer_with_orders(self, id):
        customer = self.get_customer(id)
        orders = self.order_service.get_customer_orders(customer.id)
        customer.orders = orders
        return customer
```

### Cross-Agent Coordination
```python
# Example: Creating a new order endpoint

# 1. API Agent creates endpoint skeleton
@router.post("/orders")
async def create_order(order_data: OrderCreate):
    # API Agent responsibility: Request validation
    pass

# 2. Database Agent ensures schema supports the feature
# Checks: orders table has all needed columns, indexes present

# 3. Security Agent adds authorization
@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),  # Security Agent
    _role_check: bool = Depends(RoleChecker(["salesperson", "admin"])),  # Security Agent
    db: Session = Depends(get_db_with_rls)  # Security Agent
):
    pass

# 4. i18n Agent ensures bilingual support
class OrderCreate(BaseModel):
    notes: Optional[str]
    notes_ar: Optional[str]  # i18n Agent adds Arabic field

# 5. Performance Agent optimizes
async def create_order(...):
    # Performance Agent: Use background job for heavy operations
    from app.background.tasks import send_order_confirmation
    send_order_confirmation.delay(order.id)

# 6. Testing Agent writes tests
def test_create_order_success():
    # Testing Agent: Comprehensive test coverage
    pass

# 7. Docs Agent documents
@router.post("/orders")
async def create_order(...):
    """
    Create a new order.

    **Required Permissions:** salesperson, admin

    **Request Body:**
    - customer_id: Customer identifier
    - items: List of order items
    - notes: Order notes (English)
    - notes_ar: Order notes (Arabic)

    **Returns:**
    - 201: Order created successfully
    - 400: Invalid order data
    - 403: Insufficient permissions
    - 500: Server error
    """
```

---

## 📊 Quality Metrics & Monitoring

### Code Quality Dashboard (Proposed)
```yaml
Metrics to Track:

Stability:
  - Error rate: < 0.1% of requests
  - Crash rate: 0 crashes per day
  - Test pass rate: > 99%

Security:
  - Vulnerabilities: 0 critical, 0 high
  - Authentication coverage: 100% of sensitive endpoints
  - SQL injection risks: 0

Reliability:
  - Uptime: > 99.9%
  - Transaction success rate: > 99.5%
  - Data integrity checks: 100% pass

Scalability:
  - API response time (p99): < 500ms
  - Database query time (p99): < 100ms
  - Throughput: > 1000 requests/minute

Maintainability:
  - Code complexity: < 10 (cyclomatic complexity)
  - Function size: < 50 lines average
  - Documentation coverage: > 90%

Consistency:
  - Linting pass rate: 100%
  - Arabic field coverage: 100%
  - Standard format compliance: 100%

Harmony:
  - Integration test pass rate: > 95%
  - Cross-agent collaboration score: > 8/10
  - Architecture compliance: 100%
```

### Automated Quality Gates
```yaml
Every Pull Request Must Pass:

1. Linting (Ruff):
   - Zero errors
   - Zero warnings

2. Type Checking (MyPy):
   - Zero type errors
   - 100% type coverage

3. Security Scan (Bandit):
   - Zero critical issues
   - Zero high issues

4. Unit Tests:
   - 100% pass rate
   - Coverage > 80% overall
   - Coverage > 95% for new code

5. Integration Tests:
   - 100% pass rate
   - No breaking changes

6. Performance Tests:
   - Response time within limits
   - No N+1 queries introduced

7. Documentation:
   - All new functions documented
   - API docs updated
```

---

## 🎓 Agent Training & Best Practices

### Daily Agent Checklist
Before starting work:
- [ ] Read relevant documentation (`.claude/`)
- [ ] Search for existing similar code
- [ ] Understand cross-agent dependencies
- [ ] Review recent changes in domain area

During work:
- [ ] Follow all 7 quality pillars
- [ ] Write tests alongside code
- [ ] Document as you code
- [ ] Run linting and tests locally

Before committing:
- [ ] All tests pass
- [ ] All linting passes
- [ ] Code reviewed against quality checklist
- [ ] Documentation updated

### Code Review Checklist (for Reviewers)
- [ ] Stability: Error handling present and comprehensive?
- [ ] Security: All 3 authorization layers implemented?
- [ ] Reliability: Retry logic and transactions used?
- [ ] Scalability: Pagination, indexing, caching considered?
- [ ] Maintainability: Code clear, functions small, documented?
- [ ] Consistency: Follows project patterns and conventions?
- [ ] Harmony: Integrates well with existing codebase?

---

## 🚀 Continuous Improvement

### Monthly Quality Review
- Review quality metrics dashboard
- Identify patterns in bugs and issues
- Update agent training materials
- Refine quality standards
- Share learnings across agents

### Quarterly Architecture Review
- Assess architectural patterns
- Identify technical debt
- Plan refactoring initiatives
- Update ARCHITECTURE_RULES.md
- Align all agents on changes

### Annual Technology Refresh
- Review tech stack
- Evaluate new tools and libraries
- Update dependencies
- Modernize patterns
- Retrain all agents

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0
**Maintained By:** All Agents (Collective Responsibility)
