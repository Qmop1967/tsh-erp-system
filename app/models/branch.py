from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    
    # Multi-tenancy support
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Enhanced branch information
    name_ar = Column(String(100), nullable=True)
    name_en = Column(String(100), nullable=True)
    branch_code = Column(String(20), unique=True, nullable=True, index=True)
    branch_type = Column(String(50), nullable=True)  # MAIN_WHOLESALE, DORA_BRANCH, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    address_ar = Column(Text)
    address_en = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Enhanced relationships
    warehouses = relationship("Warehouse", back_populates="branch")
    users = relationship("User", back_populates="branch")
    tenant = relationship("Tenant", back_populates="branches")
    cash_boxes = relationship("CashBox", back_populates="branch")
    expenses = relationship("Expense", back_populates="branch")