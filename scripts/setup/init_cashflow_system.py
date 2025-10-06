#!/usr/bin/env python3
"""
Initialize Cash Flow Management System Data
إعداد بيانات نظام إدارة التدفق النقدي

This script initializes the cash flow management system with:
- Branch updates for Main Wholesale and Dora Branch
- Sample salesperson (Ayad) with assigned regions
- Cash boxes for branches and salesperson
- Sample cash transactions and transfers
"""

import requests
import json
from datetime import datetime, date
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def initialize_branches():
    """تحديث بيانات الفروع"""
    print("🏢 Initializing Branch Data...")
    
    # Get existing branches
    response = requests.get(f"{BASE_URL}/branches")
    if response.status_code == 200:
        branches = response.json()
        print(f"   Found {len(branches)} existing branches")
        
        # Update first branch as Main Wholesale
        if len(branches) >= 1:
            main_branch = branches[0]
            update_data = {
                "name": "Main Wholesale Branch",
                "name_ar": "الفرع الرئيسي للجملة", 
                "name_en": "Main Wholesale Branch",
                "branch_code": "MWB-001",
                "branch_type": "MAIN_WHOLESALE",
                "location": "Baghdad - Al-Bayaa Industrial Area",
                "phone": "+964-770-123-4567",
                "email": "main@tsherp.com",
                "address_ar": "بغداد - المنطقة الصناعية في البياع",
                "address_en": "Baghdad - Al-Bayaa Industrial Area",
                "description_ar": "الفرع الرئيسي لمبيعات الجملة",
                "description_en": "Main branch for wholesale operations"
            }
            
            update_response = requests.put(f"{BASE_URL}/branches/{main_branch['id']}", 
                                         json=update_data, headers=HEADERS)
            if update_response.status_code == 200:
                print(f"   ✅ Updated Main Wholesale Branch (ID: {main_branch['id']})")
            else:
                print(f"   ❌ Failed to update main branch: {update_response.text}")
        
        # Update second branch as Dora Branch
        if len(branches) >= 2:
            dora_branch = branches[1]
            update_data = {
                "name": "Dora Branch", 
                "name_ar": "فرع الدورة",
                "name_en": "Dora Branch",
                "branch_code": "DRA-001",
                "branch_type": "DORA_BRANCH",
                "location": "Baghdad - Dora District",
                "phone": "+964-770-123-4568", 
                "email": "dora@tsherp.com",
                "address_ar": "بغداد - منطقة الدورة",
                "address_en": "Baghdad - Dora District",
                "description_ar": "فرع الدورة للمبيعات المحلية",
                "description_en": "Dora branch for local sales"
            }
            
            update_response = requests.put(f"{BASE_URL}/branches/{dora_branch['id']}", 
                                         json=update_data, headers=HEADERS)
            if update_response.status_code == 200:
                print(f"   ✅ Updated Dora Branch (ID: {dora_branch['id']})")
            else:
                print(f"   ❌ Failed to update dora branch: {update_response.text}")
        
        return branches
    else:
        print(f"   ❌ Failed to get branches: {response.text}")
        return []

def create_salesperson_ayad(main_branch_id):
    """إنشاء مندوب المبيعات أياد"""
    print("👤 Creating Salesperson Ayad...")
    
    # First check if Ayad already exists
    users_response = requests.get(f"{BASE_URL}/auth/users")
    if users_response.status_code == 200:
        users = users_response.json()
        ayad = None
        for user in users:
            if user['name'] == 'Ayad Al-Baghdadi' or user.get('employee_code') == 'SP-001':
                ayad = user
                break
        
        if ayad:
            print(f"   ✅ Ayad already exists (ID: {ayad['id']})")
            return ayad
    
    # Create Ayad if doesn't exist
    ayad_data = {
        "name": "Ayad Al-Baghdadi",
        "email": "ayad.baghdadi@tsherp.com",
        "password": "ayad123456",  # Should be changed in production
        "employee_code": "SP-001",
        "phone": "+964-770-555-0001",
        "is_salesperson": True,
        "role_id": 1,  # Assuming role 1 exists
        "branch_id": main_branch_id
    }
    
    # Note: We need to implement user creation in the auth router
    # For now, let's assume Ayad exists and return mock data
    print("   ⚠️  User creation not implemented yet. Using mock data.")
    return {
        "id": 999,  # Mock ID
        "name": "Ayad Al-Baghdadi",
        "employee_code": "SP-001",
        "phone": "+964-770-555-0001",
        "is_salesperson": True,
        "branch_id": main_branch_id
    }

