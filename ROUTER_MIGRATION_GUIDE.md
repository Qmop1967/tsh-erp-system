# Router Migration Guide

## Overview

This guide documents the migration from manual router registration in `main.py` to the automated Router Registry system in `app/core/router_registry.py`.

**Current Status:** 63+ routers manually registered in main.py (lines 174-289)
**Target:** Automated registration through Router Registry
**Foundation:** Router Registry module created at `app/core/router_registry.py`

## Why Migrate?

### Current Problems
1. **63+ manual import statements** in main.py (lines 174-219)
2. **63+ manual registration calls** (lines 229-289)
3. **Duplicate routers** (auth_router, auth_simple_router)
4. **No consistent prefix/tag naming**
5. **Hard to maintain** - changes require editing main.py
6. **No dependency injection** for router-level dependencies

### Benefits After Migration
1. **Single line** in main.py: `register_all_routers(app)`
2. **Centralized** router configuration
3. **Priority-based** registration order
4. **Easy to disable** routers via `enabled=False`
5. **Automatic discovery** of routers
6. **Consistent naming** and tagging

## Migration Strategy

### Phase 1: Create Foundation ✅ COMPLETED
- [x] Create `app/core/router_registry.py`
- [x] Implement RouterRegistry class
- [x] Implement register_all_routers() function
- [x] Document usage

### Phase 2: Incremental Migration (Week 2)
Migrate routers in groups, testing after each group:

#### Group 1: Core Authentication (Priority 50)
```python
# Remove from main.py:
app.include_router(auth_router, prefix="/api", tags=["authentication"])
app.include_router(auth_simple_router, tags=["Simple Authentication"])

# Add to router_registry.py:
registry.register(auth_router, prefix="/api/auth", tags=["Authentication"], priority=50)
# Note: Remove auth_simple_router (duplicate - consolidate later)
```

#### Group 2: Core Business Entities (Priority 100)
```python
# Branches
registry.register(branches_router, prefix="/api/branches", tags=["Branches"], priority=100)

# Products
registry.register(products_router, prefix="/api/products", tags=["Products"], priority=100)

# Customers
registry.register(customers_router, prefix="/api/customers", tags=["Customers"], priority=100)

# Users
registry.register(users_router, prefix="/api/users", tags=["Users"], priority=100)

# Warehouses
registry.register(warehouses_router, prefix="/api/warehouses", tags=["Warehouses"], priority=100)

# Items
registry.register(items_router, prefix="/api/items", tags=["Items"], priority=100)

# Vendors
registry.register(vendors_router, prefix="/api/vendors", tags=["Vendors"], priority=100)
```

#### Group 3: Business Operations (Priority 150)
```python
# Sales & Invoices
registry.register(sales_router, prefix="/api/sales", tags=["Sales"], priority=150)
registry.register(invoices_router, prefix="/api/invoices", tags=["Invoices"], priority=150)

# Inventory
registry.register(inventory_router, prefix="/api/inventory", tags=["Inventory"], priority=150)

# Accounting & Cash Flow
registry.register(accounting_router, prefix="/api/accounting", tags=["Accounting"], priority=150)
registry.register(cashflow_router, prefix="/api/cashflow", tags=["Cash Flow"], priority=150)

# Expenses
registry.register(expenses_router, prefix="/api/expenses", tags=["Expenses"], priority=150)
```

#### Group 4: POS & Store Operations (Priority 160)
```python
registry.register(pos_router, prefix="/api/pos", tags=["Point of Sale"], priority=160)
registry.register(pos_enhanced_router, prefix="/api/pos/enhanced", tags=["POS Enhanced"], priority=160)
registry.register(returns_exchange_router, prefix="/api/returns", tags=["Returns & Exchange"], priority=160)
```

#### Group 5: Pricing & Partner Systems (Priority 170)
```python
registry.register(multi_price_system_router, prefix="/api/pricing", tags=["Multi-Price System"], priority=170)
registry.register(partner_salesmen_router, prefix="/api/partners", tags=["Partner Salesmen"], priority=170)
registry.register(money_transfer_router, prefix="/api/money-transfers", tags=["Money Transfers"], priority=170)
registry.register(gps_money_transfer_router, prefix="/api/gps/money-transfers", tags=["GPS Money Transfer"], priority=170)
```

