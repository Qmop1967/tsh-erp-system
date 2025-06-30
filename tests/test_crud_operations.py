#!/usr/bin/env python3

"""
Test script for CRUD operations on migration items API endpoints
"""

import requests
import json
import sys
import random
import string

BASE_URL = "http://localhost:8000"

def generate_random_code():
    """Generate a random item code"""
    return "TEST" + ''.join(random.choices(string.digits, k=4))

def test_api_endpoints():
    """Test all CRUD operations for items"""
    
    print("🧪 Testing Items CRUD Operations")
    print("=" * 50)
    
    # Test 1: GET all items
    print("\n1. 📖 Testing GET /api/migration/items/")
    try:
        response = requests.get(f"{BASE_URL}/api/migration/items/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ Success: Retrieved {len(items)} items")
            if items:
                print(f"   📋 Sample item: {items[0]['name_en']} (ID: {items[0]['id']})")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: GET all categories
    print("\n2. 📖 Testing GET /api/migration/categories/")
    try:
        response = requests.get(f"{BASE_URL}/api/migration/categories/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Success: Retrieved {len(categories)} categories")
            if categories:
                print(f"   📋 Sample category: {categories[0]['name_en']} (ID: {categories[0]['id']})")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: POST create new item
    print("\n3. ➕ Testing POST /api/migration/items/")
    new_item = {
        "code": "TEST001",
        "name_ar": "عنصر تجريبي",
        "name_en": "Test Item",
        "description_ar": "وصف العنصر التجريبي",
        "description_en": "Test item description",
        "category_id": 1,
        "brand": "Test Brand",
        "model": "Test Model",
        "unit_of_measure": "PCS",
        "cost_price_usd": 10.50,
        "cost_price_iqd": 13650.0,
        "selling_price_usd": 15.75,
        "selling_price_iqd": 20475.0,
        "track_inventory": True,
        "reorder_level": 5,
        "reorder_quantity": 20,
        "weight": 0.5,
        "dimensions": "10x5x2",
        "is_active": True,
        "is_serialized": False,
        "is_batch_tracked": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/migration/items/", json=new_item)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            created_item = response.json()
            print(f"   ✅ Success: Created item with ID {created_item['id']}")
            test_item_id = created_item['id']
            
            # Test 4: GET specific item
            print(f"\n4. 📖 Testing GET /api/migration/items/{test_item_id}")
            get_response = requests.get(f"{BASE_URL}/api/migration/items/{test_item_id}")
            print(f"   Status: {get_response.status_code}")
            if get_response.status_code == 200:
                item = get_response.json()
                print(f"   ✅ Success: Retrieved item '{item['name_en']}'")
            else:
                print(f"   ❌ Error: {get_response.text}")
            
            # Test 5: PUT update item
            print(f"\n5. ✏️  Testing PUT /api/migration/items/{test_item_id}")
            updated_item = new_item.copy()
            updated_item['name_en'] = "Updated Test Item"
            updated_item['selling_price_usd'] = 18.00
            
            put_response = requests.put(f"{BASE_URL}/api/migration/items/{test_item_id}", json=updated_item)
            print(f"   Status: {put_response.status_code}")
            if put_response.status_code == 200:
                updated = put_response.json()
                print(f"   ✅ Success: Updated item to '{updated['name_en']}'")
                print(f"   💰 Price updated to ${updated['selling_price_usd']}")
            else:
                print(f"   ❌ Error: {put_response.text}")
            
            # Test 6: DELETE item
            print(f"\n6. 🗑️  Testing DELETE /api/migration/items/{test_item_id}")
            delete_response = requests.delete(f"{BASE_URL}/api/migration/items/{test_item_id}")
            print(f"   Status: {delete_response.status_code}")
            if delete_response.status_code == 204:
                print(f"   ✅ Success: Item deleted successfully")
                
                # Verify deletion
                verify_response = requests.get(f"{BASE_URL}/api/migration/items/{test_item_id}")
                if verify_response.status_code == 404:
                    print(f"   ✅ Verified: Item no longer exists")
                else:
                    print(f"   ⚠️  Warning: Item still exists after deletion")
            else:
                print(f"   ❌ Error: {delete_response.text}")
                
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CRUD Operations Test Complete!")

if __name__ == "__main__":
    test_api_endpoints()
