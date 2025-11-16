# TSH ERP Ecosystem - Architecture Rules

**Purpose:** Technical constraints, patterns, and conventions
**Last Updated:** 2025-11-14
**Load via:** @docs/core/architecture.md

---

## 🏗️ IMMUTABLE ARCHITECTURE DECISIONS

**These are FINAL and NON-NEGOTIABLE. Never suggest changing these.**

### Backend Stack
```yaml
✅ MUST USE:
  - FastAPI 0.104+ (NO Django, NO Flask, NO Node.js)
  - Python 3.9+
  - PostgreSQL 12+ (single database)
  - SQLAlchemy for ORM
  - Alembic for migrations
  - Pydantic for schemas

Why FastAPI:
  - Async/await (high concurrency)
  - Auto-generated OpenAPI docs
  - Type safety with Pydantic
  - Modern Python features
```

### Frontend Stack
```yaml
✅ MUST USE:
  - React 18+ with TypeScript (ERP Admin)
  - Flutter Web (Consumer App)
  - shadcn/ui components (new React UIs)

❌ NEVER SUGGEST:
  - Vue.js, Angular, Svelte
  - Plain JavaScript (use TypeScript)
```

### Mobile Stack
```yaml
✅ MUST USE:
  - Flutter 3.0+, Dart 3.0+
  - Single codebase for iOS + Android

❌ NEVER SUGGEST:
  - React Native, Ionic, Cordova
  - Native Swift/Kotlin separately

Why Flutter:
  - Single codebase, native performance
  - Already have 8 apps in Flutter
```

### Database
```yaml
✅ MUST USE:
  - PostgreSQL 12+ (single source of truth)
  - SQLAlchemy ORM

❌ NEVER SUGGEST:
  - MongoDB, MySQL, MariaDB
  - Multiple databases (no microservices DBs)

Why PostgreSQL:
  - ACID compliance (critical for financial data)
  - Complex query support
  - Proven reliability
```

### Communication & Notifications
```yaml
✅ MUST USE:
  - TSH NeuroLink (unified system for ALL communications)
  - WebSocket for real-time
  - Resend API for email delivery
  - Redis for event bus

❌ NEVER USE:
  - Twilio (any Twilio services)
  - Firebase Cloud Messaging (FCM)
  - Third-party push notification services

Why TSH NeuroLink:
  - Unified system for team chat, customer-sales, consumer support
  - Real-time WebSocket connections
  - Event-driven with Redis
  - Integrated with TSH ERP auth
```

---

## 📁 Project Structure

### Backend Structure (FastAPI)
```
app/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration management
├── database.py             # Database connection
│
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── product.py
│   ├── order.py
│
├── schemas/                # Pydantic schemas
│   ├── user.py
│   ├── product.py
│
├── routers/                # API endpoints
│   ├── auth.py
│   ├── products.py
│   ├── orders.py
│
├── services/               # Business logic
│   ├── auth_service.py
│   ├── product_service.py
│
├── utils/                  # Utility functions
│   ├── security.py
│   ├── validators.py
│
├── core/                   # Core functionality
│   ├── security.py
│   ├── deps.py            # Dependencies
│   ├── exceptions.py
│
└── tds/                    # TDS Core (Zoho sync)
    ├── sync_engine.py
    ├── processors/
    └── webhooks/
```

### Mobile Structure (Flutter)
```
mobile/flutter_apps/
├── 01_tsh_admin_app/
├── 06_travel_salesperson_app/
├── 10_tsh_consumer_app/       # Flutter Web + Mobile
└── ... (8 total apps)

Each app:
lib/
├── main.dart
├── models/
├── screens/
├── widgets/
├── services/
├── providers/
└── utils/
```

---

## 🎯 Coding Conventions

### Backend (Python/FastAPI)

