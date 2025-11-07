# TSH ERP - Modular Monolith Architecture with Event-Driven Communication
## Complete Restructuring Plan

**Created:** November 4, 2025
**Branch:** `feature/modular-monolith-refactor`
**Goal:** Transform monolithic ERP into well-organized modular monolith with event-driven communication

---

## 🎯 Vision: The Perfect Modular Monolith

### What is a Modular Monolith?
A **modular monolith** is a single application with:
- ✅ **One codebase** - All code in one repository
- ✅ **One deployment** - Single deployment unit
- ✅ **One database** - Shared database (with module boundaries)
- ✅ **Clear modules** - Well-defined boundaries between features
- ✅ **Loose coupling** - Modules communicate via events, not direct calls
- ✅ **High cohesion** - Related code stays together in modules

### Why Event-Driven Communication?
Instead of direct API calls between modules:
```python
# ❌ OLD: Direct coupling (tight coupling)
from app.services.inventory_service import InventoryService
inventory_service.update_stock(product_id, quantity)

# ✅ NEW: Event-driven (loose coupling)
from app.core.events import EventBus
event_bus.publish(ProductSoldEvent(product_id=123, quantity=5))
```

**Benefits:**
- 🔄 **Loose coupling** - Modules don't depend on each other
- 📈 **Scalability** - Easy to add new modules
- 🧪 **Testability** - Test modules in isolation
- 🔌 **Extensibility** - Add new features without modifying existing code
- 🚀 **Future-proof** - Can extract to microservices later if needed

---

## 📐 Proposed Module Structure

### Target Directory Structure:
```
TSH_ERP_Ecosystem/
├── app/
│   ├── core/                          # Core infrastructure (shared by all modules)
│   │   ├── __init__.py
│   │   ├── database.py                # Database connection & session
│   │   ├── config.py                  # Configuration management
│   │   ├── events/                    # Event-driven infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py          # Event bus implementation
│   │   │   ├── event_store.py        # Event persistence (optional)
│   │   │   ├── base_event.py         # Base event class
│   │   │   └── handlers.py           # Event handler decorators
│   │   ├── middleware/               # Shared middleware
│   │   └── exceptions.py             # Custom exceptions
│   │
│   ├── modules/                       # Business modules (bounded contexts)
│   │   │
│   │   ├── inventory/                 # Inventory Management Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py             # Inventory models
│   │   │   ├── schemas.py            # Pydantic schemas
│   │   │   ├── router.py             # API endpoints
│   │   │   ├── service.py            # Business logic
│   │   │   ├── repository.py         # Data access
│   │   │   ├── events.py             # Module events
│   │   │   └── handlers.py           # Event handlers
│   │   │
│   │   ├── sales/                     # Sales Management Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── accounting/                # Accounting Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── pos/                       # Point of Sale Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── hr/                        # Human Resources Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── zoho/                      # Zoho Integration Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py             # Zoho sync models
│   │   │   ├── schemas.py
│   │   │   ├── routers/
│   │   │   │   ├── webhooks.py
│   │   │   │   ├── dashboard.py
│   │   │   │   └── admin.py
│   │   │   ├── services/
│   │   │   │   ├── processor.py
│   │   │   │   ├── queue.py
│   │   │   │   ├── inbox.py
│   │   │   │   ├── alert.py
│   │   │   │   ├── monitoring.py
│   │   │   │   └── webhook_health.py
│   │   │   ├── events.py             # Zoho events
│   │   │   ├── handlers.py           # Zoho event handlers
│   │   │   └── worker.py             # Background worker
│   │   │
│   │   ├── consumer/                  # Consumer App (E-commerce) Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── cashflow/                  # Cash Flow Management Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── auth/                      # Authentication & Authorization Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── notifications/             # Notification Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── events.py
│   │   │   └── handlers.py
│   │   │
│   │   └── ... (other modules)
│   │
│   ├── main.py                        # Application entry point
│   └── __init__.py
│
├── tds_core/                          # (Will be archived after unification)
├── mobile/                            # Flutter apps
├── frontend/                          # React admin
├── tests/                             # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/                           # Database migrations
└── docs/                              # Documentation
```

---

## 🔄 Event-Driven Communication Pattern

### 1. Event Bus Implementation

```python
# app/core/events/base_event.py
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4, UUID
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    """Base class for all domain events"""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    module: str  # Source module
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
```

