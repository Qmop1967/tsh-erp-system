from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, date
from app.models.accounting import (
    Currency, ExchangeRate, ChartOfAccounts, Account, 
    Journal, JournalEntry, JournalLine, FiscalYear, AccountingPeriod,
    AccountTypeEnum, TransactionStatusEnum
)
from app.schemas.accounting import (
    CurrencyCreate, CurrencyUpdate, ExchangeRateCreate,
    ChartOfAccountsCreate, ChartOfAccountsUpdate,
    AccountCreate, AccountUpdate,
    JournalCreate, JournalUpdate,
    JournalEntryCreate, JournalEntryUpdate,
    FiscalYearCreate, FiscalYearUpdate,
    AccountingPeriodCreate, AccountingPeriodUpdate,
    BalanceSheet, IncomeStatement, TrialBalance
)
from fastapi import HTTPException, status


class CurrencyService:
    """خدمة إدارة العملات"""

    @staticmethod
    def create_currency(db: Session, currency: CurrencyCreate) -> Currency:
        """إنشاء عملة جديدة"""
        # التحقق من عدم تكرار رمز العملة
        existing_currency = db.query(Currency).filter(Currency.code == currency.code).first()
        if existing_currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency code already exists"
            )
        
        # إذا كانت العملة الأساسية، تعطيل العملات الأساسية الأخرى
        if currency.is_base_currency:
            db.query(Currency).filter(Currency.is_base_currency == True).update(
                {"is_base_currency": False}
            )
        
        db_currency = Currency(**currency.dict())
        db.add(db_currency)
        db.commit()
        db.refresh(db_currency)
        return db_currency

    @staticmethod
    def get_currencies(db: Session, skip: int = 0, limit: int = 100, 
                      active_only: bool = True) -> List[Currency]:
        """الحصول على قائمة العملات"""
        query = db.query(Currency)
        if active_only:
            query = query.filter(Currency.is_active == True)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_currency(db: Session, currency_id: int) -> Currency:
        """الحصول على عملة محددة"""
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Currency not found"
            )
        return currency

    @staticmethod
    def update_currency(db: Session, currency_id: int, currency_update: CurrencyUpdate) -> Currency:
        """تحديث بيانات عملة"""
        currency = CurrencyService.get_currency(db, currency_id)
        
        # إذا كانت العملة الأساسية، تعطيل العملات الأساسية الأخرى
        if currency_update.is_base_currency and currency_update.is_base_currency != currency.is_base_currency:
            db.query(Currency).filter(Currency.is_base_currency == True).update(
                {"is_base_currency": False}
            )
        
        update_data = currency_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(currency, field, value)
        
        currency.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(currency)
        return currency

    @staticmethod
    def get_base_currency(db: Session) -> Currency:
        """الحصول على العملة الأساسية"""
        currency = db.query(Currency).filter(Currency.is_base_currency == True).first()
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No base currency found"
            )
        return currency

    @staticmethod
    def convert_currency(db: Session, amount: Decimal, from_currency_id: int, 
                        to_currency_id: int, date: datetime = None) -> Decimal:
        """تحويل عملة"""
        if from_currency_id == to_currency_id:
            return amount
        
        if not date:
            date = datetime.utcnow()
        
        # البحث عن سعر الصرف
        exchange_rate = db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.from_currency_id == from_currency_id,
                ExchangeRate.to_currency_id == to_currency_id,
                ExchangeRate.date <= date,
                ExchangeRate.is_active == True
            )
        ).order_by(ExchangeRate.date.desc()).first()
        
        if not exchange_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate not found"
            )
        
        return amount * exchange_rate.rate


