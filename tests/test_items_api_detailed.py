#!/usr/bin/env python3
"""
Test Items API Script for TSH ERP System
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_items_api():
    """Test the items API endpoints"""
    print("🔧 Testing Items API...")
    
    try:
        # Test without authentication first
        print("\n1️⃣ Testing GET /api/items/ (without auth)...")
        response = requests.get(f"{BASE_URL}/items/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json()
            print(f"   Items returned: {len(items)}")
            if items:
                print(f"   First item: {items[0].get('name_en', 'No name')}")
        else:
            print(f"   Error: {response.text}")
            
        # Test direct database query via migration endpoint
        print("\n2️⃣ Testing GET /api/migration/items/...")
        response = requests.get(f"{BASE_URL}/migration/items/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json()
            print(f"   Items returned: {len(items)}")
            if items:
                print(f"   First item: {items[0].get('name_en', 'No name')}")
        else:
            print(f"   Error: {response.text}")
            
        # Test categories
        print("\n3️⃣ Testing GET /api/migration/categories/...")
        response = requests.get(f"{BASE_URL}/migration/categories/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"   Categories returned: {len(categories)}")
            for cat in categories[:3]:  # Show first 3
                print(f"   - {cat.get('name_en', 'No name')} ({cat.get('code', 'No code')})")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_items_api()
