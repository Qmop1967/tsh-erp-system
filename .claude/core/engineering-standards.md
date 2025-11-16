# TSH Global Engineering Standards

**Version:** 1.1
**Purpose:** Global engineering standards for all TSH ERP Ecosystem development
**Last Updated:** 2025-11-14
**Load via:** @docs/core/engineering-standards.md

**Scope:** Backend • Frontend • Mobile • Infrastructure • Data • Security • DevOps

---

## 🎯 1. Purpose

This document defines the **global engineering standards** for all developers working on the TSH ERP Ecosystem, covering backend, frontend, mobile, infrastructure, data logic, and operational guidelines.

### Goals

The goal is to guarantee:

```yaml
✅ Consistency - Uniform patterns across all components
✅ Scalability - Handle 500+ clients, 2,218+ products efficiently
✅ Maintainability - Code that can be understood and modified
✅ Security - Protection of sensitive data and operations
✅ Predictability - Reliable behavior across environments
✅ Cross-environment stability - Dev, Staging, Production parity
```

**These standards apply to:**
- All human developers
- All AI-assisted engineers (Claude Code)
- All contractors and partners
- All code contributions

---

## 🏗️ 2. System Architecture Standards

### 2.1 Architecture Philosophy

The TSH ERP Ecosystem follows:

```yaml
Principles:
  - Modular domain-driven design
  - Unified PostgreSQL cluster for core data
  - Dedicated BFF layer for each app family
  - Event-driven asynchronous workflows where necessary
  - Strict API contracts using DTOs
  - High observability and unified logging standards
  - Hybrid authorization model integrated at every layer

Philosophy:
  "Build for scale from day one, optimize for clarity always."
```

### 2.2 Core Components

```yaml
Backend:
  - TDS Core (FastAPI Backend)
  - TDS Sync Services (Zoho Integration + Event Logic)

Frontend:
  - TSH Web Applications (React/Next.js)
  - TSH Mobile Applications (Flutter)

Data Layer:
  - PostgreSQL 15+ (Primary database)
  - Redis (Caching + distributed locks)
  - Event Bus (optional, future)

Infrastructure:
  - Nginx (Reverse proxy)
  - Docker Images for deployment
  - GitHub Actions (CI/CD)

Integration:
  - TDS Core orchestrates ALL Zoho operations
  - TSH NeuroLink for ALL communications
```

**Reference:** @docs/core/architecture.md for detailed component interactions

---

## 🔐 3. Authorization & Access Control Standards

### 3.1 Hybrid Authorization Model

**CRITICAL:** TSH ERP implements a **combined authorization framework** using **ALL THREE layers**:

#### Layer 1: RBAC — Role-Based Access Control

```yaml
Controls:
  - High-level access
  - User roles
  - Application-level privileges

Roles:
  - Admin (full system access)
  - Accountant (financial operations)
  - Sales Representative (client management, orders)
  - Warehouse Manager (inventory operations)
  - Travel Salesperson (field operations)
  - Retail Staff (POS operations)

Implementation:
  - FastAPI dependency: require_role(["admin", "manager"])
  - Check user.role.name against allowed roles
  - Decorator: @require_role(["admin"])
```

#### Layer 2: ABAC — Attribute-Based Access Control

```yaml
Controls:
  - Contextual access rules
  - Dynamic policies based on user, resource, action, environment

Attributes:
  User:
    - role
    - assigned_warehouse_id
    - assigned_province
    - work_hours

  Resource:
    - owner_id
    - warehouse_id
    - province
    - sensitivity_level

  Environment:
    - time_of_day
    - location
    - device_type

Examples:
  ✅ "Sales rep can access only customers in the same province"
  ✅ "Warehouse user can update items only in their assigned warehouse"
  ✅ "Retail staff can access POS only during work hours"
  ✅ "Travel salesperson can create orders only for assigned clients"

Implementation:
  - FastAPI dependency: check_abac_permission("orders.read")
  - Policy engine evaluates context
  - Dynamic rule evaluation
```

#### Layer 3: RLS — Row-Level Security (PostgreSQL)

```yaml
Controls:
  - Data visibility at row level within tables
  - Enforced directly inside PostgreSQL
  - Final enforcement layer

Examples:
  ✅ Filter sales orders by assigned sales_rep_id
  ✅ Filter inventory entries by warehouse scope
  ✅ Restrict financial data by accounting permissions
  ✅ Limit client visibility by territory

Implementation:
  - PostgreSQL policies: ALTER TABLE ... ENABLE ROW LEVEL SECURITY
  - Policy creation: CREATE POLICY ... USING (condition)
  - Applied automatically on all queries
  - Cannot be bypassed by application code
```

