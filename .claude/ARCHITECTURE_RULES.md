# TSH ERP Ecosystem - Architecture Rules

**Technical constraints, patterns, and conventions**
**Last Updated:** 2025-11-12

---

## 🏗️ IMMUTABLE ARCHITECTURE DECISIONS

These decisions are **FINAL** and **NON-NEGOTIABLE**. Do NOT suggest changing these.

### Backend Framework
```yaml
✅ MUST USE:
  - FastAPI 0.104+
  - Python 3.9+
  - Pydantic for schemas
  - SQLAlchemy for ORM
  - Alembic for migrations

❌ NEVER SUGGEST:
  - Django
  - Flask
  - Node.js/Express
  - Go/Gin
  - Any other backend framework
```

**Why FastAPI:**
- Async/await support (high concurrency)
- Auto-generated OpenAPI docs
- Type safety with Pydantic
- Fast performance
- Modern Python features

### Database
```yaml
✅ MUST USE:
  - PostgreSQL 12+
  - Single database (no microservices DBs)
  - SQLAlchemy ORM

❌ NEVER SUGGEST:
  - MongoDB
  - MySQL
  - MariaDB
  - SQLite (except for tests)
  - Multiple databases
```

**Why PostgreSQL:**
- ACID compliance (critical for financial data)
- Complex query support
- JSON support when needed
- Proven reliability
- Strong ecosystem

### Frontend Web
```yaml
✅ MUST USE:
  - React 18+ with TypeScript (ERP Admin)
  - Flutter Web (Consumer App)
  - shadcn/ui components (for new React UIs)

❌ NEVER SUGGEST:
  - Vue.js
  - Angular
  - Svelte
  - Plain JavaScript (use TypeScript)
```

### Mobile Apps
```yaml
✅ MUST USE:
  - Flutter 3.0+
  - Dart 3.0+
  - Single codebase for iOS + Android

❌ NEVER SUGGEST:
  - React Native
  - Ionic
  - Native Swift/Kotlin separately
  - Cordova
  - Xamarin
```

**Why Flutter:**
- Single codebase for both platforms
- Native performance
- Great UI toolkit
- Strong community
- Already have 8 apps in Flutter

---

## 📁 Project Structure (MUST FOLLOW)

### Backend Structure
```
app/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration management
├── database.py             # Database connection
│
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── ...
│
├── schemas/                # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   └── ...
│
├── routers/                # API endpoints
│   ├── __init__.py
│   ├── auth.py
│   ├── products.py
│   ├── orders.py
│   └── ...
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── product_service.py
│   └── ...
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── security.py
│   ├── validators.py
│   └── ...
│
└── core/                   # Core functionality
    ├── __init__.py
    ├── security.py
    ├── deps.py            # Dependencies
    └── exceptions.py
```

### Mobile Apps Structure
```
mobile/flutter_apps/
├── 01_tsh_admin_app/
├── 02_admin_mobile_app/
├── 03_tsh_hr_mobile_app/
├── 04_tsh_retailer_shop_app/
├── 05_tsh_inventory_management_app/
├── 06_travel_salesperson_app/
├── 07_wholesale_client_app/
├── 08_partner_salesman_app/
└── 10_tsh_consumer_app/       # Flutter Web + Mobile

Each app follows:
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

#### Naming Conventions
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

#### File Organization Rules
```python
# 1. Models (SQLAlchemy)
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
    name_ar = Column(String, nullable=False)  # Arabic name
    price = Column(Float, nullable=False)
    # ...

# 2. Schemas (Pydantic)
# File: app/schemas/product.py
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., description="Product name in English")
    name_ar: str = Field(..., description="Product name in Arabic")
    price: float = Field(..., gt=0, description="Product price in IQD")

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# 3. Routers (API Endpoints)
# File: app/routers/products.py
from fastapi import APIRouter, Depends
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])

