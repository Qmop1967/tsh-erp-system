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
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Enhanced user information
    employee_code = Column(String(20), unique=True, nullable=True, index=True)
    phone = Column(String(20))
    is_salesperson = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # العلاقات
    role = relationship("Role", back_populates="users")
    branch = relationship("Branch", back_populates="users")
    cash_boxes = relationship("CashBox", foreign_keys="CashBox.user_id", back_populates="user")
    assigned_regions = relationship("SalespersonRegion", foreign_keys="SalespersonRegion.user_id", back_populates="salesperson")
    expenses = relationship("Expense", foreign_keys="Expense.user_id", back_populates="user") 