### 3.2 Authorization Stack (Layered Enforcement)

Authorization must work in **layers** (defense in depth):

```
Request → API Gateway → FastAPI Router → Service Layer → Repository → Database
            ↓              ↓                 ↓               ↓           ↓
         JWT Auth       RBAC            ABAC          Data Filter     RLS
```

**All layers MUST be present:**

```python
# ✅ CORRECT: All three layers present
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role(["admin", "sales"])),      # RBAC
    abac: User = Depends(check_abac_permission("orders.read")), # ABAC
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS filters applied
    return await service.get_orders()

# ❌ WRONG: Missing layers (Security Violation!)
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()  # Missing all 3 layers!
```

### 3.3 Enforcement Points

Authorization must be applied at:

```yaml
1. API Gateway:
   - JWT validation
   - Initial authentication check

2. FastAPI Service Layer:
   - RBAC role validation
   - ABAC policy evaluation

3. Repository Layer:
   - Data filtering based on user context
   - Prepare queries for RLS

4. Database Level:
   - PostgreSQL RLS policies
   - Final enforcement (cannot bypass)

No bypass of any layer is allowed.
```

**Reference:** @docs/AUTHORIZATION_FRAMEWORK.md for complete implementation guide

---

## 🌐 4. API Standards

### 4.1 Naming Convention

Endpoints follow **consistent pattern**:

```
/api/v1/{module}/{resource}/{action}
```

**Examples:**

```yaml
Inventory Module:
  - GET  /api/v1/inventory/products/list
  - POST /api/v1/inventory/products/create
  - GET  /api/v1/inventory/products/{id}
  - PATCH /api/v1/inventory/products/{id}

Sales Module:
  - POST /api/v1/sales/orders/create
  - GET  /api/v1/sales/orders/{id}
  - GET  /api/v1/sales/clients/list

Accounting Module:
  - GET  /api/v1/accounting/invoices/{id}
  - POST /api/v1/accounting/payments/create
```

**Rules:**
- Use plural nouns for resources (`products`, not `product`)
- Use verbs for actions (`create`, `list`, not `new`, `all`)
- Always include version (`v1`)
- Keep module names consistent

### 4.2 Response Structure (Standardized)

**All API responses must follow:**

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "message_ar": "تمت العملية بنجاح",
  "data": {
    "id": 123,
    "name": "Product Name",
    "name_ar": "اسم المنتج"
  },
  "error_code": null,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error response:**

```json
{
  "success": false,
  "message": "Product not found",
  "message_ar": "المنتج غير موجود",
  "data": null,
  "error_code": "PRODUCT_NOT_FOUND",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Pagination response:**

```json
{
  "success": true,
  "message": "Products retrieved successfully",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 100,
      "total_items": 2218,
      "total_pages": 23,
      "has_next": true,
      "has_previous": false
    }
  },
  "error_code": null,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

### 4.3 DTO Standards (Type Safety)

**All requests must use Pydantic DTOs:**

```python
# ✅ CORRECT: Pydantic DTO
from pydantic import BaseModel, Field

class ProductCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_ar: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    unit_price: float = Field(..., ge=0)
    cost_price: float = Field(..., ge=0)

@router.post("/products")
async def create_product(data: ProductCreateDTO):
    # Validation automatic, type-safe
    pass

# ❌ WRONG: Raw dict inputs
@router.post("/products")
async def create_product(data: dict):  # No validation!
    pass
```

**Rules:**
- No raw `dict` inputs
- No implicit typing
- All fields must have validation rules
- Use `Field()` for constraints
- Provide examples in schema

### 4.4 API Security

**Every API endpoint must implement:**

```yaml
1. JWT Authentication:
   - Token validation
   - Expiration check
   - User identification

2. Hybrid Authorization:
   - RBAC role check
   - ABAC policy evaluation
   - RLS database filtering

3. Input Validation:
   - Pydantic schemas
   - SQL injection prevention
   - XSS prevention

4. Rate Limiting:
   - Per-user limits
   - Per-endpoint limits
   - DDoS protection

No endpoint bypasses permission checks.
```

**Reference:** @docs/reference/code-templates/authentication.md

---

## 🗄️ 5. Database Standards

### 5.1 Principles

The database must use:

