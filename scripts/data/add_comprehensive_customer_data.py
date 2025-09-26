#!/usr/bin/env python3
"""
Add comprehensive customer, ally, and consumer demo data
إضافة بيانات شاملة للعملاء والحلفاء والمستهلكين
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.customer import Customer, Supplier
from app.models.user import User
from app.models.branch import Branch
from app.services.customer_service import CustomerService, SupplierService
from app.schemas.customer import CustomerCreate, SupplierCreate
from datetime import datetime
import random

def generate_customer_code(prefix="CUST", number=1):
    """Generate customer code"""
    return f"{prefix}-{number:04d}"

def generate_supplier_code(prefix="SUPP", number=1):
    """Generate supplier code"""
    return f"{prefix}-{number:04d}"

def add_comprehensive_customer_data():
    """Add comprehensive customer, ally, and consumer data"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🚀 Adding Comprehensive Customer Data")
        print("=" * 50)
        
        # Get existing customer count to continue numbering
        existing_customers = db.query(Customer).count()
        customer_number = existing_customers + 1
        
        existing_suppliers = db.query(Supplier).count()
        supplier_number = existing_suppliers + 1
        
        # Regular Customers (B2B Companies)
        customers_data = [
            {
                'customer_code': generate_customer_code("CUST", customer_number),
                'name': 'شركة بغداد للإلكترونيات',
                'company_name': 'Baghdad Electronics Corporation',
                'email': 'info@baghdad-electronics.iq',
                'phone': '+964-1-7777777',
                'address': 'الكرادة الشرقية، شارع أبو نواس',
                'city': 'بغداد',
                'country': 'العراق',
                'currency': 'IQD',
                'portal_language': 'ar',
                'credit_limit': 75000,
                'payment_terms': 30,
                'discount_percentage': 12,
                'tax_number': 'TAX-BGD-001',
                'is_active': True,
                'notes': 'موزع معتمد للأجهزة الإلكترونية والكهربائية'
            },
            {
                'customer_code': generate_customer_code("CUST", customer_number + 1),
                'name': 'مؤسسة أربيل التجارية',
                'company_name': 'Erbil Trading Establishment',
                'email': 'sales@erbil-trading.com',
                'phone': '+964-66-2222222',
                'address': 'وسط المدينة، شارع الستين متر',
                'city': 'أربيل',
                'country': 'العراق',
                'currency': 'USD',
                'portal_language': 'ar',
                'credit_limit': 100000,
                'payment_terms': 45,
                'discount_percentage': 15,
                'tax_number': 'TAX-ERB-002',
                'is_active': True,
                'notes': 'شركة استيراد وتصدير'
            },
            {
                'customer_code': generate_customer_code("CUST", customer_number + 2),
                'name': 'شركة البصرة للخدمات النفطية',
                'company_name': 'Basra Oil Services Ltd.',
                'email': 'procurement@basra-oil.iq',
                'phone': '+964-40-5555555',
                'address': 'المنطقة الصناعية، البصرة',
                'city': 'البصرة',
                'country': 'العراق',
                'currency': 'USD',
                'portal_language': 'ar',
                'credit_limit': 200000,
                'payment_terms': 60,
                'discount_percentage': 8,
                'tax_number': 'TAX-BSR-003',
                'is_active': True,
                'notes': 'مورد خدمات الصناعة النفطية'
            }
        ]
        
        # Allies (Strategic Partners)
        allies_data = [
            {
                'customer_code': generate_customer_code("ALLY", customer_number + 3),
                'name': 'تحالف الشركات التقنية',
                'company_name': 'Technology Alliance Consortium',
                'email': 'partners@tech-alliance.iq',
                'phone': '+964-53-8888888',
                'address': 'منطقة التكنولوجيا، السليمانية',
                'city': 'السليمانية',
                'country': 'العراق',
                'currency': 'USD',
                'portal_language': 'ar',
                'credit_limit': 500000,
                'payment_terms': 90,
                'discount_percentage': 25,
                'tax_number': 'TAX-ALLY-001',
                'is_active': True,
                'notes': 'شريك استراتيجي في التكنولوجيا والابتكار'
            },
            {
                'customer_code': generate_customer_code("ALLY", customer_number + 4),
                'name': 'تحالف المقاولين العراقيين',
                'company_name': 'Iraqi Contractors Alliance',
                'email': 'info@contractors-alliance.iq',
                'phone': '+964-33-9999999',
                'address': 'المنطقة الصناعية، النجف',
                'city': 'النجف',
                'country': 'العراق',
                'currency': 'IQD',
                'portal_language': 'ar',
                'credit_limit': 300000,
                'payment_terms': 120,
                'discount_percentage': 20,
                'tax_number': 'TAX-ALLY-002',
                'is_active': True,
                'notes': 'تحالف مقاولين للمشاريع الكبيرة'
            }
        ]
        
        # Consumers (Individual Customers)
        consumers_data = [
            {
                'customer_code': generate_customer_code("CONS", customer_number + 5),
                'name': 'أحمد محمد علي',
                'company_name': None,
                'email': 'ahmed.ali@gmail.com',
                'phone': '+964-770-1234567',
                'address': 'حي الجادرية، بغداد',
                'city': 'بغداد',
                'country': 'العراق',
                'currency': 'IQD',
                'portal_language': 'ar',
                'credit_limit': 5000,
                'payment_terms': 7,
                'discount_percentage': 5,
                'tax_number': None,
                'is_active': True,
                'notes': 'عميل فردي - مستهلك'
            },
            {
                'customer_code': generate_customer_code("CONS", customer_number + 6),
                'name': 'فاطمة حسن محمود',
                'company_name': None,
                'email': 'fatima.hassan@yahoo.com',
                'phone': '+964-780-2345678',
                'address': 'حي الأندلس، بغداد',
                'city': 'بغداد',
                'country': 'العراق',
                'currency': 'IQD',
                'portal_language': 'ar',
                'credit_limit': 3000,
                'payment_terms': 7,
                'discount_percentage': 3,
                'tax_number': None,
                'is_active': True,
                'notes': 'عميلة فردية - مستهلكة'
            },
            {
                'customer_code': generate_customer_code("CONS", customer_number + 7),
                'name': 'محمد عمار الكردي',
                'company_name': None,
                'email': 'mohammed.kurdi@hotmail.com',
                'phone': '+964-750-3456789',
                'address': 'حي عنكاوا، أربيل',
                'city': 'أربيل',
                'country': 'العراق',
                'currency': 'USD',
                'portal_language': 'ar',
                'credit_limit': 8000,
                'payment_terms': 14,
                'discount_percentage': 7,
                'tax_number': None,
                'is_active': True,
                'notes': 'عميل فردي من إقليم كردستان'
            }
        ]
        
        # Suppliers Data
        suppliers_data = [
            {
                'supplier_code': generate_supplier_code("SUPP", supplier_number),
                'name': 'شركة المواد الخام الدولية',
                'company_name': 'International Raw Materials Co.',
                'email': 'supply@rawmaterials-intl.com',
                'phone': '+964-1-5555555',
                'address': 'المنطقة الصناعية، بغداد',
                'city': 'بغداد',
                'country': 'العراق',
                'payment_terms': 30,
                'tax_number': 'TAX-SUPP-001',
                'is_active': True,
                'notes': 'مورد المواد الخام والمستلزمات الصناعية'
            },
            {
                'supplier_code': generate_supplier_code("SUPP", supplier_number + 1),
                'name': 'مؤسسة الأجهزة المتقدمة',
                'company_name': 'Advanced Equipment Enterprise',
                'email': 'info@advanced-equipment.iq',
                'phone': '+964-66-3333333',
                'address': 'شارع الجامعة، أربيل',
                'city': 'أربيل',
                'country': 'العراق',
                'payment_terms': 45,
                'tax_number': 'TAX-SUPP-002',
                'is_active': True,
                'notes': 'مورد الأجهزة والمعدات المتخصصة'
            }
        ]
        
        # Add customers
        print("\n👥 Adding Customers...")
        all_customer_data = customers_data + allies_data + consumers_data
        for i, customer_data in enumerate(all_customer_data, 1):
            try:
                # Check if customer already exists
                existing = db.query(Customer).filter(
                    Customer.customer_code == customer_data['customer_code']
                ).first()
                
                if existing:
                    print(f"  ⚠️ {i}. Skipped: {customer_data['name']} (already exists)")
                    continue
                
                customer_create = CustomerCreate(**customer_data)
                customer = CustomerService.create_customer(db, customer_create)
                customer_type = "حليف" if "ALLY" in customer_data['customer_code'] else "مستهلك" if "CONS" in customer_data['customer_code'] else "عميل"
                print(f"  ✅ {i}. Created {customer_type}: {customer.name} ({customer.customer_code})")
                
            except Exception as e:
                print(f"  ❌ {i}. Error creating {customer_data['name']}: {e}")
        
        # Add suppliers
        print("\n🏭 Adding Suppliers...")
        for i, supplier_data in enumerate(suppliers_data, 1):
            try:
                # Check if supplier already exists
                existing = db.query(Supplier).filter(
                    Supplier.supplier_code == supplier_data['supplier_code']
                ).first()
                
                if existing:
                    print(f"  ⚠️ {i}. Skipped: {supplier_data['name']} (already exists)")
                    continue
                
                supplier_create = SupplierCreate(**supplier_data)
                supplier = SupplierService.create_supplier(db, supplier_create)
                print(f"  ✅ {i}. Created Supplier: {supplier.name} ({supplier.supplier_code})")
                
            except Exception as e:
                print(f"  ❌ {i}. Error creating {supplier_data['name']}: {e}")
        
        # Final statistics
        print("\n📊 Final Statistics:")
        total_customers = db.query(Customer).count()
        total_suppliers = db.query(Supplier).count()
        active_customers = db.query(Customer).filter(Customer.is_active == True).count()
        active_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()
        
        customers_by_type = {
            'عملاء': db.query(Customer).filter(Customer.customer_code.like('CUST-%')).count(),
            'حلفاء': db.query(Customer).filter(Customer.customer_code.like('ALLY-%')).count(),
            'مستهلكين': db.query(Customer).filter(Customer.customer_code.like('CONS-%')).count()
        }
        
        print(f"   📈 Total Customers: {total_customers} (Active: {active_customers})")
        print(f"   🏭 Total Suppliers: {total_suppliers} (Active: {active_suppliers})")
        print(f"   🔍 Breakdown:")
        for type_name, count in customers_by_type.items():
            print(f"      - {type_name}: {count}")
        
        db.commit()
        print("\n✅ Comprehensive customer data added successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    add_comprehensive_customer_data()
    print("\n🎉 You can now test customer, ally, and consumer management in the frontend!")
    print("📝 The system includes:")
    print("   - Regular business customers with standard terms")
    print("   - Strategic allies with preferential terms")
    print("   - Individual consumers with retail terms")
    print("   - Suppliers for procurement management") 