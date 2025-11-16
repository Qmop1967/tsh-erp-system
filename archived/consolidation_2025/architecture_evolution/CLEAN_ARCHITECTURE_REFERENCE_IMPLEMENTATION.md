# Clean Architecture Reference Implementation

**Date:** November 5, 2025
**Status:** Phase 1 Complete - Customer Module
**Version:** 1.0

---

## Overview

This document describes the reference implementation of clean architecture for the TSH ERP backend. The customer module has been fully refactored to demonstrate the pattern that should be followed for all other modules.

## Architecture Layers

### 1. Domain Layer (`app/domain/`)
Pure business entities and rules (not yet implemented, using SQLAlchemy models for now).

### 2. Application Layer (`app/application/`)
Business logic and use cases.

**Structure:**
```
app/application/
├── interfaces/
│   └── repositories/
│       ├── __init__.py
│       ├── base_repository.py          # Generic repository interface
│       └── customer_repository.py      # Customer-specific repository interface
├── dtos/
│   ├── __init__.py
│   └── customer_dto.py                 # Request/response DTOs
└── services/
    ├── __init__.py
    └── customer_service.py             # Business logic
```

### 3. Infrastructure Layer (`app/infrastructure/`)
External services, database implementations.

**Structure:**
```
app/infrastructure/
├── __init__.py
└── repositories/
    ├── __init__.py
    └── sqlalchemy/
        ├── __init__.py
        └── customer_repository.py      # SQLAlchemy implementation
```

### 4. Presentation Layer (`app/routers/`)
API endpoints and request handling.

**Structure:**
```
app/routers/
└── v2/
    ├── __init__.py
    └── customers.py                    # REST API endpoints
```

### 5. Core Layer (`app/core/`)
Dependency injection and configuration.

**Structure:**
```
app/core/
└── dependencies.py                     # DI container
```

---

## Implementation Details

### 1. Base Repository Interface

**File:** `app/application/interfaces/repositories/base_repository.py`

Generic repository interface with common CRUD operations:

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')  # Entity type
ID = TypeVar('ID')  # ID type

class IBaseRepository(ABC, Generic[T, ID]):
    """Base repository interface for data access operations."""

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """Get an entity by its ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Get all entities with optional pagination and filtering."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """Check if an entity exists."""
        pass

    @abstractmethod
    async def count(self, **filters) -> int:
        """Count entities with optional filtering."""
        pass

    @abstractmethod
    async def find_one(self, **filters) -> Optional[T]:
        """Find a single entity by filters."""
        pass

    @abstractmethod
    async def find_many(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Find multiple entities by filters."""
        pass
```

### 2. Customer Repository Interface

**File:** `app/application/interfaces/repositories/customer_repository.py`

Extends base repository with customer-specific methods:

```python
from app.application.interfaces.repositories.base_repository import IBaseRepository
from app.models import Customer

class ICustomerRepository(IBaseRepository[Customer, int]):
    """Customer repository interface for data access operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by email address."""
        pass

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get a customer by phone number."""
        pass

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100,
                     is_active: Optional[bool] = None) -> List[Customer]:
        """Search customers by name, email, phone, or customer code."""
        pass

    # ... more customer-specific methods
```

### 3. Customer Repository Implementation

**File:** `app/infrastructure/repositories/sqlalchemy/customer_repository.py`

Concrete SQLAlchemy implementation (293 lines):

```python
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories.customer_repository import ICustomerRepository
from app.models import Customer

class CustomerRepository(ICustomerRepository):
    """SQLAlchemy implementation of the customer repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.id == id)
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, skip: int = 0, limit: int = 100,
                     is_active: Optional[bool] = None) -> List[Customer]:
        search_pattern = f"%{query}%"
        sql_query = select(Customer).where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                Customer.phone.ilike(search_pattern),
                Customer.customer_code.ilike(search_pattern)
            )
        )
        if is_active is not None:
            sql_query = sql_query.where(Customer.is_active == is_active)
        sql_query = sql_query.offset(skip).limit(limit)
        result = await self.db.execute(sql_query)
        return list(result.scalars().all())

    # ... all other methods implemented