```python
# app/core/events/event_bus.py
from typing import Callable, Dict, List
import asyncio
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """In-process event bus for modular monolith"""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type"""
        if asyncio.iscoroutinefunction(handler):
            if event_type not in self._async_handlers:
                self._async_handlers[event_type] = []
            self._async_handlers[event_type].append(handler)
        else:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)

    async def publish(self, event: BaseEvent):
        """Publish an event to all subscribers"""
        event_type = event.event_type

        # Execute sync handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in sync handler for {event_type}: {e}")

        # Execute async handlers
        tasks = []
        for handler in self._async_handlers.get(event_type, []):
            tasks.append(handler(event))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in async handler for {event_type}: {result}")

# Global event bus instance
event_bus = EventBus()
```

```python
# app/core/events/handlers.py
from functools import wraps
from .event_bus import event_bus

def event_handler(event_type: str):
    """Decorator to register event handlers"""
    def decorator(func):
        event_bus.subscribe(event_type, func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper
    return decorator
```

### 2. Example: Sales Module with Events

```python
# app/modules/sales/events.py
from app.core.events.base_event import BaseEvent
from typing import Any, Dict

class SalesOrderCreatedEvent(BaseEvent):
    """Event fired when a sales order is created"""
    def __init__(self, order_id: int, customer_id: int, total: float, items: list, **kwargs):
        super().__init__(
            event_type="sales.order.created",
            module="sales",
            data={
                "order_id": order_id,
                "customer_id": customer_id,
                "total": total,
                "items": items
            },
            **kwargs
        )

class SalesOrderCompletedEvent(BaseEvent):
    """Event fired when a sales order is completed"""
    def __init__(self, order_id: int, **kwargs):
        super().__init__(
            event_type="sales.order.completed",
            module="sales",
            data={"order_id": order_id},
            **kwargs
        )
```

```python
# app/modules/sales/service.py
from app.core.events.event_bus import event_bus
from .events import SalesOrderCreatedEvent, SalesOrderCompletedEvent

class SalesService:
    async def create_order(self, order_data: dict):
        # 1. Create order in database
        order = await self.repository.create(order_data)

        # 2. Publish event (instead of calling other services directly)
        await event_bus.publish(
            SalesOrderCreatedEvent(
                order_id=order.id,
                customer_id=order.customer_id,
                total=order.total,
                items=[item.to_dict() for item in order.items]
            )
        )

        return order
```

### 3. Example: Inventory Module Reacts to Sales

```python
# app/modules/inventory/handlers.py
from app.core.events.handlers import event_handler
from app.core.events.base_event import BaseEvent
from .service import InventoryService
import logging

logger = logging.getLogger(__name__)

@event_handler("sales.order.created")
async def handle_sales_order_created(event: BaseEvent):
    """
    When a sale is made, automatically reduce inventory
    """
    logger.info(f"Inventory module received: {event.event_type}")

    order_id = event.data["order_id"]
    items = event.data["items"]

    inventory_service = InventoryService()

    for item in items:
        await inventory_service.reduce_stock(
            product_id=item["product_id"],
            quantity=item["quantity"],
            reference_type="sales_order",
            reference_id=order_id
        )

    logger.info(f"Inventory updated for order {order_id}")
```

### 4. Example: Accounting Module Reacts to Sales

```python
# app/modules/accounting/handlers.py
from app.core.events.handlers import event_handler
from app.core.events.base_event import BaseEvent
from .service import AccountingService
import logging

logger = logging.getLogger(__name__)

@event_handler("sales.order.completed")
async def handle_sales_order_completed(event: BaseEvent):
    """
    When a sale is completed, create accounting journal entry
    """
    logger.info(f"Accounting module received: {event.event_type}")

    order_id = event.data["order_id"]

    accounting_service = AccountingService()

    # Create journal entry for the sale
    await accounting_service.create_sales_journal_entry(order_id)

    logger.info(f"Journal entry created for order {order_id}")
```

### 5. Example: Notification Module Reacts to Sales

```python
# app/modules/notifications/handlers.py
from app.core.events.handlers import event_handler
from app.core.events.base_event import BaseEvent
from .service import NotificationService
import logging

logger = logging.getLogger(__name__)

@event_handler("sales.order.created")
async def handle_sales_order_created(event: BaseEvent):
    """
    Send notification when order is created
    """
    logger.info(f"Notification module received: {event.event_type}")

    customer_id = event.data["customer_id"]
    order_id = event.data["order_id"]

    notification_service = NotificationService()

    # Send email/SMS/push notification
    await notification_service.send_order_confirmation(
        customer_id=customer_id,
        order_id=order_id
    )

    logger.info(f"Notification sent for order {order_id}")
```

