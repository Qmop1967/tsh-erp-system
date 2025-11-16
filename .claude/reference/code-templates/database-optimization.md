# Database Optimization Templates

**Purpose:** Production-ready database optimization patterns for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/database-optimization.md

---

## 🗄️ Template 7.1: Query with Proper Indexing

**Reasoning Context:**
- TSH ERP has 2,218+ products, 500+ clients, growing data
- Queries without indexes cause full table scans (SLOW)
- Indexes on foreign keys, search fields, filter fields are MANDATORY
- Query performance degrades linearly without indexes
- EXPLAIN ANALYZE shows if indexes are used

**When to Use:**
- Queries on tables with > 1,000 rows
- WHERE clauses on non-primary-key columns
- JOIN operations
- ORDER BY clauses
- Frequently executed queries

**Code Template:**

```python
# Database migration to add indexes
# alembic/versions/xxxx_add_product_indexes.py

from alembic import op

def upgrade():
    """Add indexes for product queries."""

    # Index on sku (frequently searched)
    op.create_index(
        'idx_products_sku',
        'products',
        ['sku'],
        unique=False
    )

    # Index on category_id (frequently filtered)
    op.create_index(
        'idx_products_category_id',
        'products',
        ['category_id'],
        unique=False
    )

    # Index on is_active (frequently filtered)
    op.create_index(
        'idx_products_is_active',
        'products',
        ['is_active'],
        unique=False
    )

    # Compound index for name search (English + Arabic)
    op.create_index(
        'idx_products_names',
        'products',
        ['name', 'name_ar'],
        unique=False
    )

    # Index on created_at for sorting
    op.create_index(
        'idx_products_created_at',
        'products',
        ['created_at'],
        unique=False
    )

def downgrade():
    """Remove indexes."""
    op.drop_index('idx_products_sku', 'products')
    op.drop_index('idx_products_category_id', 'products')
    op.drop_index('idx_products_is_active', 'products')
    op.drop_index('idx_products_names', 'products')
    op.drop_index('idx_products_created_at', 'products')

# Optimized query using indexes
def get_products_by_category(category_id: int, is_active: bool, db: Session):
    """
    Get products by category (optimized with indexes).

    Performance:
    - Without indexes: 800ms+ for 2,218 products (full table scan)
    - With indexes: 50ms (index seek)
    """
    return db.query(Product).filter(
        Product.category_id == category_id,  # Uses idx_products_category_id
        Product.is_active == is_active        # Uses idx_products_is_active
    ).order_by(
        Product.created_at.desc()             # Uses idx_products_created_at
    ).all()

# Verify index usage with EXPLAIN ANALYZE
from sqlalchemy import text

def check_query_performance(db: Session):
    """Check if indexes are being used."""
    query = text("""
        EXPLAIN ANALYZE
        SELECT * FROM products
        WHERE category_id = 5 AND is_active = true
        ORDER BY created_at DESC
    """)

    result = db.execute(query)
    plan = result.fetchall()

    # Look for "Index Scan" (good) vs "Seq Scan" (bad)
    for row in plan:
        print(row[0])
```

**Index Guidelines:**

```yaml
ALWAYS index:
□ Primary keys (automatic)
□ Foreign keys (category_id, client_id, user_id)
□ Unique constraints (email, sku)
□ Frequently searched fields (name, name_ar, phone)
□ Frequently filtered fields (is_active, status, type)
□ Frequently sorted fields (created_at, updated_at)

CONSIDER indexing:
□ Compound indexes for multi-column WHERE (category_id + is_active)
□ Partial indexes for common filters (WHERE is_active = true)
□ Full-text search indexes (name, description)

DON'T over-index:
□ Rarely queried columns
□ Columns with low cardinality (boolean with even distribution)
□ Write-heavy tables (indexes slow down INSERTs/UPDATEs)
```

**Related Patterns:**
- Pagination: @docs/reference/code-templates/pagination.md
- Template 7.2: Prevent N+1 Queries

---

## 🗄️ Template 7.2: Prevent N+1 Query Problem