def assign_regions_to_ayad(ayad_id):
    """تعيين المناطق لأياد"""
    print("🗺️  Assigning Regions to Ayad...")
    
    regions = [
        {"region": "KARBALA", "is_primary": True},
        {"region": "NAJAF", "is_primary": False},
        {"region": "BABEL", "is_primary": False}
    ]
    
    assigned_regions = []
    for region_data in regions:
        assignment_data = {
            "user_id": ayad_id,
            "region": region_data["region"],
            "is_primary": region_data["is_primary"],
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/cashflow/salesperson-regions", 
                               json=assignment_data, headers=HEADERS)
        if response.status_code == 200:
            assigned_region = response.json()
            assigned_regions.append(assigned_region)
            primary_text = " (Primary)" if region_data["is_primary"] else ""
            print(f"   ✅ Assigned {region_data['region']}{primary_text}")
        else:
            print(f"   ❌ Failed to assign {region_data['region']}: {response.text}")
    
    return assigned_regions

def create_cash_boxes(branches, ayad_data):
    """إنشاء صناديق النقد"""
    print("💰 Creating Cash Boxes...")
    
    cash_boxes = []
    
    # Main branch cash box
    if len(branches) >= 1:
        main_branch = branches[0]
        main_box_data = {
            "code": "CB-MWB-001",
            "name_ar": "صندوق الفرع الرئيسي",
            "name_en": "Main Wholesale Branch Cash Box",
            "box_type": "BRANCH",
            "branch_id": main_branch["id"],
            "balance_iqd_cash": 5000000.000,  # 5 million IQD
            "balance_iqd_digital": 2000000.000,  # 2 million IQD
            "balance_usd_cash": 15000.000,  # 15k USD
            "balance_usd_digital": 10000.000,  # 10k USD
            "description_ar": "الصندوق الرئيسي للفرع الأساسي",
            "description_en": "Main cash box for wholesale branch"
        }
        
        response = requests.post(f"{BASE_URL}/cashflow/cash-boxes", 
                               json=main_box_data, headers=HEADERS)
        if response.status_code == 200:
            cash_box = response.json()
            cash_boxes.append(cash_box)
            print(f"   ✅ Created Main Branch Cash Box (ID: {cash_box['id']})")
        else:
            print(f"   ❌ Failed to create main branch cash box: {response.text}")
    
    # Dora branch cash box
    if len(branches) >= 2:
        dora_branch = branches[1]
        dora_box_data = {
            "code": "CB-DRA-001",
            "name_ar": "صندوق فرع الدورة",
            "name_en": "Dora Branch Cash Box",
            "box_type": "BRANCH",
            "branch_id": dora_branch["id"],
            "balance_iqd_cash": 2000000.000,  # 2 million IQD
            "balance_iqd_digital": 500000.000,  # 500k IQD
            "balance_usd_cash": 5000.000,  # 5k USD
            "balance_usd_digital": 3000.000,  # 3k USD
            "description_ar": "صندوق فرع الدورة",
            "description_en": "Dora branch cash box"
        }
        
        response = requests.post(f"{BASE_URL}/cashflow/cash-boxes", 
                               json=dora_box_data, headers=HEADERS)
        if response.status_code == 200:
            cash_box = response.json()
            cash_boxes.append(cash_box)
            print(f"   ✅ Created Dora Branch Cash Box (ID: {cash_box['id']})")
        else:
            print(f"   ❌ Failed to create dora branch cash box: {response.text}")
    
    # Ayad's salesperson cash box
    ayad_box_data = {
        "code": "CB-SP-001-AYAD",
        "name_ar": "صندوق أياد البغدادي",
        "name_en": "Ayad Al-Baghdadi Cash Box",
        "box_type": "SALESPERSON",
        "branch_id": ayad_data["branch_id"],
        "user_id": ayad_data["id"],
        "balance_iqd_cash": 500000.000,  # 500k IQD
        "balance_iqd_digital": 100000.000,  # 100k IQD
        "balance_usd_cash": 2000.000,  # 2k USD
        "balance_usd_digital": 500.000,  # 500 USD
        "description_ar": "صندوق مندوب المبيعات أياد البغدادي - مناطق كربلاء والنجف وبابل",
        "description_en": "Ayad Al-Baghdadi salesperson cash box - Karbala, Najaf, Babel regions"
    }
    
    response = requests.post(f"{BASE_URL}/cashflow/cash-boxes", 
                           json=ayad_box_data, headers=HEADERS)
    if response.status_code == 200:
        cash_box = response.json()
        cash_boxes.append(cash_box)
        print(f"   ✅ Created Ayad's Cash Box (ID: {cash_box['id']})")
    else:
        print(f"   ❌ Failed to create Ayad's cash box: {response.text}")
    
    return cash_boxes