```

### 4. Customer DTOs

**File:** `app/application/dtos/customer_dto.py`

Data transfer objects for validation (220 lines):

```python
from pydantic import BaseModel, EmailStr, Field, validator

class CustomerCreateDTO(BaseModel):
    """DTO for creating a new customer."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    # ... all fields with validation

    @validator('email')
    def validate_email(cls, v):
        if v:
            return v.lower()
        return v

class CustomerUpdateDTO(BaseModel):
    """DTO for updating an existing customer."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    # ... all optional fields

class CustomerResponseDTO(BaseModel):
    """DTO for customer response."""
    id: int
    name: str
    email: Optional[str] = None
    balance: float = 0.0
    created_at: datetime
    # ... all response fields

    class Config:
        from_attributes = True

class CustomerListResponseDTO(BaseModel):
    """DTO for customer list response with pagination."""
    items: list[CustomerResponseDTO]
    total: int
    skip: int
    limit: int

class CustomerSearchDTO(BaseModel):
    """DTO for customer search parameters."""
    query: Optional[str] = None
    is_active: Optional[bool] = None
    salesperson_id: Optional[int] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
```

### 5. Customer Service

**File:** `app/application/services/customer_service.py`

Business logic layer (351 lines):

```python
from app.application.interfaces.repositories.customer_repository import ICustomerRepository
from app.application.dtos.customer_dto import *