#### Group 6: Admin & Security (Priority 180)
```python
registry.register(admin_router, prefix="/api/admin", tags=["Admin Dashboard"], priority=180)
registry.register(permissions_router, prefix="/api/permissions", tags=["Permissions"], priority=180)
registry.register(data_scope_router, prefix="/api/data-scope", tags=["Data Scope"], priority=180)
registry.register(trusted_devices_router, prefix="/api/trusted-devices", tags=["Trusted Devices"], priority=180)
registry.register(enhanced_settings_router, prefix="/api/security", tags=["Enhanced Security"], priority=180)
registry.register(settings_router, prefix="/api/settings", tags=["Settings"], priority=180)
```

#### Group 7: Integrations (Priority 190)
```python
# AI & ChatGPT
registry.register(ai_assistant_router, prefix="/api/ai", tags=["AI Assistant"], priority=190)
registry.register(chatgpt_router, prefix="/api/chatgpt", tags=["ChatGPT Integration"], priority=190)

# WhatsApp
registry.register(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp Integration"], priority=190)

# GPS Tracking
registry.register(gps_router, prefix="/api/gps/tracking", tags=["GPS Tracking"], priority=190)
```

#### Group 8: Zoho Integration (Priority 200)
```python
registry.register(zoho_webhooks_router, prefix="/api/zoho/webhooks", tags=["Zoho Webhooks"], priority=200)
registry.register(zoho_dashboard_router, prefix="/api/zoho/dashboard", tags=["Zoho Dashboard"], priority=200)
registry.register(zoho_admin_router, prefix="/api/zoho/admin", tags=["Zoho Admin"], priority=200)
registry.register(zoho_bulk_sync_router, prefix="/api/zoho/bulk-sync", tags=["Zoho Bulk Sync"], priority=200)
registry.register(zoho_proxy_router, prefix="/api/zoho/proxy", tags=["Zoho Proxy"], priority=200)
```

#### Group 9: Mobile & BFF (Priority 210)
```python
registry.register(mobile_bff_router, prefix="/api/mobile", tags=["Mobile BFF"], priority=210)
registry.register(consumer_api_router, prefix="/api/consumer", tags=["Consumer App"], priority=210)
```

#### Group 10: Clean Architecture V2 (Priority 220)
```python
registry.register(customers_v2_router, prefix="/api/v2/customers", tags=["Customers V2"], priority=220)
registry.register(products_v2_router, prefix="/api/v2/products", tags=["Products V2"], priority=220)
registry.register(orders_v2_router, prefix="/api/v2/orders", tags=["Orders V2"], priority=220)
registry.register(inventory_v2_router, prefix="/api/v2/inventory", tags=["Inventory V2"], priority=220)
```

#### Group 11: System Operations (Priority 230)
```python
registry.register(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"], priority=230)
registry.register(notifications_router, prefix="/api/notifications", tags=["Notifications"], priority=230)
registry.register(backup_restore_router, prefix="/api/backup", tags=["Backup & Restore"], priority=230)
registry.register(hr_router, prefix="/api/hr", tags=["HR Management"], priority=230)
registry.register(migration_router, prefix="/api/migration", tags=["Migration"], priority=230)
registry.register(models_router, prefix="/api/models", tags=["Models"], priority=230)
```

### Phase 3: Clean Up main.py (Week 2 End)

**Before (main.py lines 173-289):**
```python
# 116 lines of imports and registrations
from app.routers import branches_router, customers_router, ...
# ... 45 more import lines ...
app.include_router(auth_router, prefix="/api", tags=["authentication"])
# ... 60 more registration lines ...
```

**After (main.py):**
```python
# Single import and call
from app.core.router_registry import register_all_routers

# Later in the file, after CORS middleware:
register_all_routers(app)
```

**Lines saved:** 114 lines removed from main.py
**Maintainability:** All router configuration in one place

### Phase 4: Add Router-Level Dependencies (Week 3)

Example: Add authentication dependency to all routers that need it:

```python
from app.core.dependencies import get_current_user

# Protect admin routers
registry.register(
    admin_router,
    prefix="/api/admin",
    tags=["Admin Dashboard"],
    dependencies=[Depends(get_current_user)],  # Require authentication
    priority=180,
)

# Protect user data routers
registry.register(
    customers_router,
    prefix="/api/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_user)],
    priority=100,
)
```

### Phase 5: Add Feature Flags (Week 3)

Example: Make routers conditionally enabled:

```python
from app.core.config import settings

# Disable AI assistant in production if not ready
registry.register(
    ai_assistant_router,
    prefix="/api/ai",
    tags=["AI Assistant"],
    priority=190,
    enabled=settings.feature_ai_enabled,  # Add to settings
)

# Disable v2 routers until fully tested
registry.register(
    customers_v2_router,
    prefix="/api/v2/customers",
    tags=["Customers V2"],
    priority=220,
    enabled=settings.enable_v2_api,  # Feature flag
)
```

