#!/usr/bin/env python3
"""
Add sample migrated customers for testing
"""

from app.db.database import SessionLocal
from app.models.migration import MigrationCustomer, CurrencyEnum
from datetime import datetime
from decimal import Decimal

def add_sample_migrated_customers():
    db = SessionLocal()
    try:
        # Sample migrated customers from Zoho
        sample_customers = [
            {
                "code": "ZOHO-001",
                "name_ar": "شركة الزهراء للتجارة",
                "name_en": "Al-Zahra Trading Company",
                "email": "info@alzahra.com",
                "phone": "+964-1-234-5678",
                "mobile": "+964-790-123-4567",
                "address_ar": "شارع فلسطين، منطقة الكرادة",
                "address_en": "Palestine Street, Karada District",
                "city": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.IQD,
                "credit_limit": Decimal("50000.000"),
                "outstanding_receivable": Decimal("15000.000"),
                "is_active": True,
                "zoho_customer_id": "ZOHO_CUST_001",
                "zoho_deposit_account": "Sales Deposit - Ahmad",
                "created_at": datetime.utcnow()
            },
            {
                "code": "ZOHO-002", 
                "name_ar": "مؤسسة النور للإلكترونيات",
                "name_en": "Al-Noor Electronics Est.",
                "email": "sales@alnoor-electronics.com",
                "phone": "+964-1-987-6543",
                "mobile": "+964-770-987-6543",
                "address_ar": "شارع النهضة، حي المنصور",
                "address_en": "Al-Nahda Street, Mansour District",
                "city": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("25000.000"),
                "outstanding_receivable": Decimal("8500.000"),
                "is_active": True,
                "zoho_customer_id": "ZOHO_CUST_002",
                "zoho_deposit_account": "Sales Deposit - Fatima",
                "created_at": datetime.utcnow()
            },
            {
                "code": "ZOHO-003",
                "name_ar": "شركة بغداد للحاسوب",
                "name_en": "Baghdad Computer Company",
                "email": "info@baghdad-computers.com",
                "phone": "+964-1-555-0123",
                "mobile": "+964-750-555-0123",
                "address_ar": "شارع الرشيد، وسط البلد",
                "address_en": "Al-Rashid Street, Downtown",
                "city": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.IQD,
                "credit_limit": Decimal("75000.000"),
                "outstanding_receivable": Decimal("0.000"),
                "is_active": True,
                "zoho_customer_id": "ZOHO_CUST_003",
                "zoho_deposit_account": "Sales Deposit - Hassan",
                "created_at": datetime.utcnow()
            },
            {
                "code": "ZOHO-004",
                "name_ar": "مكتب الأمل للاستشارات",
                "name_en": "Al-Amal Consulting Office",
                "email": "contact@alamal-consulting.com",
                "phone": "+964-1-777-8888",
                "mobile": "+964-790-777-8888",
                "address_ar": "شارع حيفا، منطقة الجادرية",
                "address_en": "Haifa Street, Jadriya District",
                "city": "Baghdad",
                "country": "Iraq",
                "currency": CurrencyEnum.USD,
                "credit_limit": Decimal("30000.000"),
                "outstanding_receivable": Decimal("12000.000"),
                "is_active": False,  # Inactive customer for testing
                "zoho_customer_id": "ZOHO_CUST_004",
                "zoho_deposit_account": "Sales Deposit - Omar",
                "created_at": datetime.utcnow()
            }
        ]
        
        # Add customers to database
        for customer_data in sample_customers:
            # Check if customer already exists
            existing = db.query(MigrationCustomer).filter(
                MigrationCustomer.code == customer_data["code"]
            ).first()
            
            if not existing:
                customer = MigrationCustomer(**customer_data)
                db.add(customer)
                print(f"Added migrated customer: {customer.name_en}")
            else:
                print(f"Customer {customer_data['code']} already exists, skipping...")
        
        db.commit()
        print("Sample migrated customers added successfully!")
        
        # Verify the data
        total_customers = db.query(MigrationCustomer).count()
        print(f"Total migrated customers in database: {total_customers}")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding sample customers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_migrated_customers()
