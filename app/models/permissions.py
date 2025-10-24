# Advanced Permission Management Models
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base

class ActionType(enum.Enum):
    """Granular action types for permissions"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"
    PRINT = "print"

class ModuleType(enum.Enum):
    """Module-based organization of permissions"""
    APPLICATION_ACCESS = "application_access"
    USER_MANAGEMENT = "user_management"
    ROLE_PERMISSION = "role_permission"
    BRANCH_MANAGEMENT = "branch_management"
    INVENTORY = "inventory"
    SALES = "sales"
    PURCHASING = "purchasing"
    FINANCIAL = "financial"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    REPORTS = "reports"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    AUDIT = "audit"

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "inventory.products.create"
    name = Column(String(200), nullable=False)  # Human-readable name
    description = Column(Text)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    category = Column(String(100))  # Additional sub-grouping within modules
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)  # For UI ordering
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Attribute-based conditions (ABAC)
    conditions = Column(Text)  # JSON string for complex conditions
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    granter = relationship("User", foreign_keys=[granted_by])

class UserPermission(Base):
    """Direct user permissions (overrides role permissions)"""
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    is_granted = Column(Boolean, default=True)  # True=grant, False=revoke
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration
    
    # Attribute-based conditions
    conditions = Column(Text)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission")
    granter = relationship("User", foreign_keys=[granted_by])

class AuditLog(Base):
    """Comprehensive audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100))  # Can be ID or identifier
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    
    # Relationships
    user = relationship("User")
    branch = relationship("Branch")
