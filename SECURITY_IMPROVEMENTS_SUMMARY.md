# TSH ERP Security Improvements Summary

## Overview
This document summarizes the comprehensive security improvements made to the TSH ERP Access Management system based on PostgreSQL Row-Level Security (RLS) best practices.

## Improvements Implemented

### 1. PostgreSQL Row-Level Security (RLS) Policies

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/database/migrations/implement_rls_policies.sql`

**What it does:**
- Enables RLS on critical tables: `users`, `customers`, `sales_orders`, `cash_transactions`, `expenses`
- Implements defense-in-depth security at the database layer
- Prevents unauthorized data access even if application-layer security is bypassed

**Policies Implemented:**

1. **Users Table**
   - Users can only view and update their own profile
   - Admins can access all user records

2. **Customers Table**
   - Sales reps can only see their assigned customers
   - Managers can see their entire team's customers
   - Only active customers are visible (ABAC rule)

3. **Sales Orders Table**
   - Sales reps see only orders they created
   - Or orders for customers assigned to them

4. **Cash Transactions Table**
   - Users see only their own transactions

5. **Expenses Table**
   - Users can view all their expenses
   - Users can only edit expenses under $5,000 that are still PENDING

**Security Model**: Hybrid RBAC + ReBAC + ABAC
- **RBAC**: Role-based functional permissions (e.g., admin vs. salesperson)
- **ReBAC**: Relationship-based data access (e.g., ownership, team hierarchy)
- **ABAC**: Attribute-based contextual rules (e.g., status=PENDING, amount<5000)

---

### 2. Session Variable Bridge (RLS Context Manager)

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/db/rls_context.py`

**What it does:**
- Connects FastAPI application authentication to PostgreSQL RLS policies
- Sets PostgreSQL session variables that RLS policies use for decision-making
- Provides both context manager and convenience function patterns

**Key Functions:**

1. **`set_rls_context(db, user_id, role_name, tenant_id, branch_id, warehouse_id)`**
   - Sets session variables at the start of database transactions
   - Should be called after user authentication

2. **`get_current_user_from_rls(db)`**
   - Retrieves current user ID from RLS session variables
   - Useful for debugging and verification

3. **`verify_rls_enabled(db)`**
   - Checks which tables have RLS enabled
   - Returns RLS status for auditing

4. **`list_active_policies(db)`**
   - Lists all active RLS policies
   - Useful for security audits

**Usage Example:**
```python
from app.db.rls_context import set_rls_context

def process_user_request(db: Session, current_user: User):
    # Set RLS context
    set_rls_context(
        db,
        user_id=current_user.id,
        role_name=current_user.role.name,
        tenant_id=current_user.tenant_id
    )

    # Now all queries are automatically filtered by RLS
    customers = db.query(Customer).all()  # Only returns accessible customers
```

---

### 3. RLS-Aware FastAPI Dependencies

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/db/rls_dependency.py`

**What it does:**
- Provides FastAPI dependency functions that automatically set RLS context
- Eliminates need to manually call `set_rls_context()` in every endpoint
- Enforces security by default through dependency injection

**Key Dependencies:**

1. **`get_db_with_rls()`**
   - Returns a database session with RLS context already set
   - Validates JWT token
   - Extracts user info and sets session variables

2. **`get_current_user_with_rls()`**
   - Returns the authenticated user object
   - Sets RLS context automatically
   - Use when you need both user data and RLS protection

**Usage Example:**
```python
from app.db.rls_dependency import get_db_with_rls, get_current_user_with_rls

# Option 1: Just need RLS-protected database session
@router.get("/customers")
async def list_customers(db: Session = Depends(get_db_with_rls)):
    # RLS context automatically set
    customers = db.query(Customer).all()
    return customers

# Option 2: Need both user object and RLS protection
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user_with_rls),
    db: Session = Depends(get_db)
):
    # RLS context already set by dependency
    return current_user
```

---

### 4. Dashboard API Fixes

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/routers/dashboard.py`

**What it does:**
- Fixed SQL queries to use correct column names
- Changed `status = 'active'` to `is_active = true AND expires_at > NOW()`
- Improved session counting logic

**Before:**
```sql
SELECT COUNT(*) FROM user_sessions WHERE status = 'active'
```

**After:**
```sql
SELECT COUNT(*) FROM user_sessions WHERE is_active = true AND expires_at > NOW()
```

---

## Security Benefits

### 1. Defense-in-Depth
- Even if application-layer security has bugs, database-layer RLS prevents unauthorized access
- Multiple security layers: JWT authentication → Application permissions → Database RLS

### 2. Automatic Data Filtering
- No need to manually add WHERE clauses for user/tenant filtering
- Database automatically applies correct filters based on session context
- Reduces risk of developer errors leading to data leaks

