"""
Row-Level Security (RLS) - User Data Scope Models
Implements fine-grained data access control based on user assignments
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class DataScopeType:
    """Data scope types for different access levels"""
    ALL = "all"  # Full access to all data (admin, super admin)
    BRANCH = "branch"  # Access to branch data only
    WAREHOUSE = "warehouse"  # Access to assigned warehouses only
    CUSTOMER = "customer"  # Access to assigned customers only
    REGION = "region"  # Access to assigned regions only
    CUSTOM = "custom"  # Custom scope with specific assignments


# Many-to-Many relationship tables
user_customers = Table(
    'user_customers',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('customer_id', Integer, ForeignKey('customers.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'))
)

user_warehouses = Table(
    'user_warehouses',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('warehouse_id', Integer, ForeignKey('warehouses.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'))
)

user_branches = Table(
    'user_branches',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('branch_id', Integer, ForeignKey('branches.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'))
)


class UserDataScope(Base):
    """User data access scope configuration"""
    __tablename__ = "user_data_scopes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Data scope configuration
    scope_type = Column(String(50), nullable=False, default=DataScopeType.BRANCH)

    # Automatic filtering flags
    auto_filter_customers = Column(Boolean, default=False)  # Filter customers by assignment
    auto_filter_warehouses = Column(Boolean, default=False)  # Filter warehouses by assignment
    auto_filter_branches = Column(Boolean, default=False)  # Filter branches by assignment
    auto_filter_sales = Column(Boolean, default=False)  # Filter sales by customer assignment
    auto_filter_inventory = Column(Boolean, default=False)  # Filter inventory by warehouse assignment
    auto_filter_transactions = Column(Boolean, default=False)  # Filter financial transactions by customer

    # Hierarchical access (can see data from subordinates)
    include_subordinates = Column(Boolean, default=False)

    # Custom scope conditions (JSON)
    custom_conditions = Column(Text)  # JSON string for complex ABAC conditions

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="data_scope")
    creator = relationship("User", foreign_keys=[created_by])


class DataAccessLog(Base):
    """Audit log for data access attempts (RLS enforcement)"""
    __tablename__ = "data_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # customers, warehouses, sales, etc.
    resource_id = Column(Integer)  # ID of the accessed resource
    action = Column(String(50), nullable=False)  # view, create, update, delete
    access_granted = Column(Boolean, nullable=False)  # True if allowed, False if denied
    denial_reason = Column(String(500))  # Why access was denied
    scope_filter_applied = Column(Text)  # JSON: what filters were applied
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")


class DataScopeTemplate(Base):
    """Reusable data scope templates for common role patterns"""
    __tablename__ = "data_scope_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    # Template configuration (mirrors UserDataScope)
    scope_type = Column(String(50), nullable=False)
    auto_filter_customers = Column(Boolean, default=False)
    auto_filter_warehouses = Column(Boolean, default=False)
    auto_filter_branches = Column(Boolean, default=False)
    auto_filter_sales = Column(Boolean, default=False)
    auto_filter_inventory = Column(Boolean, default=False)
    auto_filter_transactions = Column(Boolean, default=False)
    include_subordinates = Column(Boolean, default=False)
    custom_conditions = Column(Text)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User")
