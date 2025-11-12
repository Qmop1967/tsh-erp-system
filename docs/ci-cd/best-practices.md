# CI/CD Best Practices for TSH ERP

Guidelines and best practices for maintaining a healthy CI/CD pipeline.

## Table of Contents

- [Git Workflow](#git-workflow)
- [Testing Strategy](#testing-strategy)
- [Code Quality](#code-quality)
- [Security](#security)
- [Docker & Containers](#docker--containers)
- [Deployment](#deployment)
- [Performance](#performance)
- [Monitoring & Alerts](#monitoring--alerts)
- [Documentation](#documentation)

## Git Workflow

### Branching Strategy

Follow GitFlow strictly:

```
main (production-ready)
  └── develop (integration branch)
       ├── feature/* (new features)
       ├── bugfix/* (non-urgent fixes)
       ├── hotfix/* (urgent production fixes)
       └── release/* (release preparation)
```

#### Branch Naming

```bash
# Features
feature/user-authentication
feature/inventory-sync
feature/JIRA-123-add-reports

# Bug fixes
bugfix/fix-product-calculation
bugfix/JIRA-456-login-redirect

# Hotfixes
hotfix/critical-security-patch
hotfix/database-connection-fix

# Releases
release/v1.2.0
release/2025-Q1
```

### Commit Messages

Follow Conventional Commits:

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Formatting, missing semi colons, etc
refactor: Code change that neither fixes a bug nor adds a feature
perf:     Performance improvement
test:     Adding missing tests
chore:    Updating build tasks, package manager configs, etc
ci:       CI/CD changes

# Examples
feat(auth): add JWT token refresh mechanism

Implements automatic token refresh when access token expires.
Users will no longer need to re-login after token expiration.

Closes #123

---

fix(inventory): correct stock calculation for bundled products

The previous implementation didn't account for component quantities
in bundled products, leading to incorrect available stock.

Fixes #456

---

perf(api): optimize product search query

Reduced query time from 2.3s to 0.4s by adding database index
on products.name and products.sku columns.

Related to #789
```

### Pull Request Guidelines

#### PR Title
```
<type>: <clear description>

Examples:
✅ feat: Add user role management system
✅ fix: Resolve inventory sync timeout issues
✅ refactor: Simplify authentication middleware
❌ Update files
❌ PR-123
❌ Work in progress
```

#### PR Description Template

Use the provided template (`.github/PULL_REQUEST_TEMPLATE.md`):

```markdown
## Description
Clear description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where necessary
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for changes
- [ ] All tests pass locally
- [ ] Dependent changes merged
```

#### PR Review Process

**Before Creating PR**:
1. Run all tests locally: `pytest tests/ -v`
2. Check code quality: `ruff check . && black . && isort .`
3. Run security scan: `bandit -r app/`
4. Ensure all commits are meaningful
5. Update relevant documentation

**PR Size**:
- Target: < 400 lines changed
- Maximum: 800 lines changed
- If larger: Split into multiple PRs

**Review Requirements**:
- Minimum 1 approval for feature branches
- Minimum 2 approvals for hotfixes to main
- CI must pass (all green checks)
- No merge conflicts

**Reviewer Checklist**:
- [ ] Code logic is correct
- [ ] Tests cover new functionality
- [ ] No security vulnerabilities introduced
- [ ] Performance implications considered
- [ ] Documentation updated
- [ ] Backward compatibility maintained

### Merge Strategy

```bash
# Feature branches to develop
gh pr merge --squash  # Squash commits for clean history

# Release branches to main
gh pr merge --merge   # Keep full history for releases

# Hotfixes to main
gh pr merge --merge   # Preserve context for urgent fixes
```

## Testing Strategy

### Test Pyramid

```
       /\        E2E Tests (10%)
      /  \       - Full user flows
     /    \      - Critical paths only
    /------\
   /        \    Integration Tests (30%)
  /          \   - API endpoints
 /            \  - Database operations
/--------------\
|              | Unit Tests (60%)
|              | - Business logic
|              | - Utilities
|              | - Services
----------------
```

### Unit Testing

#### Coverage Requirements

```python
# Minimum coverage: 80%
# Target coverage: 90%
# Critical paths: 100%

# .coveragerc
[run]
omit =
    */tests/*
    */migrations/*
    */venv/*

[report]
fail_under = 80
```

#### Test Organization

```
tests/
├── unit/
│   ├── test_models.py        # Database model tests
│   ├── test_services.py      # Business logic tests
│   ├── test_utils.py         # Utility function tests
│   └── test_validators.py    # Validation logic tests
├── integration/
│   ├── test_api_products.py  # Product API tests
│   ├── test_api_sales.py     # Sales API tests
│   └── test_auth.py          # Auth integration tests
├── e2e/
│   ├── test_auth.py          # Auth flows
│   ├── test_api.py           # API workflows
│   └── test_business.py      # Business processes
└── conftest.py               # Shared fixtures
```

#### Test Naming

```python
# Pattern: test_<function>_<scenario>_<expected_result>

def test_get_product_by_id_valid_id_returns_product():
    """Test that valid product ID returns correct product"""
    pass

def test_get_product_by_id_invalid_id_raises_not_found():
    """Test that invalid product ID raises NotFoundError"""
    pass

def test_create_order_insufficient_stock_raises_error():
    """Test that insufficient inventory prevents order creation"""
    pass
```

#### Test Best Practices

```python
# ✅ GOOD: Clear, focused, independent test
def test_user_login_valid_credentials_returns_token(client, test_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

# ❌ BAD: Testing multiple things, unclear purpose
def test_login(client):
    r = client.post("/api/auth/login", json={"email": "test@test.com", "password": "pass"})
    assert r.status_code == 200
    r2 = client.get("/api/products", headers={"Authorization": f"Bearer {r.json()['access_token']}"})
    assert r2.status_code == 200
```

### Integration Testing

#### Test Data Management

```python
# Use factories for test data
from tests.fixtures.factories import (
    UserFactory, ProductFactory, CustomerFactory
)

@pytest.fixture
def sample_data(db_session):
    """Create minimal test dataset"""
    users = UserFactory.create_batch(5)
    products = ProductFactory.create_batch(20)
    customers = CustomerFactory.create_batch(10)

    db_session.commit()

    return {
        'users': users,
        'products': products,
        'customers': customers
    }
```

#### Database Fixtures

```python
@pytest.fixture(scope="function")
def db_session():
    """Provide database session with automatic rollback"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### E2E Testing

#### When to Write E2E Tests

Write E2E tests for:
- Critical user journeys (checkout, payment)
- Cross-service workflows (inventory → sales → accounting)
- Authentication flows
- Data consistency scenarios

Don't write E2E tests for:
- Simple CRUD operations (covered by integration tests)
- UI styling/layout
- Edge cases (covered by unit tests)

#### E2E Test Structure

```python
def test_complete_sales_order_flow(api_client, seed_data):
    """
    Test complete sales order flow from creation to fulfillment

    Flow:
    1. User logs in
    2. Creates sales order
    3. Processes payment
    4. Verifies inventory reduction
    5. Checks order status
    """
    # 1. Authenticate
    login_response = api_client.post(
        "/api/auth/login",
        json={"email": "sales@tsh.sale", "password": "sales123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get product for order
    product_id = seed_data['products'][0].id
    initial_stock = seed_data['products'][0].available_stock

    # 3. Create sales order
    order_response = api_client.post(
        "/api/sales/orders",
        json={
            "customer_id": seed_data['customers'][0].id,
            "items": [{
                "product_id": product_id,
                "quantity": 5,
                "unit_price": 100.00
            }]
        },
        headers=headers
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # 4. Process payment
    payment_response = api_client.post(
        f"/api/payments/orders/{order_id}",
        json={"method": "credit_card", "amount": 500.00},
        headers=headers
    )
    assert payment_response.status_code == 200

    # 5. Verify inventory updated
    inventory_response = api_client.get(
        f"/api/inventory/products/{product_id}",
        headers=headers
    )
    assert inventory_response.status_code == 200
    current_stock = inventory_response.json()["available_stock"]
    assert current_stock == initial_stock - 5

    # 6. Verify order status
    order_check = api_client.get(
        f"/api/sales/orders/{order_id}",
        headers=headers
    )
    assert order_check.json()["status"] == "completed"
```

## Code Quality

### Linting Configuration

#### Ruff (Fast Python Linter)

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "C",    # flake8-comprehensions
    "B",    # flake8-bugbear
    "UP",   # pyupgrade
]

ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # function call in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # unused imports
"tests/**/*.py" = ["S101"]  # assert usage
```

#### Black (Code Formatter)

```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | \.pytest_cache
  | migrations
)/
'''
```

#### isort (Import Sorting)

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### Code Review Standards

#### Code Smells to Avoid

```python
# ❌ BAD: Magic numbers
def calculate_discount(price):
    if price > 1000:
        return price * 0.1
    return 0

# ✅ GOOD: Named constants
DISCOUNT_THRESHOLD = Decimal('1000.00')
DISCOUNT_RATE = Decimal('0.10')

def calculate_discount(price: Decimal) -> Decimal:
    """Calculate discount for price above threshold"""
    if price > DISCOUNT_THRESHOLD:
        return price * DISCOUNT_RATE
    return Decimal('0.00')
```

```python
# ❌ BAD: Deep nesting
def process_order(order):
    if order.is_valid():
        if order.has_stock():
            if order.customer.is_active():
                if order.payment_received():
                    order.fulfill()
                else:
                    raise PaymentError()
            else:
                raise InactiveCustomerError()
        else:
            raise InsufficientStockError()
    else:
        raise InvalidOrderError()

# ✅ GOOD: Early returns
def process_order(order):
    """Process order after validation"""
    if not order.is_valid():
        raise InvalidOrderError()

    if not order.customer.is_active():
        raise InactiveCustomerError()

    if not order.has_stock():
        raise InsufficientStockError()

    if not order.payment_received():
        raise PaymentError()

    order.fulfill()
```

```python
# ❌ BAD: God object
class OrderService:
    def create_order(self): pass
    def update_inventory(self): pass
    def process_payment(self): pass
    def send_email(self): pass
    def generate_invoice(self): pass
    def update_accounting(self): pass

# ✅ GOOD: Single responsibility
class OrderService:
    def __init__(
        self,
        inventory_service: InventoryService,
        payment_service: PaymentService,
        notification_service: NotificationService
    ):
        self.inventory = inventory_service
        self.payment = payment_service
        self.notifications = notification_service

    def create_order(self, order_data: dict) -> Order:
        """Create order and coordinate other services"""
        order = Order(**order_data)
        self.inventory.reserve_stock(order.items)
        self.payment.process(order)
        self.notifications.send_order_confirmation(order)
        return order
```

## Security

### Secret Management

#### Never Commit Secrets

```bash
# .gitignore must include
.env
.env.*
*.key
*.pem
credentials.json
secrets.yaml
config/production.yml
```

#### Use GitHub Secrets

```bash
# Set secrets via CLI
gh secret set SECRET_NAME -b "secret-value"

# Or from file
gh secret set SSH_KEY < ~/.ssh/id_rsa

# List secrets
gh secret list
```

#### Environment-Specific Secrets

```python
# ✅ GOOD: Load from environment
import os
from functools import lru_cache

class Settings:
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    API_KEY: str = os.getenv("API_KEY")

    @property
    def database_url(self) -> str:
        return f"postgresql://user:{self.DB_PASSWORD}@host/db"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# ❌ BAD: Hardcoded secrets
DB_PASSWORD = "MySecretPassword123"
API_KEY = "sk-1234567890abcdef"
```

### Dependency Management

#### Regular Updates

```bash
# Weekly dependency review
gh pr list --label dependencies

# Update critical security issues immediately
pip install --upgrade package-name

# Test after updates
pytest tests/ -v
```

#### Dependabot Configuration

Review and merge Dependabot PRs regularly:
- **Patch updates**: Auto-merge (low risk)
- **Minor updates**: Review and merge within 1 week
- **Major updates**: Review carefully, test thoroughly

### Security Scanning

#### Pre-Commit Checks

```bash
# Run security linters
bandit -r app/ -f json -o bandit-report.json

# Check dependencies
safety check --json

# Scan Docker images
trivy image tsh-erp-app:latest
```

#### Vulnerability Response

**HIGH/CRITICAL Severity**:
1. Create hotfix branch immediately
2. Update vulnerable dependency
3. Run full test suite
4. Deploy to staging for verification
5. Create PR to main
6. Deploy to production within 24 hours

**MEDIUM Severity**:
1. Create bug fix branch within 1 week
2. Update dependency in regular release cycle
3. Monitor for exploitation attempts

**LOW Severity**:
1. Add to backlog
2. Update in next minor release
3. Document known issues

## Docker & Containers

### Dockerfile Best Practices

#### Layer Optimization

```dockerfile
# ✅ GOOD: Minimal layers, cached effectively
FROM python:3.11-slim as builder

# Install system dependencies (rarely changes)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (changes occasionally)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
WORKDIR /app

# Copy application code (changes frequently)
COPY ./app ./app

ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```dockerfile
# ❌ BAD: Many layers, poor caching
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y gcc
CMD ["python", "app/main.py"]
```

#### Security

```dockerfile
# ✅ GOOD: Non-root user, minimal image
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser ./app /app
WORKDIR /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Image Tagging Strategy

```bash
# Semantic versioning
v1.2.3          # Release version
v1.2            # Minor version alias
v1              # Major version alias

# Environment tags
latest          # Latest stable release
production      # Currently in production
staging         # Currently in staging
develop         # Latest develop branch

# Commit-based
sha-a1b2c3d     # Specific commit
main-latest     # Latest main branch
develop-latest  # Latest develop branch
```

### Multi-Stage Builds

```dockerfile
# Stage 1: Build
FROM node:20 as builder
WORKDIR /build
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
USER node
CMD ["node", "dist/main.js"]
```

## Deployment

### Pre-Deployment Checklist

- [ ] All tests pass on staging
- [ ] Schema migrations tested
- [ ] Database backup completed
- [ ] Security scan passed
- [ ] Performance test results acceptable
- [ ] Rollback plan documented
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled (if needed)

### Deployment Process

#### Blue-Green Deployment (Planned)

```
Current State:
  Production → Blue (v1.0)
  Staging → Green (v1.1)

Deployment Steps:
  1. Deploy v1.1 to Green
  2. Run smoke tests on Green
  3. Switch traffic: Blue → Green
  4. Monitor for 10 minutes
  5. If successful: Retire Blue
  6. If failed: Switch back to Blue
```

#### Database Migrations

```bash
# 1. Generate migration
alembic revision --autogenerate -m "Add customer_tier column"

# 2. Review migration file
cat alembic/versions/abc123_add_customer_tier.py

# 3. Test on local
alembic upgrade head

# 4. Test on staging
ssh staging
cd /opt/tsh-erp
source .venv/bin/activate
alembic upgrade head

# 5. Verify data integrity
psql -U app_user -d tsh_erp -c "SELECT COUNT(*) FROM customers"

# 6. Deploy to production (automatic in workflow)
gh workflow run deploy-production.yml
```

#### Rollback Procedure

Automated rollback triggers on:
- Smoke test failure
- Health check timeout
- Critical error rate spike

Manual rollback:
```bash
# 1. SSH to production
ssh root@167.71.39.50

# 2. Navigate to deployment directory
cd /opt/tsh-erp

# 3. Check current version
cat .deployment_version

# 4. View available versions
git tag --list

# 5. Rollback to previous version
git checkout v1.0.5
docker-compose restart

# 6. Verify health
curl https://erp.tsh.sale/health
```

### Post-Deployment

- [ ] Smoke tests passed
- [ ] Health endpoints responding
- [ ] Error rates normal
- [ ] Response times acceptable
- [ ] No critical logs
- [ ] Monitoring dashboards green
- [ ] User acceptance confirmation
- [ ] Documentation updated

## Performance

### Database Query Optimization

```python
# ❌ BAD: N+1 query problem
def get_orders_with_items(db: Session):
    orders = db.query(Order).all()
    for order in orders:
        # Triggers separate query for each order!
        items = order.items
    return orders

# ✅ GOOD: Eager loading with joinedload
from sqlalchemy.orm import joinedload

def get_orders_with_items(db: Session):
    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).all()
    return orders
```

### Caching Strategy

```python
from functools import lru_cache
from fastapi_cache.decorator import cache

# ✅ In-memory cache for frequently accessed data
@lru_cache(maxsize=128)
def get_product_categories() -> List[str]:
    """Cache product categories (changes rarely)"""
    return db.query(Category.name).all()

# ✅ Redis cache for API responses
@cache(expire=3600)  # 1 hour
async def get_popular_products():
    """Cache popular products list"""
    return db.query(Product).order_by(Product.sales_count.desc()).limit(20).all()

# ✅ Cache invalidation on updates
async def update_product(product_id: int, data: dict):
    product = update_product_in_db(product_id, data)
    await cache_client.delete(f"product:{product_id}")
    return product
```

### Load Testing

```bash
# Run before major releases
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=200 \
  -f run_time=10m

# Analyze results
gh run view --log | grep "success_rate"
```

### Performance Budgets

Set and monitor:
- API response time: P95 < 500ms
- Database queries: < 100ms
- Page load time: < 2 seconds
- Time to interactive: < 3 seconds

## Monitoring & Alerts

### Health Checks

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health with service checks"""
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }

    all_healthy = all(check["status"] == "healthy" for check in checks.values())

    return JSONResponse(
        status_code=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks}
    )
```

### Logging Best Practices

```python
import logging
from pythonjsonlogger import jsonlogger

# ✅ Structured logging
logger = logging.getLogger(__name__)

def process_order(order_id: int):
    logger.info(
        "Processing order",
        extra={
            "order_id": order_id,
            "user_id": current_user.id,
            "action": "process_order",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    try:
        # Process order
        pass
    except Exception as e:
        logger.error(
            "Order processing failed",
            extra={
                "order_id": order_id,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise
```

### Alert Thresholds

Configure alerts for:

**Critical (Immediate Response)**:
- Service downtime > 1 minute
- Error rate > 5%
- Response time P95 > 2 seconds
- Database connection failures
- Disk space > 90%

**Warning (Review Within 1 Hour)**:
- Error rate > 1%
- Response time P95 > 1 second
- Memory usage > 80%
- Deployment failures

**Info (Review Daily)**:
- Dependency updates available
- Schema drift detected
- Performance degradation trends

## Documentation

### Code Documentation

```python
from typing import List, Optional
from decimal import Decimal

def calculate_order_total(
    items: List[OrderItem],
    discount_code: Optional[str] = None,
    tax_rate: Decimal = Decimal('0.05')
) -> Decimal:
    """
    Calculate total order amount including discounts and tax.

    Args:
        items: List of order items with product and quantity
        discount_code: Optional discount code to apply
        tax_rate: Tax rate as decimal (default 5%)

    Returns:
        Total order amount including all adjustments

    Raises:
        InvalidDiscountCodeError: If discount code is invalid
        InsufficientStockError: If any item is out of stock

    Examples:
        >>> items = [OrderItem(product_id=1, quantity=2, price=100)]
        >>> calculate_order_total(items)
        Decimal('210.00')  # 200 + 5% tax

        >>> calculate_order_total(items, discount_code="SAVE10")
        Decimal('189.00')  # 200 - 10% discount + 5% tax on discounted amount
    """
    subtotal = sum(item.quantity * item.price for item in items)

    if discount_code:
        discount = get_discount(discount_code)
        subtotal -= subtotal * discount.rate

    tax = subtotal * tax_rate
    total = subtotal + tax

    return total.quantize(Decimal('0.01'))
```

### API Documentation

Use OpenAPI/Swagger with detailed descriptions:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

class CreateProductRequest(BaseModel):
    """Request model for creating a new product"""
    name: str = Field(..., description="Product name", min_length=1, max_length=200)
    sku: str = Field(..., description="Stock Keeping Unit", regex=r"^[A-Z0-9-]+$")
    unit_price: Decimal = Field(..., description="Price per unit", gt=0)

    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop Dell XPS 15",
                "sku": "LAPTOP-DELL-XPS15",
                "unit_price": "1299.99"
            }
        }

@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=201,
    summary="Create new product",
    description="Create a new product in the inventory system",
    responses={
        201: {"description": "Product created successfully"},
        400: {"description": "Invalid product data"},
        409: {"description": "Product with SKU already exists"}
    },
    tags=["Products"]
)
async def create_product(product: CreateProductRequest):
    """
    Create a new product with the following validations:

    - Name must be unique
    - SKU must follow format: CATEGORY-BRAND-MODEL
    - Price must be positive
    - All fields are required
    """
    pass
```

### Workflow Documentation

Keep workflow files self-documenting:

```yaml
name: Production Deployment

# This workflow handles deployment to production with:
# 1. Pre-deployment validation (secrets, schema, security)
# 2. Automatic database backup
# 3. Zero-downtime deployment
# 4. Post-deployment smoke tests
# 5. Automatic rollback on failure

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version/tag to deploy (leave empty for latest main)'
        required: false
        type: string
      skip_tests:
        description: 'Skip pre-deployment tests (not recommended)'
        required: false
        type: boolean
        default: false
```

---

## Quick Reference Checklist

### Daily

- [ ] Review CI/CD pipeline status
- [ ] Check Telegram notifications
- [ ] Monitor error rates
- [ ] Review Dependabot PRs

### Weekly

- [ ] Review DevOps report
- [ ] Update dependencies
- [ ] Run performance tests
- [ ] Review security alerts
- [ ] Clean up merged branches

### Monthly

- [ ] Audit GitHub secrets
- [ ] Review and update documentation
- [ ] Analyze deployment metrics
- [ ] Update CI/CD workflows
- [ ] Security audit

---

**Last Updated**: 2025-01-11
**Version**: 1.0.0