**Reasoning Context:**
- N+1 queries happen when loading related data in loops
- Example: Load 100 orders, then 100 separate queries for clients (101 total queries!)
- SQLAlchemy's joinedload/selectinload solves this (2 queries instead of 101)
- Critical for performance at TSH ERP scale
- Easy to miss during development, catastrophic in production

**When to Use:**
- Loading resources with related data (orders → clients, products → categories)
- List endpoints that include relationships
- Any time you access `.relationship` in a loop

**Code Template:**

```python
# ❌ BAD: N+1 Query Problem
@router.get("/orders")
async def list_orders_bad(db: Session = Depends(get_db)):
    """BAD: Causes N+1 queries."""

    orders = db.query(Order).limit(100).all()  # 1 query

    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "client_name": order.client.name,  # 👈 100 additional queries!
            "total": order.total_amount
        })

    # Total: 101 queries (1 + 100)
    return result

# ✅ GOOD: Optimized with joinedload
from sqlalchemy.orm import joinedload, selectinload

@router.get("/orders")
async def list_orders_good(db: Session = Depends(get_db)):
    """GOOD: Uses eager loading to prevent N+1."""

    orders = db.query(Order).options(
        joinedload(Order.client)  # 👈 Load clients in same query
    ).limit(100).all()  # 1 query with JOIN

    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "client_name": order.client.name,  # No additional query!
            "total": order.total_amount
        })

    # Total: 1 query (100x faster!)
    return result

# When to use joinedload vs selectinload
@router.get("/orders/detailed")
async def list_orders_detailed(db: Session = Depends(get_db)):
    """
    joinedload: Use for one-to-one or many-to-one (Order → Client)
    selectinload: Use for one-to-many (Order → OrderItems)
    """

    orders = db.query(Order).options(
        joinedload(Order.client),              # One-to-one: use joinedload
        selectinload(Order.order_items).       # One-to-many: use selectinload
            joinedload(OrderItem.product)       # Nested eager loading
    ).limit(100).all()

    # Total: 2-3 queries (vs 100+ without eager loading)
    return orders
```

**Performance Comparison:**

```python
# Benchmark example
import time

def benchmark_n_plus_one():
    """Compare N+1 vs eager loading performance."""

    # Bad: N+1 queries
    start = time.time()
    orders = db.query(Order).limit(100).all()
    for order in orders:
        _ = order.client.name  # Triggers lazy load
    bad_time = time.time() - start

    # Good: Eager loading
    start = time.time()
    orders = db.query(Order).options(
        joinedload(Order.client)
    ).limit(100).all()
    for order in orders:
        _ = order.client.name  # No additional query
    good_time = time.time() - start

    print(f"N+1: {bad_time:.2f}s | Eager: {good_time:.2f}s | Speedup: {bad_time/good_time:.1f}x")
    # Example output: N+1: 2.45s | Eager: 0.18s | Speedup: 13.6x
```

**Detecting N+1 Queries:**

```python
# Enable SQL logging to detect N+1
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Run your endpoint and watch for repeated similar queries
# Example of N+1 pattern in logs:
# SELECT * FROM orders LIMIT 100
# SELECT * FROM clients WHERE id = 1    # 👈 Repeated for each order
# SELECT * FROM clients WHERE id = 2
# SELECT * FROM clients WHERE id = 3
# ... (100 more queries)
```

**Related Patterns:**
- CRUD list operations: @docs/reference/code-templates/crud-operations.md
- Indexing: Template 7.1

---

## ⚡ Database Performance Checklist

```yaml
Query Optimization:
□ Indexes on all foreign keys
□ Indexes on search/filter fields
□ Use EXPLAIN ANALYZE to verify index usage
□ Avoid N+1 queries (use joinedload/selectinload)
□ Paginate results (max 100 items)
□ Use transactions for multiple writes

Connection Pooling:
□ Configure connection pool size
□ Set proper timeout values
□ Monitor connection usage
□ Close connections properly

Query Patterns to Avoid:
❌ SELECT * (specify columns)
❌ Queries without WHERE clause on large tables
❌ Lazy loading in loops (N+1)
❌ Sorting without indexes
❌ No pagination on large result sets
```

---

**Related Documentation:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Pagination: @docs/reference/code-templates/pagination.md
- Architecture: @docs/core/architecture.md
