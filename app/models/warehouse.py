from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    name_ar = Column(String(100), nullable=False, index=True)  # Arabic name (MANDATORY)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit fields (MANDATORY)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    branch = relationship("Branch", back_populates="warehouses")
    inventory_items = relationship("InventoryItem", back_populates="warehouse") 