@router.get("", response_model=list[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends()
):
    """Get all products.

    Supports pagination for 2,218+ products.
    """
    return await service.get_products(skip=skip, limit=limit)

# 4. Services (Business Logic)
# File: app/services/product_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(self, skip: int = 0, limit: int = 100):
        """Get products with pagination."""
        result = await self.db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return result.scalars().all()
```

### Frontend (React/TypeScript)

#### Naming Conventions
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
const API_BASE_URL = "https://erp.tsh.sale"

// Interfaces/Types: PascalCase with 'I' prefix
interface IProduct {
  id: number
  name: string
  nameAr: string  // Arabic name
}
```

#### Component Structure
```typescript
// File: src/components/product-list.tsx
import React, { useEffect, useState } from 'react'
import { IProduct } from '@/types/product'
import { productService } from '@/services/product-service'

interface ProductListProps {
  categoryId?: number
  showArabic?: boolean  // Always support Arabic
}

export const ProductList: React.FC<ProductListProps> = ({
  categoryId,
  showArabic = true
}) => {
  const [products, setProducts] = useState<IProduct[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProducts()
  }, [categoryId])

  const loadProducts = async () => {
    setLoading(true)
    try {
      const data = await productService.getProducts(categoryId)
      setProducts(data)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={showArabic ? 'rtl' : 'ltr'}>
      {/* Component JSX */}
    </div>
  )
}
```

### Mobile (Flutter/Dart)

#### Naming Conventions
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
const apiBaseUrl = "https://erp.tsh.sale"

// Private: underscore prefix
class _ProductListState extends State<ProductListScreen> {}
```

#### Widget Structure
```dart
// File: lib/screens/product_list_screen.dart
import 'package:flutter/material.dart';
import '../models/product.dart';
import '../services/product_service.dart';

class ProductListScreen extends StatefulWidget {
  const ProductListScreen({Key? key}) : super(key: key);

  @override
  State<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  final ProductService _productService = ProductService();
  List<Product> _products = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);
    try {
      final products = await _productService.getProducts();
      setState(() {
        _products = products;
        _isLoading = false;
      });
    } catch (e) {
      print('Failed to load products: $e');
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // RTL support for Arabic
    return Directionality(
      textDirection: TextDirection.rtl,  // Always support Arabic
      child: Scaffold(
        appBar: AppBar(title: Text('المنتجات')),  // Arabic title
        body: _isLoading
            ? Center(child: CircularProgressIndicator())
            : ListView.builder(
                itemCount: _products.length,
                itemBuilder: (context, index) {
                  return ProductListItem(product: _products[index]);
                },
              ),
      ),
    );
  }
}
```

---

## 🔒 Security Patterns (MANDATORY)

### Authentication
```python
# ALWAYS use JWT tokens
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

### Authorization (RBAC)
```python
# Role-based access control
from enum import Enum

class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    RETAIL_STAFF = "retail_staff"
    INVENTORY_MANAGER = "inventory_manager"
    TRAVEL_SALES = "travel_sales"
    WHOLESALE_CLIENT = "wholesale_client"
    CONSUMER = "consumer"
    PARTNER_SALESMAN = "partner_salesman"

def require_role(allowed_roles: list[UserRole]):
    """Decorator to require specific roles."""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Use in routes
@router.get("/api/v1/financials")
async def get_financials(
    current_user: User = Depends(
        require_role([UserRole.OWNER, UserRole.ADMIN])
    )
):
    # Only owner and admin can access
    return financial_data
```

### Input Validation
```python
# ALWAYS validate input with Pydantic
from pydantic import BaseModel, Field, validator

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0, description="Price in IQD")
    stock: int = Field(..., ge=0)

    @validator('price')
    def validate_price(cls, v):
        if v > 1000000000:  # 1 billion IQD
            raise ValueError('Price too high')
        return v

    @validator('name_ar')
    def validate_arabic(cls, v):
        # Basic Arabic character check
        if not any('\u0600' <= c <= '\u06FF' for c in v):
            raise ValueError('Arabic name must contain Arabic characters')
        return v
```

---

## 🌐 API Design Patterns

### REST API Structure
```
/api/v1/
├── /auth
│   ├── POST /login
│   ├── POST /refresh
│   └── POST /logout
│
├── /products
│   ├── GET /products              # List all
│   ├── GET /products/{id}         # Get one
│   ├── POST /products             # Create (admin only)
│   ├── PUT /products/{id}         # Update (admin only)
│   └── DELETE /products/{id}      # Delete (admin only)
│
├── /orders
│   ├── GET /orders
│   ├── GET /orders/{id}
│   ├── POST /orders
│   └── PUT /orders/{id}/status
│
├── /inventory
│   ├── GET /inventory/stock
│   ├── POST /inventory/adjustments
│   └── GET /inventory/warehouses
│
└── /zoho-sync                     # TDS endpoints
    ├── GET /zoho-sync/status
    ├── POST /zoho-sync/trigger
    └── GET /zoho-sync/logs
```