### 3. Multi-Tenancy Support
- Built-in support for tenant_id, branch_id, warehouse_id
- Prevents data leakage between tenants
- Scalable for future growth

### 4. Audit Trail Ready
- All RLS policy evaluations are logged by PostgreSQL
- Session variables provide clear audit trail
- Easy to debug access control issues

### 5. Performance Optimized
- Proper indexes created for RLS policy columns
- Efficient query execution even with RLS enabled
- Minimal performance overhead

---

## Migration Status

### ✅ Completed
1. RLS policies created and applied to database
2. Session variable bridge (rls_context.py) implemented
3. RLS-aware FastAPI dependencies created
4. Dashboard API schema issues fixed
5. Performance indexes created

### 📝 Next Steps (Recommended)
1. **Gradual Rollout**: Start using `get_db_with_rls()` in new endpoints
2. **Migrate Existing Endpoints**: Replace `get_db()` with `get_db_with_rls()` in security-critical endpoints
3. **Testing**: Test RLS policies with different user roles
4. **Monitoring**: Monitor query performance after RLS enablement
5. **Audit**: Regularly review active policies using `list_active_policies()`

---

## Testing RLS Policies

### Manual Testing

**Option 1: Using PostgreSQL Function**
```sql
-- Test as user ID 123
SELECT test_rls_as_user(
    123,
    'SELECT * FROM customers'
);
```

**Option 2: Using Python**
```python
from app.db.rls_context import set_rls_context
from app.db.database import SessionLocal

with SessionLocal() as db:
    # Test as sales rep (user_id=5)
    set_rls_context(db, user_id=5, role_name='salesperson')

    # Should only return customers assigned to user 5
    customers = db.query(Customer).all()
    print(f"Sales rep sees {len(customers)} customers")

    # Test as manager (user_id=2)
    set_rls_context(db, user_id=2, role_name='manager')

    # Should return customers from entire team
    customers = db.query(Customer).all()
    print(f"Manager sees {len(customers)} customers")
```

### Verification Queries

**Check which tables have RLS enabled:**
```sql
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
```

**List all active policies:**
```sql
SELECT tablename, policyname, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

**Check current session variables:**
```sql
SELECT current_setting('app.current_user_id', true) AS user_id,
       current_setting('app.current_user_role', true) AS role,
       current_setting('app.current_tenant_id', true) AS tenant_id;
```

---

## Performance Considerations

### Indexes Created
- `idx_customers_salesperson_id_active` - For customer ownership lookups
- `idx_sales_orders_created_by` - For order creator lookups
- `idx_sales_orders_customer_id` - For customer relationship lookups
- `idx_cash_transactions_created_by` - For transaction creator lookups
- `idx_expenses_user_id_status` - For expense ownership and status filtering
- `idx_employees_manager_id` - For manager hierarchy lookups

### Query Performance Tips
1. RLS policies add WHERE clauses - proper indexes are critical
2. All indexes have been created for RLS policy columns
3. Monitor slow query log after RLS enablement
4. Use `EXPLAIN ANALYZE` to verify index usage

---

## Security Audit Checklist

- [x] RLS enabled on all sensitive tables
- [x] FORCE ROW LEVEL SECURITY applied (affects table owners too)
- [x] Session variable bridge implemented
- [x] FastAPI dependencies created for automatic RLS context
- [x] Performance indexes created
- [x] Documentation written
- [ ] All endpoints migrated to use `get_db_with_rls()`
- [ ] Integration tests written for RLS policies
- [ ] Load testing performed
- [ ] Security audit conducted

---

## Troubleshooting

### Issue: RLS Blocking All Access

**Symptom**: No rows returned from queries

**Solution**: Verify session variables are set correctly
```sql
SELECT current_setting('app.current_user_id', true);
```

If NULL, ensure `set_rls_context()` is being called after authentication.

### Issue: Admin Can't See All Data

**Symptom**: Admin users seeing filtered results

**Solution**: Check if admin role has bypass policies:
```sql
SELECT * FROM pg_policies WHERE tablename = 'users' AND roles = '{postgres}';
```

Admins should use superuser account or have explicit ALL access policies.

### Issue: Performance Degradation

**Symptom**: Queries slower after RLS enablement

**Solution**: Verify indexes are being used:
```sql
EXPLAIN ANALYZE
SELECT * FROM customers WHERE salesperson_id = 5;
```

Look for "Index Scan" in query plan. If seeing "Seq Scan", index may not be created properly.

---

## References

- PostgreSQL RLS Documentation: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- SQLAlchemy Session Management: https://docs.sqlalchemy.org/en/20/orm/session_basics.html

---

## Contact & Support

For questions or issues with these security improvements, contact the development team or refer to the TSH ERP documentation.

**Generated**: 2025-10-23
**Version**: 1.0
