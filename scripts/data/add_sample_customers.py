#!/usr/bin/env python3
"""
Add sample customers to test the customer management functionality
إضافة عملاء عينة لاختبار وظائف إدارة العملاء
"""

import requests
import json

def add_sample_customers():
    """Add sample customers"""
    
    # Login to get token
    print("🔐 Logging in...")
    login_data = {'email': 'admin@tsh-erp.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Sample customers
    customers = [
        {
            'customer_code': 'CUST-002',
            'name': 'Baghdad Electronics',
            'company_name': 'Baghdad Electronics Co.',
            'email': 'info@baghdad-electronics.com',
            'phone': '+964-1-7777777',
            'address': 'Al-Karrada, Baghdad',
            'city': 'Baghdad',
            'country': 'Iraq',
            'credit_limit': 50000,
            'payment_terms': 30,
            'discount_percentage': 10,
            'is_active': True,
            'notes': 'Electronics distributor in Baghdad'
        },
        {
            'customer_code': 'CUST-003',
            'name': 'Erbil Trading LLC',
            'company_name': 'Erbil Trading LLC',
            'email': 'sales@erbil-trading.com',
            'phone': '+964-66-2222222',
            'address': 'Downtown, Erbil',
            'city': 'Erbil',
            'country': 'Iraq',
            'credit_limit': 75000,
            'payment_terms': 45,
            'discount_percentage': 15,
            'is_active': True,
            'notes': 'Import/Export company'
        },
        {
            'customer_code': 'CUST-004',
            'name': 'Basra Oil Services',
            'company_name': 'Basra Oil Services Ltd.',
            'email': 'procurement@basra-oil.com',
            'phone': '+964-40-5555555',
            'address': 'Industrial Zone, Basra',
            'city': 'Basra',
            'country': 'Iraq',
            'credit_limit': 100000,
            'payment_terms': 60,
            'discount_percentage': 8,
            'is_active': True,
            'notes': 'Oil industry supplier'
        },
        {
            'customer_code': 'CUST-005',
            'name': 'Najaf Construction',
            'company_name': 'Najaf Construction Co.',
            'email': 'projects@najaf-const.com',
            'phone': '+964-33-8888888',
            'address': 'Industrial Area, Najaf',
            'city': 'Najaf',
            'country': 'Iraq',
            'credit_limit': 25000,
            'payment_terms': 30,
            'discount_percentage': 5,
            'is_active': True,
            'notes': 'Construction and building materials'
        },
        {
            'customer_code': 'CUST-006',
            'name': 'Sulaymaniyah Tech Hub',
            'company_name': 'Sulaymaniyah Technology Hub',
            'email': 'info@suli-tech.com',
            'phone': '+964-53-9999999',
            'address': 'Tech District, Sulaymaniyah',
            'city': 'Sulaymaniyah',
            'country': 'Iraq',
            'credit_limit': 40000,
            'payment_terms': 30,
            'discount_percentage': 12,
            'is_active': True,
            'notes': 'Technology and IT services'
        }
    ]
    
    print(f"🏢 Adding {len(customers)} sample customers...")
    
    for i, customer_data in enumerate(customers, 1):
        try:
            response = requests.post('http://localhost:8000/api/customers', json=customer_data, headers=headers)
            if response.status_code == 201:
                customer = response.json()
                print(f"  ✅ {i}. Created: {customer['name']} ({customer['customer_code']})")
            elif response.status_code == 400 and 'already exists' in response.text:
                print(f"  ⚠️ {i}. Skipped: {customer_data['name']} (already exists)")
            else:
                print(f"  ❌ {i}. Failed: {customer_data['name']} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ {i}. Error creating {customer_data['name']}: {e}")
    
    # Get final count
    try:
        response = requests.get('http://localhost:8000/api/customers/all/combined', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Final customer count:")
            print(f"   Total: {data['total']} customers")
            print(f"   Regular: {data['total_regular']} customers")
            print(f"   Zoho: {data['total_migrated']} customers")
        else:
            print(f"❌ Error getting customer count: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Adding Sample Customers to TSH ERP System")
    print("=" * 50)
    add_sample_customers()
    print("\n✅ Sample customers added successfully!")
    print("Now you can test the customer management features in the frontend.")
