# Authentication & Authorization Templates

**Purpose:** Production-ready authentication and authorization patterns for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/authentication.md

---

## 🔐 Template 1.1: Protected API Endpoint

**Reasoning Context:**
- TSH ERP handles sensitive data (500+ clients, financial transactions)
- Unauthenticated access would allow data theft or manipulation
- Every data-modifying operation must verify user identity
- Required by ARCHITECTURE_RULES.md security patterns

**When to Use:**
- Any endpoint that reads sensitive data
- Any endpoint that modifies data (POST, PUT, DELETE)
- Admin operations
- Client-specific data access

**Code Template:**

```python
# app/routers/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.example import ExampleResponse

router = APIRouter(prefix="/api/examples", tags=["examples"])

@router.get("/", response_model=list[ExampleResponse])
async def get_examples(
    current_user: User = Depends(get_current_user),  # 👈 Authentication required
    db: Session = Depends(get_db)
):
    """
    Get all examples visible to current user.

    Requires authentication.
    Returns data scoped to user's permissions.
    """
    # User is authenticated, proceed with business logic
    examples = db.query(Example).filter(
        Example.created_by_id == current_user.id
    ).all()

    return examples
```

**Customization Points:**
- Replace `Example` with your model name
- Adjust query filters based on business logic
- Add role-based filtering if needed

**Related Patterns:**
- Template 1.2: RBAC Protected Endpoint
- Template 1.3: Login/Token Generation

---

## 🔐 Template 1.2: RBAC (Role-Based Access Control) Endpoint

**Reasoning Context:**
- Not all authenticated users should access all features
- Managers can create orders, but clients cannot
- Admins can delete data, but salespeople cannot
- Role checks prevent privilege escalation attacks

**When to Use:**
- Admin-only operations (user management, system config)
- Manager operations (reporting, analytics)
- Operations that differ by role (salespeople see their clients only)

**Code Template:**

```python
# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(["admin", "manager"])),  # 👈 RBAC check
    db: Session = Depends(get_db)
):
    """
    Delete a product. Only admins and managers allowed.

    Requires authentication + admin or manager role.
    Returns 403 if user lacks required role.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
```

**Customization Points:**
- Change allowed roles: `require_role(["admin"])` for admin-only
- Add multiple role checks for complex permissions
- Customize error messages

**Dependencies Required:**

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from app.models.user import User

def require_role(allowed_roles: list[str]):
    """
    Dependency that checks if current user has one of the allowed roles.

    Usage: Depends(require_role(["admin", "manager"]))
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
```

**Related Patterns:**
- Template 1.1: Protected Endpoint
- ABAC patterns: @docs/AUTHORIZATION_FRAMEWORK.md

---

## 🔐 Template 1.3: Login & Token Generation

**Reasoning Context:**
- Users need to authenticate before accessing protected endpoints
- JWT tokens provide stateless authentication (no server-side sessions)
- Token expiration prevents indefinite access from compromised tokens
- Refresh tokens allow long-term access without storing passwords

**When to Use:**
- User login endpoints
- Token refresh endpoints
- Password reset flows

**Code Template:**

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.dependencies import get_db
from app.utils.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter(prefix="/api/auth", tags=["authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint.

    Returns JWT access token on successful authentication.
    Returns 401 if credentials are invalid.
    """
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.name},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.name
        }
    }
```

**Security Utilities:**

```python
# app/utils/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
```

**Pydantic Schemas:**

```python
# app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    """Data extracted from JWT token."""
    email: Optional[str] = None
    role: Optional[str] = None
```

**Get Current User Dependency:**

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.auth import TokenData
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)

    except JWTError:
        raise credentials_exception

    # Find user in database
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None:
        raise credentials_exception

    return user
```

**Related Patterns:**
- Template 1.1: Protected Endpoint
- Password reset: @docs/reference/code-templates/user-management.md (future)

---

## 🔒 TSH ERP Authorization Framework

**CRITICAL:** TSH ERP uses **HYBRID AUTHORIZATION: RBAC + ABAC + RLS**

Every endpoint must implement ALL THREE layers:

```python
# ✅ CORRECT: All three layers present
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role([...])),           # RBAC Layer
    abac: User = Depends(check_abac_permission(...)),    # ABAC Layer
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS Layer (Row-Level Security)
    return await service.get_orders()
```

**For Full Details:**
- @docs/AUTHORIZATION_FRAMEWORK.md
- @docs/core/architecture.md

---

## 🧪 Testing Authentication

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient, test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email

def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "invalid@test.com", "password": "wrongpass"}
    )

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_endpoint_without_auth(client: TestClient):
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/products/")

    assert response.status_code == 401

def test_protected_endpoint_with_auth(client: TestClient, auth_headers):
    """Test accessing protected endpoint with valid token."""
    response = client.get("/api/products/", headers=auth_headers)

    assert response.status_code == 200
```

---

**Related Documentation:**
- Authorization framework: @docs/AUTHORIZATION_FRAMEWORK.md
- Security patterns: @docs/core/architecture.md
- CRUD operations: @docs/reference/code-templates/crud-operations.md