```yaml
Core:
  - PostgreSQL 15+
  - UTF-8 encoding
  - Timezone-aware timestamps

Design:
  - UUID primary keys (for distributed systems)
  - Soft delete (is_deleted, deleted_at)
  - Audit columns (created_at, updated_at, created_by_id)
  - Foreign key constraints (enforce relationships)
  - No orphaned data (cascading rules)
  - Proper indexing and normalization

Performance:
  - Indexes on all foreign keys
  - Indexes on search fields (name, sku, phone)
  - Indexes on filter fields (is_active, status)
  - Compound indexes where appropriate
```

### 5.2 Naming Conventions

```yaml
Tables:
  - snake_case plural
  - Examples: products, sales_orders, warehouse_items

Columns:
  - snake_case
  - Examples: product_name, unit_price, created_at

Foreign Keys:
  - {entity}_id
  - Examples: category_id, client_id, warehouse_id

Indexes:
  - idx_{table}_{columns}
  - Examples: idx_products_sku, idx_orders_client_id

Constraints:
  - ck_{table}_{constraint}
  - Examples: ck_products_price_positive

Policies (RLS):
  - {table}_{action}_policy
  - Examples: orders_select_policy, products_update_policy
```

### 5.3 RLS Implementation (Row-Level Security)

**RLS must:**

```yaml
Requirements:
  ✅ Be enabled for all sensitive modules
  ✅ Be tested using integration tests
  ✅ Use policies tied to user attributes and roles
  ✅ Never rely solely on backend filters

Examples:
  - Sales orders filtered by sales_rep_id
  - Inventory filtered by warehouse_id
  - Clients filtered by assigned territory
  - Financial data filtered by accounting permissions
```

**RLS Implementation Pattern:**

```sql
-- Enable RLS on table
ALTER TABLE sales_orders ENABLE ROW LEVEL SECURITY;

-- Create policy for SELECT
CREATE POLICY orders_select_policy ON sales_orders
FOR SELECT
USING (
  -- Admin sees all
  (current_setting('app.user_role') = 'admin')
  OR
  -- Sales rep sees only their orders
  (sales_rep_id = current_setting('app.user_id')::int)
);

-- Create policy for INSERT
CREATE POLICY orders_insert_policy ON sales_orders
FOR INSERT
WITH CHECK (
  -- Can only create orders for themselves
  sales_rep_id = current_setting('app.user_id')::int
);
```

**Application Code:**

```python
# Set RLS context before queries
db.execute(text("SET app.user_id = :user_id"), {"user_id": current_user.id})
db.execute(text("SET app.user_role = :role"), {"role": current_user.role.name})

# Queries automatically filtered by RLS
orders = db.query(Order).all()  # RLS policy applies
```

### 5.4 Data Integrity

**Requires:**

```yaml
Constraints:
  ✅ UNIQUE constraints (email, sku, phone)
  ✅ CHECK constraints (price > 0, quantity >= 0)
  ✅ NOT NULL constraints (required fields)
  ✅ Foreign key rules (ON DELETE CASCADE/RESTRICT)

Validation:
  ✅ Application-level validation (Pydantic)
  ✅ Database-level validation (constraints)
  ✅ Business logic validation (service layer)

Anti-Patterns:
  ❌ No soft-registry hacks
  ❌ No dangling foreign keys
  ❌ No implicit assumptions
  ❌ No unvalidated data
```

**Reference:** @docs/reference/code-templates/database-optimization.md

---

## 💻 6. Coding Standards

### 6.1 Backend (FastAPI)

```yaml
Style:
  - PEP8 enforced (flake8, black)
  - Type hints required (mypy)
  - Docstrings required (Google style)

Architecture:
  - Business logic in services only
  - Repositories handle DB operations
  - No logic inside routers (thin controllers)
  - DTOs for all inputs/outputs
  - All exceptions must be centralized

Structure:
  app/
    ├── routers/       # API endpoints (thin)
    ├── services/      # Business logic
    ├── repositories/  # Database operations
    ├── models/        # SQLAlchemy models
    ├── schemas/       # Pydantic DTOs
    ├── dependencies/  # FastAPI dependencies
    └── utils/         # Helper functions
```

**Example:**

```python
# ✅ CORRECT: Separation of concerns
# router (thin)
@router.post("/products", response_model=ProductResponse)
async def create_product(
    data: ProductCreateDTO,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProductService(db, user)
    return await service.create_product(data)

# service (business logic)
class ProductService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.repo = ProductRepository(db)

    async def create_product(self, data: ProductCreateDTO) -> Product:
        # Validate business rules
        if await self.repo.sku_exists(data.sku):
            raise BusinessLogicError("SKU already exists")

        # Create product
        product = Product(**data.dict(), created_by_id=self.user.id)
        return await self.repo.create(product)

# repository (database)
class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
```

