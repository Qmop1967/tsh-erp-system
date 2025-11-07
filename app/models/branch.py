from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)  # Matches unified schema
    code = Column(String(50), unique=True, nullable=False, index=True)  # Matches unified schema
    address = Column(Text, nullable=True)  # Matches unified schema
    city = Column(String(100), nullable=True)  # Matches unified schema
    phone = Column(String(50), nullable=True)  # Matches unified schema
    email = Column(String(200), nullable=True)  # Matches unified schema
    is_active = Column(Boolean, default=True, nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True)  # Matches unified schema

    # Multi-tenancy support (not used in unified database)
    # tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)

    # Legacy fields (not in unified database)
    # location = Column(String(255), nullable=True)
    # name_ar = Column(String(100), nullable=True)
    # name_en = Column(String(100), nullable=True)
    # branch_code = Column(String(20), unique=True, nullable=True, index=True)
    # branch_type = Column(String(50), nullable=True)
    # description_ar = Column(Text)
    # description_en = Column(Text)
    # address_ar = Column(Text)
    # address_en = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Enhanced relationships
    warehouses = relationship("Warehouse", back_populates="branch")
    users = relationship("User", back_populates="branch")
    # tenant = relationship("Tenant", back_populates="branches")  # Not used in unified database
    cash_boxes = relationship("CashBox", back_populates="branch")
    expenses = relationship("Expense", back_populates="branch")
    promotions = relationship("Promotion", back_populates="branch")