class ChartOfAccountsService:
    """خدمة إدارة دليل الحسابات"""

    @staticmethod
    def create_chart_account(db: Session, chart_account: ChartOfAccountsCreate) -> ChartOfAccounts:
        """إنشاء حساب في دليل الحسابات"""
        # التحقق من عدم تكرار رمز الحساب
        existing_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.code == chart_account.code
        ).first()
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account code already exists"
            )
        
        # تحديد المستوى إذا كان هناك حساب أب
        if chart_account.parent_id:
            parent = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == chart_account.parent_id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent account not found"
                )
            chart_account.level = parent.level + 1
        
        db_chart_account = ChartOfAccounts(**chart_account.dict())
        db.add(db_chart_account)
        db.commit()
        db.refresh(db_chart_account)
        return db_chart_account

    @staticmethod
    def get_chart_accounts(db: Session, account_type: Optional[str] = None,
                          parent_id: Optional[int] = None, active_only: bool = True) -> List[ChartOfAccounts]:
        """الحصول على دليل الحسابات"""
        query = db.query(ChartOfAccounts)
        
        if active_only:
            query = query.filter(ChartOfAccounts.is_active == True)
        
        if account_type:
            query = query.filter(ChartOfAccounts.account_type == account_type)
        
        if parent_id is not None:
            query = query.filter(ChartOfAccounts.parent_id == parent_id)
        
        return query.order_by(ChartOfAccounts.code).all()

    @staticmethod
    def get_charts_of_accounts(db: Session, account_type: Optional[str] = None,
                          parent_id: Optional[int] = None, active_only: bool = True) -> List[ChartOfAccounts]:
        """الحصول على دليل الحسابات - Get chart of accounts"""
        return ChartOfAccountsService.get_chart_accounts(db, account_type, parent_id, active_only)

    @staticmethod
    def create_chart_of_accounts(db: Session, chart_account: ChartOfAccountsCreate) -> ChartOfAccounts:
        """إنشاء حساب في دليل الحسابات - Create chart of accounts entry"""
        return ChartOfAccountsService.create_chart_account(db, chart_account)

    @staticmethod
    def get_chart_of_accounts(db: Session, chart_id: int) -> ChartOfAccounts:
        """الحصول على حساب محدد من دليل الحسابات - Get specific chart of accounts entry"""
        chart = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == chart_id).first()
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart of accounts entry not found"
            )
        return chart

    @staticmethod
    def update_chart_of_accounts(db: Session, chart_id: int, chart_update: ChartOfAccountsUpdate) -> ChartOfAccounts:
        """تحديث حساب في دليل الحسابات - Update chart of accounts entry"""
        chart = ChartOfAccountsService.get_chart_of_accounts(db, chart_id)
        
        update_data = chart_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chart, field, value)
        
        chart.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(chart)
        return chart


class JournalService:
    """خدمة إدارة دفاتر اليومية"""

    @staticmethod
    def create_journal_entry(db: Session, journal_entry: JournalEntryCreate, user_id: int) -> JournalEntry:
        """إنشاء قيد يومية"""
        # التحقق من توازن القيد
        total_debit = sum(line.debit_amount for line in journal_entry.journal_lines)
        total_credit = sum(line.credit_amount for line in journal_entry.journal_lines)
        
        if total_debit != total_credit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total debit must equal total credit"
            )
        
        # إنشاء القيد
        db_entry = JournalEntry(
            **journal_entry.dict(exclude={'journal_lines'}),
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=user_id
        )
        db.add(db_entry)
        db.flush()  # للحصول على ID القيد
        
        # إنشاء سطور القيد
        for line_data in journal_entry.journal_lines:
            db_line = JournalLine(
                **line_data.dict(),
                journal_entry_id=db_entry.id
            )
            db.add(db_line)
        
        db.commit()
        db.refresh(db_entry)
        return db_entry

    @staticmethod
    def post_journal_entry(db: Session, entry_id: int, user_id: int) -> JournalEntry:
        """ترحيل قيد يومية"""
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        if entry.status != TransactionStatusEnum.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft entries can be posted"
            )
        
        # تحديث أرصدة الحسابات
        for line in entry.journal_lines:
            account = db.query(Account).filter(Account.id == line.account_id).first()
            if account:
                account.balance_debit += line.debit_amount
                account.balance_credit += line.credit_amount
                
                # حساب الرصيد حسب نوع الحساب
                chart_account = account.chart_account
                if chart_account.account_type in [AccountTypeEnum.ASSET, AccountTypeEnum.EXPENSE]:
                    account.balance = account.balance_debit - account.balance_credit
                else:
                    account.balance = account.balance_credit - account.balance_debit
        
        # تحديث حالة القيد
        entry.status = TransactionStatusEnum.POSTED
        entry.posted_by = user_id
        entry.posted_at = datetime.utcnow()
        entry.posting_date = datetime.utcnow()
        
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_journals(db: Session, skip: int = 0, limit: int = 100) -> List[Journal]:
        """الحصول على قائمة دفاتر اليومية"""
        return db.query(Journal).offset(skip).limit(limit).all()

    @staticmethod
    def create_journal(db: Session, journal: JournalCreate) -> Journal:
        """إنشاء دفتر يومية جديد"""
        db_journal = Journal(**journal.dict())
        db.add(db_journal)
        db.commit()
        db.refresh(db_journal)
        return db_journal

    @staticmethod
    def get_journal(db: Session, journal_id: int) -> Journal:
        """الحصول على دفتر يومية محدد"""
        journal = db.query(Journal).filter(Journal.id == journal_id).first()
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal not found"
            )
        return journal

    @staticmethod
    def update_journal(db: Session, journal_id: int, journal_update: JournalUpdate) -> Journal:
        """تحديث بيانات دفتر يومية"""
        journal = JournalService.get_journal(db, journal_id)
        
        update_data = journal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(journal, field, value)
        
        journal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(journal)
        return journal


