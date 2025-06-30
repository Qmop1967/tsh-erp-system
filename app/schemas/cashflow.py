"""
Cash Flow Management Schemas
مخططات إدارة التدفق النقدي

Pydantic schemas for cash flow models including validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums matching the model enums
class CashBoxTypeEnum(str, Enum):
    SALESPERSON = "SALESPERSON"
    BRANCH = "BRANCH" 
    MAIN = "MAIN"
    PETTY_CASH = "PETTY_CASH"


class TransferStatusEnum(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    RECEIVED = "RECEIVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PaymentMethodEnum(str, Enum):
    CASH = "CASH"
    DIGITAL = "DIGITAL"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"


class RegionEnum(str, Enum):
    KARBALA = "KARBALA"
    NAJAF = "NAJAF"
    BABEL = "BABEL"
    BAGHDAD = "BAGHDAD"
    BASRA = "BASRA"
    MOSUL = "MOSUL"
    ERBIL = "ERBIL"
    DUHOK = "DUHOK"
    SULAYMANIYAH = "SULAYMANIYAH"
    KIRKUK = "KIRKUK"
    ANBAR = "ANBAR"
    DIYALA = "DIYALA"
    SALAHUDDIN = "SALAHUDDIN"
    WASIT = "WASIT"
    QADISIYYAH = "QADISIYYAH"
    MUTHANNA = "MUTHANNA"
    DHI_QAR = "DHI_QAR"
    MAYSAN = "MAYSAN"


class BranchTypeEnum(str, Enum):
    MAIN_WHOLESALE = "MAIN_WHOLESALE"
    DORA_BRANCH = "DORA_BRANCH"
    SALES_OFFICE = "SALES_OFFICE"
    WAREHOUSE = "WAREHOUSE"


# Cash Box Schemas
class CashBoxBase(BaseModel):
    code: str = Field(..., max_length=50)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    box_type: CashBoxTypeEnum
    branch_id: int
    user_id: Optional[int] = None
    balance_iqd_cash: Decimal = Field(0.000, ge=0)
    balance_iqd_digital: Decimal = Field(0.000, ge=0)
    balance_usd_cash: Decimal = Field(0.000, ge=0)
    balance_usd_digital: Decimal = Field(0.000, ge=0)
    balance_rmb_cash: Decimal = Field(0.000, ge=0)
    balance_rmb_digital: Decimal = Field(0.000, ge=0)
    is_active: bool = True
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class CashBoxCreate(CashBoxBase):
    pass


class CashBoxUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    balance_iqd_cash: Optional[Decimal] = Field(None, ge=0)
    balance_iqd_digital: Optional[Decimal] = Field(None, ge=0)
    balance_usd_cash: Optional[Decimal] = Field(None, ge=0)
    balance_usd_digital: Optional[Decimal] = Field(None, ge=0)
    balance_rmb_cash: Optional[Decimal] = Field(None, ge=0)
    balance_rmb_digital: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class CashBox(CashBoxBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_transaction_date: Optional[datetime]
    created_by: Optional[int]
    
    # Computed fields
    total_balance_iqd: Optional[Decimal] = None
    total_balance_usd: Optional[Decimal] = None
    total_balance_rmb: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# Salesperson Region Schemas
class SalespersonRegionBase(BaseModel):
    user_id: int
    region: RegionEnum
    is_primary: bool = False
    is_active: bool = True


class SalespersonRegionCreate(SalespersonRegionBase):
    pass


class SalespersonRegionUpdate(BaseModel):
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class SalespersonRegion(SalespersonRegionBase):
    id: int
    assigned_date: datetime
    created_at: datetime
    assigned_by: Optional[int]
    
    class Config:
        from_attributes = True


# Cash Transaction Schemas
class CashTransactionBase(BaseModel):
    cash_box_id: int
    transaction_type: str = Field(..., max_length=50)  # RECEIPT, PAYMENT, TRANSFER_IN, TRANSFER_OUT
    payment_method: PaymentMethodEnum
    currency_code: str = Field(..., max_length=3)
    amount: Decimal = Field(..., gt=0)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    notes: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = Field(None, max_length=255)
    transaction_date: datetime
    region: Optional[RegionEnum] = None
    location_details: Optional[str] = Field(None, max_length=500)


class CashTransactionCreate(CashTransactionBase):
    pass


class CashTransactionUpdate(BaseModel):
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    notes: Optional[str] = None
    location_details: Optional[str] = Field(None, max_length=500)


class CashTransaction(CashTransactionBase):
    id: int
    transaction_number: str
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


# Cash Transfer Schemas
class CashTransferBase(BaseModel):
    from_cash_box_id: int
    to_cash_box_id: int
    currency_code: str = Field(..., max_length=3)
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethodEnum
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    transfer_reason: Optional[str] = Field(None, max_length=500)
    
    @validator('to_cash_box_id')
    def validate_different_cash_boxes(cls, v, values):
        if 'from_cash_box_id' in values and v == values['from_cash_box_id']:
            raise ValueError('Cannot transfer to the same cash box')
        return v


class CashTransferCreate(CashTransferBase):
    pass


class CashTransferUpdate(BaseModel):
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    transfer_reason: Optional[str] = Field(None, max_length=500)
    admin_notes: Optional[str] = None
    transfer_receipt_url: Optional[str] = Field(None, max_length=500)
    paper_attachment_url: Optional[str] = Field(None, max_length=500)


class CashTransferApproval(BaseModel):
    status: TransferStatusEnum
    admin_notes: Optional[str] = None


class CashTransfer(CashTransferBase):
    id: int
    transfer_number: str
    status: TransferStatusEnum
    requested_date: datetime
    approved_date: Optional[datetime]
    received_date: Optional[datetime]
    requested_by: int
    approved_by: Optional[int]
    received_by: Optional[int]
    admin_notes: Optional[str]
    transfer_receipt_url: Optional[str]
    paper_attachment_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Cash Flow Summary Schemas
class CashFlowSummaryBase(BaseModel):
    branch_id: int
    user_id: Optional[int] = None
    summary_date: datetime
    summary_type: str = Field(..., max_length=20)  # DAILY, WEEKLY, MONTHLY
    total_receipts_iqd: Decimal = Field(0.000, ge=0)
    total_payments_iqd: Decimal = Field(0.000, ge=0)
    total_receipts_usd: Decimal = Field(0.000, ge=0)
    total_payments_usd: Decimal = Field(0.000, ge=0)
    total_receipts_rmb: Decimal = Field(0.000, ge=0)
    total_payments_rmb: Decimal = Field(0.000, ge=0)
    net_flow_iqd: Decimal = 0.000
    net_flow_usd: Decimal = 0.000
    net_flow_rmb: Decimal = 0.000
    total_transactions: int = Field(0, ge=0)
    total_transfers_sent: int = Field(0, ge=0)
    total_transfers_received: int = Field(0, ge=0)


class CashFlowSummaryCreate(CashFlowSummaryBase):
    pass


class CashFlowSummary(CashFlowSummaryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Dashboard Schemas
class BranchCashFlowDashboard(BaseModel):
    """Dashboard data for branch cash flow overview"""
    branch_id: int
    branch_name: str
    branch_type: str
    total_cash_boxes: int
    active_salespeople: int
    
    # Total balances across all cash boxes in branch
    total_iqd_cash: Decimal
    total_iqd_digital: Decimal
    total_usd_cash: Decimal
    total_usd_digital: Decimal
    total_rmb_cash: Decimal
    total_rmb_digital: Decimal
    
    # Today's activity
    today_receipts_iqd: Decimal
    today_payments_iqd: Decimal
    today_receipts_usd: Decimal
    today_payments_usd: Decimal
    today_transactions_count: int
    
    # Pending transfers
    pending_transfers_in: int
    pending_transfers_out: int
    pending_transfers_amount_iqd: Decimal
    pending_transfers_amount_usd: Decimal


class SalespersonCashFlowDashboard(BaseModel):
    """Dashboard data for individual salesperson"""
    user_id: int
    user_name: str
    employee_code: Optional[str]
    assigned_regions: List[RegionEnum]
    
    # Cash box details
    cash_box_id: Optional[int]
    cash_box_code: Optional[str]
    balance_iqd_cash: Decimal
    balance_iqd_digital: Decimal
    balance_usd_cash: Decimal
    balance_usd_digital: Decimal
    
    # Today's activity
    today_receipts_iqd: Decimal
    today_payments_iqd: Decimal
    today_receipts_usd: Decimal
    today_payments_usd: Decimal
    today_transactions_count: int
    
    # Transfer status
    pending_transfers_sent: int
    pending_transfers_received: int
    last_transfer_date: Optional[datetime]


class CashFlowDashboardData(BaseModel):
    """Main dashboard data combining all cash flow information"""
    branches: List[BranchCashFlowDashboard]
    salespeople: List[SalespersonCashFlowDashboard]
    
    # System-wide totals
    system_total_iqd: Decimal
    system_total_usd: Decimal
    system_total_rmb: Decimal
    
    # Activity summary
    total_transactions_today: int
    total_pending_transfers: int
    
    last_updated: datetime


class TransferReceiptData(BaseModel):
    """Data for generating transfer receipts"""
    transfer_id: int
    transfer_number: str
    from_salesperson: str
    to_branch: str
    amount: Decimal
    currency: str
    transfer_date: datetime
    notes: Optional[str]
