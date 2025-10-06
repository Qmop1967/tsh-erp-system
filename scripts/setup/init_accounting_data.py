#!/usr/bin/env python3
"""
Script to initialize TSH ERP Accounting System with basic data
تهيئة نظام المحاسبة في نظام إدارة الموارد لشركة TSH
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.models.accounting import (
    Currency, ExchangeRate, ChartOfAccounts, Journal, FiscalYear,
    AccountTypeEnum, JournalTypeEnum
)
from datetime import datetime, date


def init_currencies(db: Session):
    """Initialize currencies"""
    print("Initializing currencies...")
    
    currencies_data = [
        {
            "code": "IQD",
            "name_ar": "دينار عراقي",
            "name_en": "Iraqi Dinar",
            "symbol": "ع.د",
            "exchange_rate": 1.0,
            "is_base_currency": True,
            "is_active": True
        },
        {
            "code": "USD",
            "name_ar": "دولار أمريكي",
            "name_en": "US Dollar",
            "symbol": "$",
            "exchange_rate": 1310.0,
            "is_base_currency": False,
            "is_active": True
        },
        {
            "code": "RMB",
            "name_ar": "يوان صيني",
            "name_en": "Chinese Yuan Renminbi",
            "symbol": "¥",
            "exchange_rate": 189.0,
            "is_base_currency": False,
            "is_active": True
        }
    ]
    
    for currency_data in currencies_data:
        existing = db.query(Currency).filter(Currency.code == currency_data["code"]).first()
        if not existing:
            currency = Currency(**currency_data)
            db.add(currency)
            print(f"Created currency: {currency_data['name_en']} ({currency_data['code']})")
    
    db.commit()


def init_chart_of_accounts(db: Session):
    """Initialize basic chart of accounts"""
    print("Initializing chart of accounts...")
    
    chart_accounts = [
        # Assets - الأصول
        {
            "code": "1000",
            "name_ar": "الأصول",
            "name_en": "Assets",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,
            "level": 1,
            "allow_posting": False
        },
        {
            "code": "1100",
            "name_ar": "الأصول المتداولة",
            "name_en": "Current Assets",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,  # Will be set after parent creation
            "level": 2,
            "allow_posting": False
        },
        {
            "code": "1110",
            "name_ar": "النقدية في الصندوق",
            "name_en": "Cash in Hand",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "1120",
            "name_ar": "البنك",
            "name_en": "Bank",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "1130",
            "name_ar": "العملاء والذمم المدينة",
            "name_en": "Accounts Receivable",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "1140",
            "name_ar": "المخزون",
            "name_en": "Inventory",
            "account_type": AccountTypeEnum.ASSET,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        
        # Liabilities - الخصوم
        {
            "code": "2000",
            "name_ar": "الخصوم",
            "name_en": "Liabilities",
            "account_type": AccountTypeEnum.LIABILITY,
            "parent_id": None,
            "level": 1,
            "allow_posting": False
        },
        {
            "code": "2100",
            "name_ar": "الخصوم المتداولة",
            "name_en": "Current Liabilities",
            "account_type": AccountTypeEnum.LIABILITY,
            "parent_id": None,
            "level": 2,
            "allow_posting": False
        },
        {
            "code": "2110",
            "name_ar": "الموردون والذمم الدائنة",
            "name_en": "Accounts Payable",
            "account_type": AccountTypeEnum.LIABILITY,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "2120",
            "name_ar": "الضرائب المستحقة",
            "name_en": "Accrued Taxes",
            "account_type": AccountTypeEnum.LIABILITY,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        
        # Equity - حقوق الملكية
        {
            "code": "3000",
            "name_ar": "حقوق الملكية",
            "name_en": "Equity",
            "account_type": AccountTypeEnum.EQUITY,
            "parent_id": None,
            "level": 1,
            "allow_posting": False
        },
        {
            "code": "3100",
            "name_ar": "رأس المال",
            "name_en": "Capital",
            "account_type": AccountTypeEnum.EQUITY,
            "parent_id": None,
            "level": 2,
            "allow_posting": True
        },
        {
            "code": "3200",
            "name_ar": "الأرباح المحتجزة",
            "name_en": "Retained Earnings",
            "account_type": AccountTypeEnum.EQUITY,
            "parent_id": None,
            "level": 2,
            "allow_posting": True
        },
        
        # Revenue - الإيرادات
        {
            "code": "4000",
            "name_ar": "الإيرادات",
            "name_en": "Revenue",
            "account_type": AccountTypeEnum.REVENUE,
            "parent_id": None,
            "level": 1,
            "allow_posting": False
        },
        {
            "code": "4100",
            "name_ar": "مبيعات البضائع",
            "name_en": "Sales Revenue",
            "account_type": AccountTypeEnum.REVENUE,
            "parent_id": None,
            "level": 2,
            "allow_posting": True
        },
        {
            "code": "4200",
            "name_ar": "إيرادات أخرى",
            "name_en": "Other Revenue",
            "account_type": AccountTypeEnum.REVENUE,
            "parent_id": None,
            "level": 2,
            "allow_posting": True
        },
        
        # Expenses - المصروفات
        {
            "code": "5000",
            "name_ar": "المصروفات",
            "name_en": "Expenses",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 1,
            "allow_posting": False
        },
        {
            "code": "5100",
            "name_ar": "تكلفة البضاعة المباعة",
            "name_en": "Cost of Goods Sold",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 2,
            "allow_posting": True
        },
        {
            "code": "5200",
            "name_ar": "مصروفات التشغيل",
            "name_en": "Operating Expenses",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 2,
            "allow_posting": False
        },
        {
            "code": "5210",
            "name_ar": "رواتب ومكافآت",
            "name_en": "Salaries and Benefits",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "5220",
            "name_ar": "إيجار",
            "name_en": "Rent Expense",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        },
        {
            "code": "5230",
            "name_ar": "مصروفات نقل وشحن",
            "name_en": "Transportation and Shipping",
            "account_type": AccountTypeEnum.EXPENSE,
            "parent_id": None,
            "level": 3,
            "allow_posting": True
        }
    ]
    
    # Create accounts and set parent relationships
    created_accounts = {}
    
    # First pass: create all accounts
    for account_data in chart_accounts:
        existing = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == account_data["code"]).first()
        if not existing:
            account = ChartOfAccounts(**account_data)
            db.add(account)
            db.commit()
            db.refresh(account)
            created_accounts[account.code] = account
            print(f"Created account: {account.code} - {account.name_en}")
    
    # Second pass: set parent relationships
    parent_mappings = {
        "1100": "1000",  # Current Assets -> Assets
        "1110": "1100",  # Cash -> Current Assets
        "1120": "1100",  # Bank -> Current Assets
        "1130": "1100",  # AR -> Current Assets
        "1140": "1100",  # Inventory -> Current Assets
        "2100": "2000",  # Current Liabilities -> Liabilities
        "2110": "2100",  # AP -> Current Liabilities
        "2120": "2100",  # Taxes -> Current Liabilities
        "3100": "3000",  # Capital -> Equity
        "3200": "3000",  # Retained Earnings -> Equity
        "4100": "4000",  # Sales -> Revenue
        "4200": "4000",  # Other Revenue -> Revenue
        "5100": "5000",  # COGS -> Expenses
        "5200": "5000",  # Operating -> Expenses
        "5210": "5200",  # Salaries -> Operating
        "5220": "5200",  # Rent -> Operating
        "5230": "5200",  # Transportation -> Operating
    }
    
    for child_code, parent_code in parent_mappings.items():
        child_account = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == child_code).first()
        parent_account = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == parent_code).first()
        if child_account and parent_account:
            child_account.parent_id = parent_account.id
            print(f"Set parent for {child_code} -> {parent_code}")
    
    db.commit()


def init_journals(db: Session):
    """Initialize basic journals"""
    print("Initializing journals...")
    
    journals_data = [
        {
            "code": "GJ",
            "name_ar": "دفتر اليومية العام",
            "name_en": "General Journal",
            "journal_type": JournalTypeEnum.GENERAL,
            "description_ar": "دفتر اليومية العام للقيود المحاسبية",
            "description_en": "General journal for accounting entries"
        },
        {
            "code": "SJ",
            "name_ar": "دفتر يومية المبيعات",
            "name_en": "Sales Journal",
            "journal_type": JournalTypeEnum.SALES,
            "description_ar": "دفتر يومية خاص بعمليات المبيعات",
            "description_en": "Journal for sales transactions"
        },
        {
            "code": "PJ",
            "name_ar": "دفتر يومية المشتريات",
            "name_en": "Purchase Journal",
            "journal_type": JournalTypeEnum.PURCHASE,
            "description_ar": "دفتر يومية خاص بعمليات الشراء",
            "description_en": "Journal for purchase transactions"
        },
        {
            "code": "CJ",
            "name_ar": "دفتر يومية النقدية",
            "name_en": "Cash Journal",
            "journal_type": JournalTypeEnum.CASH,
            "description_ar": "دفتر يومية للعمليات النقدية",
            "description_en": "Journal for cash transactions"
        }
    ]
    
    for journal_data in journals_data:
        existing = db.query(Journal).filter(Journal.code == journal_data["code"]).first()
        if not existing:
            journal = Journal(**journal_data)
            db.add(journal)
            print(f"Created journal: {journal_data['name_en']} ({journal_data['code']})")
    
    db.commit()


def init_fiscal_year(db: Session):
    """Initialize current fiscal year"""
    print("Initializing fiscal year...")
    
    current_year = datetime.now().year
    fiscal_year_data = {
        "name_ar": f"السنة المالية {current_year}",
        "name_en": f"Fiscal Year {current_year}",
        "start_date": datetime(current_year, 1, 1),
        "end_date": datetime(current_year, 12, 31),
        "is_current": True,
        "is_closed": False
    }
    
    existing = db.query(FiscalYear).filter(FiscalYear.is_current == True).first()
    if not existing:
        fiscal_year = FiscalYear(**fiscal_year_data)
        db.add(fiscal_year)
        db.commit()
        print(f"Created fiscal year: {fiscal_year_data['name_en']}")


def main():
    """Main function to initialize accounting data"""
    print("=== TSH ERP Accounting System Initialization ===")
    print("=== تهيئة نظام المحاسبة لشركة TSH ===\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize basic accounting data
        init_currencies(db)
        init_chart_of_accounts(db)
        init_journals(db)
        init_fiscal_year(db)
        
        print("\n=== Accounting system initialization completed! ===")
        print("=== تم إنهاء تهيئة النظام المحاسبي بنجاح! ===")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
