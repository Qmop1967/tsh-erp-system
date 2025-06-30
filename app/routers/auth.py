from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def get_user_permissions(user: User) -> list:
    """Get permissions based on user role"""
    if not user.role:
        return []
    
    role_name = user.role.name.lower()
    
    # Define permissions for each role
    permissions = {
        'admin': [
            'admin',
            'dashboard.view',
            'users.view',
            'hr.view',
            'branches.view',
            'warehouses.view',
            'items.view',
            'products.view',
            'inventory.view',
            'customers.view',
            'vendors.view',
            'sales.view',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view',
            'migration.view'
        ],
        'manager': [
            'dashboard.view',
            'users.view',
            'hr.view',
            'branches.view',
            'warehouses.view',
            'items.view',
            'products.view',
            'inventory.view',
            'customers.view',
            'vendors.view',
            'sales.view',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view'
        ],
        'sales': [
            'dashboard.view',
            'customers.view',
            'sales.view',
            'pos.view',
            'products.view',
            'inventory.view'
        ],
        'inventory': [
            'dashboard.view',
            'items.view',
            'products.view',
            'inventory.view',
            'warehouses.view'
        ],
        'accounting': [
            'dashboard.view',
            'accounting.view',
            'cashflow.view'
        ],
        'cashier': [
            'dashboard.view',
            'pos.view',
            'sales.view'
        ],
        'viewer': [
            'dashboard.view'
        ]
    }
    
    return permissions.get(role_name, ['dashboard.view'])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "branch": user.branch.name if user.branch else None,
            "permissions": get_user_permissions(user)
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name if user.role else "No Role",
        branch=user.branch.name if user.branch else "No Branch",
        permissions=get_user_permissions(user)
    )

@router.post("/logout")
async def logout():
    """
    Logout user (client should discard the token)
    """
    return {"message": "Successfully logged out"}

# Dependency to get current user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Keep backward compatibility
get_current_user_dependency = get_current_user