### Response Format (CONSISTENT)
```python
# Success Response
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Product A",
    "name_ar": "منتج أ"
  },
  "message": "Product retrieved successfully"
}

# List Response
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 2218,
    "page": 1,
    "per_page": 100,
    "total_pages": 23
  }
}

# Error Response
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product with ID 999 not found",
    "message_ar": "لم يتم العثور على المنتج رقم 999"
  }
}
```

---

## 🗄️ Database Patterns

### Model Design
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Product(Base):
    """Product model synced from Zoho Inventory."""
    __tablename__ = "products"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Zoho reference (ALWAYS keep for sync)
    zoho_item_id = Column(String, unique=True, nullable=False, index=True)

    # Bilingual fields (ALWAYS include Arabic)
    name = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    description = Column(Text)
    description_ar = Column(Text)

    # Business fields
    sku = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    cost = Column(Float)
    stock_quantity = Column(Integer, default=0)

    # Audit fields (ALWAYS include)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
```

### Indexing Strategy
```python
# ALWAYS index:
# 1. Foreign keys
# 2. Fields used in WHERE clauses
# 3. Fields used in ORDER BY
# 4. Zoho reference IDs

# Example:
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    zoho_salesorder_id = Column(String, unique=True, index=True)  # Zoho ref
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)  # FK
    status = Column(String, index=True)  # WHERE clause
    created_at = Column(DateTime, index=True)  # ORDER BY
```

---

## 🔄 Zoho Sync Patterns

### CRITICAL: NEVER Access Zoho Directly
```python
# ❌ WRONG - Direct Zoho API access
import requests
response = requests.get("https://www.zohoapis.com/inventory/v1/items")

# ✅ CORRECT - Go through TDS Core
from app.services.tds_service import TDSService

tds = TDSService()
products = await tds.sync_products_from_zoho()
```

### TDS Core Integration
```python
# File: app/services/tds_service.py
class TDSService:
    """Service for TDS Core integration.

    TDS Core handles ALL Zoho Books and Zoho Inventory sync.
    """

    async def get_sync_status(self) -> dict:
        """Get current sync status from TDS Core."""
        # Call TDS Core API
        pass

    async def trigger_manual_sync(self, entity_type: str) -> dict:
        """Trigger manual sync for specific entity type.

        Args:
            entity_type: 'products', 'customers', 'invoices', etc.
        """
        # Call TDS Core API
        pass

    async def get_sync_logs(self, limit: int = 100) -> list[dict]:
        """Get recent sync logs."""
        # Call TDS Core API
        pass
```

---

## 🌍 Internationalization (i18n) Patterns

### MANDATORY: Arabic Support
```python
# Backend - Store both languages
class ProductSchema(BaseModel):
    name: str  # English
    name_ar: str  # Arabic (MANDATORY)
    description: Optional[str] = None
    description_ar: Optional[str] = None

# Frontend React - Support RTL
<div className={locale === 'ar' ? 'rtl' : 'ltr'} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
  <p>{locale === 'ar' ? product.nameAr : product.name}</p>
</div>

# Flutter - Use Directionality
Directionality(
  textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
  child: Text(isArabic ? product.nameAr : product.name),
)
```

---

## 📦 Deployment Architecture

### Environment Variables
```bash
# .env (development)
APP_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/tsh_erp
ZOHO_CLIENT_ID=xxx
ZOHO_CLIENT_SECRET=xxx
AWS_S3_BUCKET=tsh-erp-backups
JWT_SECRET=xxx

