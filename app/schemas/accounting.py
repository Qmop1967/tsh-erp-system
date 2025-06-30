from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CurrencyEnum(str, Enum):
    IQD = "IQD"
    USD = "USD"
    RMB = "RMB"


class LanguageEnum(str, Enum):
    AR = "ar"
    EN = "en"


class AccountTypeEnum(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class JournalTypeEnum(str, Enum):
    GENERAL = "GENERAL"
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    CASH = "CASH"
    BANK = "BANK"


class TransactionStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


# Currency Schemas
class CurrencyBase(BaseModel):
    code: str = Field(..., max_length=3)
    name_ar: str = Field(..., max_length=100)
    name_en: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=10)
    exchange_rate: Decimal = Field(1.0, gt=0)
    is_base_currency: bool = False
    is_active: bool = True

    @validator('code')
    def validate_code(cls, v):
        if v not in ['IQD', 'USD', 'RMB']:
            raise ValueError('Currency code must be IQD, USD, or RMB')
        return v.upper()


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    is_base_currency: Optional[bool] = None
    is_active: Optional[bool] = None


class Currency(CurrencyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Exchange Rate Schemas
class ExchangeRateBase(BaseModel):
    from_currency_id: int
    to_currency_id: int
    rate: Decimal = Field(..., gt=0)
    date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRate(ExchangeRateBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chart of Accounts Schemas
class ChartOfAccountsBase(BaseModel):
    code: str = Field(..., max_length=20)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    account_type: AccountTypeEnum
    parent_id: Optional[int] = None
    level: int = 1
    is_active: bool = True
    allow_posting: bool = True
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass


class ChartOfAccountsUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    account_type: Optional[AccountTypeEnum] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    allow_posting: Optional[bool] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class ChartOfAccounts(ChartOfAccountsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Account Schemas
class AccountBase(BaseModel):
    chart_account_id: int
    currency_id: int
    branch_id: Optional[int] = None
    balance_debit: Decimal = Field(0, ge=0)
    balance_credit: Decimal = Field(0, ge=0)
    balance: Decimal = 0
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    balance_debit: Optional[Decimal] = Field(None, ge=0)
    balance_credit: Optional[Decimal] = Field(None, ge=0)
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class Account(AccountBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Journal Schemas
class JournalBase(BaseModel):
    code: str = Field(..., max_length=20)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    journal_type: JournalTypeEnum
    is_active: bool = True
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class JournalCreate(JournalBase):
    pass


class JournalUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    journal_type: Optional[JournalTypeEnum] = None
    is_active: Optional[bool] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class Journal(JournalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Journal Line Schemas
class JournalLineBase(BaseModel):
    account_id: int
    line_number: int
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    debit_amount: Decimal = Field(0, ge=0)
    credit_amount: Decimal = Field(0, ge=0)

    @validator('debit_amount', 'credit_amount')
    def validate_amounts(cls, v, values):
        # Either debit or credit should be greater than 0, but not both
        if 'debit_amount' in values and 'credit_amount' in values:
            if values['debit_amount'] > 0 and v > 0:
                raise ValueError('Cannot have both debit and credit amounts')
            if values['debit_amount'] == 0 and v == 0:
                raise ValueError('Either debit or credit amount must be greater than 0')
        return v


class JournalLineCreate(JournalLineBase):
    pass


class JournalLine(JournalLineBase):
    id: int
    journal_entry_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    journal_id: int
    currency_id: int
    branch_id: Optional[int] = None
    entry_number: str = Field(..., max_length=50)
    reference: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    entry_date: datetime = Field(default_factory=datetime.utcnow)
    posting_date: Optional[datetime] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    status: TransactionStatusEnum = TransactionStatusEnum.DRAFT


class JournalEntryCreate(JournalEntryBase):
    journal_lines: List[JournalLineCreate]

    @validator('journal_lines')
    def validate_journal_lines(cls, v):
        if len(v) < 2:
            raise ValueError('Journal entry must have at least 2 lines')
        
        total_debit = sum(line.debit_amount for line in v)
        total_credit = sum(line.credit_amount for line in v)
        
        if total_debit != total_credit:
            raise ValueError('Total debit must equal total credit')
        
        return v


class JournalEntryUpdate(BaseModel):
    reference: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    entry_date: Optional[datetime] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    status: Optional[TransactionStatusEnum] = None


class JournalEntry(JournalEntryBase):
    id: int
    total_debit: Decimal
    total_credit: Decimal
    posted_by: Optional[int]
    posted_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    journal_lines: List[JournalLine] = []
    
    class Config:
        from_attributes = True


# Fiscal Year Schemas
class FiscalYearBase(BaseModel):
    name_ar: str = Field(..., max_length=100)
    name_en: str = Field(..., max_length=100)
    start_date: datetime
    end_date: datetime
    is_current: bool = False
    is_closed: bool = False

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class FiscalYearCreate(FiscalYearBase):
    pass


class FiscalYearUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    is_closed: Optional[bool] = None


class FiscalYear(FiscalYearBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Accounting Period Schemas
class AccountingPeriodBase(BaseModel):
    fiscal_year_id: int
    name_ar: str = Field(..., max_length=100)
    name_en: str = Field(..., max_length=100)
    start_date: datetime
    end_date: datetime
    is_closed: bool = False

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class AccountingPeriodCreate(AccountingPeriodBase):
    pass


class AccountingPeriodUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_closed: Optional[bool] = None


class AccountingPeriod(AccountingPeriodBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Report Schemas
class BalanceSheetItem(BaseModel):
    """عنصر في الميزانية العمومية"""
    account_code: str
    account_name_ar: str
    account_name_en: str
    account_type: AccountTypeEnum
    balance: Decimal
    currency_code: str


class BalanceSheet(BaseModel):
    """الميزانية العمومية"""
    as_of_date: datetime
    currency_code: str
    assets: List[BalanceSheetItem]
    liabilities: List[BalanceSheetItem]
    equity: List[BalanceSheetItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal


class IncomeStatementItem(BaseModel):
    """عنصر في قائمة الدخل"""
    account_code: str
    account_name_ar: str
    account_name_en: str
    account_type: AccountTypeEnum
    amount: Decimal
    currency_code: str


class IncomeStatement(BaseModel):
    """قائمة الدخل"""
    from_date: datetime
    to_date: datetime
    currency_code: str
    revenues: List[IncomeStatementItem]
    expenses: List[IncomeStatementItem]
    total_revenue: Decimal
    total_expenses: Decimal
    net_income: Decimal


class TrialBalance(BaseModel):
    """ميزان المراجعة"""
    as_of_date: datetime
    currency_code: str
    accounts: List[dict]  # Account details with debit/credit balances
    total_debit: Decimal
    total_credit: Decimal