class AccountingReportService:
    """خدمة التقارير المحاسبية"""

    @staticmethod
    def get_trial_balance(db: Session, currency_id: int, as_of_date: datetime = None) -> TrialBalance:
        """ميزان المراجعة"""
        if not as_of_date:
            as_of_date = datetime.utcnow()
        
        # الحصول على جميع الحسابات مع الأرصدة
        accounts = db.query(Account).filter(
            Account.currency_id == currency_id,
            Account.is_active == True
        ).all()
        
        trial_balance_accounts = []
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        
        for account in accounts:
            if account.balance_debit > 0 or account.balance_credit > 0:
                account_data = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "debit_balance": account.balance_debit,
                    "credit_balance": account.balance_credit
                }
                trial_balance_accounts.append(account_data)
                total_debit += account.balance_debit
                total_credit += account.balance_credit
        
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        
        return TrialBalance(
            as_of_date=as_of_date,
            currency_code=currency.code,
            accounts=trial_balance_accounts,
            total_debit=total_debit,
            total_credit=total_credit
        )

    @staticmethod
    def get_balance_sheet(db: Session, currency_id: int, as_of_date: datetime = None) -> BalanceSheet:
        """الميزانية العمومية"""
        if not as_of_date:
            as_of_date = datetime.utcnow()
        
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        
        # الأصول
        assets = db.query(Account).join(ChartOfAccounts).filter(
            Account.currency_id == currency_id,
            ChartOfAccounts.account_type == AccountTypeEnum.ASSET,
            Account.is_active == True
        ).all()
        
        # الخصوم
        liabilities = db.query(Account).join(ChartOfAccounts).filter(
            Account.currency_id == currency_id,
            ChartOfAccounts.account_type == AccountTypeEnum.LIABILITY,
            Account.is_active == True
        ).all()
        
        # حقوق الملكية
        equity = db.query(Account).join(ChartOfAccounts).filter(
            Account.currency_id == currency_id,
            ChartOfAccounts.account_type == AccountTypeEnum.EQUITY,
            Account.is_active == True
        ).all()
        
        # بناء التقرير
        assets_items = []
        liabilities_items = []
        equity_items = []
        
        total_assets = Decimal(0)
        total_liabilities = Decimal(0)
        total_equity = Decimal(0)
        
        for account in assets:
            if account.balance != 0:
                asset_item = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "account_type": account.chart_account.account_type,
                    "balance": account.balance,
                    "currency_code": currency.code
                }
                assets_items.append(asset_item)
                total_assets += account.balance
        
        for account in liabilities:
            if account.balance != 0:
                liability_item = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "account_type": account.chart_account.account_type,
                    "balance": account.balance,
                    "currency_code": currency.code
                }
                liabilities_items.append(liability_item)
                total_liabilities += account.balance
        
        for account in equity:
            if account.balance != 0:
                equity_item = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "account_type": account.chart_account.account_type,
                    "balance": account.balance,
                    "currency_code": currency.code
                }
                equity_items.append(equity_item)
                total_equity += account.balance
        
        return BalanceSheet(
            as_of_date=as_of_date,
            currency_code=currency.code,
            assets=assets_items,
            liabilities=liabilities_items,
            equity=equity_items,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            total_equity=total_equity
        )

    @staticmethod
    def get_income_statement(db: Session, currency_id: int, 
                           from_date: datetime, to_date: datetime) -> IncomeStatement:
        """قائمة الدخل"""
        currency = db.query(Currency).filter(Currency.id == currency_id).first()
        
        # الإيرادات
        revenues = db.query(Account).join(ChartOfAccounts).filter(
            Account.currency_id == currency_id,
            ChartOfAccounts.account_type == AccountTypeEnum.REVENUE,
            Account.is_active == True
        ).all()
        
        # المصروفات
        expenses = db.query(Account).join(ChartOfAccounts).filter(
            Account.currency_id == currency_id,
            ChartOfAccounts.account_type == AccountTypeEnum.EXPENSE,
            Account.is_active == True
        ).all()
        
        # بناء التقرير
        revenue_items = []
        expense_items = []
        
        total_revenue = Decimal(0)
        total_expenses = Decimal(0)
        
        for account in revenues:
            if account.balance != 0:
                revenue_item = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "account_type": account.chart_account.account_type,
                    "amount": account.balance,
                    "currency_code": currency.code
                }
                revenue_items.append(revenue_item)
                total_revenue += account.balance
        
        for account in expenses:
            if account.balance != 0:
                expense_item = {
                    "account_code": account.chart_account.code,
                    "account_name_ar": account.chart_account.name_ar,
                    "account_name_en": account.chart_account.name_en,
                    "account_type": account.chart_account.account_type,
                    "amount": account.balance,
                    "currency_code": currency.code
                }
                expense_items.append(expense_item)
                total_expenses += account.balance
        
        net_income = total_revenue - total_expenses
        
        return IncomeStatement(
            from_date=from_date,
            to_date=to_date,
            currency_code=currency.code,
            revenues=revenue_items,
            expenses=expense_items,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_income=net_income
        )