---

## 📊 Benefits of This Architecture

### 1. Loose Coupling
- Modules don't know about each other
- Can add/remove modules without breaking others
- Easy to test in isolation

### 2. Event Flow Example:
```
User creates order
    ↓
Sales Module: create_order()
    ↓ publishes SalesOrderCreatedEvent
    ├→ Inventory Module: reduce_stock()
    ├→ Accounting Module: create_journal_entry()
    ├→ Notification Module: send_confirmation()
    └→ Zoho Module: sync_to_zoho()
```

All happen automatically, asynchronously, without Sales module knowing!

### 3. Scalability
```
Current: 51 routers in one directory (hard to manage)
New: 10-15 modules, each self-contained (easy to manage)
```

### 4. Team Organization
```
Module = Team responsibility
- Sales team owns app/modules/sales/
- Inventory team owns app/modules/inventory/
- Each team can work independently
```

---

## 🗺️ Module Mapping (Current → New)

### Core Modules:

| Current Location | New Location | Module Name |
|-----------------|--------------|-------------|
| `app/routers/inventory.py` | `app/modules/inventory/router.py` | Inventory |
| `app/routers/sales.py` | `app/modules/sales/router.py` | Sales |
| `app/routers/accounting.py` | `app/modules/accounting/router.py` | Accounting |
| `app/routers/pos.py` | `app/modules/pos/router.py` | POS |
| `app/routers/hr.py` | `app/modules/hr/router.py` | HR |
| `app/routers/invoices.py` | `app/modules/invoicing/router.py` | Invoicing |
| `app/routers/products.py` | `app/modules/catalog/router.py` | Product Catalog |
| `app/routers/customers.py` | `app/modules/crm/router.py` | CRM |
| `app/routers/cashflow.py` | `app/modules/cashflow/router.py` | Cash Flow |
| `app/routers/expenses.py` | `app/modules/expenses/router.py` | Expenses |
| `app/routers/consumer_api.py` | `app/modules/consumer/router.py` | Consumer App |
| `app/routers/zoho_*.py` | `app/modules/zoho/routers/` | Zoho Integration |
| `app/routers/notifications.py` | `app/modules/notifications/router.py` | Notifications |
| `app/routers/auth_*.py` | `app/modules/auth/router.py` | Auth |
| `app/routers/whatsapp_*.py` | `app/modules/whatsapp/router.py` | WhatsApp |
| `app/routers/ai_assistant.py` | `app/modules/ai/router.py` | AI Assistant |

---

## 🚀 Implementation Phases

### Phase 1: Setup Infrastructure (Week 1)
1. Create `app/core/events/` infrastructure
2. Implement EventBus
3. Create BaseEvent class
4. Add event handler decorators
5. Write tests for event system

### Phase 2: Create First Module (Week 1-2)
1. Choose pilot module (Sales recommended)
2. Create `app/modules/sales/` structure
3. Move models, schemas, router, service
4. Define events
5. Test module works

### Phase 3: Migrate Remaining Modules (Week 2-4)
1. Create module structure for each domain
2. Move code to modules
3. Define inter-module events
4. Implement event handlers
5. Test each module

### Phase 4: Event-Driven Integration (Week 4-5)
1. Replace direct service calls with events
2. Implement event handlers in each module
3. Test event flow end-to-end
4. Add event logging/monitoring

### Phase 5: Testing & Optimization (Week 5-6)
1. Unit tests for each module
2. Integration tests for event flows
3. Performance testing
4. Documentation

### Phase 6: Deployment (Week 6)
1. Database migration (if needed)
2. Deploy to staging
3. Monitor event flows
4. Deploy to production

---

## 📝 Module Design Template

### Each module should have:

```
app/modules/[module_name]/
├── __init__.py              # Module initialization & exports
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas (request/response)
├── router.py                # FastAPI router (API endpoints)
├── service.py               # Business logic layer
├── repository.py            # Data access layer (optional)
├── events.py                # Module events definition
├── handlers.py              # Event handlers (react to other modules)
├── exceptions.py            # Module-specific exceptions (optional)
└── README.md                # Module documentation
```

