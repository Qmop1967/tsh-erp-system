from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Item(Base):
    """Simple Item model for frontend inventory testing"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    quantity_on_hand = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', sku='{self.sku}')>"
