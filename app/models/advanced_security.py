"""
Advanced Security Models for TSH ERP System
Hyper-Advanced ABAC, RBAC, PBAC, RLS, FLS Implementation

Features:
- Attribute-Based Access Control (ABAC)
- Role-Based Access Control (RBAC) 
- Policy-Based Access Control (PBAC)
- Row-Level Security (RLS)
- Field-Level Security (FLS)
- Centralized Audit Logging
- Multi-Factor Authentication (MFA)
- Device Management
- Session Control
- Location-Based Access Control
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import enum
import json
from typing import Dict, List, Any, Optional
import uuid

from app.db.database import Base

# === ENUMS ===

class SecurityLevel(enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class AccessAction(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    AUDIT = "audit"
    MANAGE = "manage"

class ResourceType(enum.Enum):
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    BRANCH = "branch"
    INVENTORY = "inventory"
    SALES = "sales"
    FINANCIAL = "financial"
    HR = "hr"
    SYSTEM = "system"
    DATA = "data"
    REPORT = "report"
    API = "api"

class PolicyEffect(enum.Enum):
    ALLOW = "allow"
    DENY = "deny"

class AuthFactor(enum.Enum):
    PASSWORD = "password"
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    PUSH_NOTIFICATION = "push_notification"

class DeviceStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    PENDING = "pending"

class SessionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# === ADVANCED PERMISSION MODELS ===

class AdvancedPermission(Base):
    """Enhanced permissions with attribute-based conditions"""
    __tablename__ = "advanced_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    display_name = Column(String(300))
    description = Column(Text)
    resource_type = Column(Enum(ResourceType), nullable=False)
    action = Column(Enum(AccessAction), nullable=False)
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)
    
    # Condition-based access (ABAC)
    conditions = Column(JSON)  # Complex conditions for attribute-based access
    constraints = Column(JSON)  # Additional constraints (time, location, etc.)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    role_permissions = relationship("RolePermissionMapping", back_populates="permission")
    user_permissions = relationship("UserPermissionOverride", back_populates="permission")
    policy_permissions = relationship("PolicyPermissionMapping", back_populates="permission")

class AdvancedRole(Base):
    """Enhanced roles with hierarchical structure"""
    __tablename__ = "security_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)

    # Hierarchical roles
    parent_role_id = Column(Integer, ForeignKey("security_roles.id"))
    level = Column(Integer, default=0)  # Hierarchy level

    # Role attributes for ABAC
    attributes = Column(JSON)  # Department, location, clearance level, etc.
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL)

    # Restrictions
    max_users = Column(Integer)  # Maximum users that can have this role
    requires_approval = Column(Boolean, default=False)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_role = relationship("AdvancedRole", remote_side=[id])
    child_roles = relationship("AdvancedRole")
    role_permissions = relationship("RolePermissionMapping", back_populates="role")
    # users relationship commented out - User model doesn't have advanced_role foreign key
    # users = relationship("User", back_populates="advanced_role")
    restriction_groups = relationship("RoleRestrictionGroup", back_populates="role")

class RolePermissionMapping(Base):
    """Role to Permission mapping with conditions"""
    __tablename__ = "role_permission_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("security_roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("advanced_permissions.id"), nullable=False)
    
    # Conditional access
    conditions = Column(JSON)  # When this permission applies
    constraints = Column(JSON)  # Additional constraints
    expires_at = Column(DateTime)  # Permission expiration
    
    # Grant tracking
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    role = relationship("AdvancedRole", back_populates="role_permissions")
    permission = relationship("AdvancedPermission", back_populates="role_permissions")
    granter = relationship("User", foreign_keys=[granted_by])

class UserPermissionOverride(Base):
    """User-specific permission overrides"""
    __tablename__ = "user_permission_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("advanced_permissions.id"), nullable=False)
    
    # Override type
    is_granted = Column(Boolean, default=True)  # True=grant, False=revoke
    override_reason = Column(Text)
    
    # Conditional access
    conditions = Column(JSON)
    constraints = Column(JSON)
    expires_at = Column(DateTime)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Grant tracking
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("AdvancedPermission", back_populates="user_permissions")
    granter = relationship("User", foreign_keys=[granted_by])
    approver = relationship("User", foreign_keys=[approved_by])

# === POLICY-BASED ACCESS CONTROL (PBAC) ===

class SecurityPolicy(Base):
    """Policy-Based Access Control policies"""
    __tablename__ = "security_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    display_name = Column(String(300))
    description = Column(Text)
    
    # Policy definition
    policy_document = Column(JSON, nullable=False)  # XACML-like policy
    effect = Column(Enum(PolicyEffect), default=PolicyEffect.ALLOW)
    priority = Column(Integer, default=100)  # Higher number = higher priority
    
    # Scope
    applies_to_resources = Column(JSON)  # Resource types this applies to
    applies_to_actions = Column(JSON)  # Actions this applies to
    applies_to_subjects = Column(JSON)  # Users/roles this applies to
    
    # Conditions
    conditions = Column(JSON)  # When this policy applies
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    policy_permissions = relationship("PolicyPermissionMapping", back_populates="policy")

class PolicyPermissionMapping(Base):
    """Policy to Permission mapping"""
    __tablename__ = "policy_permission_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("security_policies.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("advanced_permissions.id"), nullable=False)
    
    effect = Column(Enum(PolicyEffect), default=PolicyEffect.ALLOW)
    conditions = Column(JSON)
    
    # Relationships
    policy = relationship("SecurityPolicy", back_populates="policy_permissions")
    permission = relationship("AdvancedPermission", back_populates="policy_permissions")

# === ROW-LEVEL SECURITY (RLS) ===

class RowLevelSecurityRule(Base):
    """Row-Level Security rules for database filtering"""
    __tablename__ = "rls_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    
    # Target
    table_name = Column(String(100), nullable=False)
    
    # Rule definition
    rule_expression = Column(Text, nullable=False)  # SQL WHERE clause
    applies_to_actions = Column(JSON)  # Which actions this applies to
    
    # Scope
    applies_to_roles = Column(JSON)  # Role IDs
    applies_to_users = Column(JSON)  # User IDs
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

# === FIELD-LEVEL SECURITY (FLS) ===

class FieldLevelSecurityRule(Base):
    """Field-Level Security rules for column access control"""
    __tablename__ = "fls_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    
    # Target
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100), nullable=False)
    
    # Access control
    is_readable = Column(Boolean, default=True)
    is_writable = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    
    # Masking/encryption
    masking_pattern = Column(String(100))  # Pattern for data masking
    requires_encryption = Column(Boolean, default=False)
    
    # Scope
    applies_to_roles = Column(JSON)
    applies_to_users = Column(JSON)
    conditions = Column(JSON)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

# === RESTRICTION GROUPS ===

class RestrictionGroup(Base):
    """Groups of restrictions that can be applied to roles/users"""
    __tablename__ = "restriction_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    
    # Restrictions
    restrictions = Column(JSON, nullable=False)  # JSON defining restrictions
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    role_restrictions = relationship("RoleRestrictionGroup", back_populates="restriction_group")
    user_restrictions = relationship("UserRestrictionGroup", back_populates="restriction_group")

class RoleRestrictionGroup(Base):
    """Restriction groups applied to roles"""
    __tablename__ = "role_restriction_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("security_roles.id"), nullable=False)
    restriction_group_id = Column(Integer, ForeignKey("restriction_groups.id"), nullable=False)
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    role = relationship("AdvancedRole", back_populates="restriction_groups")
    restriction_group = relationship("RestrictionGroup", back_populates="role_restrictions")

class UserRestrictionGroup(Base):
    """Restriction groups applied to users"""
    __tablename__ = "user_restriction_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restriction_group_id = Column(Integer, ForeignKey("restriction_groups.id"), nullable=False)
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    restriction_group = relationship("RestrictionGroup", back_populates="user_restrictions")

# === MULTI-FACTOR AUTHENTICATION ===

class MFAMethod(Base):
    """Multi-Factor Authentication methods"""
    __tablename__ = "mfa_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Method details
    factor_type = Column(Enum(AuthFactor), nullable=False)
    is_primary = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    
    # Method-specific data (encrypted)
    secret_key = Column(Text)  # For TOTP
    phone_number = Column(String(20))  # For SMS
    email_address = Column(String(255))  # For email
    device_id = Column(String(255))  # For push notifications
    
    # Backup codes
    backup_codes = Column(JSON)  # Encrypted backup codes
    backup_codes_used = Column(JSON)  # Track used backup codes
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    use_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    challenges = relationship("MFAChallenge", back_populates="mfa_method")

class MFAChallenge(Base):
    """MFA challenge instances"""
    __tablename__ = "mfa_challenges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mfa_method_id = Column(Integer, ForeignKey("mfa_methods.id"), nullable=False)
    
    # Challenge details
    challenge_code = Column(String(10))  # 6-digit code
    challenge_data = Column(JSON)  # Additional challenge data
    
    # Status
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5))
    verified_at = Column(DateTime)
    
    # Security
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    mfa_method = relationship("MFAMethod", back_populates="challenges")

# === DEVICE MANAGEMENT ===

class UserDevice(Base):
    """User devices for session and access control"""
    __tablename__ = "user_devices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Device information
    device_name = Column(String(200))
    device_type = Column(String(50))  # mobile, desktop, tablet
    platform = Column(String(50))  # iOS, Android, Windows, etc.
    browser = Column(String(100))
    
    # Device fingerprint
    device_fingerprint = Column(String(255), unique=True)
    device_token = Column(String(500))  # For push notifications
    
    # Status
    status = Column(Enum(DeviceStatus), default=DeviceStatus.PENDING)
    is_trusted = Column(Boolean, default=False)
    
    # Location tracking
    last_ip_address = Column(String(45))
    last_location = Column(JSON)  # Lat, lng, address
    allowed_locations = Column(JSON)  # Geofencing
    
    # Metadata
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    registered_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    # sessions relationship disabled - UserSession doesn't have device property
    # sessions = relationship("UserSession", back_populates="device")
    approver = relationship("User", foreign_keys=[approved_by])

# === SESSION MANAGEMENT ===

class AdvancedUserSession(Base):
    """Enhanced user sessions with device tracking"""
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(36), ForeignKey("user_devices.id"))

    # Session details
    session_token = Column(String(500), unique=True, nullable=False)
    refresh_token = Column(String(500), unique=True)

    # Status
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    is_mobile = Column(Boolean, default=False)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    terminated_at = Column(DateTime)

    # Location and security
    ip_address = Column(String(45))
    location = Column(JSON)
    user_agent = Column(String(500))
    risk_score = Column(Float, default=0.0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)

    # Admin controls
    can_be_terminated = Column(Boolean, default=True)
    requires_mfa = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    device = relationship("UserDevice", foreign_keys=[device_id])  # Removed back_populates - UserDevice.sessions is disabled
    activities = relationship("SessionActivity", back_populates="session")

class SessionActivity(Base):
    """Track session activities for audit"""
    __tablename__ = "session_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("user_sessions.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(100))  # login, logout, access, action
    activity_description = Column(Text)
    resource_accessed = Column(String(200))
    
    # Context
    ip_address = Column(String(45))
    location = Column(JSON)
    user_agent = Column(String(500))
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("AdvancedUserSession", back_populates="activities")

# === CENTRALIZED AUDIT LOGGING ===

class AdvancedAuditLog(Base):
    """Comprehensive audit logging"""
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)

    # Who
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(36), ForeignKey("user_sessions.id"))
    
    # What
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), index=True)
    
    # Details
    description = Column(Text)
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # When
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Where
    ip_address = Column(String(45), index=True)
    location = Column(JSON)
    user_agent = Column(String(500))
    
    # How
    method = Column(String(20))  # GET, POST, PUT, DELETE
    endpoint = Column(String(200))
    
    # Context
    branch_id = Column(Integer, ForeignKey("branches.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    # Security
    risk_score = Column(Float, default=0.0)
    is_suspicious = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    session = relationship("AdvancedUserSession", foreign_keys=[session_id])

# === SECURITY EVENTS ===

class AdvancedSecurityEvent(Base):
    """Security events and alerts"""
    __tablename__ = "security_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)

    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(Enum(RiskLevel), default=RiskLevel.LOW, index=True)
    title = Column(String(200))
    description = Column(Text)

    # Context
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(36), ForeignKey("user_sessions.id"))
    ip_address = Column(String(45))
    user_agent = Column(String(500))  # Added for security tracking
    location = Column(JSON)
    
    # Event data
    event_data = Column(JSON)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    session = relationship("AdvancedUserSession", foreign_keys=[session_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

# === PASSLESS AUTHENTICATION ===

class PasslessToken(Base):
    """Passless authentication tokens"""
    __tablename__ = "passless_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(36), ForeignKey("user_devices.id"))
    
    # Token details
    token_type = Column(String(50))  # magic_link, qr_code, push_notification
    token_hash = Column(String(255), unique=True)
    
    # Status
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    used_at = Column(DateTime)
    
    # Security context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    location = Column(JSON)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    device = relationship("UserDevice", foreign_keys=[device_id])
