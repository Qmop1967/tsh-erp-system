"""
Cash Flow Management Models
نماذج إدارة التدفق النقدي

This module contains models for managing cash flow, cash boxes, transfers, and branch-specific accounting.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.db.database import Base


class CashBoxTypeEnum(enum.Enum):
    """أنواع صناديق النقد"""
    SALESPERSON = "SALESPERSON"  # صندوق مندوب مبيعات
    BRANCH = "BRANCH"            # صندوق فرع
    MAIN = "MAIN"               # الصندوق الرئيسي
    PETTY_CASH = "PETTY_CASH"   # المصروفات النثرية


class TransferStatusEnum(enum.Enum):
    """حالات التحويل"""
    PENDING = "PENDING"         # في الانتظار
    APPROVED = "APPROVED"       # موافق عليه
    RECEIVED = "RECEIVED"       # تم الاستلام
    REJECTED = "REJECTED"       # مرفوض
    CANCELLED = "CANCELLED"     # ملغي


class CashPaymentMethodEnum(enum.Enum):
    """طرق الدفع النقدي"""
    CASH = "CASH"              # نقدي
    DIGITAL = "DIGITAL"        # رقمي
    BANK_TRANSFER = "BANK_TRANSFER"  # تحويل بنكي
    CHECK = "CHECK"            # شيك


class RegionEnum(enum.Enum):
    """المناطق الجغرافية"""
    KARBALA = "KARBALA"        # كربلاء
    NAJAF = "NAJAF"            # النجف
    BABEL = "BABEL"            # بابل
    BAGHDAD = "BAGHDAD"        # بغداد
    BASRA = "BASRA"            # البصرة
    MOSUL = "MOSUL"            # الموصل
    ERBIL = "ERBIL"            # أربيل
    DUHOK = "DUHOK"            # دهوك
    SULAYMANIYAH = "SULAYMANIYAH"  # السليمانية
    KIRKUK = "KIRKUK"          # كركوك
    ANBAR = "ANBAR"            # الأنبار
    DIYALA = "DIYALA"          # ديالى
    SALAHUDDIN = "SALAHUDDIN" # صلاح الدين
    WASIT = "WASIT"            # واسط
    QADISIYYAH = "QADISIYYAH"  # القادسية
    MUTHANNA = "MUTHANNA"      # المثنى
    DHI_QAR = "DHI_QAR"        # ذي قار
    MAYSAN = "MAYSAN"          # ميسان


class BranchTypeEnum(enum.Enum):
    """أنواع الفروع"""
    MAIN_WHOLESALE = "MAIN_WHOLESALE"  # الفرع الرئيسي للجملة
    DORA_BRANCH = "DORA_BRANCH"        # فرع الدورة
    SALES_OFFICE = "SALES_OFFICE"      # مكتب مبيعات
    WAREHOUSE = "WAREHOUSE"            # مستودع


class CashBox(Base):
    """
    صندوق النقد - Cash Box
    Represents a cash box for tracking money in different currencies
    """
    __tablename__ = "cash_boxes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    box_type = Column(SQLEnum(CashBoxTypeEnum), nullable=False)
    
    # Branch and User relationships
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For salesperson boxes
    
    # Currency balances
    balance_iqd_cash = Column(Numeric(15, 3), default=0.000, nullable=False)      # رصيد نقدي دينار عراقي
    balance_iqd_digital = Column(Numeric(15, 3), default=0.000, nullable=False)   # رصيد رقمي دينار عراقي
    balance_usd_cash = Column(Numeric(15, 3), default=0.000, nullable=False)      # رصيد نقدي دولار
    balance_usd_digital = Column(Numeric(15, 3), default=0.000, nullable=False)   # رصيد رقمي دولار
    balance_rmb_cash = Column(Numeric(15, 3), default=0.000, nullable=False)      # رصيد نقدي يوان
    balance_rmb_digital = Column(Numeric(15, 3), default=0.000, nullable=False)   # رصيد رقمي يوان
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    last_transaction_date = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    branch = relationship("Branch", back_populates="cash_boxes")
    user = relationship("User", foreign_keys=[user_id], back_populates="cash_boxes")
    creator = relationship("User", foreign_keys=[created_by])
    transactions = relationship("CashTransaction", back_populates="cash_box")
    transfers_sent = relationship("CashTransfer", foreign_keys="CashTransfer.from_cash_box_id", back_populates="from_cash_box")
    transfers_received = relationship("CashTransfer", foreign_keys="CashTransfer.to_cash_box_id", back_populates="to_cash_box")
    
    def __repr__(self):
        return f"<CashBox {self.code}: {self.name_en}>"


class SalespersonRegion(Base):
    """
    مناطق مندوب المبيعات - Salesperson Regions
    Links salespeople to their assigned regions
    """
    __tablename__ = "salesperson_regions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Salesperson
    region = Column(SQLEnum(RegionEnum), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # المنطقة الأساسية
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    assigned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    salesperson = relationship("User", foreign_keys=[user_id], back_populates="assigned_regions")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f"<SalespersonRegion {self.user_id}: {self.region.value}>"


class CashTransaction(Base):
    """
    معاملة نقدية - Cash Transaction
    Records all cash movements in and out of cash boxes
    """
    __tablename__ = "cash_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(100), unique=True, nullable=False, index=True)
    cash_box_id = Column(Integer, ForeignKey("cash_boxes.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # RECEIPT, PAYMENT, TRANSFER_IN, TRANSFER_OUT
    payment_method = Column(SQLEnum(CashPaymentMethodEnum), nullable=False)
    currency_code = Column(String(3), nullable=False)  # IQD, USD, RMB
    amount = Column(Numeric(15, 3), nullable=False)
    
    # References
    reference_type = Column(String(50))  # ORDER, INVOICE, TRANSFER, EXPENSE
    reference_id = Column(Integer)
    reference_number = Column(String(100))
    
    # Description and notes
    description_ar = Column(Text)
    description_en = Column(Text)
    notes = Column(Text)
    
    # Customer/Supplier info
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String(255))
    
    # Location and date
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    region = Column(SQLEnum(RegionEnum))
    location_details = Column(String(500))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    cash_box = relationship("CashBox", back_populates="transactions")
    customer = relationship("User", foreign_keys=[customer_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<CashTransaction {self.transaction_number}: {self.amount} {self.currency_code}>"


class CashTransfer(Base):
    """
    تحويل نقدي - Cash Transfer
    Represents money transfers between cash boxes with approval workflow
    """
    __tablename__ = "cash_transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Transfer details
    from_cash_box_id = Column(Integer, ForeignKey("cash_boxes.id"), nullable=False)
    to_cash_box_id = Column(Integer, ForeignKey("cash_boxes.id"), nullable=False)
    currency_code = Column(String(3), nullable=False)
    amount = Column(Numeric(15, 3), nullable=False)
    payment_method = Column(SQLEnum(CashPaymentMethodEnum), nullable=False)
    
    # Status and workflow
    status = Column(SQLEnum(TransferStatusEnum), default=TransferStatusEnum.PENDING, nullable=False)
    
    # Descriptions and notes
    description_ar = Column(Text)
    description_en = Column(Text)
    transfer_reason = Column(String(500))
    admin_notes = Column(Text)
    
    # Dates
    requested_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_date = Column(DateTime)
    received_date = Column(DateTime)
    
    # User tracking
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    received_by = Column(Integer, ForeignKey("users.id"))
    
    # Document attachments
    transfer_receipt_url = Column(String(500))  # URL to transfer receipt image
    paper_attachment_url = Column(String(500))  # URL to physical paper attachment
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_cash_box = relationship("CashBox", foreign_keys=[from_cash_box_id], back_populates="transfers_sent")
    to_cash_box = relationship("CashBox", foreign_keys=[to_cash_box_id], back_populates="transfers_received")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
    receiver = relationship("User", foreign_keys=[received_by])
    
    def __repr__(self):
        return f"<CashTransfer {self.transfer_number}: {self.amount} {self.currency_code} ({self.status.value})>"


class CashFlowSummary(Base):
    """
    ملخص التدفق النقدي - Cash Flow Summary
    Daily/Monthly summaries for dashboard reporting
    """
    __tablename__ = "cash_flow_summaries"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For salesperson summaries
    summary_date = Column(DateTime, nullable=False)
    summary_type = Column(String(20), nullable=False)  # DAILY, WEEKLY, MONTHLY
    
    # Cash flow totals by currency
    total_receipts_iqd = Column(Numeric(15, 3), default=0.000)
    total_payments_iqd = Column(Numeric(15, 3), default=0.000)
    total_receipts_usd = Column(Numeric(15, 3), default=0.000)
    total_payments_usd = Column(Numeric(15, 3), default=0.000)
    total_receipts_rmb = Column(Numeric(15, 3), default=0.000)
    total_payments_rmb = Column(Numeric(15, 3), default=0.000)
    
    # Net cash flow
    net_flow_iqd = Column(Numeric(15, 3), default=0.000)
    net_flow_usd = Column(Numeric(15, 3), default=0.000)
    net_flow_rmb = Column(Numeric(15, 3), default=0.000)
    
    # Transaction counts
    total_transactions = Column(Integer, default=0)
    total_transfers_sent = Column(Integer, default=0)
    total_transfers_received = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branch = relationship("Branch")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<CashFlowSummary {self.summary_date}: Branch {self.branch_id}>"
