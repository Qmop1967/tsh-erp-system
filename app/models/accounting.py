from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.database import Base
from datetime import datetime
import enum


class CurrencyEnum(str, enum.Enum):
    IQD = "IQD"  # Iraqi Dinar
    USD = "USD"  # US Dollar
    RMB = "RMB"  # Chinese Yuan


class LanguageEnum(str, enum.Enum):
    AR = "ar"  # Arabic
    EN = "en"  # English


class AccountTypeEnum(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class JournalTypeEnum(str, enum.Enum):
    GENERAL = "GENERAL"
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    CASH = "CASH"
    BANK = "BANK"


class TransactionStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


class Currency(Base):
    """عملة - Currency"""
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)  # IQD, USD, RMB
    name_ar = Column(String(100), nullable=False)  # دينار عراقي
    name_en = Column(String(100), nullable=False)  # Iraqi Dinar
    symbol = Column(String(10), nullable=False)  # د.ع, $, ¥
    exchange_rate = Column(Numeric(15, 6), nullable=False, default=1.0)  # Rate to base currency
    is_base_currency = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="currency")
    journal_entries = relationship("JournalEntry", back_populates="currency")
    exchange_rates = relationship("ExchangeRate", foreign_keys="ExchangeRate.from_currency_id", back_populates="from_currency")
    pos_sessions = relationship("POSSession", back_populates="currency")
    expenses = relationship("Expense", back_populates="currency")


class ExchangeRate(Base):
    """سعر الصرف - Exchange Rate"""
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    from_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    to_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    rate = Column(Numeric(15, 6), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    from_currency = relationship("Currency", foreign_keys=[from_currency_id])
    to_currency = relationship("Currency", foreign_keys=[to_currency_id])


class ChartOfAccounts(Base):
    """دليل الحسابات - Chart of Accounts"""
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountTypeEnum), nullable=False)
    parent_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    allow_posting = Column(Boolean, default=True)  # Can post transactions to this account
    description_ar = Column(Text)
    description_en = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("ChartOfAccounts", remote_side=[id], back_populates="children")
    children = relationship("ChartOfAccounts", back_populates="parent")
    accounts = relationship("Account", back_populates="chart_account")


class Account(Base):
    """حساب - Account"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    balance_debit = Column(Numeric(15, 2), nullable=False, default=0)
    balance_credit = Column(Numeric(15, 2), nullable=False, default=0)
    balance = Column(Numeric(15, 2), nullable=False, default=0)  # Calculated balance
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chart_account = relationship("ChartOfAccounts", back_populates="accounts")
    currency = relationship("Currency", back_populates="accounts")
    branch = relationship("Branch")
    journal_lines = relationship("JournalLine", back_populates="account")
    expenses = relationship("Expense", back_populates="account")


class Journal(Base):
    """دفتر اليومية - Journal"""
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    journal_type = Column(Enum(JournalTypeEnum), nullable=False)
    is_active = Column(Boolean, default=True)
    description_ar = Column(Text)
    description_en = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="journal")


class JournalEntry(Base):
    """قيد يومية - Journal Entry"""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    reference = Column(String(100))  # Reference to source document
    reference_type = Column(String(50))  # SALE, PURCHASE, PAYMENT, etc.
    reference_id = Column(Integer)  # ID of source document
    
    entry_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    posting_date = Column(DateTime)
    
    description_ar = Column(Text)
    description_en = Column(Text)
    
    total_debit = Column(Numeric(15, 2), nullable=False, default=0)
    total_credit = Column(Numeric(15, 2), nullable=False, default=0)
    
    status = Column(Enum(TransactionStatusEnum), nullable=False, default=TransactionStatusEnum.DRAFT)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    journal = relationship("Journal", back_populates="journal_entries")
    currency = relationship("Currency", back_populates="journal_entries")
    branch = relationship("Branch")
    journal_lines = relationship("JournalLine", back_populates="journal_entry", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    poster = relationship("User", foreign_keys=[posted_by])


class JournalLine(Base):
    """سطر قيد يومية - Journal Line"""
    __tablename__ = "journal_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    debit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="journal_lines")
    account = relationship("Account", back_populates="journal_lines")


class FiscalYear(Base):
    """السنة المالية - Fiscal Year"""
    __tablename__ = "fiscal_years"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AccountingPeriod(Base):
    """فترة محاسبية - Accounting Period"""
    __tablename__ = "accounting_periods"

    id = Column(Integer, primary_key=True, index=True)
    fiscal_year_id = Column(Integer, ForeignKey("fiscal_years.id"), nullable=False)
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fiscal_year = relationship("FiscalYear")
