from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.database import Base
from datetime import datetime

class PricingList(Base):
    __tablename__ = "pricing_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price_list_type = Column(String, nullable=False)
    description = Column(Text)
    minimum_order_value = Column(Numeric(15, 2), default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True)
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product_prices = relationship("ProductPrice", back_populates="pricing_list")
    categories = relationship("PriceListCategory", back_populates="pricing_list")

class ProductPrice(Base):
    __tablename__ = "product_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    pricing_list_id = Column(Integer, ForeignKey("pricing_lists.id"), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    minimum_quantity = Column(Integer, default=1)
    is_negotiable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship("Product")
    pricing_list = relationship("PricingList", back_populates="product_prices")

class PriceListCategory(Base):
    __tablename__ = "price_list_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    pricing_list_id = Column(Integer, ForeignKey("pricing_lists.id"), nullable=False)
    customer_category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    pricing_list = relationship("PricingList", back_populates="categories")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    pricing_list_id = Column(Integer, ForeignKey("pricing_lists.id"), nullable=False)
    old_price = Column(Numeric(15, 2), nullable=False)
    new_price = Column(Numeric(15, 2), nullable=False)
    update_type = Column(String, nullable=False)
    notes = Column(Text)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product")
    pricing_list = relationship("PricingList")
    user = relationship("User")

class PriceNegotiationRequest(Base):
    __tablename__ = "price_negotiation_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_price = Column(Numeric(15, 2), nullable=False)
    requested_price = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    justification = Column(Text)
    status = Column(String, default="pending")
    valid_until = Column(Date)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    customer = relationship("Customer")
    product = relationship("Product")
    approver = relationship("User")

class CustomerPriceCategory(Base):
    __tablename__ = "customer_price_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    pricing_list_id = Column(Integer, ForeignKey("pricing_lists.id"), nullable=False)
    category = Column(String, nullable=False)
    effective_date = Column(Date)
    reason = Column(Text)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    customer = relationship("Customer")
    pricing_list = relationship("PricingList")
    user = relationship("User") 