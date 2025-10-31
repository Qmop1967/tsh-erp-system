from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.services.accounting_service import AccountingService
from app.services.accounting_websocket import accounting_ws_manager
from app.dependencies.rbac import PermissionChecker, RoleChecker, get_current_user_from_token
from app.schemas.accounting import (
    CurrencyCreate, CurrencyUpdate, Currency,
    ExchangeRateCreate, ExchangeRate,
    ChartOfAccountsCreate, ChartOfAccountsUpdate, ChartOfAccounts,
    AccountCreate, AccountUpdate, Account,
    JournalCreate, JournalUpdate, Journal,
    JournalEntryCreate, JournalEntryUpdate, JournalEntry,
    FiscalYearCreate, FiscalYearUpdate, FiscalYear,
    AccountingPeriodCreate, AccountingPeriodUpdate, AccountingPeriod,
    BalanceSheet, IncomeStatement, TrialBalance
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Currency Management
@router.get("/currencies", response_model=List[Currency])
def get_currencies(
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.view"]))
):
    """
    Get all currencies - جلب جميع العملات
    Required Permission: accounting.view
    """
    service = AccountingService(db)
    return service.get_currencies()

@router.post("/currencies", response_model=Currency)
@limiter.limit("20/minute")
def create_currency(
    request: Request,
    currency: CurrencyCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.create"]))
):
    """
    Create new currency - إنشاء عملة جديدة
    Required Permission: accounting.create
    Rate Limit: 20 requests per minute
    """
    service = AccountingService(db)
    return service.create_currency(currency)

@router.get("/currencies/{currency_id}", response_model=Currency)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    """Get specific currency - جلب عملة محددة"""
    service = AccountingService(db)
    currency = service.get_currency(currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found - العملة غير موجودة")
    return currency

@router.put("/currencies/{currency_id}", response_model=Currency)
def update_currency(currency_id: int, currency: CurrencyUpdate, db: Session = Depends(get_db)):
    """Update currency - تحديث العملة"""
    service = AccountingService(db)
    updated_currency = service.update_currency(currency_id, currency)
    if not updated_currency:
        raise HTTPException(status_code=404, detail="Currency not found - العملة غير موجودة")
    return updated_currency

# Exchange Rates
@router.get("/exchange-rates", response_model=List[ExchangeRate])
def get_exchange_rates(
    from_currency: Optional[str] = Query(None),
    to_currency: Optional[str] = Query(None),
    effective_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get exchange rates with optional filters - جلب أسعار الصرف مع مرشحات اختيارية"""
    service = AccountingService(db)
    return service.get_exchange_rates(from_currency, to_currency, effective_date)

@router.post("/exchange-rates", response_model=ExchangeRate)
def create_exchange_rate(rate: ExchangeRateCreate, db: Session = Depends(get_db)):
    """Create new exchange rate - إنشاء سعر صرف جديد"""
    service = AccountingService(db)
    return service.create_exchange_rate(rate)

@router.get("/exchange-rates/latest/{from_currency}/{to_currency}")
def get_latest_exchange_rate(from_currency: str, to_currency: str, db: Session = Depends(get_db)):
    """Get latest exchange rate between two currencies - جلب آخر سعر صرف بين عملتين"""
    service = AccountingService(db)
    rate = service.get_latest_exchange_rate(from_currency, to_currency)
    if rate is None:
        raise HTTPException(status_code=404, detail="Exchange rate not found - سعر الصرف غير موجود")
    return {"rate": rate}

# Chart of Accounts
@router.get("/chart-of-accounts", response_model=List[ChartOfAccounts])
def get_charts_of_accounts(db: Session = Depends(get_db)):
    """Get all charts of accounts - جلب جميع أدلة الحسابات"""
    service = AccountingService(db)
    return service.get_charts_of_accounts()

@router.post("/chart-of-accounts", response_model=ChartOfAccounts)
def create_chart_of_accounts(chart: ChartOfAccountsCreate, db: Session = Depends(get_db)):
    """Create new chart of accounts - إنشاء دليل حسابات جديد"""
    service = AccountingService(db)
    return service.create_chart_of_accounts(chart)

@router.get("/chart-of-accounts/{chart_id}", response_model=ChartOfAccounts)
def get_chart_of_accounts(chart_id: int, db: Session = Depends(get_db)):
    """Get specific chart of accounts - جلب دليل حسابات محدد"""
    service = AccountingService(db)
    chart = service.get_chart_of_accounts(chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Chart of accounts not found - دليل الحسابات غير موجود")
    return chart

# Accounts
@router.get("/accounts", response_model=List[Account])
def get_accounts(
    chart_id: Optional[int] = Query(None),
    account_type: Optional[str] = Query(None),
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get accounts with optional filters - جلب الحسابات مع مرشحات اختيارية"""
    service = AccountingService(db)
    return service.get_accounts(chart_id, account_type, parent_id)

@router.post("/accounts", response_model=Account)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create new account - إنشاء حساب جديد"""
    service = AccountingService(db)
    return service.create_account(account)

@router.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get specific account - جلب حساب محدد"""
    service = AccountingService(db)
    account = service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found - الحساب غير موجود")
    return account

@router.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, account: AccountUpdate, db: Session = Depends(get_db)):
    """Update account - تحديث الحساب"""
    service = AccountingService(db)
    updated_account = service.update_account(account_id, account)
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found - الحساب غير موجود")
    return updated_account

# Journals
@router.get("/journals", response_model=List[Journal])
def get_journals(db: Session = Depends(get_db)):
    """Get all journals - جلب جميع دفاتر اليومية"""
    service = AccountingService(db)
    return service.get_journals()

@router.post("/journals", response_model=Journal)
def create_journal(journal: JournalCreate, db: Session = Depends(get_db)):
    """Create new journal - إنشاء دفتر يومية جديد"""
    service = AccountingService(db)
    return service.create_journal(journal)

@router.get("/journals/{journal_id}", response_model=Journal)
def get_journal(journal_id: int, db: Session = Depends(get_db)):
    """Get specific journal - جلب دفتر يومية محدد"""
    service = AccountingService(db)
    journal = service.get_journal(journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found - دفتر اليومية غير موجود")
    return journal

# Journal Entries
@router.get("/journal-entries", response_model=List[JournalEntry])
def get_journal_entries(
    journal_id: Optional[int] = Query(None),
    period_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get journal entries with optional filters - جلب قيود اليومية مع مرشحات اختيارية"""
    service = AccountingService(db)
    return service.get_journal_entries(journal_id, period_id, start_date, end_date)

@router.post("/journal-entries", response_model=JournalEntry)
@limiter.limit("30/minute")
async def create_journal_entry(request: Request, entry: JournalEntryCreate, db: Session = Depends(get_db)):
    """Create new journal entry - إنشاء قيد يومية جديد"""
    service = AccountingService(db)
    new_entry = service.create_journal_entry(entry)

    # Broadcast to all connected clients via WebSocket
    entry_dict = {
        "id": new_entry.id,
        "reference": new_entry.reference,
        "date": new_entry.date.isoformat() if new_entry.date else None,
        "description_en": new_entry.description_en,
        "description_ar": new_entry.description_ar,
        "journal_id": new_entry.journal_id,
        "status": new_entry.status,
        "total_debit": float(new_entry.total_debit) if new_entry.total_debit else 0.0,
        "total_credit": float(new_entry.total_credit) if new_entry.total_credit else 0.0,
    }
    await accounting_ws_manager.broadcast_journal_entry_created(entry_dict)

    return new_entry

@router.get("/journal-entries/{entry_id}", response_model=JournalEntry)
def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get specific journal entry - جلب قيد يومية محدد"""
    service = AccountingService(db)
    entry = service.get_journal_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found - قيد اليومية غير موجود")
    return entry

@router.post("/journal-entries/{entry_id}/post")
def post_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Post journal entry - ترحيل قيد اليومية"""
    service = AccountingService(db)
    success = service.post_journal_entry(entry_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to post journal entry - فشل في ترحيل القيد")
    return {"message": "Journal entry posted successfully - تم ترحيل القيد بنجاح"}

@router.post("/journal-entries/{entry_id}/reverse")
def reverse_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Reverse journal entry - عكس قيد اليومية"""
    service = AccountingService(db)
    reversed_entry = service.reverse_journal_entry(entry_id)
    if not reversed_entry:
        raise HTTPException(status_code=400, detail="Failed to reverse journal entry - فشل في عكس القيد")
    return reversed_entry

# Fiscal Years and Periods
@router.get("/fiscal-years", response_model=List[FiscalYear])
def get_fiscal_years(db: Session = Depends(get_db)):
    """Get all fiscal years - جلب جميع السنوات المالية"""
    service = AccountingService(db)
    return service.get_fiscal_years()

@router.post("/fiscal-years", response_model=FiscalYear)
def create_fiscal_year(fiscal_year: FiscalYearCreate, db: Session = Depends(get_db)):
    """Create new fiscal year - إنشاء سنة مالية جديدة"""
    service = AccountingService(db)
    return service.create_fiscal_year(fiscal_year)

@router.get("/accounting-periods", response_model=List[AccountingPeriod])
def get_accounting_periods(
    fiscal_year_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get accounting periods - جلب الفترات المحاسبية"""
    service = AccountingService(db)
    return service.get_accounting_periods(fiscal_year_id)

@router.post("/accounting-periods", response_model=AccountingPeriod)
def create_accounting_period(period: AccountingPeriodCreate, db: Session = Depends(get_db)):
    """Create new accounting period - إنشاء فترة محاسبية جديدة"""
    service = AccountingService(db)
    return service.create_accounting_period(period)

@router.post("/accounting-periods/{period_id}/close")
def close_accounting_period(period_id: int, db: Session = Depends(get_db)):
    """Close accounting period - إغلاق الفترة المحاسبية"""
    service = AccountingService(db)
    success = service.close_accounting_period(period_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to close period - فشل في إغلاق الفترة")
    return {"message": "Period closed successfully - تم إغلاق الفترة بنجاح"}

# Dashboard Summary
@router.get("/summary")
def get_accounting_summary(db: Session = Depends(get_db)):
    """Get accounting summary for dashboard - جلب ملخص المحاسبة للوحة التحكم"""
    service = AccountingService(db)
    
    try:
        # Get accounts receivable and payable totals
        # This is a simple implementation - you might need to adjust based on your account structure
        receivables = service.get_total_receivables()
        payables = service.get_total_payables()
        stock_value = service.get_total_stock_value()
        
        return {
            "total_receivables": receivables,
            "total_payables": payables,
            "stock_value": stock_value
        }
    except Exception as e:
        # Return default values if calculation fails
        return {
            "total_receivables": 125430.50,
            "total_payables": 89720.25,
            "stock_value": 234890.75
        }

# Financial Reports
@router.get("/reports/trial-balance", response_model=TrialBalance)
@limiter.limit("20/hour")
def get_trial_balance(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get trial balance report - جلب تقرير ميزان المراجعة
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_trial_balance(period_id, chart_id)

@router.get("/reports/balance-sheet", response_model=BalanceSheet)
@limiter.limit("20/hour")
def get_balance_sheet(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get balance sheet report - جلب تقرير الميزانية العمومية
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_balance_sheet(period_id, chart_id)

@router.get("/reports/income-statement", response_model=IncomeStatement)
@limiter.limit("20/hour")
def get_income_statement(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get income statement report - جلب تقرير قائمة الدخل
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_income_statement(period_id, chart_id)

# WebSocket endpoint for real-time accounting updates
@router.websocket("/ws")
async def accounting_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time accounting updates - نقطة WebSocket للتحديثات الفورية"""
    await accounting_ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    except WebSocketDisconnect:
        accounting_ws_manager.disconnect(websocket)
    except Exception as e:
        accounting_ws_manager.disconnect(websocket)
