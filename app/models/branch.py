from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_ar = Column(String(200), nullable=False, index=True)  # Arabic name (MANDATORY for user-facing data)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # Arabic description (MANDATORY for user-facing data)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True, index=True)

    # Audit fields (MANDATORY)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Enhanced relationships
    warehouses = relationship("Warehouse", back_populates="branch")
    users = relationship("User", back_populates="branch")
    # tenant = relationship("Tenant", back_populates="branches")  # Not used in unified database
    cash_boxes = relationship("CashBox", back_populates="branch")
    expenses = relationship("Expense", back_populates="branch")
    promotions = relationship("Promotion", back_populates="branch")