#### Naming
```python
# Files: snake_case
user_service.py
product_schema.py

# Classes: PascalCase
class UserService:
class ProductSchema:

# Functions/Variables: snake_case
def get_user_by_id():
user_name = "Ahmad"

# Constants: UPPER_SNAKE_CASE
MAX_ITEMS_PER_PAGE = 100
API_VERSION = "v1"

# API Endpoints: kebab-case
@router.get("/api/v1/wholesale-clients")
@router.post("/api/v1/stock-adjustments")
```

#### Model Pattern (SQLAlchemy)
```python
# File: app/models/product.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Product(Base):
    """Product model for inventory management.

    Synced from Zoho Inventory via TDS Core.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)  # Arabic - MANDATORY
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, index=True)

    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### Schema Pattern (Pydantic)
```python
# File: app/schemas/product.py
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., description="Product name in English")
    name_ar: str = Field(..., description="Product name in Arabic")
    price: float = Field(..., gt=0, description="Price in IQD")

class ProductCreate(ProductBase):
    sku: str

class ProductResponse(ProductBase):
    id: int
    sku: str

    class Config:
        from_attributes = True
```

#### Router Pattern (API Endpoints)
```python
# File: app/routers/products.py
from fastapi import APIRouter, Depends
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/products", tags=["products"])

@router.get("", response_model=list[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends()
):
    """Get all products with pagination.

    Supports 2,218+ products with mandatory pagination.
    """
    return await service.get_products(skip=skip, limit=limit, user=current_user)
```

#### Service Pattern (Business Logic)
```python
# File: app/services/product_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(self, skip: int = 0, limit: int = 100, user: User = None):
        """Get products with RLS filtering."""
        query = select(Product)

        # RLS: Filter based on user permissions
        if user and not user.is_admin:
            query = query.filter(Product.is_active == True)

        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all()
```

### Frontend (React/TypeScript)

#### Naming
```typescript
// Files: kebab-case
user-profile.tsx
product-list.tsx

// Components: PascalCase
function UserProfile() {}
export const ProductList = () => {}

// Functions/Variables: camelCase
const getUserById = () => {}
const userName = "Ahmad"

// Constants: UPPER_SNAKE_CASE
const MAX_ITEMS = 100

// Interfaces: PascalCase with 'I' prefix
interface IProduct {
  id: number
  name: string
  nameAr: string  // Always include Arabic
}
```

### Mobile (Flutter/Dart)

#### Naming
```dart
// Files: snake_case
user_service.dart
product_list_screen.dart

// Classes: PascalCase
class UserService {}
class ProductListScreen extends StatelessWidget {}

// Functions/Variables: camelCase
String getUserName() {}
final userName = "Ahmad"

// Constants: lowerCamelCase (Dart convention)
const maxItems = 100

// Private: underscore prefix
class _ProductListState extends State<ProductListScreen> {}
```

#### RTL Support (MANDATORY)
```dart
// Always wrap with Directionality for Arabic support
@override
Widget build(BuildContext context) {
  return Directionality(
    textDirection: TextDirection.rtl,  // Arabic RTL
    child: Scaffold(
      appBar: AppBar(title: Text('المنتجات')),  // Arabic title
      body: ProductList(),
    ),
  );
}
```

---

## 🔒 Security Patterns (MANDATORY)

### Authorization Framework: RBAC + ABAC + RLS

**CRITICAL: TSH ERP uses HYBRID authorization with 3 layers:**

1. **RBAC** (Role-Based Access Control) - Permission sets based on roles
2. **ABAC** (Attribute-Based Access Control) - Fine-grained attribute checks
3. **RLS** (Row-Level Security) - Data filtering at query level

**ALL endpoints MUST implement all 3 layers:**

```python
# ✅ CORRECT: All three layers present
@router.get("/orders")
async def get_orders(
    # Layer 1: RBAC - Check role permissions
    user: User = Depends(require_role(["admin", "salesperson"])),

    # Layer 2: ABAC - Check user attributes
    abac_check: User = Depends(check_abac_permission("orders.read")),

    db: Session = Depends(get_db)
):
    # Layer 3: RLS - Filter data at query level
    service = OrderService(db, user)
    return await service.get_orders()  # RLS filtering inside service

# ❌ WRONG: Missing layers (Security Violation!)
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()  # Missing all 3 layers!
```

### Authentication Pattern
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPCredentials = Depends(security)
) -> User:
    """Verify JWT token and return current user."""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return await get_user_by_id(payload["user_id"])

# Use in routes
@router.get("/api/v1/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

### Input Validation (MANDATORY)
```python
# ✅ ALWAYS use Pydantic schemas
@router.post("/api/v1/products")
async def create_product(
    data: ProductCreate,  # Pydantic schema validates input
    current_user: User = Depends(get_current_user)
):
    return await service.create_product(data, current_user)

# ❌ NEVER accept raw dict
@router.post("/api/v1/products")
async def create_product(data: dict):  # WRONG! No validation
    return await service.create_product(data)
```

### SQL Injection Prevention
```python
# ✅ ALWAYS use parameterized queries or ORM
result = await db.execute(
    select(Product).filter(Product.sku == user_input)
)

# ❌ NEVER concatenate user input into SQL
query = f"SELECT * FROM products WHERE sku = '{user_input}'"  # DANGEROUS!
```

---

## ⚡ Performance Patterns (MANDATORY)

### Pagination (> 100 records)
```python
# ✅ ALWAYS paginate large datasets
@router.get("/products")
async def get_products(
    skip: int = 0,
    limit: int = 100,  # Max 100 per page for 2,218+ products
):
    return await service.get_products(skip=skip, limit=limit)

# ❌ NEVER return all records without pagination
@router.get("/products")
async def get_products():
    return db.query(Product).all()  # WRONG! Returns all 2,218+ products
```

### Database Indexing
```python
# ✅ ALWAYS index foreign keys and search fields
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, index=True)  # Indexed for search
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)  # FK index

    __table_args__ = (
        Index('idx_product_name', 'name'),  # Search by name
        Index('idx_product_name_ar', 'name_ar'),  # Search by Arabic name
    )