class CustomerService:
    """Service class for customer business logic."""

    def __init__(self, customer_repository: ICustomerRepository):
        self.repository = customer_repository

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerResponseDTO:
        """Create a new customer with validation."""
        # Check for duplicate email
        if dto.email:
            existing = await self.repository.get_by_email(dto.email)
            if existing:
                raise ValueError(f"Customer with email {dto.email} already exists")

        # Check for duplicate customer code
        if dto.customer_code:
            existing = await self.repository.get_by_customer_code(dto.customer_code)
            if existing:
                raise ValueError(f"Customer with code {dto.customer_code} already exists")

        # Create customer entity
        customer = Customer(**dto.model_dump())
        created_customer = await self.repository.create(customer)
        return CustomerResponseDTO.model_validate(created_customer)

    async def validate_customer_credit(self, customer_id: int,
                                       order_amount: float) -> tuple[bool, str]:
        """Validate if customer has enough credit for an order."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return False, "Customer not found"

        if not customer.is_active:
            return False, "Customer is not active"

        available_credit = customer.credit_limit - customer.balance
        if available_credit < order_amount:
            return False, f"Insufficient credit. Available: {available_credit:.2f}"

        return True, "Credit validation passed"

    # ... all business logic methods
```

### 6. Dependency Injection

**File:** `app/core/dependencies.py`

FastAPI dependency injection:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.infrastructure.repositories.sqlalchemy.customer_repository import CustomerRepository
from app.application.services.customer_service import CustomerService

async def get_customer_repository(db: AsyncSession = Depends(get_db)):
    """Get customer repository dependency."""
    return CustomerRepository(db)

async def get_customer_service(
    customer_repository = Depends(get_customer_repository)
) -> CustomerService:
    """Get customer service dependency."""
    return CustomerService(customer_repository)
```

### 7. API Router

**File:** `app/routers/v2/customers.py`

Clean API endpoints (360 lines):

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from app.application.services.customer_service import CustomerService
from app.application.dtos.customer_dto import *
from app.core.dependencies import get_customer_service

router = APIRouter(prefix="/v2/customers", tags=["customers-v2"])

@router.get("", response_model=CustomerListResponseDTO)
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    service: CustomerService = Depends(get_customer_service)
):
    """Get all customers with optional filtering."""
    return await service.get_all_customers(skip, limit, is_active)

@router.post("", response_model=CustomerResponseDTO, status_code=201)
async def create_customer(
    dto: CustomerCreateDTO,
    service: CustomerService = Depends(get_customer_service)
):
    """Create a new customer."""
    try:
        return await service.create_customer(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=CustomerListResponseDTO)
async def search_customers(
    query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    # ... more filters
    service: CustomerService = Depends(get_customer_service)
):
    """Search customers with advanced filters."""
    search_dto = CustomerSearchDTO(query=query, is_active=is_active, ...)
    return await service.search_customers(search_dto)

# ... 14 total endpoints
```

---

## Usage Examples

### Example 1: Get All Customers

```bash
curl -X GET "http://erp.tsh.sale/api/v2/customers?skip=0&limit=10&is_active=true"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "ABC Company",
      "email": "contact@abc.com",
      "phone": "+96512345678",
      "customer_code": "CUST-001",
      "balance": 5000.00,
      "credit_limit": 10000.00,
      "is_active": true,
      "created_at": "2025-01-01T10:00:00"
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 10
}
```

### Example 2: Search Customers

```bash
curl -X GET "http://erp.tsh.sale/api/v2/customers/search?query=ABC&is_active=true"
```

### Example 3: Create Customer

```bash
curl -X POST "http://erp.tsh.sale/api/v2/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Customer Ltd",
    "email": "contact@newcustomer.com",
    "phone": "+96512345678",
    "credit_limit": 5000.00,
    "payment_terms": 30,
    "is_active": true
  }'
```

### Example 4: Validate Credit

```bash
curl -X POST "http://erp.tsh.sale/api/v2/customers/1/validate-credit?order_amount=2000.00"
```

**Response:**
```json
{
  "valid": true,
  "message": "Credit validation passed"
}
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v2/customers` | Get all customers (with pagination) |
| GET | `/v2/customers/search` | Search customers (advanced filters) |
| GET | `/v2/customers/active/summary` | Get active customers summary |
| GET | `/v2/customers/{id}` | Get customer by ID |
| GET | `/v2/customers/{id}/stats` | Get customer statistics |
| GET | `/v2/customers/email/{email}` | Get customer by email |
| GET | `/v2/customers/code/{code}` | Get customer by code |
| GET | `/v2/customers/salesperson/{id}` | Get customers by salesperson |
| POST | `/v2/customers` | Create new customer |
| PUT | `/v2/customers/{id}` | Update customer |
| DELETE | `/v2/customers/{id}` | Delete customer (soft delete) |
| POST | `/v2/customers/{id}/validate-credit` | Validate customer credit |

---

## Benefits Achieved

### 1. Separation of Concerns
- **Presentation** (routers) - HTTP handling
- **Application** (services) - Business logic
- **Infrastructure** (repositories) - Data access
- **Domain** (models) - Business entities

### 2. Testability
Each layer can be tested independently:

```python
# Test service with mock repository
async def test_create_customer():
    mock_repo = Mock(ICustomerRepository)
    service = CustomerService(mock_repo)
    # ... test without database
```

### 3. Flexibility
Easy to swap implementations:

```python
# Switch from SQLAlchemy to MongoDB
async def get_customer_repository(db = Depends(get_mongo_db)):
    return MongoCustomerRepository(db)  # Same interface!
```

### 4. Type Safety
Full type hints enable IDE support and compile-time checking.

### 5. Validation
Pydantic DTOs validate all input/output automatically.

### 6. Documentation
FastAPI generates OpenAPI docs automatically from DTOs.

---

## Migration Strategy

### Step 1: Create Interfaces (Day 1)
```bash
app/application/interfaces/repositories/
├── product_repository.py
├── order_repository.py
└── inventory_repository.py
```

### Step 2: Create DTOs (Day 1-2)
```bash
app/application/dtos/
├── product_dto.py
├── order_dto.py
└── inventory_dto.py
```

### Step 3: Implement Repositories (Day 2-3)
```bash
app/infrastructure/repositories/sqlalchemy/
├── product_repository.py
├── order_repository.py
└── inventory_repository.py
```

### Step 4: Create Services (Day 3-4)
```bash
app/application/services/
├── product_service.py
├── order_service.py
└── inventory_service.py
```

### Step 5: Update Dependencies (Day 4)
```python
# app/core/dependencies.py
async def get_product_service(...): ...
async def get_order_service(...): ...
```

### Step 6: Create V2 Routers (Day 5)
```bash
app/routers/v2/
├── products.py
├── orders.py
└── inventory.py
```

### Step 7: Integration & Testing (Day 6)
- Register routers in main.py
- Integration tests
- Load testing

### Step 8: Deprecate V1 (Gradual)
- Keep v1 routes for backward compatibility
- Update mobile app to use v2
- Monitor usage
- Remove v1 after 2-3 months

---

## Code Quality Metrics

### Lines of Code
- Base Repository Interface: 145 lines
- Customer Repository Interface: 163 lines
- Customer Repository Implementation: 293 lines
- Customer DTOs: 220 lines
- Customer Service: 351 lines
- Customer Router: 360 lines
- **Total:** 1,532 lines

### Files Created
- 14 new files
- 0 errors
- 100% syntax validated

### Test Coverage (Planned)
- Unit tests for services: 90%+ target
- Integration tests for repositories: 85%+ target
- E2E tests for endpoints: 80%+ target

---

## Next Steps

### Phase 2: Order Module (Days 7-9)
1. Create order repository interface
2. Implement order repository
3. Create order DTOs
4. Refactor order service
5. Create v2/orders router

### Phase 3: Product Module (Days 10-12)
1. Create product repository interface
2. Implement product repository
3. Create product DTOs
4. Refactor product service
5. Create v2/products router

### Phase 4: Additional Modules (Days 13-15)
- Inventory
- Payments
- Invoices
- Reports

### Phase 5: Testing & Documentation (Days 16-18)
- Write unit tests
- Write integration tests
- Update API documentation
- Create developer guide

### Phase 6: Deployment & Monitoring (Days 19-20)
- Deploy to staging
- Performance testing
- Deploy to production
- Monitor metrics

---

## File Reference

### Created Files

1. **`app/application/interfaces/__init__.py`** - Application interfaces package
2. **`app/application/interfaces/repositories/__init__.py`** - Repository interfaces package
3. **`app/application/interfaces/repositories/base_repository.py`** - Base repository interface
4. **`app/application/interfaces/repositories/customer_repository.py`** - Customer repository interface
5. **`app/application/dtos/__init__.py`** - DTOs package
6. **`app/application/dtos/customer_dto.py`** - Customer DTOs
7. **`app/application/services/__init__.py`** - Services package
8. **`app/application/services/customer_service.py`** - Customer service
9. **`app/infrastructure/__init__.py`** - Infrastructure package
10. **`app/infrastructure/repositories/__init__.py`** - Repositories package
11. **`app/infrastructure/repositories/sqlalchemy/__init__.py`** - SQLAlchemy repositories package
12. **`app/infrastructure/repositories/sqlalchemy/customer_repository.py`** - Customer repository implementation
13. **`app/core/dependencies.py`** - Dependency injection
14. **`app/routers/v2/__init__.py`** - V2 routers package
15. **`app/routers/v2/customers.py`** - Customer router v2

### All Files Validated
All 15 files compiled successfully with `python3 -m py_compile` - 0 errors.

---

## References

- **Clean Architecture:** Robert C. Martin (Uncle Bob)
- **Repository Pattern:** Martin Fowler
- **Dependency Injection:** Mark Seemann
- **FastAPI Best Practices:** FastAPI official documentation

---

**Document Version:** 1.0
**Last Updated:** November 5, 2025
**Authors:** TSH ERP Development Team