### 6.2 Frontend (React/Next.js)

```yaml
Style:
  - Functional components only (no class components)
  - Hooks for logic (useState, useEffect, custom hooks)
  - Atomic UI design (components, molecules, organisms)
  - Strict dependency control (package.json)

Architecture:
  - No direct backend calls — BFF only
  - State management (Context API or Zustand)
  - Type safety (TypeScript required)
  - Error boundaries for graceful failures

Structure:
  src/
    ├── components/    # Reusable UI components
    ├── pages/         # Next.js pages
    ├── hooks/         # Custom React hooks
    ├── services/      # API client (BFF)
    ├── types/         # TypeScript types
    └── utils/         # Helper functions
```

### 6.3 Mobile (Flutter)

```yaml
Architecture:
  - MVVM/Clean Architecture
  - Network layer separated (Dio client)
  - Typed models (Freezed/json_serializable)
  - Offline-first support (local storage)
  - Consistent error handling

Structure:
  lib/
    ├── presentation/  # UI (screens, widgets)
    ├── business/      # ViewModels, BLoC
    ├── data/          # Repositories, data sources
    ├── domain/        # Entities, use cases
    └── core/          # Constants, utilities

RTL Support:
  - Always use Directionality widget
  - Test with Arabic language
  - Proper text alignment
```

**Reference:** @docs/core/architecture.md for component patterns

---

## 🔀 7. Version Control Standards (Git)

### 7.1 Branching Model (GitFlow)

```yaml
Branches:
  main:
    - Production code only
    - Protected branch
    - Requires PR approval

  develop:
    - Staging code
    - Integration branch
    - Auto-deploys to staging

  feature/*:
    - New features
    - Branch from develop
    - Merge back to develop

  bugfix/*:
    - Bug fixes
    - Branch from develop
    - Merge back to develop

  release/*:
    - Release preparation
    - Branch from develop
    - Merge to main + develop

  hotfix/*:
    - Emergency fixes
    - Branch from main
    - Merge to main + develop
```

### 7.2 Commit Standards (Conventional Commits)

```yaml
Format:
  <type>(<scope>): <description>

  [optional body]

  [optional footer]

Types:
  feat:     New feature
  fix:      Bug fix
  refactor: Code refactoring
  perf:     Performance improvement
  test:     Add/update tests
  docs:     Documentation
  style:    Code style (formatting)
  chore:    Maintenance tasks

Examples:
  feat(inventory): implement product sync with Zoho
  fix(sales): correct tax calculation for IQD currency
  refactor(auth): update RLS policy handlers
  perf(db): add indexes on frequently queried columns
  test(orders): add integration tests for order creation
  docs(api): update authentication endpoint documentation
```

**Reference:** @docs/core/workflows.md for git workflows

---

## 🚀 8. CI/CD Standards

### 8.1 Pipeline Requirements

**Every deployment must run:**

```yaml
1. Linting:
   - Python: flake8, black, isort
   - JavaScript: ESLint, Prettier
   - Flutter: dart format, flutter analyze

2. Unit Tests:
   - Backend: pytest (70%+ coverage)
   - Frontend: Jest (60%+ coverage)
   - Mobile: Flutter test (60%+ coverage)

3. Integration Tests:
   - API integration tests
   - Database integration tests
   - Authorization tests (RBAC, ABAC, RLS)

4. Security Scanning:
   - Python: Bandit, Safety
   - Docker: Trivy
   - Dependencies: Snyk

5. Build Artifacts:
   - Docker images
   - Static assets
   - Mobile APK/IPA

6. Push Docker Images:
   - GitHub Container Registry (GHCR)
   - Tagged with version + commit SHA

7. Deploy:
   - Auto-deploy to Dev/Staging
   - Manual approval for Production
```

### 8.2 GitHub Actions Workflows

```yaml
Workflow Files:
  .github/workflows/
    ├── ci-backend.yml       # Backend CI
    ├── ci-frontend.yml      # Frontend CI
    ├── ci-mobile.yml        # Mobile CI
    ├── deploy-staging.yml   # Deploy to staging
    ├── deploy-production.yml # Deploy to production

Secrets Required:
  - GHCR_TOKEN             # GitHub Container Registry
  - PRODUCTION_SSH_KEY     # Production server SSH
  - STAGING_SSH_KEY        # Staging server SSH
  - DATABASE_URL           # Database connection
  - SECRET_KEY             # Application secret
  - ZOHO_CLIENT_ID         # Zoho API credentials
  - ZOHO_CLIENT_SECRET
```

