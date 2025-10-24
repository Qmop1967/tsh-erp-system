"""Product model"""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from prss.db import Base


class Product(Base):
    """Product reference model"""
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    external_product_id = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    requires_serial = Column(Boolean, default=False)
    warranty_months = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
