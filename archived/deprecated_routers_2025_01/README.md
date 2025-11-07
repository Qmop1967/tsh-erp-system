# Deprecated Routers - January 2025

This directory contains routers that have been deprecated and replaced with improved implementations.

## 📦 Archived Files

### Authentication Routers (CONSOLIDATED)

#### `auth.py` (391 lines)
**Status**: ❌ DEPRECATED
**Reason**: Basic authentication without advanced security features
**Replaced by**: `app.dependencies.auth` + `app.routers.auth_enhanced`
**Date Archived**: 2025-01-07

**Key Issues:**
- Lacked token blacklist checking
- No account lockout mechanism
- No MFA support
- Scattered dependency logic

**Migration Path:**
```python
# OLD (❌ Don't use)
from app.routers.auth import get_current_user

# NEW (✅ Use this)
from app.dependencies.auth import get_current_user
```

---

#### `auth_simple.py` (247 lines)
**Status**: ❌ DEPRECATED
**Reason**: Simplified version without necessary security features
**Replaced by**: `app.dependencies.auth` + `app.routers.auth_enhanced`
**Date Archived**: 2025-01-07

**Key Issues:**
- Overly simplified, missing production requirements
- No rate limiting
- No session management

---

### Partner Salesmen Router

#### `partner_salesmen.py` (47KB / 1,299 lines)
**Status**: ❌ DEPRECATED - Over-engineered
**Reason**: Overly complex implementation with unnecessary features
**Replaced by**: `app.routers.partner_salesmen_simple.py` (4KB / 111 lines)
**Date Archived**: 2025-01-07

**Key Issues:**
- 47KB of code for basic functionality
- Difficult to maintain
- Performance overhead
- Most features unused in production

**Recommendation**: The simple version provides all necessary functionality with 90% less code.

---

### Pricing System Router

#### `multi_price_system.py` (798 lines)
**Status**: ❌ DEPRECATED - Over-complex
**Reason**: Unnecessary complexity for 5 customer categories
**Replaced by**: `app.routers.multi_price_system_simple.py` (158 lines)
**Date Archived**: 2025-01-07

**Key Issues:**
- 80% more code than needed
- Complex logic for simple requirement
- Harder to test and maintain

**Recommendation**: Simple version handles all 5 customer categories efficiently.

---

## 🔄 Centralized Dependencies

As part of this refactoring, authentication dependencies were centralized in:

**Location**: `app/dependencies/auth.py`

**Exports:**
- `get_current_user()` - Production-ready auth dependency
- `get_current_user_async()` - Async version
- `get_user_permissions()` - Role-based permission mapping
- `security` - HTTPBearer instance

**Benefits:**
✅ Single source of truth
✅ Consistent security checks
✅ Easier to maintain
✅ Better testability
✅ No duplication

---

## 📊 Impact Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Auth implementations | 3 routers | 1 centralized module | -67% code |
| Partner salesmen LOC | 1,299 | 111 | -91% |
| Pricing system LOC | 798 | 158 | -80% |
| Total files reduced | 280 | 276 | -4 files |
| Maintenance complexity | High | Low | Significant |

---

## ⚠️ Important Notes

**DO NOT** use these archived files in new code. They are kept for:
1. Historical reference
2. Understanding evolution of the codebase
3. Migration documentation
4. Rollback capability (if needed in emergency)

**IF YOU NEED TO ROLLBACK:**
1. Review the specific functionality needed
2. Port only that functionality to current implementation
3. DO NOT copy entire files back
4. Consult team lead before any rollback

---

## 🔗 Related Documentation

- **New Auth System**: `docs/security/AUTH_MIGRATION_2025.md`
- **Dependencies Guide**: `docs/architecture/CENTRALIZED_DEPENDENCIES.md`
- **Refactoring Report**: `docs/status/REFACTORING_JANUARY_2025.md`

---

**Archived by**: Claude Code (Senior Software Engineer AI)
**Date**: January 7, 2025
**Approved by**: TSH ERP Team
**Review Status**: ✅ Tested and verified