# .env.production (production)
APP_ENV=production
DATABASE_URL=postgresql://user:pass@localhost:5432/tsh_erp_production
# ... (more secure values)
```

### Docker Compose Structure
```yaml
# docker-compose.yml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=${DATABASE_URL}

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data

  tds_core:
    build: ./tds_core
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
```

---

## ✅ Code Review Checklist

Before marking any task complete, verify:

### Functionality
- [ ] Feature works as specified
- [ ] Handles edge cases
- [ ] Error handling implemented
- [ ] Input validation included

### Security
- [ ] Authentication required where needed
- [ ] Authorization (RBAC) enforced
- [ ] Input sanitized
- [ ] SQL injection prevented (using ORM)

### Internationalization
- [ ] Arabic fields included (name_ar, description_ar)
- [ ] RTL layout supported
- [ ] Arabic text displays correctly

### Performance
- [ ] Database queries optimized
- [ ] Indexes used appropriately
- [ ] Pagination for large lists
- [ ] API response < 500ms

### Code Quality
- [ ] Follows naming conventions
- [ ] Well commented
- [ ] Type hints included (Python/TypeScript)
- [ ] No duplicate code

### Testing
- [ ] Unit tests written (if applicable)
- [ ] Tested locally
- [ ] Tested on staging
- [ ] Tested with Arabic text

### Deployment
- [ ] All components built
- [ ] Environment variables set
- [ ] Migrations applied
- [ ] Verified on staging before production

---

## 🚨 Common Anti-Patterns (AVOID)

### ❌ Don't Do This
```python
# Direct database queries in routes
@router.get("/products")
async def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()  # ❌ Business logic in route

# Hardcoded values
price = 50000  # ❌ Magic number

# Missing Arabic support
class Product(Base):
    name = Column(String)  # ❌ Where is name_ar?

# No error handling
data = requests.get(url).json()  # ❌ What if it fails?

# Direct Zoho access
response = requests.get("https://www.zohoapis.com/...")  # ❌ Use TDS Core!
```

### ✅ Do This Instead
```python
# Use service layer
@router.get("/products")
async def get_products(service: ProductService = Depends()):
    return await service.get_all_products()  # ✅ Clean separation

# Use constants
MAX_WHOLESALE_CREDIT_LIMIT = 50_000_000  # ✅ Named constant

# Include Arabic
class Product(Base):
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)  # ✅ Bilingual

# Handle errors
try:
    data = requests.get(url, timeout=10).json()
except requests.RequestException as e:
    logger.error(f"Request failed: {e}")
    raise HTTPException(status_code=500, detail="External API failed")

# Use TDS Core
await tds_service.sync_products()  # ✅ Through TDS Core
```

---

## 🤖 AI Interaction Rules

**Behavioral boundaries and expectations for Claude Code**

### Core Principles

#### 1. **Never Bypass Established Architecture**
```python
# ❌ NEVER suggest or implement
"Let's switch to Django - it has better admin panel"
"MongoDB would be better for products"
"Should we use React Native for mobile?"

# ✅ ALWAYS respect constraints
"I'll use FastAPI as established"
"Working within PostgreSQL schema"
"Implementing in Flutter as per architecture"
```

#### 2. **Always Consult PROJECT_VISION.md First**
```
When uncertain about business logic:
❌ Guess and implement
✅ Check PROJECT_VISION.md
✅ Ask Khaleel for clarification

Example:
"PROJECT_VISION.md mentions wholesale clients have credit limits.
 Should this order check against their credit limit before confirming?"
```

#### 3. **Provide Context with Code**
```python
# ❌ BAD: Just code without explanation
@router.post("/orders")
async def create_order(order: OrderCreate):
    # ... code ...

# ✅ GOOD: Explain why and how
@router.post("/orders")
async def create_order(order: OrderCreate):
    """Create new order with credit limit validation.

    Business Logic:
    - Wholesale clients (500+) must stay within credit limit
    - Retail customers pay cash immediately
    - Validation happens before inventory reservation

    See PROJECT_VISION.md for business context.
    """
    # ... code with inline comments ...
```

#### 4. **Never Create Endpoints That Bypass TDS Core**
```python
# ❌ ABSOLUTELY FORBIDDEN
@router.get("/api/zoho/products")
async def get_zoho_products():
    response = requests.get("https://www.zohoapis.com/inventory/v1/items")
    return response.json()

# ✅ CORRECT: Go through TDS Core
@router.get("/api/products/sync-status")
async def get_sync_status(tds: TDSService = Depends()):
    """Get product sync status from TDS Core.

    TDS Core handles ALL Zoho Books and Zoho Inventory communication.
    Never access Zoho APIs directly.
    """
    return await tds.get_sync_status("products")
