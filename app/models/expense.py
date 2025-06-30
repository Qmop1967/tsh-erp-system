from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class ExpenseStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ExpenseCategoryEnum(str, enum.Enum):
    OFFICE_SUPPLIES = "OFFICE_SUPPLIES"
    TRAVEL = "TRAVEL"
    UTILITIES = "UTILITIES"
    RENT = "RENT"
    INSURANCE = "INSURANCE"
    MAINTENANCE = "MAINTENANCE"
    MARKETING = "MARKETING"
    TRAINING = "TRAINING"
    MEALS = "MEALS"
    TRANSPORTATION = "TRANSPORTATION"
    SOFTWARE = "SOFTWARE"
    EQUIPMENT = "EQUIPMENT"
    CONSULTING = "CONSULTING"
    OTHER = "OTHER"


class ExpensePaymentMethodEnum(str, enum.Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_CARD = "CREDIT_CARD"
    CHECK = "CHECK"
    PETTY_CASH = "PETTY_CASH"


class Expense(Base):
    """نفقة - Expense"""
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(ExpenseCategoryEnum), nullable=False)
    
    # Financial Information
    amount = Column(Numeric(15, 3), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    tax_amount = Column(Numeric(15, 3), default=0)
    total_amount = Column(Numeric(15, 3), nullable=False)
    
    # Dates
    expense_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    payment_date = Column(DateTime)
    
    # Status and Approval
    status = Column(Enum(ExpenseStatusEnum), default=ExpenseStatusEnum.DRAFT)
    payment_method = Column(Enum(ExpensePaymentMethodEnum))
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Employee who submitted
    approved_by_id = Column(Integer, ForeignKey("users.id"))  # Manager who approved
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))  # Vendor/Supplier
    branch_id = Column(Integer, ForeignKey("branches.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))  # Expense account
    
    # Tracking
    receipt_number = Column(String(100))
    reference = Column(String(100))
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    currency = relationship("Currency", back_populates="expenses")
    user = relationship("User", foreign_keys=[user_id], back_populates="expenses")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    supplier = relationship("Supplier", back_populates="expenses")
    branch = relationship("Branch", back_populates="expenses")
    account = relationship("Account", back_populates="expenses")
    expense_items = relationship("ExpenseItem", back_populates="expense", cascade="all, delete-orphan")
    expense_attachments = relationship("ExpenseAttachment", back_populates="expense", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Expense(id={self.id}, number='{self.expense_number}', title='{self.title}', amount={self.amount})>"


class ExpenseItem(Base):
    """بند النفقة - Expense Item"""
    __tablename__ = "expense_items"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    
    # Item details
    description = Column(String(200), nullable=False)
    quantity = Column(Numeric(10, 3), default=1)
    unit_price = Column(Numeric(15, 3), nullable=False)
    amount = Column(Numeric(15, 3), nullable=False)
    
    # Optional product reference
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", back_populates="expense_items")
    product = relationship("Product", back_populates="expense_items")

    def __repr__(self):
        return f"<ExpenseItem(id={self.id}, expense_id={self.expense_id}, description='{self.description}', amount={self.amount})>"


class ExpenseAttachment(Base):
    """مرفق النفقة - Expense Attachment"""
    __tablename__ = "expense_attachments"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Metadata
    description = Column(String(200))
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expense = relationship("Expense", back_populates="expense_attachments")
    uploaded_by = relationship("User")

    def __repr__(self):
        return f"<ExpenseAttachment(id={self.id}, expense_id={self.expense_id}, filename='{self.filename}')>"
