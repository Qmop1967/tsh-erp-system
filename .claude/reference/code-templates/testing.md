# Testing Templates

**Purpose:** Production-ready testing patterns for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/testing.md

---

## 🧪 Template 9.1: Integration Test for API Endpoint

**Reasoning Context:**
- Tests prevent regressions (ensure fixes stay fixed)
- Integration tests verify entire flow (database, business logic, API)
- Critical for TSH ERP (500+ clients depend on correct behavior)
- Tests document expected behavior (living documentation)

**When to Use:**
- New API endpoints
- Critical business logic (order creation, payment processing)
- Bug fixes (test first, then fix)
- Before refactoring

**Code Template:**

```python
# tests/test_products.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.product import Product
from app.models.user import User
from tests.utils import create_test_user, create_test_product

client = TestClient(app)

class TestProductEndpoints:
    """Integration tests for product endpoints."""

    def test_create_product_success(self, db: Session, auth_headers: dict):
        """Test successful product creation."""

        product_data = {
            "name": "Test Laptop",
            "name_ar": "لابتوب تجريبي",
            "description": "Test description",
            "description_ar": "وصف تجريبي",
            "sku": "TEST-LAPTOP-001",
            "category_id": 1,
            "unit_price": 1500.00,
            "cost_price": 1200.00,
            "stock_quantity": 10
        }

        response = client.post(
            "/api/products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["name_ar"] == product_data["name_ar"]
        assert data["sku"] == product_data["sku"]
        assert "id" in data

    def test_create_product_duplicate_sku(self, db: Session, auth_headers: dict):
        """Test creating product with duplicate SKU fails."""

        # Create first product
        existing = create_test_product(db, sku="DUP-SKU-001")

        # Try to create duplicate
        product_data = {
            "name": "Duplicate",
            "name_ar": "مكرر",
            "sku": "DUP-SKU-001",  # Same SKU
            "category_id": 1,
            "unit_price": 100.00,
            "cost_price": 80.00
        }

        response = client.post(
            "/api/products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_product_missing_arabic(self, db: Session, auth_headers: dict):
        """Test that Arabic fields are required."""

        product_data = {
            "name": "Test Product",
            # Missing name_ar
            "sku": "TEST-NO-ARABIC",
            "category_id": 1,
            "unit_price": 100.00,
            "cost_price": 80.00
        }

        response = client.post(
            "/api/products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error
        errors = response.json()["detail"]
        assert any(e["loc"] == ["body", "name_ar"] for e in errors)

    def test_list_products_pagination(self, db: Session):
        """Test product list pagination."""

        # Create 150 test products
        for i in range(150):
            create_test_product(db, sku=f"TEST-{i:03d}")

        # Request first page
        response = client.get("/api/products/?page=1&limit=100")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 100  # Max per page
        assert data["pagination"]["total_items"] == 150
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["has_next"] == True

        # Request second page
        response = client.get("/api/products/?page=2&limit=100")
        data = response.json()
        assert len(data["items"]) == 50  # Remaining items
        assert data["pagination"]["has_next"] == False

    def test_update_product(self, db: Session, auth_headers: dict):
        """Test product update."""

        product = create_test_product(db, sku="UPDATE-TEST")

        update_data = {
            "unit_price": 1600.00,
            "stock_quantity": 15
        }

        response = client.patch(
            f"/api/products/{product.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["unit_price"] == 1600.00
        assert data["stock_quantity"] == 15

    def test_delete_product_soft_delete(self, db: Session, auth_headers: dict):
        """Test soft delete preserves product."""

        product = create_test_product(db, sku="DELETE-TEST")

        response = client.delete(
            f"/api/products/{product.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify product still exists but is_active = False
        db.refresh(product)
        assert product.is_active == False

    def test_authorization_required(self, db: Session):
        """Test that authentication is required."""

        response = client.post("/api/products/", json={})

        assert response.status_code == 401
```

**Test Fixtures:**

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, Role
from app.utils.security import hash_password, create_access_token

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost/test_tsh_erp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    """Create test user."""
    role = Role(name="admin")
    db.add(role)
    db.commit()

    user = User(
        email="test@tsh.sale",
        name="Test User",
        password_hash=hash_password("testpass123"),
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}
```

**Test Utilities:**

```python
# tests/utils.py
from app.models.product import Product
from app.models.user import User

def create_test_product(db, **kwargs):
    """Helper to create test product."""
    defaults = {
        "name": "Test Product",
        "name_ar": "منتج تجريبي",
        "sku": f"TEST-{int(time.time())}",
        "category_id": 1,
        "unit_price": 100.00,
        "cost_price": 80.00,
        "stock_quantity": 10,
        "is_active": True
    }
    defaults.update(kwargs)

    product = Product(**defaults)
    db.add(product)
    db.commit()
    db.refresh(product)

    return product

def create_test_user(db, **kwargs):
    """Helper to create test user."""
    defaults = {
        "email": f"test{int(time.time())}@tsh.sale",
        "name": "Test User",
        "password_hash": hash_password("testpass123"),
        "role_id": 1
    }
    defaults.update(kwargs)

    user = User(**defaults)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
```

**Running Tests:**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_products.py

# Run specific test
pytest tests/test_products.py::TestProductEndpoints::test_create_product_success

# Run with coverage
pytest --cov=app --cov-report=html

# Run only integration tests
pytest -m integration

# Run with verbose output
pytest -v
```

**Related Patterns:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Authentication: @docs/reference/code-templates/authentication.md

---

## ✅ Testing Best Practices

```yaml
What to Test:
✅ All CRUD operations
✅ Authentication and authorization
✅ Validation (required fields, data types)
✅ Business logic rules
✅ Error handling
✅ Edge cases (empty lists, null values)
✅ Arabic field requirements

Test Structure:
✅ Arrange (setup data)
✅ Act (execute action)
✅ Assert (verify result)
✅ Clear test names (test_what_when_expected)
✅ One assertion per test (when possible)

Test Data:
✅ Use fixtures for reusable data
✅ Clean up after each test
✅ Use separate test database
✅ Mock external services (Zoho, etc.)
```

---

**Related Documentation:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Authentication: @docs/reference/code-templates/authentication.md
- Workflows: @docs/core/workflows.md
