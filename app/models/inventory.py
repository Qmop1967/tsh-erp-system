from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class InventoryItem(Base):
    """عناصر المخزون - المخزون الحالي لكل منتج في كل مستودع"""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity_on_hand = Column(Numeric(15, 3), default=0)  # الكمية المتوفرة
    quantity_reserved = Column(Numeric(15, 3), default=0)  # الكمية المحجوزة
    quantity_ordered = Column(Numeric(15, 3), default=0)  # الكمية المطلوبة
    last_cost = Column(Numeric(10, 2), nullable=True)  # آخر تكلفة شراء
    average_cost = Column(Numeric(10, 2), nullable=True)  # متوسط التكلفة
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    stock_movements = relationship("StockMovement", back_populates="inventory_item")

    @property
    def available_quantity(self):
        """الكمية المتاحة للبيع"""
        return self.quantity_on_hand - self.quantity_reserved


class StockMovement(Base):
    """حركات المخزون - تسجيل جميع حركات دخول وخروج المخزون"""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    movement_type = Column(String(50), nullable=False)  # IN, OUT, TRANSFER, ADJUSTMENT
    reference_type = Column(String(50), nullable=True)  # SALE, PURCHASE, TRANSFER, ADJUSTMENT
    reference_id = Column(Integer, nullable=True)  # معرف المرجع (معرف الفاتورة مثلا)
    quantity = Column(Numeric(15, 3), nullable=False)  # الكمية (موجبة للدخول، سالبة للخروج)
    unit_cost = Column(Numeric(10, 2), nullable=True)  # تكلفة الوحدة
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    inventory_item = relationship("InventoryItem", back_populates="stock_movements")
    created_by_user = relationship("User")
