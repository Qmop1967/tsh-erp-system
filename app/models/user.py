from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(Text, nullable=True)  # Display name
    email = Column(Text, nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=True)  # Nullable for Zoho-synced users without local password
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # Made nullable for unified schema
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)  # Made nullable for unified schema

    # Multi-tenancy support (not used in unified database)
    # tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)

    # Enhanced security fields (not yet migrated to database)
    # password_hash = Column(String(255), nullable=True)  # New hashed password field
    # password_salt = Column(String(64), nullable=True)   # Salt for password hashing

    # User information (matching actual database schema)
    full_name = Column(Text, nullable=True)  # Synced from Zoho
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Enhanced fields (not yet migrated to database)
    # employee_code = Column(String(20), unique=True, nullable=True, index=True)
    # is_salesperson = Column(Boolean, default=False, nullable=False)
    # is_verified = Column(Boolean, default=False)  # Email verification status

    # Zoho sync fields
    zoho_user_id = Column(String(100), unique=True, nullable=True, index=True)  # Zoho Books/Inventory user ID
    zoho_customer_id = Column(Text, nullable=True)  # Zoho customer ID
    zoho_contact_id = Column(Text, nullable=True)   # Zoho contact ID
    zoho_last_sync = Column(DateTime, nullable=True)  # Last sync timestamp with Zoho

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Enhanced relationships
    role = relationship("Role", back_populates="users")
    branch = relationship("Branch", back_populates="users")
    # tenant = relationship("Tenant", back_populates="users")  # Not used in unified database
    cash_boxes = relationship("CashBox", foreign_keys="CashBox.user_id", back_populates="user")
    assigned_regions = relationship("SalespersonRegion", foreign_keys="SalespersonRegion.user_id", back_populates="salesperson")
    expenses = relationship("Expense", foreign_keys="Expense.user_id", back_populates="user")
    
    # CRITICAL: Money Transfer Tracking (Fraud Prevention)
    money_transfers = relationship("MoneyTransfer", back_populates="salesperson")
    
    # HR System Integration
    employee_profile = relationship("Employee", foreign_keys="Employee.user_id", back_populates="user", uselist=False)

    # Security relationships
    mfa_config = relationship("UserMFA", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    password_history = relationship("PasswordHistory", back_populates="user", order_by="PasswordHistory.created_at.desc()")