def create_sample_transactions(cash_boxes):
    """إنشاء معاملات نقدية نموذجية"""
    print("📝 Creating Sample Cash Transactions...")
    
    if len(cash_boxes) < 3:
        print("   ❌ Not enough cash boxes created")
        return []
    
    ayad_cash_box = cash_boxes[2]  # Ayad's cash box
    transactions = []
    
    # Sample customer payments received by Ayad
    sample_transactions = [
        {
            "transaction_type": "RECEIPT",
            "payment_method": "CASH",
            "currency_code": "IQD",
            "amount": 250000.000,
            "customer_name": "شركة المعالم التجارية",
            "description_ar": "استلام دفعة من عميل في كربلاء",
            "description_en": "Payment received from client in Karbala",
            "region": "KARBALA",
            "location_details": "كربلاء - شارع الحر"
        },
        {
            "transaction_type": "RECEIPT", 
            "payment_method": "DIGITAL",
            "currency_code": "IQD",
            "amount": 150000.000,
            "customer_name": "مؤسسة النجف للتجارة",
            "description_ar": "تحويل بنكي من عميل في النجف",
            "description_en": "Bank transfer from client in Najaf",
            "region": "NAJAF",
            "location_details": "النجف - شارع الصادق"
        },
        {
            "transaction_type": "PAYMENT",
            "payment_method": "CASH",
            "currency_code": "IQD", 
            "amount": 50000.000,
            "description_ar": "مصاريف سفر ووقود",
            "description_en": "Travel and fuel expenses",
            "region": "BABEL",
            "location_details": "بابل - الحلة"
        },
        {
            "transaction_type": "RECEIPT",
            "payment_method": "CASH",
            "currency_code": "USD",
            "amount": 500.000,
            "customer_name": "Al-Furat Trading Co.",
            "description_ar": "استلام دفعة بالدولار من عميل كبير",
            "description_en": "USD payment from major client",
            "region": "KARBALA",
            "location_details": "كربلاء - المنطقة الصناعية"
        }
    ]
    
    for tx_data in sample_transactions:
        transaction = {
            "cash_box_id": ayad_cash_box["id"],
            "transaction_date": datetime.now().isoformat(),
            **tx_data
        }
        
        response = requests.post(f"{BASE_URL}/cashflow/cash-transactions",
                               json=transaction, headers=HEADERS)
        if response.status_code == 200:
            created_tx = response.json()
            transactions.append(created_tx)
            print(f"   ✅ Created {tx_data['transaction_type']} transaction: {tx_data['amount']} {tx_data['currency_code']}")
        else:
            print(f"   ❌ Failed to create transaction: {response.text}")
    
    return transactions

