# Multi-tenancy Models and Row-Level Security
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Tenant(Base):
    """Multi-tenant organization model"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # URL-safe identifier
    domain = Column(String(255))  # Custom domain
    subdomain = Column(String(100), unique=True)  # tenant.tsh-erp.com
    
    # Subscription and billing
    subscription_tier = Column(String(50), default="basic")  # basic, premium, enterprise
    max_users = Column(Integer, default=10)
    max_branches = Column(Integer, default=1)
    max_storage_gb = Column(Integer, default=5)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings (JSON)
    settings = Column(Text)  # JSON string for tenant-specific settings
    
    # Relationships
    branches = relationship("Branch", back_populates="tenant")
    users = relationship("User", back_populates="tenant")

class TenantSettings(Base):
    """Tenant-specific configuration settings"""
    __tablename__ = "tenant_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'ui', 'features', 'integrations'
    key = Column(String(100), nullable=False)
    value = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant")

# Row-Level Security Mixin
class TenantMixin:
    """Mixin to add tenant_id to models for row-level security"""
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

# Enhanced models with multi-tenancy
class Branch(Base, TenantMixin):
    """Branch model with tenant isolation"""
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="branches")

class User(Base, TenantMixin):
    """User model with tenant isolation"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(64), nullable=False)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Role and branch assignment
    role_id = Column(Integer, ForeignKey("roles.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role")
    branch = relationship("Branch")

# Multi-tenant service for context management
class TenantContext:
    """Thread-local tenant context for row-level security"""
    _tenant_id: Optional[int] = None
    _user_id: Optional[int] = None
    _branch_id: Optional[int] = None
    
    @classmethod
    def set_context(cls, tenant_id: int, user_id: Optional[int] = None, 
                   branch_id: Optional[int] = None):
        cls._tenant_id = tenant_id
        cls._user_id = user_id
        cls._branch_id = branch_id
    
    @classmethod
    def get_tenant_id(cls) -> Optional[int]:
        return cls._tenant_id
    
    @classmethod
    def get_user_id(cls) -> Optional[int]:
        return cls._user_id
    
    @classmethod
    def get_branch_id(cls) -> Optional[int]:
        return cls._branch_id
    
    @classmethod
    def clear_context(cls):
        cls._tenant_id = None
        cls._user_id = None
        cls._branch_id = None

# Enhanced database service with row-level security
class TenantAwareSession:
    """Database session wrapper with automatic tenant filtering"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self._setup_row_level_security()
    
    def _setup_row_level_security(self):
        """Setup row-level security policies"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id:
            # Set session variable for PostgreSQL RLS
            self.db.execute(text(f"SET app.current_tenant_id = {tenant_id}"))
    
    def query(self, model):
        """Override query to automatically filter by tenant"""
        query = self.db.query(model)
        
        # Apply tenant filter if model has tenant_id
        if hasattr(model, 'tenant_id'):
            tenant_id = TenantContext.get_tenant_id()
            if tenant_id:
                query = query.filter(model.tenant_id == tenant_id)
        
        return query
    
    def add(self, instance):
        """Override add to automatically set tenant_id"""
        if hasattr(instance, 'tenant_id') and not instance.tenant_id:
            tenant_id = TenantContext.get_tenant_id()
            if tenant_id:
                instance.tenant_id = tenant_id
        
        self.db.add(instance)
    
    def commit(self):
        return self.db.commit()
    
    def rollback(self):
        return self.db.rollback()
    
    def close(self):
        return self.db.close()

# Tenant management service
class TenantService:
    """Service for managing tenants and multi-tenancy"""
    
    def __init__(self, db: Session):
        self.db = TenantAwareSession(db)
    
    def create_tenant(self, name: str, code: str, subdomain: str,
                     admin_user: dict) -> Tenant:
        """Create new tenant with admin user"""
        # Create tenant
        tenant = Tenant(
            name=name,
            code=code,
            subdomain=subdomain
        )
        self.db.add(tenant)
        self.db.commit()
        
        # Set tenant context
        TenantContext.set_context(tenant.id)
        
        # Create default branch
        branch = Branch(
            name=f"{name} Main Branch",
            code="MAIN",
            tenant_id=tenant.id
        )
        self.db.add(branch)
        
        # Create admin role
        from app.models.permissions import Permission, Role, RolePermission
        admin_role = Role(
            name="Admin",
            description="Administrator with full access",
            tenant_id=tenant.id
        )
        self.db.add(admin_role)
        self.db.commit()
        
        # Create admin user
        from app.services.security_service import SecurityService
        security_service = SecurityService(self.db.db)
        password_hash, salt = security_service.hash_password(admin_user["password"])
        
        user = User(
            username=admin_user["username"],
            email=admin_user["email"],
            password_hash=password_hash,
            password_salt=salt,
            first_name=admin_user.get("first_name", ""),
            last_name=admin_user.get("last_name", ""),
            role_id=admin_role.id,
            branch_id=branch.id,
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        self.db.add(user)
        self.db.commit()
        
        return tenant
    
    def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain"""
        return self.db.query(Tenant).filter(
            Tenant.subdomain == subdomain,
            Tenant.is_active == True
        ).first()
    
    def get_tenant_stats(self, tenant_id: int) -> dict:
        """Get tenant usage statistics"""
        TenantContext.set_context(tenant_id)
        
        stats = {
            "users_count": self.db.query(User).filter(User.is_active == True).count(),
            "branches_count": self.db.query(Branch).filter(Branch.is_active == True).count(),
            "storage_used_mb": self._calculate_storage_usage(),
        }
        
        return stats
    
    def _calculate_storage_usage(self) -> float:
        """Calculate storage usage for tenant (placeholder)"""
        # This would calculate actual storage usage
        # For now, return a placeholder value
        return 0.0
    
    def check_tenant_limits(self, tenant_id: int) -> dict:
        """Check if tenant is within subscription limits"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return {"valid": False, "error": "Tenant not found"}
        
        stats = self.get_tenant_stats(tenant_id)
        
        violations = []
        
        if stats["users_count"] > tenant.max_users:
            violations.append(f"User limit exceeded: {stats['users_count']}/{tenant.max_users}")
        
        if stats["branches_count"] > tenant.max_branches:
            violations.append(f"Branch limit exceeded: {stats['branches_count']}/{tenant.max_branches}")
        
        if stats["storage_used_mb"] > (tenant.max_storage_gb * 1024):
            violations.append(f"Storage limit exceeded: {stats['storage_used_mb']:.1f}MB/{tenant.max_storage_gb}GB")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "stats": stats,
            "limits": {
                "max_users": tenant.max_users,
                "max_branches": tenant.max_branches,
                "max_storage_gb": tenant.max_storage_gb
            }
        }

# Database setup for Row-Level Security (PostgreSQL)
RLS_POLICIES = {
    "users": """
        CREATE POLICY tenant_isolation_policy ON users
        FOR ALL TO app_user
        USING (tenant_id = current_setting('app.current_tenant_id')::int);
    """,
    "branches": """
        CREATE POLICY tenant_isolation_policy ON branches
        FOR ALL TO app_user
        USING (tenant_id = current_setting('app.current_tenant_id')::int);
    """,
    "products": """
        CREATE POLICY tenant_isolation_policy ON products
        FOR ALL TO app_user
        USING (tenant_id = current_setting('app.current_tenant_id')::int);
    """,
    # Add more tables as needed
}

def setup_row_level_security(db_session: Session):
    """Setup PostgreSQL Row-Level Security policies"""
    for table_name, policy_sql in RLS_POLICIES.items():
        try:
            # Enable RLS on table
            db_session.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))
            
            # Drop existing policy if exists
            db_session.execute(text(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table_name};"))
            
            # Create new policy
            db_session.execute(text(policy_sql))
            
            db_session.commit()
            print(f"RLS enabled for table: {table_name}")
        except Exception as e:
            print(f"Error setting up RLS for {table_name}: {e}")
            db_session.rollback()