```

### N+1 Query Prevention
```python
# ✅ USE joinedload or selectinload
from sqlalchemy.orm import joinedload

orders = await db.execute(
    select(Order)
    .options(joinedload(Order.client))  # Single query with join
    .filter(Order.status == "pending")
)

# ❌ DON'T query in loops
orders = await db.execute(select(Order))
for order in orders:
    client = await db.execute(
        select(Client).filter(Client.id == order.client_id)
    )  # N+1 queries!
```

### Async/Await Pattern
```python
# ✅ USE async for I/O operations
async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Product).filter(Product.id == product_id)
    )
    return result.scalar_one_or_none()

# ❌ DON'T block async functions with sync I/O
async def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()  # Blocks!
```

---

## 🌍 Arabic Support (MANDATORY)

### Database Models
```python
# ✅ ALWAYS include Arabic fields for user-facing data
class Product(Base):
    name = Column(String, nullable=False)       # English
    name_ar = Column(String, nullable=False)    # Arabic - MANDATORY
    description = Column(Text)                  # English
    description_ar = Column(Text)               # Arabic - MANDATORY
```

### API Responses
```json
{
  "id": 123,
  "name": "Laptop",
  "name_ar": "حاسوب محمول",
  "description": "15-inch laptop",
  "description_ar": "حاسوب محمول 15 بوصة"
}
```

### Frontend (React)
```typescript
// Support RTL layout
<div className={isArabic ? 'rtl' : 'ltr'} dir={isArabic ? 'rtl' : 'ltr'}>
  <h1>{product.nameAr || product.name}</h1>
