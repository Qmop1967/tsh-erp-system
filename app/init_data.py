"""
Initial data setup for TSH ERP System
بيانات البداية لنظام TSH ERP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.accounting import Currency, ChartOfAccounts, Account, FiscalYear, AccountingPeriod, Journal
from app.models.pos import POSDiscount, POSPromotion
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def initialize_currencies(db: Session):
    """Initialize default currencies - تهيئة العملات الافتراضية"""
    currencies = [
        {
            "code": "IQD",
            "name_en": "Iraqi Dinar",
            "name_ar": "دينار عراقي",
            "symbol": "ع.د",
            "exchange_rate": 1.0,
            "is_base_currency": True,
            "is_active": True
        },
        {
            "code": "USD",
            "name_en": "US Dollar",
            "name_ar": "دولار أمريكي",
            "symbol": "$",
            "exchange_rate": 1310.0,
            "is_base_currency": False,
            "is_active": True
        },
        {
            "code": "RMB",
            "name_en": "Chinese Yuan Renminbi",
            "name_ar": "يوان صيني",
            "symbol": "¥",
            "exchange_rate": 189.0,
            "is_base_currency": False,
            "is_active": True
        }
    ]
    
    for currency_data in currencies:
        existing = db.query(Currency).filter(Currency.code == currency_data["code"]).first()
        if not existing:
            currency = Currency(**currency_data)
            db.add(currency)
            logger.info(f"Added currency: {currency_data['code']}")
    
    db.commit()

def initialize_chart_of_accounts(db: Session):
    """Initialize default chart of accounts - تهيئة دليل الحسابات الافتراضي"""
    chart_data = {
        "code": "STD",
        "name_en": "Standard Chart of Accounts",
        "name_ar": "دليل الحسابات المعياري",
        "account_type": "ASSET",  # Required field
        "description_en": "Standard chart of accounts for TSH ERP",
        "description_ar": "دليل الحسابات المعياري لنظام TSH ERP",
        "is_active": True
    }
    
    existing = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == chart_data["code"]).first()
    if not existing:
        chart = ChartOfAccounts(**chart_data)
        db.add(chart)
        db.commit()
        db.refresh(chart)
        logger.info(f"Added chart of accounts: {chart_data['code']}")
        return chart
    return existing

def initialize_accounts(db: Session, chart_id: int):
    """Initialize default accounts - تهيئة الحسابات الافتراضية"""
    # Get the base currency (IQD)
    base_currency = db.query(Currency).filter(Currency.is_base_currency == True).first()
    if not base_currency:
        logger.error("Base currency not found. Please initialize currencies first.")
        return
    
    accounts = [
        # Assets - الأصول
        {
            "chart_account_id": chart_id,
            "currency_id": base_currency.id,
            "balance_debit": 0,
            "balance_credit": 0,
            "balance": 0,
            "is_active": True,
            "branch_id": None
        }
    ]
    
    # For now, let's create just one sample account to test
    for account_data in accounts:
        account = Account(**account_data)
        db.add(account)
        logger.info(f"Added account: {account_data}")
    
    db.commit()

def initialize_journals(db: Session):
    """Initialize default journals - تهيئة دفاتر اليومية الافتراضية"""
    journals = [
        {
            "code": "GJ",
            "name_en": "General Journal",
            "name_ar": "دفتر اليومية العام",
            "journal_type": "GENERAL",
            "description_en": "General journal for all transactions",
            "description_ar": "دفتر اليومية العام لجميع المعاملات",
            "is_active": True
        },
        {
            "code": "SJ",
            "name_en": "Sales Journal",
            "name_ar": "دفتر يومية المبيعات",
            "journal_type": "SALES",
            "description_en": "Journal for sales transactions",
            "description_ar": "دفتر يومية معاملات المبيعات",
            "is_active": True
        },
        {
            "code": "PJ",
            "name_en": "Purchase Journal",
            "name_ar": "دفتر يومية المشتريات",
            "journal_type": "PURCHASE",
            "description_en": "Journal for purchase transactions",
            "description_ar": "دفتر يومية معاملات المشتريات",
            "is_active": True
        },
        {
            "code": "CJ",
            "name_en": "Cash Journal",
            "name_ar": "دفتر يومية النقدية",
            "journal_type": "CASH",
            "description_en": "Journal for cash transactions",
            "description_ar": "دفتر يومية المعاملات النقدية",
            "is_active": True
        }
    ]
    
    for journal_data in journals:
        existing = db.query(Journal).filter(Journal.code == journal_data["code"]).first()
        if not existing:
            journal = Journal(**journal_data)
            db.add(journal)
            logger.info(f"Added journal: {journal_data['code']}")
    
    db.commit()

def initialize_fiscal_year(db: Session):
    """Initialize current fiscal year - تهيئة السنة المالية الحالية"""
    current_year = datetime.now().year
    fiscal_year_data = {
        "name_ar": f"السنة المالية {current_year}",
        "name_en": f"Fiscal Year {current_year}",
        "start_date": datetime(current_year, 1, 1),
        "end_date": datetime(current_year, 12, 31),
        "is_current": True,
        "is_closed": False
    }
    
    existing = db.query(FiscalYear).filter(
        FiscalYear.name_en == fiscal_year_data["name_en"]
    ).first()
    if not existing:
        fiscal_year = FiscalYear(**fiscal_year_data)
        db.add(fiscal_year)
        db.commit()
        db.refresh(fiscal_year)
        logger.info(f"Added fiscal year: {current_year}")
        
        # Create 12 monthly periods
        for month in range(1, 13):
            if month == 12:
                start_date = datetime(current_year, month, 1)
                end_date = datetime(current_year, 12, 31)
            else:
                start_date = datetime(current_year, month, 1)
                next_month = datetime(current_year, month + 1, 1)
                end_date = next_month - timedelta(days=1)
            
            period_data = {
                "fiscal_year_id": fiscal_year.id,
                "name_ar": f"الفترة {month:02d}/{current_year}",
                "name_en": f"Period {month:02d}/{current_year}",
                "start_date": start_date,
                "end_date": end_date,
                "is_closed": False
            }
            
            period = AccountingPeriod(**period_data)
            db.add(period)
        
        db.commit()
        logger.info(f"Added 12 accounting periods for fiscal year {current_year}")
    else:
        logger.info(f"Fiscal year {current_year} already exists")

def initialize_pos_data(db: Session):
    """Initialize default POS data - تهيئة بيانات نقاط البيع الافتراضية"""
    # Default discounts
    discounts = [
        {
            "code": "STUDENT10",
            "name_en": "Student Discount",
            "name_ar": "خصم الطلاب",
            "discount_type": "PERCENTAGE",
            "discount_value": 10.0,
            "min_amount": 0.0,
            "is_active": True,
            "valid_from": datetime.today(),
            "valid_to": datetime(2025, 12, 31)
        },
        {
            "code": "BULK20",
            "name_en": "Bulk Purchase Discount",
            "name_ar": "خصم الشراء بالجملة",
            "discount_type": "PERCENTAGE",
            "discount_value": 20.0,
            "min_amount": 1000.0,
            "is_active": True,
            "valid_from": datetime.today(),
            "valid_to": datetime(2025, 12, 31)
        }
    ]
    
    for discount_data in discounts:
        existing = db.query(POSDiscount).filter(POSDiscount.code == discount_data["code"]).first()
        if not existing:
            discount = POSDiscount(**discount_data)
            db.add(discount)
            logger.info(f"Added POS discount: {discount_data['code']}")
    
    # Default promotions
    promotions = [
        {
            "code": "WELCOME2025",
            "name_en": "Welcome 2025 Promotion",
            "name_ar": "عرض أهلاً 2025",
            "description_en": "Special promotion for new year",
            "description_ar": "عرض خاص للسنة الجديدة",
            "promotion_type": "BUY_X_GET_Y",
            "rules": '{"buy": 2, "get": 1, "product_ids": []}',
            "is_active": True,
            "valid_from": datetime.today(),
            "valid_to": datetime(2025, 12, 31)
        }
    ]
    
    for promotion_data in promotions:
        existing = db.query(POSPromotion).filter(POSPromotion.code == promotion_data["code"]).first()
        if not existing:
            promotion = POSPromotion(**promotion_data)
            db.add(promotion)
            logger.info(f"Added POS promotion: {promotion_data['code']}")
    
    db.commit()

def initialize_all_data():
    """Initialize all default data - تهيئة جميع البيانات الافتراضية"""
    db = SessionLocal()
    try:
        logger.info("Starting data initialization - بدء تهيئة البيانات")
        
        # Initialize currencies
        initialize_currencies(db)
        
        # Initialize chart of accounts and accounts
        chart = initialize_chart_of_accounts(db)
        initialize_accounts(db, chart.id)
        
        # Initialize journals
        initialize_journals(db)
        
        # Initialize fiscal year and periods
        initialize_fiscal_year(db)
        
        # Initialize POS data
        initialize_pos_data(db)
        
        logger.info("Data initialization completed successfully - تم إكمال تهيئة البيانات بنجاح")
        
    except Exception as e:
        logger.error(f"Error during data initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_all_data()
