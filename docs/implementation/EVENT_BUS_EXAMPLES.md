# Event Bus Usage Examples

**Date:** November 4, 2025
**Branch:** `feature/monolithic-unification`
**Status:** Event infrastructure complete, ready to use

---

## Overview

The Event Bus infrastructure is now part of the unified TSH ERP monolith. It provides:

- **Decoupled communication** between modules without direct API calls
- **Event persistence** for audit trail and debugging
- **Async/sync event handling** for flexibility
- **Easy registration** via decorators

---

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Module A  │         │   EventBus   │         │   Module B  │
│  (Publisher)│────────▶│  (Mediator)  │────────▶│ (Subscriber)│
└─────────────┘ publish └──────────────┘ dispatch└─────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │  EventStore  │
                        │  (Database)  │
                        └──────────────┘
```

---

## Basic Usage Example

### 1. Publishing Events

When something important happens in your code, publish an event:

```python
from app.events.event_bus import EventBus, Event

# Example: Product created
async def create_product(product_data: dict):
    # Create product in database
    product = Product(**product_data)
    db.add(product)
    db.commit()

    # Publish event
    event = Event(
        event_type="product.created",
        data={
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "price": float(product.unit_price)
        }
    )
    await EventBus.publish(event)

    return product
```

### 2. Subscribing to Events

Register handlers to react to events:

```python
from app.events.event_bus import EventBus, Event
from app.events.decorators import event_handler

@event_handler("product.created")
async def update_inventory_on_product_creation(event: Event):
    """
    When a product is created, initialize its inventory record
    """
    product_id = event.data.get("product_id")

    # Create inventory item
    inventory_item = InventoryItem(
        product_id=product_id,
        quantity_on_hand=0,
        warehouse_id=1  # Default warehouse
    )
    db.add(inventory_item)
    db.commit()

    logger.info(f"Inventory initialized for product {product_id}")


@event_handler("product.created")
async def sync_to_zoho_on_product_creation(event: Event):
    """
    When a product is created, sync it to Zoho Books
    """
    product_data = event.data

    # Call Zoho API
    zoho_service = ZohoService()
    result = await zoho_service.create_item(product_data)

    logger.info(f"Product synced to Zoho: {result}")
```

---

## Real-World Use Cases

### Use Case 1: Order Processing Flow

```python
# 1. Customer creates order
@router.post("/orders")
async def create_order(order_data: OrderCreate):
    # Create order
    order = SalesOrder(**order_data.dict())
    db.add(order)
    db.commit()

    # Publish event
    await EventBus.publish(Event(
        event_type="order.created",
        data={
            "order_id": order.id,
            "customer_id": order.customer_id,
            "total": float(order.total_amount),
            "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in order.items]
        }
    ))

    return order


# 2. Inventory module listens and reduces stock
@event_handler("order.created")
async def reduce_inventory_on_order(event: Event):
    order_id = event.data["order_id"]
    items = event.data["items"]

    for item in items:
        inventory = db.query(InventoryItem).filter(
            InventoryItem.product_id == item["product_id"]
        ).first()

        inventory.quantity_on_hand -= item["quantity"]
        db.commit()

    logger.info(f"Inventory reduced for order {order_id}")


# 3. Accounting module listens and creates invoice
@event_handler("order.created")
async def create_invoice_on_order(event: Event):
    order_id = event.data["order_id"]
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()

    invoice = SalesInvoice(
        order_id=order.id,
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        status="pending"
    )
    db.add(invoice)
    db.commit()

    logger.info(f"Invoice created for order {order_id}")


# 4. Notification module listens and sends email
@event_handler("order.created")
async def send_order_confirmation_email(event: Event):
    order_id = event.data["order_id"]
    customer_id = event.data["customer_id"]

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    # Send email
    email_service = EmailService()
    await email_service.send_email(
        to=customer.email,
        subject="Order Confirmation",
        body=f"Your order #{order_id} has been confirmed!"
    )

    logger.info(f"Confirmation email sent for order {order_id}")
```

**Result:** One `order.created` event triggers 4 different actions across 4 modules, all decoupled!

---

### Use Case 2: Price Change Propagation

```python
# 1. Admin changes product price
@router.put("/products/{product_id}/price")
async def update_product_price(product_id: int, new_price: float):
    product = db.query(Product).filter(Product.id == product_id).first()
    old_price = product.unit_price

    product.unit_price = new_price
    db.commit()

    # Publish event
    await EventBus.publish(Event(
        event_type="product.price_changed",
        data={
            "product_id": product.id,
            "sku": product.sku,
            "old_price": float(old_price),
            "new_price": float(new_price),
            "changed_by": "admin"
        }
    ))

    return product


# 2. Pricing module records history
@event_handler("product.price_changed")
async def record_price_history(event: Event):
    price_history = PriceHistory(
        product_id=event.data["product_id"],
        old_price=event.data["old_price"],
        new_price=event.data["new_price"],
        changed_at=datetime.utcnow(),
        changed_by=event.data["changed_by"]
    )
    db.add(price_history)
    db.commit()