**Reference:** @docs/DEPLOYMENT_GUIDE.md

---

## 🐳 9. Docker Standards

### 9.1 Compose Structure

**Three environment files:**

```yaml
Files:
  - docker-compose.dev.yml      # Local development
  - docker-compose.staging.yml  # Staging environment
  - docker-compose.prod.yml     # Production environment

Structure:
  services:
    backend:
      build: ./backend
      env_file: .env.production
      depends_on: [postgres, redis]

    postgres:
      image: postgres:15-alpine
      volumes: [postgres_data:/var/lib/postgresql/data]

    redis:
      image: redis:7-alpine

    nginx:
      image: nginx:alpine
      depends_on: [backend]
```

### 9.2 Dockerfile Rules

```yaml
Requirements:
  ✅ No secrets in Dockerfile
  ✅ Slim base images only (alpine preferred)
  ✅ Multi-stage builds (separate build + runtime)
  ✅ Clean, reproducible images
  ✅ Minimize layers
  ✅ Use .dockerignore

Example:
  # ✅ CORRECT: Multi-stage build
  FROM python:3.11-alpine AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --user -r requirements.txt

  FROM python:3.11-alpine
  WORKDIR /app
  COPY --from=builder /root/.local /root/.local
  COPY . .
  ENV PATH=/root/.local/bin:$PATH
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## 🔒 10. Security Standards

### 10.1 Principles

```yaml
Core Principles:
  - Least privilege (minimum necessary access)
  - Defense in depth (multiple security layers)
  - Zero trust (verify everything)
  - Encryption in transit (HTTPS everywhere)
  - Encryption at rest (database encryption)
  - Strict role/permission separation
  - No PII logging (protect privacy)
  - Token rotation (security best practice)
```

### 10.2 Hybrid Authorization

**Enforced via:**

```yaml
1. Backend Policies:
   - RBAC role checks (FastAPI dependencies)
   - ABAC policy evaluation (context-aware)

2. Database RLS:
   - PostgreSQL row-level security
   - Cannot be bypassed by application

3. BFF Filtering:
   - UI-level data filtering
   - Additional protection layer
```

### 10.3 Secrets Management

```yaml
Storage:
  - Encrypted GitHub Secrets (CI/CD)
  - Environment variables (.env files)
  - AWS Secrets Manager (future)

Rules:
  ❌ Zero secret exposure in code
  ❌ No secrets in git history
  ❌ No secrets in Docker images
  ❌ No secrets in logs

Access:
  - Rotate regularly (90 days)
  - Audit access logs
  - Principle of least privilege
```

### 10.4 Common Vulnerabilities (Prevent)

```yaml
OWASP Top 10:
  ✅ SQL Injection → Use parameterized queries
  ✅ XSS → Sanitize user input
  ✅ Authentication Bypass → JWT validation
  ✅ Authorization Bypass → Hybrid auth model
  ✅ Sensitive Data Exposure → Encryption + RLS
  ✅ Security Misconfiguration → Secure defaults
  ✅ CSRF → CSRF tokens required
  ✅ Insecure Deserialization → Validate inputs
  ✅ Insufficient Logging → Structured logging
  ✅ API Rate Limiting → Throttle requests
```

**Reference:** @docs/reference/ai-guidelines/ai-monitoring.md

---

## 📊 11. Observability Standards

### 11.1 Logging

```yaml
Format:
  - JSON logs (structured)
  - ISO8601 timestamps
  - Trace ID per request
  - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Content:
  ✅ Request/response details
  ✅ User ID (hashed if PII)
  ✅ Error stack traces
  ✅ Performance metrics

  ❌ No passwords
  ❌ No API keys
  ❌ No credit cards
  ❌ No PII (unless hashed)

Centralization:
  - Centralized logging server
  - Log retention policy (90 days)
  - Full-text search capability
```

**Log Format:**

```json
{
  "timestamp": "2025-11-14T10:30:00Z",
  "level": "INFO",
  "trace_id": "abc123xyz",
  "user_id": 42,
  "endpoint": "/api/v1/products/list",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 145,
  "message": "Products retrieved successfully"
}
```

### 11.2 Monitoring

```yaml
Tools:
  - Grafana (dashboards)
  - Prometheus (metrics)
  - Uptime monitoring (health checks)