</div>
```

### Mobile (Flutter)
```dart
// Wrap with Directionality
Directionality(
  textDirection: TextDirection.rtl,
  child: Text(product.nameAr ?? product.name),
)
```

---

## 🔗 API Design Patterns

### RESTful Conventions
```
GET    /api/v1/products         # List products (paginated)
GET    /api/v1/products/{id}    # Get single product
POST   /api/v1/products         # Create product
PUT    /api/v1/products/{id}    # Update product (full)
PATCH  /api/v1/products/{id}    # Update product (partial)
DELETE /api/v1/products/{id}    # Delete product
```

### Response Format
```json
{
  "data": [...],
  "total": 2218,
  "page": 1,
  "pageSize": 100,
  "totalPages": 23
}
```

### Error Format
```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product with ID 123 not found",
    "message_ar": "المنتج رقم 123 غير موجود",
    "details": {}
  }
}
```

---

## 🎯 TDS Core Integration (CRITICAL)

**NEVER bypass TDS Core to access Zoho APIs directly.**

### Correct Pattern
```python
# ✅ CORRECT: Through TDS Core
from app.tds.sync_engine import TDSCore

tds = TDSCore()
products = await tds.get_products_from_zoho()  # TDS Core handles API calls

# ❌ WRONG: Direct Zoho API access
import requests
response = requests.get(
    "https://www.zohoapis.com/inventory/v1/items",
    headers={"Authorization": f"Zoho-oauthtoken {token}"}
)  # VIOLATES ARCHITECTURE!
```

### TDS Core Responsibilities
- ALL Zoho Books API calls
- ALL Zoho Inventory API calls
- Webhook handling
- Data transformation
- Error handling and retries
- Rate limit management
- Sync logging and monitoring

---

## 🚀 Deployment Patterns

### Environment Variables (NEVER hardcode)
```python
# ✅ CORRECT: Use environment variables
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    zoho_client_id: str
    zoho_client_secret: str

    class Config:
        env_file = ".env"

settings = Settings()

# ❌ WRONG: Hardcoded credentials
database_url = "postgresql://user:password123@localhost/db"  # DANGEROUS!
```

### Docker Deployment
```yaml
# docker-compose.yml pattern
services:
  backend:
    build: .
    env_file: .env.production
    depends_on:
      - db
      - redis

  db:
    image: postgres:12
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Zero-Downtime Deployment
```bash
# Blue-Green deployment pattern
1. Deploy new version to staging (develop branch)
2. Test thoroughly
3. Create PR (develop → main)
4. Deploy to production without stopping old version
5. Health check new version
6. Switch traffic to new version
7. Monitor for issues
8. Keep old version for quick rollback
```

---

## 📊 Monitoring & Logging

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

# ✅ LOG important events
logger.info(f"User {user.id} placed order {order.id}")
logger.error(f"Failed to sync product {product_id} from Zoho", exc_info=True)

# ❌ DON'T log sensitive data
logger.info(f"User password: {password}")  # SECURITY VIOLATION!
```

### Health Check Endpoint
```python
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check for monitoring."""
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## 🔍 Testing Patterns

### Unit Tests
```python
# tests/test_product_service.py
import pytest
from app.services.product_service import ProductService

@pytest.mark.asyncio
async def test_get_products_with_pagination():
    service = ProductService(db)
    products = await service.get_products(skip=0, limit=10)

    assert len(products) <= 10
    assert all(p.name_ar is not None for p in products)  # Verify Arabic
```

### Integration Tests
```python
# tests/test_product_api.py
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_products_api(client: AsyncClient):
    response = await client.get("/api/v1/products?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10
```

---

## 📋 Checklist for New Features

```yaml
Before implementing ANY feature:
□ Search existing code for similar functionality
□ Read relevant @docs/ files
□ Include Arabic fields (name_ar, description_ar)
□ Implement all 3 authorization layers (RBAC + ABAC + RLS)
□ Add input validation (Pydantic schemas)
□ Add pagination if > 100 records
□ Add database indexes for search/foreign keys
□ Prevent N+1 queries (use joinedload)
□ Use async/await for I/O operations
□ Route Zoho operations through TDS Core
□ Add error handling (try/except)
□ Add logging for important events
□ Write unit tests
□ Test on staging before production
```

---

**For More Details:**
- Business context: @docs/core/project-context.md
- Workflows: @docs/core/workflows.md
- Authorization framework: @docs/AUTHORIZATION_FRAMEWORK.md
- Code templates: @docs/reference/code-templates/
- Failsafe protocols: @docs/FAILSAFE_PROTOCOL.md
