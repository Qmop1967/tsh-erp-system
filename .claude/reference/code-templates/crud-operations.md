# CRUD Operations Templates

**Purpose:** Production-ready CRUD patterns with Arabic support and pagination for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/crud-operations.md

---

## 📊 Template 2.1: Create Resource (with Arabic Fields)

**Reasoning Context:**
- Arabic is PRIMARY language for TSH ERP users
- Every user-facing resource needs name_ar, description_ar
- Input validation prevents bad data (Pydantic)
- Created_by tracking for audit trail
- Pagination must be considered from day one (scales to 2,218+ products)

**When to Use:**
- Creating products, clients, orders, categories
- Any user-facing resource
- Resources that need audit trail

**Code Template:**

```python
# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,  # 👈 Pydantic validation
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product.

    Requires authentication.
    Includes Arabic fields (name_ar, description_ar).
    Tracks who created the product (audit trail).
    """
    # Check if SKU already exists (business rule)
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU {product_data.sku} already exists"
        )

    # Create new product
    new_product = Product(
        **product_data.dict(),
        created_by_id=current_user.id  # 👈 Audit trail
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product
```

**Pydantic Schema:**

```python
# app/schemas/product.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    """Schema for creating a product."""

    # English fields
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    # Arabic fields (MANDATORY for TSH ERP)
    name_ar: str = Field(..., min_length=1, max_length=255)
    description_ar: Optional[str] = Field(None, max_length=1000)

    # Product-specific fields
    sku: str = Field(..., min_length=1, max_length=100)
    category_id: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    cost_price: float = Field(..., ge=0)
    stock_quantity: int = Field(default=0, ge=0)

    @validator('unit_price')
    def unit_price_must_be_greater_than_cost(cls, v, values):
        """Ensure profit margin exists."""
        if 'cost_price' in values and v < values['cost_price']:
            raise ValueError('Unit price must be greater than or equal to cost price')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Dell XPS 15",
                "name_ar": "لابتوب ديل اكس بي اس 15",
                "description": "High-performance laptop",
                "description_ar": "لابتوب عالي الأداء",
                "sku": "LAPTOP-DELL-XPS15",
                "category_id": 5,
                "unit_price": 1500.00,
                "cost_price": 1200.00,
                "stock_quantity": 10
            }
        }

class ProductResponse(BaseModel):
    """Schema for product response."""
    id: int
    name: str
    name_ar: str
    description: Optional[str]
    description_ar: Optional[str]
    sku: str
    category_id: int
    unit_price: float
    cost_price: float
    stock_quantity: int
    is_active: bool
    created_at: datetime
    created_by_id: int

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode = True in v1)
```

**Database Model:**

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Bilingual fields
    name = Column(String(255), nullable=False, index=True)
    name_ar = Column(String(255), nullable=False, index=True)  # 👈 Arabic support
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # 👈 Arabic support

    # Product data
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    created_by = relationship("User", back_populates="created_products")
```

**Customization Points:**
- Replace `Product` with your model
- Adjust validation rules in Pydantic schema
- Add business-specific fields
- Modify error messages

**Related Patterns:**
- Template 2.2: List Resources with Pagination
- Template 2.3: Update Resource
- Arabic Bilingual Mixin: @docs/reference/code-templates/arabic-bilingual.md

---

## 📊 Template 2.2: List Resources with Pagination

**Reasoning Context:**
- TSH ERP has 2,218+ products, 500+ clients, 30+ daily orders
- Returning all records without pagination causes:
  - Slow API response (> 5 seconds)
  - High memory usage
  - Poor mobile app performance
  - Timeout errors
- Max 100 items per page is industry standard and proven at TSH scale
- Pagination metadata helps frontend build navigation UI

**When to Use:**
- ANY list endpoint that could return > 100 records
- Product lists, client lists, order history
- Search results
- Report data

**Code Template:**

```python
# app/routers/products.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(100, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search in name/name_ar/sku"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    List products with pagination, search, and filters.

    Returns paginated results with metadata.
    Max 100 items per page to ensure performance.
    Searches in English and Arabic names.
    """
    # Base query
    query = db.query(Product).filter(Product.is_active == is_active)

    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) |
            (Product.name_ar.ilike(search_pattern)) |
            (Product.sku.ilike(search_pattern))
        )

    # Get total count (before pagination)
    total_count = query.count()

    # Calculate pagination
    offset = (page - 1) * limit
    total_pages = (total_count + limit - 1) // limit  # Ceiling division

    # Apply pagination
    products = query.offset(offset).limit(limit).all()

    return {
        "items": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
```

**Pagination Schema:**

```python
# app/schemas/pagination.py
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    pagination: PaginationMetadata
```

**Customization Points:**
- Adjust max `limit` (default 100, can lower for large objects)
- Add more filters (price range, stock status, etc.)
- Add sorting options
- Customize search fields

**Performance Notes:**
- Query count is executed before pagination (necessary for total_pages)
- Consider adding indexes on filtered/searched columns
- For very large tables (> 100K rows), consider cursor-based pagination

**Related Patterns:**
- Template 2.1: Create Resource
- Database optimization: @docs/reference/code-templates/database-optimization.md
- Mobile pagination: @docs/reference/code-templates/pagination.md

---

## 📊 Template 2.3: Update Resource (Partial Update)

**Reasoning Context:**
- PATCH allows updating only specific fields (not entire resource)
- Prevents accidental data loss from missing fields
- Allows frontend to send only changed fields
- Audit trail tracks who made changes

**When to Use:**
- Updating product details
- Updating client information
- Editing orders (before completion)
- Any resource modification

**Code Template:**

```python
# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductUpdate, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,  # 👈 All fields optional
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a product (partial update).

    Only provided fields are updated.
    Requires authentication.
    Tracks who updated the product.
    """
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Update only provided fields
    update_data = product_data.dict(exclude_unset=True)  # 👈 Only sent fields

    for field, value in update_data.items():
        setattr(product, field, value)

    # Track who updated
    product.updated_by_id = current_user.id

    db.commit()
    db.refresh(product)

    return product
