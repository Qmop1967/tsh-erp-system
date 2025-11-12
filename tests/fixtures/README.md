# Test Data Fixtures & Factories

Comprehensive test data generation framework using `factory_boy` for TSH ERP Ecosystem.

## Overview

This package provides factory-based test data generation with two main components:
1. **Factories** - Define how to create test objects
2. **Seeders** - Populate database with realistic datasets

## Quick Start

### Install Dependencies

```bash
pip install factory-boy==3.3.0 Faker==30.8.2
```

### Basic Usage

```python
from tests.fixtures import UserFactory, ProductFactory, seed_minimal

# Create individual objects
user = UserFactory()
product = ProductFactory(name="Test Product", unit_price=100)

# Create with relations
order = SalesOrderFactory(customer=customer, items__size=5)

# Seed database
seed_minimal()  # Fast, for unit tests
seed_full()     # Comprehensive, for integration tests
```

## Available Factories

### Core Factories
- `RoleFactory` - User roles
- `BranchFactory` - Business branches
- `WarehouseFactory` - Warehouses
- `UserFactory` - System users

### Product Factories
- `CategoryFactory` - Product categories
- `ProductFactory` - Products with SKU, pricing
- `InventoryItemFactory` - Stock levels

### Customer Factories
- `CustomerFactory` - Customers with credit limits
- `SupplierFactory` - Suppliers with payment terms

### Transaction Factories
- `SalesOrderFactory` - Sales orders
- `SalesItemFactory` - Order line items
- `PurchaseOrderFactory` - Purchase orders
- `PurchaseItemFactory` - Purchase line items
- `InvoiceFactory` - Sales invoices

### POS Factories
- `POSSessionFactory` - POS sessions
- `POSTransactionFactory` - POS transactions

### HR Factories
- `DepartmentFactory` - Departments
- `PositionFactory` - Job positions
- `EmployeeFactory` - Employees

### Cash Flow Factories
- `CashBoxFactory` - Cash boxes
- `CashTransactionFactory` - Cash transactions

## Seeder Functions

### `seed_minimal()`
**Fast seeding for unit tests**

Creates:
- 3 roles
- 2 branches
- 4 warehouses
- 6 users
- 5 categories
- 20 products
- 10 customers
- 5 suppliers

**Usage:**
```python
from tests.fixtures import seed_minimal

summary = seed_minimal()
print(summary)  # {'roles': 3, 'branches': 2, ...}
```

### `seed_full()`
**Comprehensive seeding for integration tests**

Creates:
- 5 roles
- 5 branches
- 10 warehouses
- 20 users
- 10 categories
- 100 products
- 200 inventory items
- 50 customers
- 20 suppliers
- 100 sales orders
- 50 purchase orders
- 80 invoices
- 20 POS sessions
- 20 employees
- 30 cash transactions

**Usage:**
```python
from tests.fixtures import seed_full

summary = seed_full()
```

### `seed_test_database(dataset="full")`
**Main seeding function**

```python
from tests.fixtures import seed_test_database

# Seed full dataset
seed_test_database("full")

# Seed minimal dataset
seed_test_database("minimal")
```

## CLI Usage

Seed from command line:

```bash
# Seed full dataset
python tests/fixtures/seeders.py --dataset full

# Seed minimal dataset
python tests/fixtures/seeders.py --dataset minimal

# Recreate tables and seed
python tests/fixtures/seeders.py --dataset full --recreate
```

## Factory Customization

### Override Attributes

```python
# Override specific attributes
user = UserFactory(
    email="admin@tsh.sale",
    name="Admin User",
    is_active=True
)
```

### Batch Creation

```python
# Create multiple objects
users = UserFactory.create_batch(10)
products = ProductFactory.create_batch(50)
```

### Relations

```python
# Create with foreign keys
branch = BranchFactory()
warehouse = WarehouseFactory(branch_id=branch.id)

# Or use SubFactory
product = ProductFactory(category=CategoryFactory())
```

### Post-Generation Hooks

```python
# Create order with items
order = SalesOrderWithItemsFactory(items__size=10)
```

## Integration with pytest

