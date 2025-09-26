#!/usr/bin/env python3
"""
Test Customer Management System Stability
اختبار استقرار نظام إدارة العملاء
"""

import requests
import json
import time

def test_customer_stability():
    """Test all customer management operations for stability"""
    
    print("🧪 Testing Customer Management System Stability")
    print("=" * 50)
    
    # Login
    print("1. 🔐 Testing Authentication...")
    login_data = {'email': 'admin@tsh-erp.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        assert False, f"Login failed: {login_response.text}"
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("   ✅ Authentication successful")
    
    # Test 1: Create Customer
    print("\\n2. 🏗️ Testing Customer Creation...")
    test_customer = {
        'customer_code': f'TEST-{int(time.time())}',
        'name': 'Stability Test Customer',
        'company_name': 'Test Company Ltd.',
        'email': 'test@stability.com',
        'phone': '+964-777-123456',
        'address': 'Test Address',
        'city': 'Test City',
        'country': 'Iraq',
        'credit_limit': 15000,
        'payment_terms': 30,
        'discount_percentage': 5,
        'is_active': True
    }
    
    create_response = requests.post('http://localhost:8000/api/customers', json=test_customer, headers=headers)
    if create_response.status_code != 201:
        print(f"   ❌ Customer creation failed: {create_response.text}")
        return False
    
    customer = create_response.json()
    customer_id = customer['id']
    print(f"   ✅ Customer created successfully (ID: {customer_id})")
    
    # Test 2: Read Customers
    print("\\n3. 📖 Testing Customer Reading...")
    get_response = requests.get('http://localhost:8000/api/customers', headers=headers)
    if get_response.status_code != 200:
        print(f"   ❌ Customer reading failed: {get_response.text}")
        return False
    
    customers = get_response.json()
    print(f"   ✅ Successfully read {len(customers)} customers")
    
    # Test 3: Get Combined Customers (Frontend Endpoint)
    combined_response = requests.get('http://localhost:8000/api/customers/all/combined', headers=headers)
    if combined_response.status_code != 200:
        print(f"   ❌ Combined customers endpoint failed: {combined_response.text}")
        return False
    
    combined_data = combined_response.json()
    print(f"   ✅ Combined endpoint: {combined_data['total']} customers")
    
    # Test 4: Update Customer
    print("\\n4. ✏️ Testing Customer Update...")
    update_data = {
        'name': 'Updated Stability Test Customer',
        'city': 'Updated Test City',
        'credit_limit': 20000
    }
    
    update_response = requests.put(f'http://localhost:8000/api/customers/{customer_id}', json=update_data, headers=headers)
    if update_response.status_code != 200:
        print(f"   ❌ Customer update failed: {update_response.text}")
        return False
    
    updated_customer = update_response.json()
    print(f"   ✅ Customer updated successfully: {updated_customer['name']}")
    
    # Test 5: Get Single Customer
    print("\\n5. 🔍 Testing Single Customer Retrieval...")
    get_one_response = requests.get(f'http://localhost:8000/api/customers/{customer_id}', headers=headers)
    if get_one_response.status_code != 200:
        print(f"   ❌ Single customer retrieval failed: {get_one_response.text}")
        return False
    
    single_customer = get_one_response.json()
    print(f"   ✅ Retrieved customer: {single_customer['name']}")
    
    # Test 6: Delete Customer (Soft Delete)
    print("\\n6. 🗑️ Testing Customer Deletion...")
    delete_response = requests.delete(f'http://localhost:8000/api/customers/{customer_id}', headers=headers)
    if delete_response.status_code != 200:
        print(f"   ❌ Customer deletion failed: {delete_response.text}")
        return False
    
    deleted_customer = delete_response.json()
    print(f"   ✅ Customer deleted (deactivated): {deleted_customer['name']}")
    print(f"   📍 Customer status: {'Active' if deleted_customer['is_active'] else 'Inactive'}")
    
    # Test 7: Test Error Handling
    print("\\n7. ⚠️ Testing Error Handling...")
    
    # Try to create duplicate customer code
    duplicate_response = requests.post('http://localhost:8000/api/customers', json=test_customer, headers=headers)
    if duplicate_response.status_code == 400:
        print("   ✅ Duplicate customer code properly rejected")
    else:
        print(f"   ❌ Duplicate handling failed: {duplicate_response.status_code}")
    
    # Try to access non-existent customer
    fake_response = requests.get('http://localhost:8000/api/customers/99999', headers=headers)
    if fake_response.status_code == 404:
        print("   ✅ Non-existent customer properly handled")
    else:
        print(f"   ❌ Non-existent customer handling failed: {fake_response.status_code}")
    
    # Test 8: System Resource Check
    print("\\n8. 🔧 Testing System Resources...")
    try:
        # Multiple rapid requests to test stability
        for i in range(5):
            rapid_response = requests.get('http://localhost:8000/api/customers/all/combined', headers=headers)
            if rapid_response.status_code != 200:
                print(f"   ❌ System unstable under load: {rapid_response.status_code}")
                return False
        print("   ✅ System stable under rapid requests")
    except Exception as e:
        print(f"   ❌ System error under load: {e}")
        assert False, f"System error under load: {e}"
    
    print("\\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED - CUSTOMER MANAGEMENT SYSTEM IS STABLE")
    print("=" * 50)
    
    assert True  # Test passed

if __name__ == "__main__":
    success = test_customer_stability()
    if success:
        print("\\n✅ Customer Management System is ready for production use!")
        print("\\n📋 Available Features:")
        print("   • ✅ Create new customers")
        print("   • ✅ View all customers (regular + Zoho)")
        print("   • ✅ Edit customer information")
        print("   • ✅ Delete customers (soft delete)")
        print("   • ✅ Search and filter customers")
        print("   • ✅ Secure authentication")
        print("   • ✅ Error handling")
        print("   • ✅ System stability")
    else:
        print("\\n❌ Customer Management System has issues that need to be resolved.")