```

**Update Schema:**

```python
# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductUpdate(BaseModel):
    """Schema for updating a product. All fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    description_ar: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "unit_price": 1600.00,  # Only updating price
                "stock_quantity": 15     # and quantity
            }
        }
```

**Related Patterns:**
- Template 2.1: Create Resource
- Template 2.4: Delete Resource

---

## 📊 Template 2.4: Delete Resource (Soft Delete)

**Reasoning Context:**
- Hard deletes are dangerous (data loss, broken foreign keys)
- Soft delete preserves data integrity and audit trail
- Can be "un-deleted" if mistake made
- Historical reports still work (orders reference deleted products)
- Required for compliance (some industries forbid data deletion)

**When to Use:**
- Deleting products (keep for order history)
- Deactivating clients (keep for financial records)
- Archiving orders (keep for audits)
- Any resource that might be referenced

**Code Template:**

```python
# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, require_role, get_db
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/api/products", tags=["products"])

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(["admin", "manager"])),  # 👈 RBAC
    db: Session = Depends(get_db)
):
    """
    Delete a product (soft delete).

    Sets is_active = False instead of actually deleting.
    Preserves product for order history.
    Only admins and managers can delete products.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Soft delete (set is_active = False)
    product.is_active = False
    product.deleted_at = func.now()  # Optional: track when deleted
    product.deleted_by_id = current_user.id  # Optional: track who deleted

    db.commit()

    return  # 204 No Content (no body returned)
```

**Database Model Update:**

```python
# app/models/product.py
# Add these columns for complete soft delete tracking:

deleted_at = Column(DateTime(timezone=True), nullable=True)
deleted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
```

**Un-Delete Endpoint (Restore):**

```python
@router.post("/{product_id}/restore", response_model=ProductResponse)
async def restore_product(
    product_id: int,
    current_user: User = Depends(require_role(["admin"])),  # Admin only
    db: Session = Depends(get_db)
):
    """Restore a soft-deleted product."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = True
    product.deleted_at = None
    product.deleted_by_id = None

    db.commit()
    db.refresh(product)

    return product
```

**Related Patterns:**
- Template 2.2: List Resources (filter by is_active)
- Authentication: @docs/reference/code-templates/authentication.md

---

## 🧪 Testing CRUD Operations

```python
# tests/test_products.py
import pytest
from fastapi.testclient import TestClient

def test_create_product_success(client: TestClient, auth_headers):
    """Test successful product creation."""
    product_data = {
        "name": "Test Laptop",
        "name_ar": "لابتوب تجريبي",
        "sku": "TEST-001",
        "category_id": 1,
        "unit_price": 1500.00,
        "cost_price": 1200.00
    }

    response = client.post("/api/products/", json=product_data, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["name"] == product_data["name"]

def test_list_products_pagination(client: TestClient):
    """Test product list pagination."""
    response = client.get("/api/products/?page=1&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) <= 10

def test_update_product(client: TestClient, auth_headers, test_product):
    """Test product update."""
    update_data = {"unit_price": 1600.00}

    response = client.patch(
        f"/api/products/{test_product.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["unit_price"] == 1600.00

def test_delete_product_soft_delete(client: TestClient, auth_headers, test_product):
    """Test soft delete."""
    response = client.delete(
        f"/api/products/{test_product.id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify product still exists but is_active = False
    db_product = db.query(Product).filter(Product.id == test_product.id).first()
    assert db_product is not None
    assert db_product.is_active is False
```

---

**Related Documentation:**
- Arabic support: @docs/reference/code-templates/arabic-bilingual.md
- Authentication: @docs/reference/code-templates/authentication.md
- Database optimization: @docs/reference/code-templates/database-optimization.md
- Testing: @docs/reference/code-templates/testing.md