class AccountingService:
    """خدمة المحاسبة الرئيسية - Main Accounting Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.currency_service = CurrencyService()
        self.chart_service = ChartOfAccountsService()
        self.journal_service = JournalService()
        self.reporting_service = AccountingReportService()
    
    # Currency methods
    def get_currencies(self):
        return self.currency_service.get_currencies(self.db)
    
    def create_currency(self, currency: CurrencyCreate):
        return self.currency_service.create_currency(self.db, currency)
    
    def get_currency(self, currency_id: int):
        return self.currency_service.get_currency(self.db, currency_id)
    
    def update_currency(self, currency_id: int, currency: CurrencyUpdate):
        return self.currency_service.update_currency(self.db, currency_id, currency)
    
    # Exchange Rate methods - simple implementations
    def get_exchange_rates(self, from_currency: str = None, to_currency: str = None, effective_date: date = None):
        query = self.db.query(ExchangeRate)
        if from_currency:
            query = query.join(Currency, ExchangeRate.from_currency_id == Currency.id).filter(Currency.code == from_currency)
        if to_currency:
            query = query.join(Currency, ExchangeRate.to_currency_id == Currency.id).filter(Currency.code == to_currency)
        if effective_date:
            query = query.filter(ExchangeRate.date <= effective_date)
        return query.order_by(ExchangeRate.date.desc()).all()
    
    def create_exchange_rate(self, rate: ExchangeRateCreate):
        db_rate = ExchangeRate(**rate.dict())
        self.db.add(db_rate)
        self.db.commit()
        self.db.refresh(db_rate)
        return db_rate
    
    def get_latest_exchange_rate(self, from_currency: str, to_currency: str):
        from_curr = self.db.query(Currency).filter(Currency.code == from_currency).first()
        to_curr = self.db.query(Currency).filter(Currency.code == to_currency).first()
        if not from_curr or not to_curr:
            return None
        
        latest_rate = self.db.query(ExchangeRate).filter(
            ExchangeRate.from_currency_id == from_curr.id,
            ExchangeRate.to_currency_id == to_curr.id,
            ExchangeRate.is_active == True
        ).order_by(ExchangeRate.date.desc()).first()
        
        return latest_rate.rate if latest_rate else None
    
    # Chart of Accounts methods
    def get_charts_of_accounts(self):
        return self.chart_service.get_charts_of_accounts(self.db)
    
    def create_chart_of_accounts(self, chart: ChartOfAccountsCreate):
        return self.chart_service.create_chart_of_accounts(self.db, chart)
    
    def get_chart_of_accounts(self, chart_id: int):
        return self.chart_service.get_chart_of_accounts(self.db, chart_id)
    
    # Account methods - simple implementations
    def get_accounts(self, chart_id: int = None, account_type: str = None, parent_id: int = None):
        query = self.db.query(Account)
        if chart_id:
            query = query.filter(Account.chart_account_id == chart_id)
        return query.all()
    
    def create_account(self, account: AccountCreate):
        db_account = Account(**account.dict())
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def get_account(self, account_id: int):
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def update_account(self, account_id: int, account: AccountUpdate):
        db_account = self.get_account(account_id)
        if db_account:
            for field, value in account.dict(exclude_unset=True).items():
                setattr(db_account, field, value)
            self.db.commit()
            self.db.refresh(db_account)
        return db_account
    
    # Journal methods
    def get_journals(self):
        return self.journal_service.get_journals(self.db)
    
    def create_journal(self, journal: JournalCreate):
        return self.journal_service.create_journal(self.db, journal)
    
    def get_journal(self, journal_id: int):
        return self.journal_service.get_journal(self.db, journal_id)
    
    # Journal Entry methods - simple implementations
    def get_journal_entries(self, journal_id: int = None, period_id: int = None, start_date: date = None, end_date: date = None):
        query = self.db.query(JournalEntry)
        if journal_id:
            query = query.filter(JournalEntry.journal_id == journal_id)
        if period_id:
            query = query.filter(JournalEntry.period_id == period_id)
        if start_date:
            query = query.filter(JournalEntry.entry_date >= start_date)
        if end_date:
            query = query.filter(JournalEntry.entry_date <= end_date)
        return query.all()
    
    def create_journal_entry(self, entry: JournalEntryCreate):
        db_entry = JournalEntry(**entry.dict(exclude={'lines'}))
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        
        # Add journal lines
        for line_data in entry.lines:
            line_data.journal_entry_id = db_entry.id
            db_line = JournalLine(**line_data.dict())
            self.db.add(db_line)
        
        self.db.commit()
        return db_entry
    
    def get_journal_entry(self, entry_id: int):
        return self.db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    
    def post_journal_entry(self, entry_id: int):
        entry = self.get_journal_entry(entry_id)
        if entry and entry.status == "DRAFT":
            entry.status = "POSTED"
            entry.posted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def reverse_journal_entry(self, entry_id: int):
        original_entry = self.get_journal_entry(entry_id)
        if not original_entry or original_entry.status != "POSTED":
            return None
        
        # Create reverse entry
        reverse_entry = JournalEntry(
            journal_id=original_entry.journal_id,
            period_id=original_entry.period_id,
            currency_id=original_entry.currency_id,
            entry_number=f"REV-{original_entry.entry_number}",
            reference=f"Reversal of {original_entry.reference}",
            description_ar=f"عكس {original_entry.description_ar}",
            description_en=f"Reversal of {original_entry.description_en}",
            total_debit=original_entry.total_credit,
            total_credit=original_entry.total_debit,
            status="POSTED",
            posted_at=datetime.utcnow(),
            entry_date=datetime.utcnow().date()
        )
        
        self.db.add(reverse_entry)
        self.db.commit()
        self.db.refresh(reverse_entry)
        
        # Reverse the lines
        for line in original_entry.lines:
            reverse_line = JournalLine(
                journal_entry_id=reverse_entry.id,
                account_id=line.account_id,
                description_ar=f"عكس {line.description_ar}",
                description_en=f"Reversal of {line.description_en}",
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount
            )
            self.db.add(reverse_line)
        
        self.db.commit()
        return reverse_entry
    
    # Fiscal Year and Period methods - simple implementations
    def get_fiscal_years(self):
        return self.db.query(FiscalYear).all()
    
    def create_fiscal_year(self, fiscal_year: FiscalYearCreate):
        db_fiscal_year = FiscalYear(**fiscal_year.dict())
        self.db.add(db_fiscal_year)
        self.db.commit()
        self.db.refresh(db_fiscal_year)
        return db_fiscal_year
    
    def get_accounting_periods(self, fiscal_year_id: int = None):
        query = self.db.query(AccountingPeriod)
        if fiscal_year_id:
            query = query.filter(AccountingPeriod.fiscal_year_id == fiscal_year_id)
        return query.all()
    
    def create_accounting_period(self, period: AccountingPeriodCreate):
        db_period = AccountingPeriod(**period.dict())
        self.db.add(db_period)
        self.db.commit()
        self.db.refresh(db_period)
        return db_period
    
    def close_accounting_period(self, period_id: int):
        period = self.db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id).first()
        if period and not period.is_closed:
            period.is_closed = True
            self.db.commit()
            return True
        return False
    
    # Reporting methods
    def generate_trial_balance(self, period_id: int, chart_id: int = None):
        return self.reporting_service.generate_trial_balance(self.db, period_id, chart_id)
    
    def generate_balance_sheet(self, period_id: int, chart_id: int = None):
        return self.reporting_service.generate_balance_sheet(self.db, period_id, chart_id)
    
    def generate_income_statement(self, period_id: int, chart_id: int = None):
        return self.reporting_service.generate_income_statement(self.db, period_id, chart_id)