### Module Rules:
1. ✅ **DO:** Publish events when state changes
2. ✅ **DO:** React to events from other modules
3. ✅ **DO:** Keep business logic in service.py
4. ❌ **DON'T:** Import from other modules (except core)
5. ❌ **DON'T:** Call other module's services directly
6. ❌ **DON'T:** Access other module's models directly

---

## 🎯 Event Naming Convention

```
[module].[entity].[action]

Examples:
- sales.order.created
- sales.order.updated
- sales.order.completed
- sales.order.cancelled
- inventory.stock.updated
- inventory.stock.low_threshold
- accounting.journal_entry.created
- zoho.product.synced
- zoho.customer.synced
- notifications.email.sent
- notifications.sms.sent
- auth.user.logged_in
- auth.user.logged_out
```

---

## 📚 Key Concepts

### 1. Bounded Context
Each module represents a **bounded context** (Domain-Driven Design concept):
- Sales has its own understanding of "Order"
- Inventory has its own understanding of "Stock"
- Accounting has its own understanding of "Transaction"

### 2. Event Sourcing (Optional Enhancement)
Later, you can add event store to keep history of all events:
```python
# app/core/events/event_store.py
class EventStore:
    async def save(self, event: BaseEvent):
        # Save to database for audit/replay
        pass

    async def get_events_for_entity(self, entity_id: str):
        # Get all events for an entity
        pass
```

### 3. CQRS (Optional Enhancement)
Separate read and write models:
```python
# Write model (commands)
async def create_order(command: CreateOrderCommand)

# Read model (queries)
async def get_order(query: GetOrderQuery)
```

---

## 🔍 Example Event Flow: Complete Sales Order

```
1. User creates sales order via API
   ↓
2. Sales Module
   - Validates order
   - Saves to database
   - Publishes: sales.order.created
   ↓
3. Inventory Module (listens to sales.order.created)
   - Reduces stock for each item
   - Publishes: inventory.stock.updated
   ↓
4. Accounting Module (listens to sales.order.created)
   - Creates journal entry
   - Publishes: accounting.journal_entry.created
   ↓
5. Notification Module (listens to sales.order.created)
   - Sends email to customer
   - Publishes: notifications.email.sent
   ↓
6. Zoho Module (listens to sales.order.created)
   - Syncs order to Zoho Books
   - Publishes: zoho.order.synced
   ↓
7. All modules updated independently!
```

---

## ✅ Success Criteria

### Architecture:
- ✅ All modules in `app/modules/` directory
- ✅ EventBus implemented and working
- ✅ No direct imports between modules
- ✅ All inter-module communication via events

### Code Quality:
- ✅ Each module has clear responsibility
- ✅ Tests for each module
- ✅ Tests for event flows
- ✅ Documentation for each module

### Performance:
- ✅ Event processing < 100ms
- ✅ No performance degradation vs current
- ✅ Able to handle 1000+ events/minute

### Developer Experience:
- ✅ Easy to add new modules
- ✅ Easy to find code (organized by domain)
- ✅ Clear event contracts
- ✅ Good documentation

---

## 🎉 Expected Outcomes

### Before (Current):
```
app/
├── routers/        (51 files - hard to manage)
├── services/       (30+ files - scattered)
├── models/         (40+ files - monolithic)
└── schemas/        (many files)
```

### After (Modular Monolith):
```
app/
├── core/           (shared infrastructure)
├── modules/
│   ├── sales/      (all sales code here)
│   ├── inventory/  (all inventory code here)
│   ├── accounting/ (all accounting code here)
│   ├── zoho/       (all zoho code here)
│   └── ... (10-15 well-organized modules)
```

### Benefits:
1. **Organization:** 10-15 modules vs 51+ scattered files
2. **Maintainability:** Each module is self-contained
3. **Scalability:** Easy to add new modules
4. **Team Work:** Each team owns a module
5. **Testing:** Test modules independently
6. **Future-proof:** Can extract to microservices if needed

---

## 📖 Next Steps

1. **Review this plan** with team
2. **Approve architecture** decisions
3. **Start with Phase 1** (Event infrastructure)
4. **Pilot with Sales module**
5. **Gradually migrate** other modules
6. **Celebrate success!** 🎉

---

**This is the perfect architecture for TSH ERP! 🚀**

Let's build ONE excellent, well-organized system!