### In conftest.py

```python
import pytest
from tests.fixtures import seed_minimal, seed_full

@pytest.fixture(scope="session")
def seeded_db():
    """Seed database once per test session"""
    summary = seed_minimal()
    yield summary
    # Cleanup if needed

@pytest.fixture(scope="function")
def fresh_db():
    """Fresh database for each test"""
    from app.db.database import Base, engine
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

### In Test Files

```python
def test_product_creation(seeded_db):
    """Test using seeded data"""
    from app.models import Product
    from app.db.database import SessionLocal

    db = SessionLocal()
    products = db.query(Product).all()
    assert len(products) >= 20  # seed_minimal creates 20 products


def test_custom_product():
    """Test with custom factory"""
    from tests.fixtures import ProductFactory

    product = ProductFactory(name="Custom Product", unit_price=500)
    assert product.name == "Custom Product"
    assert product.unit_price == 500
```

## Advanced Features

### Lazy Attributes

```python
class InvoiceFactory(BaseFactory):
    subtotal = fuzzy.FuzzyDecimal(1000, 50000, 2)
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.15'))
    total_amount = factory.LazyAttribute(
        lambda obj: obj.subtotal + obj.tax_amount - obj.discount_amount
    )
```

### Sequences

```python
class ProductFactory(BaseFactory):
    sku = factory.Sequence(lambda n: f"SKU{n:06d}")  # SKU000001, SKU000002, ...
```

### Iterators

```python
class CategoryFactory(BaseFactory):
    name = factory.Iterator([
        "Electronics", "Furniture", "Office Supplies", "Hardware"
    ])
```

### Fuzzy Data

```python
class ProductFactory(BaseFactory):
    unit_price = fuzzy.FuzzyDecimal(10.0, 1000.0, 2)  # Random decimal 10-1000
    quantity = fuzzy.FuzzyInteger(100, 1000)  # Random integer 100-1000
```

## Best Practices

### 1. Deterministic Tests
```python
# Use factory_boy's Faker provider with seed
import factory.random
factory.random.reseed_random(123)
```

### 2. Minimal Data in Tests
```python
# Only create what you need
def test_product():
    product = ProductFactory()  # Creates product + category
    assert product.sku.startswith("SKU")
```

### 3. Use Traits for Variations
```python
class UserFactory(BaseFactory):
    class Meta:
        model = User

    class Params:
        admin = factory.Trait(
            role=factory.SubFactory(RoleFactory, name="Admin")
        )
        inactive = factory.Trait(is_active=False)

# Usage
admin_user = UserFactory(admin=True)
inactive_user = UserFactory(inactive=True)
```

### 4. Cleanup After Tests
```python
@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
```

## Performance Tips

1. **Use `build()` instead of `create()`** for tests that don't need DB persistence
2. **Seed once per test session** instead of per test
3. **Use `seed_minimal()` for unit tests**, `seed_full()` only for integration tests
4. **Batch create** objects when possible: `UserFactory.create_batch(100)`
5. **Disable cascade deletes** during cleanup for faster teardown

## Troubleshooting

### IntegrityError: duplicate key value

**Problem:** Multiple factories creating same unique values

**Solution:** Use sequences
```python
email = factory.Sequence(lambda n: f"user{n}@example.com")
```

### Foreign Key Violations

**Problem:** Creating objects without required relations

**Solution:** Use SubFactory
```python
product_id = factory.SubFactory(ProductFactory)
```

### Slow Tests

**Problem:** Creating too much data

**Solution:** Use minimal dataset or build() instead of create()
```python
product = ProductFactory.build()  # No DB insertion
```

## Examples

See `tests/` directory for real-world examples:
- `tests/unit/` - Unit tests with minimal data
- `tests/integration/` - Integration tests with full dataset
- `tests/e2e/` - End-to-end tests with seeded database

## Contributing

When adding new models:

1. Create factory in `factories.py`
2. Add to `__init__.py` exports
3. Add seeding method to `DatabaseSeeder` class
4. Update this README

## Resources

- [factory_boy Documentation](https://factoryboy.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Maintained by:** TSH DevOps Team
