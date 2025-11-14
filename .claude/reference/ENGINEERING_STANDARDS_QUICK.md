# Engineering Standards Quick Reference

**Full Standards:** @docs/core/engineering-standards.md

---

## ⚡ Quick Compliance Checklist

**Before ANY code deployment:**

```yaml
Authorization (ALL 3 LAYERS):
  □ RBAC - Role check implemented
  □ ABAC - Attribute-based policy check
  □ RLS - PostgreSQL row-level security

API Standards:
  □ Follows /api/v1/{module}/{resource}/{action}
  □ Uses standardized response structure
  □ Pydantic DTOs for all inputs
  □ JWT authentication required

Database:
  □ snake_case naming convention
  □ Indexes on foreign keys
  □ RLS policies enabled
  □ Soft delete (is_deleted)
  □ Audit columns (created_at, updated_at)

Code Quality:
  □ Type hints (Python) / TypeScript
  □ Passes linting (PEP8/ESLint)
  □ Unit tests (70%+ backend, 60%+ frontend)
  □ Integration tests for critical flows
  □ Docstrings/comments included

Security:
  □ No secrets in code
  □ Input validation (Pydantic)
  □ All 3 authorization layers
  □ No SQL injection vulnerabilities
  □ No XSS vulnerabilities

Testing:
  □ Authorization tests (RBAC, ABAC, RLS)
  □ Unit tests passing
  □ Integration tests passing
  □ Load tests (if heavy operation)

Documentation:
  □ README updated
  □ API docs updated
  □ CHANGELOG updated
  □ Migration notes (if breaking)
```

---

## 🚨 Common Violations to Avoid

```yaml
❌ Missing ANY authorization layer (need all 3)
❌ Direct Zoho API access (use TDS Core only)
❌ No Pydantic DTOs (raw dict inputs)
❌ Missing Arabic fields (name_ar, description_ar)
❌ No pagination (lists > 100 records)
❌ N+1 queries (use joinedload)
❌ No indexes on foreign keys
❌ Secrets in code/Docker/git
❌ No tests for critical features
❌ Skipping staging verification
```

---

## 📋 Response Structure (Standard)

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "message_ar": "تمت العملية بنجاح",
  "data": { ... },
  "error_code": null,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

## 🔐 Authorization Pattern (Required)

```python
# ✅ CORRECT: All 3 layers
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role(["admin", "sales"])),      # RBAC
    abac: User = Depends(check_abac_permission("orders.read")), # ABAC
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS applied
    return await service.get_orders()
```

---

**Load Full Standards:** @docs/core/engineering-standards.md