Metrics:
  - API response times (p50, p95, p99)
  - Error rates (4xx, 5xx)
  - Database query times
  - Active users
  - Resource usage (CPU, memory, disk)

Health Endpoints:
  - /health (basic check)
  - /health/detailed (component status)
  - /metrics (Prometheus metrics)

Alerts:
  - API response time > 2 seconds
  - Error rate > 5%
  - Database connection failures
  - Disk usage > 80%
  - Memory usage > 90%
```

### 11.3 Error Tracking

```yaml
Tool:
  - Sentry (or similar)

Coverage:
  - Backend (FastAPI)
  - Frontend (React)
  - Mobile (Flutter)

Features:
  - Real-time error notifications
  - Error grouping and deduplication
  - Stack traces
  - User context (non-PII)
  - Release tracking
```

---

## 📚 12. Documentation Standards

### 12.1 Required Documents

**Every repository must have:**

```yaml
Root Level:
  - README.md              # Project overview
  - CHANGELOG.md           # Version history
  - LICENSE.md             # License information

Architecture:
  - ARCHITECTURE.md        # System architecture
  - API_REFERENCE.md       # API documentation
  - DATABASE_SCHEMA.md     # Database structure
  - AUTHORIZATION_MODEL.md # Auth framework

Operations:
  - DEPLOYMENT.md          # Deployment procedures
  - MONITORING.md          # Monitoring setup
  - TROUBLESHOOTING.md     # Common issues

Decision Logs:
  - DECISIONS.md           # Architecture decisions
  - SESSION_STATE.md       # Current project state
```

### 12.2 Documentation Location

```
Internal Documentation:
  /TSH/PORTAL/ENGINEERING/
    ├── standards/
    ├── architecture/
    ├── decisions/
    └── procedures/

Code Documentation:
  - In-code comments (why, not what)
  - Docstrings (all public functions)
  - API documentation (auto-generated)
```

### 12.3 Documentation Quality

```yaml
Requirements:
  ✅ Up-to-date (review quarterly)
  ✅ Accurate (no outdated info)
  ✅ Complete (cover all features)
  ✅ Clear (understandable by new team members)
  ✅ Examples (code samples included)
  ✅ Diagrams (architecture visualizations)

Format:
  - Markdown preferred
  - Mermaid for diagrams
  - OpenAPI for API docs
  - ERD for database schema
```

---

## 🧪 13. Testing Standards

### 13.1 Test Coverage Requirements

```yaml
Backend (FastAPI):
  - Unit tests: 70%+ coverage
  - Services layer: 90%+ coverage
  - Critical business logic: 100% coverage
  - Integration tests: All major flows
  - Authorization tests: RBAC, ABAC, RLS

Frontend (React):
  - Component tests: 60%+ coverage
  - Critical user flows: 80%+ coverage
  - Integration tests: Major features

Mobile (Flutter):
  - Widget tests: 60%+ coverage
  - Integration tests: Critical flows
  - Golden tests: UI consistency
```

### 13.2 Test Types

```yaml
Unit Tests:
  - Services
  - Utilities
  - Repositories
  - Business logic

Integration Tests:
  - API endpoints
  - Database operations
  - Authorization flow
  - Third-party integrations

E2E Tests:
  - Complete user flows
  - Critical business processes
  - Cross-component interactions

Load Tests:
  - Heavy operations (reports, exports)
  - Concurrent user scenarios
  - Database stress testing
```

### 13.3 Authorization Testing

**CRITICAL:** Must test all 3 layers:

```python
# Test RBAC
def test_admin_can_delete_product():
    user = create_user(role="admin")
    response = client.delete("/api/v1/products/123", auth=user)
    assert response.status_code == 204

def test_sales_cannot_delete_product():
    user = create_user(role="sales")
    response = client.delete("/api/v1/products/123", auth=user)
    assert response.status_code == 403

# Test ABAC
def test_warehouse_user_can_only_update_their_warehouse():
    user = create_user(role="warehouse", assigned_warehouse_id=1)
    response = client.patch("/api/v1/inventory/items/123",
                           json={"quantity": 100},
                           auth=user)
    assert response.status_code == 200

# Test RLS
def test_sales_rep_sees_only_their_orders():
    user = create_user(role="sales", id=42)
    response = client.get("/api/v1/orders", auth=user)
    orders = response.json()["data"]["items"]
    assert all(order["sales_rep_id"] == 42 for order in orders)