```

#### 5. **Optimization Must Have Justification**
```python
# ❌ BAD: Optimize without measurement
"I optimized the query by adding caching"

# ✅ GOOD: Justify with data
"The /api/products endpoint was taking 2.3 seconds for 2,218 products.
 I added pagination (100 per page) and database indexes on category_id
 and is_active. Response time is now 180ms. Tested with production data."
```

### Communication Standards

#### When to Ask Questions
```
✅ Ask when:
- Business logic is unclear
- Multiple valid approaches exist
- Requirements are ambiguous
- You're about to make a major change
- Current phase constraints are uncertain

❌ Don't ask when:
- Tech stack choice (already established)
- Code style (follow ARCHITECTURE_RULES.md)
- Whether to support Arabic (always yes)
- Whether to deploy all components (always yes)
```

#### How to Ask Questions
```
✅ GOOD:
"Should wholesale clients see retail prices or only wholesale prices?"
"When stock reaches zero, should we hide the product or show 'out of stock'?"
"I found existing commission calculation in app/services/commission.py.
 Should I enhance it or create new logic?"

❌ BAD:
"What should I do about prices?"
"How do you want to handle stock?"
"Should I write commission code?"
```

#### When to Explain vs When to Just Do
```
Explain First:
- Major architectural decisions
- Performance optimizations
- Security implementations
- Database schema changes
- Breaking changes

Just Do (with brief note):
- Bug fixes
- Code formatting
- Adding missing validation
- Implementing clear requirements
- Following established patterns
```

### Decision-Making Authority

#### Claude CAN Decide:
```yaml
✅ Code Organization:
  - File structure within established patterns
  - Function decomposition
  - Variable naming (following conventions)

✅ Technical Implementation:
  - Which SQLAlchemy query pattern to use
  - Error handling approach
  - Validation logic implementation
  - API endpoint naming (following conventions)

✅ Code Quality:
  - Refactoring for readability
  - Adding type hints
  - Writing docstrings
  - Code comments
```

#### Claude MUST Ask:
```yaml
❓ Business Logic:
  - Pricing rules
  - Commission calculations
  - Credit limit policies
  - Order approval workflows

❓ User Experience:
  - What to show/hide based on user role
  - Workflow sequences
  - Error messages content
  - UI/UX decisions

❓ Architecture Changes:
  - New external dependencies
  - Database schema modifications
  - API contract changes
  - Authentication/authorization rules

❓ Deployment Timing:
  - When to push to production
  - Whether staging testing is sufficient
  - Rolling back if issues found
```

### Error Handling Behavior

#### When Encountering Errors:
```
1. Analyze immediately:
   - Read error message completely
   - Check stack trace
   - Review recent changes

2. Diagnose root cause:
   - Don't guess
   - Use logs and debugging
   - Understand the "why"

3. Explain findings:
   "The error is a foreign key constraint violation because we're
    trying to create an order for a customer_id that doesn't exist.
    Root cause: The customer was deleted but we didn't check before
    creating the order."

4. Propose solution:
   "I'll add a check to verify customer exists before order creation,
    and also add a soft-delete pattern for customers to prevent this."

5. Implement and verify:
   - Fix the issue
   - Add test to prevent recurrence
   - Verify fix works
```

#### Never Do When Errors Occur:
```
❌ Panic or give up: "I can't fix this"
❌ Random changes: "Let me try changing this..."
❌ Skip root cause: "I'll just catch the error"
❌ Ignore patterns: "This only happened once"
❌ Blame tools: "PostgreSQL is broken"
```

### Code Review Self-Checklist

Before saying "task complete", verify:

```yaml
✅ Functionality:
  - [ ] Feature works as specified
  - [ ] Handles edge cases
  - [ ] Error handling implemented
  - [ ] Input validation added

✅ Architecture Compliance:
  - [ ] Follows established patterns
  - [ ] Uses correct tech stack
  - [ ] Doesn't bypass TDS Core
  - [ ] Maintains separation of concerns

✅ Internationalization:
  - [ ] Arabic fields included (name_ar, description_ar)
  - [ ] RTL layout supported (if UI)
  - [ ] Arabic text displays correctly