## Testing Strategy

### 1. Unit Tests
Create `app/tests/unit/test_router_registry.py`:

```python
import pytest
from fastapi import FastAPI, APIRouter
from app.core.router_registry import RouterRegistry


def test_router_registration():
    """Test basic router registration"""
    registry = RouterRegistry()
    router = APIRouter()

    @router.get("/test")
    def test_endpoint():
        return {"test": "ok"}

    registry.register(router, prefix="/api/test", tags=["test"])
    assert "/api/test" in registry.get_registered_routers()


def test_priority_ordering():
    """Test routers are registered in priority order"""
    registry = RouterRegistry()
    app = FastAPI()

    router1 = APIRouter()
    router2 = APIRouter()
    router3 = APIRouter()

    # Register in wrong order
    registry.register(router2, prefix="/second", priority=200)
    registry.register(router1, prefix="/first", priority=100)
    registry.register(router3, prefix="/third", priority=150)

    registry.register_all(app)

    routers = registry.get_registered_routers()
    # Should be sorted by priority
    assert routers == ["/first", "/third", "/second"]


def test_disabled_router():
    """Test disabled routers are not registered"""
    registry = RouterRegistry()
    app = FastAPI()

    router = APIRouter()
    registry.register(router, prefix="/disabled", enabled=False)

    registry.register_all(app)

    assert "/disabled" not in registry.get_registered_routers()
```

### 2. Integration Tests
After migrating each group, test that:
1. All endpoints still respond correctly
2. Authentication still works
3. No duplicate routes
4. OpenAPI docs still load

```bash
# Test after each group migration
pytest app/tests/integration/test_routers.py -v

# Check OpenAPI schema is valid
curl https://erp.tsh.sale/openapi.json | jq .

# Verify specific endpoints
curl https://erp.tsh.sale/api/customers
curl https://erp.tsh.sale/api/products
```

### 3. Manual Testing Checklist
After full migration:
- [ ] All 63 routers accessible
- [ ] Authentication works
- [ ] Admin panel loads
- [ ] Mobile BFF responds
- [ ] Zoho webhooks work
- [ ] OpenAPI docs complete
- [ ] No duplicate routes
- [ ] Health check passes

## Rollback Plan

If migration causes issues:

```bash
# On VPS
cd /home/deploy/TSH_ERP_Ecosystem
git log --oneline -5
git revert HEAD  # Revert router registry changes
systemctl restart tsh-erp
```

Keep old main.py in version control:
```bash
git show HEAD~1:app/main.py > app/main.py.backup
```

## Progress Tracking

### Week 1 ✅ COMPLETED
- [x] Create Router Registry foundation
- [x] Document migration strategy

### Week 2 (Upcoming)
- [ ] Migrate Group 1 (Auth) - 2 routers
- [ ] Migrate Group 2 (Core Entities) - 7 routers
- [ ] Migrate Group 3 (Business Ops) - 6 routers
- [ ] Test all migrated routers
- [ ] Deploy to VPS
- [ ] Verify no regressions

### Week 3 (Upcoming)
- [ ] Migrate Groups 4-6 (POS, Pricing, Admin) - 15 routers
- [ ] Migrate Groups 7-8 (Integrations, Zoho) - 9 routers
- [ ] Add router-level dependencies
- [ ] Add feature flags
- [ ] Clean up main.py
- [ ] Full testing suite

### Week 4 (Upcoming)
- [ ] Migrate Groups 9-11 (Mobile, V2, System) - 15 routers
- [ ] Final cleanup
- [ ] Performance testing
- [ ] Documentation update
- [ ] Deploy to production

## Expected Outcomes

### Code Quality Improvements
- **116 lines removed** from main.py
- **Single source of truth** for router configuration
- **Consistent naming** across all routers
- **Easy to maintain** and extend

### Developer Experience
- **New routers:** Just add to registry, not main.py
- **Disable router:** Change `enabled=False`
- **Reorder routers:** Change priority number
- **Add auth:** Add to dependencies list

### Production Benefits
- **Feature flags:** Enable/disable routers per environment
- **Better logging:** See which routers registered
- **Easier debugging:** Clear registration order
- **Safer deployments:** Isolated router changes

## Related Documents
- `BACKEND_SIMPLIFICATION_PLAN.md` - Overall simplification strategy
- `ARCHITECTURE.md` - Current architecture documentation
- `QUICK_START_SIMPLIFICATION.md` - Week 1 action items

## Notes for Future
- Consider automatic router discovery via decorators
- Add router health checks
- Implement router versioning strategy
- Add router-level rate limiting
- Consider router grouping for microservices split