```

**Reference:** @docs/reference/code-templates/testing.md

---

## 🚢 14. Release Management

### 14.1 Semantic Versioning

```yaml
Format: MAJOR.MINOR.PATCH

MAJOR: Breaking changes
  - API contract changes
  - Database schema changes
  - Configuration changes

MINOR: New features (backward compatible)
  - New endpoints
  - New features
  - Performance improvements

PATCH: Bug fixes (backward compatible)
  - Bug fixes
  - Security patches
  - Minor improvements

Examples:
  1.0.0 → Initial release
  1.1.0 → Added product sync feature
  1.1.1 → Fixed tax calculation bug
  2.0.0 → New API authentication system
```

### 14.2 Release Checklist

**Each release must include:**

```yaml
Documentation:
  - CHANGELOG.md updated
  - Version bumped in package files
  - Release notes prepared

Content:
  - Summary (1-2 paragraphs)
  - Features (list of new features)
  - Fixes (list of bug fixes)
  - Breaking changes (if any)
  - Migration notes (if needed)
  - Known issues (if any)

Verification:
  - All tests passing
  - Security scan passed
  - Staging deployment successful
  - User acceptance testing done
  - Performance benchmarks met

Deployment:
  - Backup created
  - Rollback plan ready
  - Monitoring alerts configured
  - Deployment scheduled (off-peak hours)
```

### 14.3 Release Communication

```yaml
Stakeholders to Notify:
  - Development team
  - Operations team
  - QA team
  - User (Khaleel)
  - End users (if public-facing changes)

Channels:
  - Email notification
  - Slack/Teams announcement
  - Release notes published
  - User documentation updated
```

---

## ⚡ 15. Performance Standards

### 15.1 Response Time Targets

```yaml
API Endpoints:
  - 90% of requests: < 150ms
  - 95% of requests: < 300ms
  - 99% of requests: < 1000ms
  - Maximum acceptable: 2000ms

Database Queries:
  - Simple queries: < 50ms
  - Complex queries: < 200ms
  - Report queries: < 2000ms

Page Load (Frontend):
  - First Contentful Paint: < 1.5s
  - Time to Interactive: < 3s
  - Largest Contentful Paint: < 2.5s
```

### 15.2 Performance Optimization

```yaml
Backend:
  ✅ Redis caching for heavy operations
  ✅ No N+1 database queries (use joinedload)
  ✅ Database query optimization (indexes)
  ✅ Connection pooling
  ✅ Async I/O where beneficial

Frontend:
  ✅ Code splitting (lazy loading)
  ✅ Image optimization (compression, CDN)
  ✅ Minimize bundle size
  ✅ Server-side rendering (Next.js)
  ✅ Caching strategies

Database:
  ✅ Proper indexing strategy
  ✅ RLS policies optimized
  ✅ Query plan analysis (EXPLAIN ANALYZE)
  ✅ Vacuuming and maintenance
  ✅ Connection limits configured
```

### 15.3 Scale Targets

```yaml
Current Scale (Must Handle):
  - 500+ wholesale clients
  - 2,218+ active products
  - 30+ daily orders
  - 100+ concurrent users
  - 12 travel salespersons (field operations)

Future Scale (Prepare For):
  - 1,000 clients
  - 5,000 products
  - 100+ daily orders
  - 500 concurrent users
```

---

## 📋 16. Compliance & Auditing

### 16.1 Audit Logs (Mandatory)

**Must log:**

```yaml
Security Events:
  - User login/logout
  - Authentication failures
  - Authorization denials
  - Password changes
  - Role changes

Financial Operations:
  - Invoice creation
  - Payment processing
  - Credit limit changes
  - Price modifications
  - Discount applications

Inventory Operations:
  - Stock movements
  - Product creation/deletion
  - Warehouse transfers
  - Stock adjustments

Customer Data:
  - Client creation/modification
  - Address changes
  - Credit limit updates
  - Customer assignments

System Operations:
  - Zoho sync operations
  - Database migrations
  - Configuration changes
  - Deployments