✅ Security:
  - [ ] Authentication enforced
  - [ ] Authorization checked (RBAC)
  - [ ] Input validated
  - [ ] SQL injection prevented (using ORM)

✅ Performance:
  - [ ] Database queries optimized
  - [ ] Pagination for large datasets
  - [ ] Indexes used appropriately
  - [ ] Response time < 500ms for critical operations

✅ Code Quality:
  - [ ] Naming conventions followed
  - [ ] Type hints included (Python/TypeScript)
  - [ ] Docstrings written
  - [ ] Comments for complex logic
  - [ ] No duplicate code

✅ Testing:
  - [ ] Tested locally
  - [ ] Tested with Arabic text
  - [ ] Tested edge cases
  - [ ] Ready for staging

✅ Documentation:
  - [ ] API documented (OpenAPI)
  - [ ] Complex logic explained
  - [ ] Breaking changes noted
  - [ ] Update documentation if needed
```

### Proactive Behaviors

#### Always Do Proactively:
```
✅ Search existing code before creating new
   "Before creating new commission calculator, let me search
    for existing commission code..."

✅ Use todo lists for complex tasks
   "This feature has multiple steps. Let me create a todo list
    to track progress..."

✅ Verify deployment completeness
   "Before marking deployment done, let me verify:
    - Backend API health check
    - ERP Admin frontend loads
    - Consumer app loads
    - All URLs return 200"

✅ Check for similar patterns
   "I see we need a new product endpoint. Let me check how
    existing product endpoints are structured..."

✅ Consider scale and performance
   "This query returns all 2,218+ products. I should add
    pagination to handle the scale..."
```

#### Never Do Presumptuously:
```
❌ Change working code without asking
❌ Add features not requested
❌ Modify database schema unilaterally
❌ Deploy without testing
❌ Skip established workflows
❌ Make assumptions about business logic
```

### Integration-Specific Rules

#### TDS Core Integration:
```
ALWAYS:
✅ Access Zoho through TDS Core only
✅ Check TDS Dashboard for sync status
✅ Use TDS Core API endpoints
✅ Respect current migration phase

NEVER:
❌ Import Zoho SDK directly
❌ Make direct API calls to Zoho Books
❌ Make direct API calls to Zoho Inventory
❌ Bypass TDS Core for "quick fix"
```

#### Database Operations:
```
ALWAYS:
✅ Use SQLAlchemy ORM
✅ Write migrations for schema changes
✅ Index foreign keys and frequent WHERE clauses
✅ Use transactions for multi-step operations

NEVER:
❌ Write raw SQL strings (SQL injection risk)
❌ Modify database directly without migrations
❌ Forget to index high-traffic queries
❌ Commit half-finished transactions
```

### Success Indicators

Claude is performing well when:

```
✅ Khaleel doesn't have to repeat context
✅ Features work correctly first time
✅ Deployments are complete and smooth
✅ Code is maintainable and well-documented
✅ Arabic support is never forgotten
✅ Questions are relevant and well-timed
✅ Errors are caught and explained clearly
✅ Performance is considered proactively
✅ Security is built in, not bolted on
✅ Khaleel feels productive and confident
```

### Warning Signs

Adjust behavior if:

```
⚠️ Khaleel repeatedly corrects same mistake
⚠️ Features require multiple iterations
⚠️ Deployments are incomplete or fail
⚠️ Code doesn't follow established patterns
⚠️ Arabic support is forgotten
⚠️ Questions are too vague or too frequent
⚠️ Errors are dismissed without understanding
⚠️ Performance degrades after changes
⚠️ Security issues are discovered later
⚠️ Khaleel seems frustrated or confused
```

---

## 📚 Additional Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Flutter: https://flutter.dev/docs
- PostgreSQL: https://www.postgresql.org/docs/
- React: https://react.dev/

### Internal Docs
- PROJECT_VISION.md - Business context
- WORKING_TOGETHER.md - Collaboration guide
- STAGING_TO_PRODUCTION_WORKFLOW.md - Deployment process
- COMPLETE_PROJECT_DEPLOYMENT_RULES.md - Deployment rules

---

**Remember:** These rules exist to maintain consistency, security, and quality across the TSH ERP ecosystem. Follow them religiously!
