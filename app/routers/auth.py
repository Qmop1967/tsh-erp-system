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
    
    # Normalize role names to handle variations
    # Map "Travel Salesperson", "Sales", "Salesperson" to same permissions
    if 'sales' in role_name or 'salesperson' in role_name:
        role_name = 'salesperson'
    
    # Define permissions for each role
    permissions = {
        'admin': [
            'admin',
            'dashboard.view',
            'users.view',
            'users.create',
            'users.update',
            'users.delete',
            'hr.view',
            'branches.view',
            'warehouses.view',
            'items.view',
            'products.view',
            'inventory.view',
            'customers.view',
            'vendors.view',
            'sales.view',
            'sales.create',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view',
            'migration.view',
            'reports.view',
            'settings.view'
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
            'sales.create',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view',
            'reports.view'
        ],
        'salesperson': [
            'dashboard.view',
            'customers.view',
            'customers.create',
            'customers.update',
            'sales.view',
            'sales.create',
            'sales.update',
            'products.view',
            'inventory.view',
            'pos.view',
            'cashflow.view',
            'reports.view'
        ],
        'inventory': [
            'dashboard.view',
            'items.view',
            'items.create',
            'items.update',
            'products.view',
            'inventory.view',
            'inventory.create',
            'inventory.update',
            'warehouses.view'
        ],
        'accountant': [
            'dashboard.view',
            'accounting.view',
            'accounting.create',
            'accounting.update',
            'cashflow.view',
            'reports.view',
            'sales.view',
            'purchase.view'
        ],
        'cashier': [
            'dashboard.view',
            'pos.view',
            'pos.create',
            'sales.view',
            'sales.create',
            'customers.view',
            'products.view'
        ],
        'hr': [
            'dashboard.view',
            'hr.view',
            'hr.create',
            'hr.update',
            'users.view',
            'reports.view'
        ],
        'viewer': [
            'dashboard.view',
            'reports.view'
        ]
    }
    
    return permissions.get(role_name, ['dashboard.view'])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    WEB LOGIN: Only Admin users can login to web frontend
    Mobile users should use mobile apps
    """
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has web access permission
    # Only Admin role can access web frontend
    role_name = user.role.name if user.role else ""
    
    # Block non-admin users from web login
    if role_name.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Web access denied. {role_name} users must use the mobile application. Please download the TSH {role_name} App.",
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

@router.post("/login/mobile", response_model=LoginResponse)
async def mobile_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Mobile App Authentication - All users can login via mobile apps
    This endpoint is for mobile applications only
    """
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact your administrator.",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "platform": "mobile"}, expires_delta=access_token_expires
    )
    
    role_name = user.role.name if user.role else "User"
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role_name,
            "branch": user.branch.name if user.branch else None,
            "permissions": get_user_permissions(user),
            "mobile_app": get_recommended_mobile_app(role_name),
            "platform": "mobile"
        }
    )

def get_recommended_mobile_app(role_name: str) -> str:
    """Get the recommended mobile app for each role"""
    role_lower = role_name.lower()
    
    app_mapping = {
        'admin': 'TSH Admin Dashboard App',
        'manager': 'TSH Admin Dashboard App',
        'salesperson': 'TSH Salesperson App',
        'travel salesperson': 'TSH Salesperson App',
        'cashier': 'TSH Retail Sales App',
        'inventory': 'TSH Inventory Management App',
        'accountant': 'TSH Admin Dashboard App',
        'hr': 'TSH HR Management App',
        'viewer': 'TSH Admin Dashboard App'
    }
    
    # Check if role contains certain keywords
    if 'sales' in role_lower or 'salesperson' in role_lower:
        return 'TSH Salesperson App'
    
    return app_mapping.get(role_lower, 'TSH Admin Dashboard App')

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
