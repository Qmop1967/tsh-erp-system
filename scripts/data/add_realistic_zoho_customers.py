#!/usr/bin/env python3
"""
Add realistic migrated customers from Zoho Books simulation
"""

from app.db.database import SessionLocal
from app.models.migration import MigrationCustomer, CurrencyEnum
from datetime import datetime, timedelta
from decimal import Decimal
import random

def add_realistic_zoho_customers():
    db = SessionLocal()
    try:
        # Realistic customer data that would come from Zoho Books
        zoho_customers = [
            {
                "code": "CUST00001",
                "name_ar": "شركة المستقبل للتكنولوجيا",
                "name_en": "Future Technology Company",
                "email": "info@future-tech.iq",
                "phone": "+964-1-234-5678",
                "mobile": "+964-790-123-4567",
                "address_ar": "حي الجادرية، شارع الجامعة، بناية رقم 15",
                "address_en": "Al-Jadriya District, University Street, Building No. 15",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("25000.000"),
                "outstanding_receivable": Decimal("5432.50"),
                "payment_terms": "Net 30",
                "is_active": True,
                "zoho_customer_id": "4000000000001",
                "zoho_deposit_account": "Sales Deposit - Ahmad Mahmoud",
                "tax_number": "12345678901",
                "created_at": datetime.utcnow() - timedelta(days=45),
                "updated_at": datetime.utcnow() - timedelta(days=2)
            },
            {
                "code": "CUST00002",
                "name_ar": "مؤسسة النور للتجارة العامة",
                "name_en": "Al-Noor General Trading Est.",
                "email": "sales@alnoor-trading.com",
                "phone": "+964-1-987-6543",
                "mobile": "+964-770-987-6543",
                "address_ar": "منطقة الكرادة، شارع أبو نواس، مجمع الأعمال رقم 8",
                "address_en": "Karada District, Abu Nawas Street, Business Complex No. 8",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.IQD,
                "credit_limit": Decimal("50000.000"),
                "outstanding_receivable": Decimal("12750.00"),
                "payment_terms": "Net 15",
                "is_active": True,
                "zoho_customer_id": "4000000000002",
                "zoho_deposit_account": "Sales Deposit - Fatima Ali",
                "tax_number": "98765432101",
                "created_at": datetime.utcnow() - timedelta(days=62),
                "updated_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "code": "CUST00003",
                "name_ar": "شركة بغداد للحاسبات والشبكات",
                "name_en": "Baghdad Computers & Networks Co.",
                "email": "info@baghdad-computers.net",
                "phone": "+964-1-555-0123",
                "mobile": "+964-750-555-0123",
                "address_ar": "شارع الرشيد، وسط البلد، بناية التجارة الحديثة",
                "address_en": "Al-Rashid Street, Downtown, Modern Trade Building",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("75000.000"),
                "outstanding_receivable": Decimal("0.000"),
                "payment_terms": "Net 45",
                "is_active": True,
                "zoho_customer_id": "4000000000003",
                "zoho_deposit_account": "Sales Deposit - Hassan Omar",
                "tax_number": "55512345678",
                "created_at": datetime.utcnow() - timedelta(days=38),
                "updated_at": datetime.utcnow() - timedelta(hours=6)
            },
            {
                "code": "CUST00004",
                "name_ar": "مكتب الإبداع للاستشارات الهندسية",
                "name_en": "Innovation Engineering Consultancy Office",
                "email": "contact@innovation-eng.iq",
                "phone": "+964-1-777-8888",
                "mobile": "+964-790-777-8888",
                "address_ar": "حي المنصور، شارع الأميرات، مجمع المهندسين",
                "address_en": "Al-Mansour District, Al-Amirat Street, Engineers Complex",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("30000.000"),
                "outstanding_receivable": Decimal("8900.75"),
                "payment_terms": "Net 30",
                "is_active": True,
                "zoho_customer_id": "4000000000004",
                "zoho_deposit_account": "Sales Deposit - Omar Khalil",
                "tax_number": "77788899901",
                "created_at": datetime.utcnow() - timedelta(days=28),
                "updated_at": datetime.utcnow() - timedelta(hours=12)
            },
            {
                "code": "CUST00005",
                "name_ar": "شركة الشام للاستيراد والتصدير",
                "name_en": "Al-Sham Import & Export Company",
                "email": "info@alsham-trade.com",
                "phone": "+964-1-444-5555",
                "mobile": "+964-780-444-5555",
                "address_ar": "منطقة العلوية، شارع حيفا، مركز الأعمال الدولي",
                "address_en": "Al-Alawiya District, Haifa Street, International Business Center",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("100000.000"),
                "outstanding_receivable": Decimal("23456.80"),
                "payment_terms": "Net 60",
                "is_active": True,
                "zoho_customer_id": "4000000000005",
                "zoho_deposit_account": "Sales Deposit - Layla Hassan",
                "tax_number": "11122334455",
                "created_at": datetime.utcnow() - timedelta(days=55),
                "updated_at": datetime.utcnow() - timedelta(hours=3)
            },
            {
                "code": "CUST00006",
                "name_ar": "مؤسسة الفجر للصناعات الغذائية",
                "name_en": "Al-Fajr Food Industries Est.",
                "email": "sales@alfajr-food.iq",
                "phone": "+964-1-333-4444",
                "mobile": "+964-760-333-4444",
                "address_ar": "المنطقة الصناعية، شارع الصناعة، مجمع رقم 12",
                "address_en": "Industrial Zone, Industry Street, Complex No. 12",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.IQD,
                "credit_limit": Decimal("40000.000"),
                "outstanding_receivable": Decimal("15670.25"),
                "payment_terms": "Net 21",
                "is_active": True,
                "zoho_customer_id": "4000000000006",
                "zoho_deposit_account": "Sales Deposit - Youssef Ali",
                "tax_number": "66677788899",
                "created_at": datetime.utcnow() - timedelta(days=72),
                "updated_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "code": "CUST00007",
                "name_ar": "شركة الأردن للصيانة والخدمات التقنية",
                "name_en": "Jordan Technical Maintenance & Services Co.",
                "email": "service@jordan-tech.com",
                "phone": "+964-1-666-7777",
                "mobile": "+964-740-666-7777",
                "address_ar": "حي الصدرية، شارع الخدمات، مركز الصيانة التقنية",
                "address_en": "Al-Sadriya District, Services Street, Technical Maintenance Center",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("20000.000"),
                "outstanding_receivable": Decimal("4320.00"),
                "payment_terms": "Net 30",
                "is_active": False,  # Inactive customer
                "zoho_customer_id": "4000000000007",
                "zoho_deposit_account": "Sales Deposit - Mariam Saad",
                "tax_number": "33344455566",
                "created_at": datetime.utcnow() - timedelta(days=95),
                "updated_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "code": "CUST00008",
                "name_ar": "مكتب الخليج للاستشارات المالية",
                "name_en": "Gulf Financial Consultancy Office",
                "email": "info@gulf-finance.iq",
                "phone": "+964-1-888-9999",
                "mobile": "+964-720-888-9999",
                "address_ar": "حي الجادرية، شارع الجامعة، برج الأعمال الطابق العاشر",
                "address_en": "Al-Jadriya District, University Street, Business Tower 10th Floor",
                "city": "Baghdad",
                "region": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("15000.000"),
                "outstanding_receivable": Decimal("2750.50"),
                "payment_terms": "Net 14",
                "is_active": True,
                "zoho_customer_id": "4000000000008",
                "zoho_deposit_account": "Sales Deposit - Khalil Ibrahim",
                "tax_number": "99988877766",
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(hours=8)
            }
        ]
        
        # Add customers to database
        for customer_data in zoho_customers:
            customer = MigrationCustomer(**customer_data)
            db.add(customer)
            print(f"Added Zoho customer: {customer.name_en}")
        
        db.commit()
        print(f"\n✅ Successfully added {len(zoho_customers)} realistic Zoho customers!")
        
        # Show summary
        total_customers = db.query(MigrationCustomer).count()
        active_customers = db.query(MigrationCustomer).filter(MigrationCustomer.is_active == True).count()
        print(f"📊 Total migrated customers: {total_customers}")
        print(f"📊 Active customers: {active_customers}")
        print(f"📊 Inactive customers: {total_customers - active_customers}")
        
        # Show outstanding receivables
        total_outstanding = db.query(MigrationCustomer).with_entities(
            db.func.sum(MigrationCustomer.outstanding_receivable)
        ).scalar() or 0
        print(f"💰 Total outstanding receivables: ${total_outstanding:,.2f}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding Zoho customers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_realistic_zoho_customers()