def create_sample_transfer(cash_boxes):
    """إنشاء تحويل نقدي نموذجي"""
    print("🔄 Creating Sample Cash Transfer...")
    
    if len(cash_boxes) < 2:
        print("   ❌ Not enough cash boxes for transfer")
        return None
    
    ayad_cash_box = cash_boxes[2]  # Ayad's cash box
    main_branch_box = cash_boxes[0]  # Main branch cash box
    
    transfer_data = {
        "from_cash_box_id": ayad_cash_box["id"],
        "to_cash_box_id": main_branch_box["id"],
        "currency_code": "IQD",
        "amount": 300000.000,  # 300k IQD
        "payment_method": "CASH",
        "description_ar": "تحويل المتحصلات اليومية من أياد إلى الفرع الرئيسي",
        "description_en": "Daily collections transfer from Ayad to main branch",
        "transfer_reason": "End of day collections transfer"
    }
    
    response = requests.post(f"{BASE_URL}/cashflow/cash-transfers",
                           json=transfer_data, headers=HEADERS)
    if response.status_code == 200:
        transfer = response.json()
        print(f"   ✅ Created transfer request: {transfer['transfer_number']}")
        print(f"      Status: {transfer['status']}")
        print(f"      Amount: {transfer['amount']} {transfer['currency_code']}")
        return transfer
    else:
        print(f"   ❌ Failed to create transfer: {response.text}")
        return None

def test_dashboard_endpoints():
    """اختبار نقاط الاتصال للوحة المعلومات"""
    print("📊 Testing Dashboard Endpoints...")
    
    # Test system dashboard
    response = requests.get(f"{BASE_URL}/cashflow/dashboard/system")
    if response.status_code == 200:
        dashboard = response.json()
        print(f"   ✅ System Dashboard: {len(dashboard.get('branches', []))} branches, {len(dashboard.get('salespeople', []))} salespeople")
    else:
        print(f"   ❌ Failed to get system dashboard: {response.text}")
    
    # Test cash boxes endpoint
    response = requests.get(f"{BASE_URL}/cashflow/cash-boxes")
    if response.status_code == 200:
        cash_boxes = response.json()
        print(f"   ✅ Cash Boxes: {len(cash_boxes)} boxes found")
        for box in cash_boxes:
            total_iqd = box['balance_iqd_cash'] + box['balance_iqd_digital']
            total_usd = box['balance_usd_cash'] + box['balance_usd_digital']
            print(f"      - {box['name_en']}: {total_iqd:,.0f} IQD, {total_usd:,.0f} USD")
    else:
        print(f"   ❌ Failed to get cash boxes: {response.text}")

def main():
    """الدالة الرئيسية"""
    print("🚀 TSH ERP Cash Flow Management System Initialization")
    print("=" * 60)
    
    try:
        # Step 1: Initialize branches
        branches = initialize_branches()
        if not branches:
            print("❌ Failed to initialize branches. Exiting.")
            return
        
        # Step 2: Create/get salesperson Ayad
        main_branch_id = branches[0]["id"] if branches else 1
        ayad_data = create_salesperson_ayad(main_branch_id)
        
        # Step 3: Assign regions to Ayad
        assigned_regions = assign_regions_to_ayad(ayad_data["id"])
        
        # Step 4: Create cash boxes
        cash_boxes = create_cash_boxes(branches, ayad_data)
        
        # Step 5: Create sample transactions
        transactions = create_sample_transactions(cash_boxes)
        
        # Step 6: Create sample transfer
        transfer = create_sample_transfer(cash_boxes)
        
        # Step 7: Test dashboard
        test_dashboard_endpoints()
        
        print("\n🎉 Cash Flow Management System Initialization Complete!")
        print("\n📋 Summary:")
        print(f"   - Branches updated: {len(branches)}")
        print(f"   - Regions assigned to Ayad: {len(assigned_regions)}")
        print(f"   - Cash boxes created: {len(cash_boxes)}")
        print(f"   - Sample transactions: {len(transactions)}")
        print(f"   - Sample transfers: {1 if transfer else 0}")
        
        print("\n📱 Next Steps:")
        print("   1. Access the cash flow dashboard at /api/cashflow/dashboard/system")
        print("   2. Check Ayad's cash box status at /api/cashflow/cash-boxes")
        print("   3. Review pending transfers at /api/cashflow/cash-transfers")
        print("   4. Test the mobile quick actions for receipts and payments")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")

if __name__ == "__main__":
    main()