```

### 16.2 Audit Log Format

```json
{
  "timestamp": "2025-11-14T10:30:00Z",
  "event_type": "ORDER_CREATED",
  "user_id": 42,
  "user_email": "sales@tsh.sale",
  "user_role": "sales_rep",
  "resource_type": "order",
  "resource_id": 12345,
  "action": "CREATE",
  "changes": {
    "before": null,
    "after": {
      "client_id": 789,
      "total_amount": 15000.00,
      "status": "pending"
    }
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### 16.3 Retention Policies

```yaml
Logs:
  - Application logs: 90 days
  - Audit logs: 7 years (regulatory)
  - Error logs: 1 year
  - Access logs: 180 days

Backups:
  - Daily backups: 30 days
  - Weekly backups: 12 weeks
  - Monthly backups: 12 months
  - Yearly backups: 7 years

Data:
  - Active records: Indefinite
  - Soft-deleted records: 2 years
  - Archived records: 7 years (regulatory)
```

### 16.4 Compliance Requirements

```yaml
Privacy:
  - GDPR-style data protection (best practice)
  - Right to access (user can request their data)
  - Right to deletion (soft delete with retention)
  - Data encryption (in transit and at rest)

Security:
  - Regular security audits
  - Penetration testing (annual)
  - Vulnerability scanning (continuous)
  - Security training (team members)

Auditability:
  - Complete audit trail
  - Tamper-proof logs
  - Regular compliance reviews
  - Documentation maintenance
```

---

## ✅ Standards Compliance Checklist

**Before deploying ANY code, verify:**

```yaml
Architecture:
  □ Follows modular domain-driven design
  □ Uses correct component (TDS Core for Zoho, etc.)
  □ Implements hybrid authorization (RBAC + ABAC + RLS)

API:
  □ Follows naming convention (/api/v1/module/resource/action)
  □ Uses standardized response structure
  □ Implements Pydantic DTOs
  □ Has proper authentication and authorization

Database:
  □ Follows naming conventions (snake_case)
  □ Has proper indexes
  □ Implements RLS policies
  □ Has audit columns (created_at, updated_at)
  □ Uses soft delete (is_deleted)

Code Quality:
  □ Passes linting (PEP8/ESLint)
  □ Has type hints (Python/TypeScript)
  □ Includes docstrings/comments
  □ Follows separation of concerns
  □ Has unit tests (70%+ coverage)
  □ Has integration tests

Security:
  □ No secrets in code
  □ Input validation implemented
  □ Authorization enforced at all layers
  □ No SQL injection vulnerabilities
  □ No XSS vulnerabilities

Documentation:
  □ README updated
  □ API docs updated
  □ CHANGELOG updated
  □ Migration notes (if needed)

Testing:
  □ Unit tests passing
  □ Integration tests passing
  □ Authorization tests passing
  □ Load tests passing (if heavy operation)

Deployment:
  □ Staging tested
  □ Performance verified
  □ Monitoring configured
  □ Rollback plan ready
```

---

## 🎓 For AI-Assisted Engineers (Claude Code)

**When working on TSH ERP:**

```yaml
Always Reference:
  - @docs/core/engineering-standards.md (this file)
  - @docs/core/architecture.md (system architecture)
  - @docs/core/project-context.md (business context)
  - @docs/AUTHORIZATION_FRAMEWORK.md (security)

Never Violate:
  - Hybrid authorization (RBAC + ABAC + RLS)
  - API standards (naming, response structure)
  - Database standards (RLS, indexing, constraints)
  - Security standards (no bypasses)
  - Documentation requirements

Always Include:
  - Type hints (Python) / TypeScript types
  - Input validation (Pydantic DTOs)
  - Error handling (try/except, error boundaries)
  - Authorization checks (all 3 layers)
  - Tests (unit + integration)
  - Documentation updates

Ask User If:
  - Unsure about business logic
  - Multiple valid technical approaches
  - Breaking changes needed
  - Security implications unclear
```

---

## 📞 Enforcement & Review

```yaml
Code Review:
  - All PRs require review
  - Standards compliance checked
  - Security review for sensitive changes
  - Performance review for heavy operations

Automated Checks:
  - Linting (GitHub Actions)
  - Testing (CI/CD pipeline)
  - Security scanning (Bandit, Trivy)
  - Coverage reports

Periodic Review:
  - Standards review: Quarterly
  - Documentation audit: Monthly
  - Security audit: Annual
  - Performance audit: Semi-annual
```

---

**Version History:**
- v1.1 (2025-11-14): Integrated into Claude Code configuration
- v1.0 (2025-11-12): Initial version by senior software engineer

**Related Documentation:**
- @docs/core/architecture.md - System architecture patterns
- @docs/core/project-context.md - Business context and scale
- @docs/AUTHORIZATION_FRAMEWORK.md - Complete authorization guide
- @docs/reference/code-templates/ - Implementation templates
- @docs/core/workflows.md - Development workflows
