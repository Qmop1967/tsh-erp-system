from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)  # سيتم تشفيرها
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # Made nullable for unified schema
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)  # Made nullable for unified schema

    # Multi-tenancy support (not used in unified database)
    # tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Enhanced security fields
    password_hash = Column(String(255), nullable=True)  # New hashed password field
    password_salt = Column(String(64), nullable=True)   # Salt for password hashing
    
    # Enhanced user information
    employee_code = Column(String(20), unique=True, nullable=True, index=True)
    phone = Column(String(20))
    is_salesperson = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False)  # Email verification status
    
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