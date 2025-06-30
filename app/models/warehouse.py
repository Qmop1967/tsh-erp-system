from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # العلاقات
    branch = relationship("Branch", back_populates="warehouses")
    inventory_items = relationship("InventoryItem", back_populates="warehouse") 