# 3. Cache module invalidates cached prices
@event_handler("product.price_changed")
async def invalidate_price_cache(event: Event):
    product_id = event.data["product_id"]
    cache_service = CacheService()
    await cache_service.delete(f"product_price_{product_id}")
    logger.info(f"Price cache invalidated for product {product_id}")


# 4. Notification module alerts salespeople
@event_handler("product.price_changed")
async def notify_salespeople_of_price_change(event: Event):
    product_id = event.data["product_id"]

    # Get all salespeople
    salespeople = db.query(User).filter(User.role_id == SALESPERSON_ROLE_ID).all()

    # Send notifications
    notification_service = NotificationService()
    for salesperson in salespeople:
        await notification_service.send_notification(
            user_id=salesperson.id,
            title="Product Price Changed",
            message=f"Product {event.data['sku']} price changed: ${event.data['old_price']} → ${event.data['new_price']}"
        )
```

---

### Use Case 3: Customer Registration Flow

```python
# 1. Customer registers
@router.post("/customers/register")
async def register_customer(customer_data: CustomerCreate):
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()

    await EventBus.publish(Event(
        event_type="customer.registered",
        data={
            "customer_id": customer.id,
            "email": customer.email,
            "name": customer.name
        }
    ))

    return customer


# 2. CRM module creates customer profile
@event_handler("customer.registered")
async def create_customer_profile(event: Event):
    customer_id = event.data["customer_id"]

    # Create CRM profile with default settings
    crm_profile = CustomerProfile(
        customer_id=customer_id,
        loyalty_points=0,
        tier="bronze",
        preferences={}
    )
    db.add(crm_profile)
    db.commit()


# 3. Marketing module adds to mailing list
@event_handler("customer.registered")
async def add_to_mailing_list(event: Event):
    email = event.data["email"]
    name = event.data["name"]

    marketing_service = MarketingService()
    await marketing_service.add_to_list(email, name, list_name="new_customers")


# 4. Email module sends welcome email
@event_handler("customer.registered")
async def send_welcome_email(event: Event):
    customer_id = event.data["customer_id"]
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    email_service = EmailService()
    await email_service.send_template_email(
        to=customer.email,
        template="welcome",
        data={"name": customer.name}
    )
```

---

## Event Types Registry

Here are suggested event types you can use:

### Product Events
- `product.created`
- `product.updated`
- `product.deleted`
- `product.price_changed`
- `product.stock_low`
- `product.out_of_stock`

### Order Events
- `order.created`
- `order.confirmed`
- `order.shipped`
- `order.delivered`
- `order.cancelled`
- `order.refunded`

### Customer Events
- `customer.registered`
- `customer.updated`
- `customer.deleted`
- `customer.tier_upgraded`
- `customer.loyalty_points_earned`

### Inventory Events
- `inventory.stock_adjusted`
- `inventory.transfer_completed`
- `inventory.reorder_triggered`

### Payment Events
- `payment.received`
- `payment.failed`
- `payment.refunded`

### Zoho Sync Events
- `zoho.item.synced`
- `zoho.customer.synced`
- `zoho.invoice.synced`

---

## Testing Events

### Manual Testing

```python
# Test event publishing
async def test_event_publishing():
    event = Event(
        event_type="test.event",
        data={"message": "Hello from test!"}
    )

    result = await EventBus.publish(event)
    print(f"Event published: {result}")


# Test event handling
@event_handler("test.event")
async def handle_test_event(event: Event):
    print(f"Received test event: {event.data}")
```

### Automated Testing

```python
import pytest
from app.events.event_bus import EventBus, Event

@pytest.mark.asyncio
async def test_product_created_event():
    # Setup
    event_received = False

    @event_handler("product.created")
    async def test_handler(event: Event):
        nonlocal event_received
        event_received = True

    # Execute
    await EventBus.publish(Event(
        event_type="product.created",
        data={"product_id": 123}
    ))

    # Verify
    assert event_received == True
```

---

## Performance Tips

### 1. Async Handlers
Always use `async` handlers for I/O operations:

```python
@event_handler("order.created")
async def process_order(event: Event):
    # Good: async I/O
    result = await external_api.call()

    # Bad: blocking I/O (will slow down event bus)
    # result = requests.post("...")
```

### 2. Fire-and-Forget
Don't wait for handlers if you don't need to:

```python
# Fire-and-forget (recommended for most cases)
await EventBus.publish(event)

# Wait for all handlers (only if you need to)
await EventBus.publish(event, wait_for_handlers=True)
```

### 3. Error Handling
Handlers should handle their own errors:

```python
@event_handler("order.created")
async def risky_operation(event: Event):
    try:
        # Risky operation
        result = await might_fail()
    except Exception as e:
        logger.error(f"Failed to process order event: {e}")
        # Don't re-raise - let other handlers continue
```

---

## Next Steps

1. **Start using events** in your code instead of direct module calls
2. **Monitor EventStore** table to see event flow
3. **Add custom event types** for your specific use cases
4. **Create event documentation** for your team

---

**Generated with** 🤖 [Claude Code](https://claude.com/claude-code)
