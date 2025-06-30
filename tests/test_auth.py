#!/usr/bin/env python3
"""
TSH ERP Authentication Test Script
This script tests the authentication functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_authentication():
    """Test authentication endpoints"""
    print("🔐 Testing TSH ERP Authentication")
    print("=" * 50)
    
    # Test data
    test_users = [
        {
            "email": "admin@tsh.com",
            "password": "admin2025!",
            "name": "TSH Admin"
        },
        {
            "email": "ahmed.kareem@tsh.com", 
            "password": "ahmed2025!",
            "name": "Ahmed Kareem"
        },
        {
            "email": "ayad.fadel@tsh.com",
            "password": "ayad2025!",
            "name": "Ayad Fadel"
        }
    ]
    
    for user in test_users:
        print(f"\n🧪 Testing login for: {user['name']}")
        
        # Test login
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Login successful!")
                print(f"     Token: {result['access_token'][:50]}...")
                print(f"     User: {result['user']['name']}")
                print(f"     Role: {result['user']['role']}")
                print(f"     Branch: {result['user']['branch']}")
                
                # Test getting current user info
                headers = {"Authorization": f"Bearer {result['access_token']}"}
                me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    me_result = me_response.json()
                    print(f"  ✅ Token verification successful!")
                    print(f"     Verified User: {me_result['name']}")
                else:
                    print(f"  ❌ Token verification failed: {me_response.status_code}")
                    
            else:
                print(f"  ❌ Login failed: {response.status_code}")
                print(f"     Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Cannot connect to server. Make sure the server is running on {BASE_URL}")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n✅ Authentication test completed!")

if __name__ == "__main__":
    test_authentication()
