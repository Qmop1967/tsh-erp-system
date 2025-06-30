"""
Test User Management API Endpoints
اختبار نقاط النهاية لإدارة المستخدمين
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test user login"""
    print("Testing login...")
    
    login_data = {
        "email": "admin@tsh-erp.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"Token: {data['access_token'][:50]}...")
        print(f"User: {data['user']['name']} ({data['user']['role']})")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_get_users(token):
    """Test getting users list"""
    print("\nTesting get users...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Got {len(users)} users:")
        for user in users:
            print(f"  - {user['name']} ({user['email']})")
        return users
    else:
        print(f"❌ Failed to get users: {response.status_code}")
        print(response.text)
        return []

def test_get_roles(token):
    """Test getting roles list"""
    print("\nTesting get roles...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/roles", headers=headers)
    
    if response.status_code == 200:
        roles = response.json()
        print(f"✅ Got {len(roles)} roles:")
        for role in roles:
            print(f"  - {role['name']} (ID: {role['id']})")
        return roles
    else:
        print(f"❌ Failed to get roles: {response.status_code}")
        print(response.text)
        return []

def test_get_branches(token):
    """Test getting branches list"""
    print("\nTesting get branches...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/branches", headers=headers)
    
    if response.status_code == 200:
        branches = response.json()
        print(f"✅ Got {len(branches)} branches:")
        for branch in branches:
            print(f"  - {branch['name']} ({branch['code']}) (ID: {branch['id']})")
        return branches
    else:
        print(f"❌ Failed to get branches: {response.status_code}")
        print(response.text)
        return []

def test_create_user(token, roles, branches):
    """Test creating a new user"""
    print("\nTesting create user...")
    
    if not roles or not branches:
        print("❌ Cannot create user without roles and branches")
        return None
    
    new_user_data = {
        "name": "Test User",
        "email": "test@tsh-erp.com",
        "password": "test123",
        "role_id": roles[0]["id"],  # Use first role
        "branch_id": branches[0]["id"],  # Use first branch
        "employee_code": "TEST001",
        "phone": "+964-xxx-test",
        "is_salesperson": False,
        "is_active": True
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/users/", json=new_user_data, headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Created user: {user['name']} (ID: {user['id']})")
        return user
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        print(response.text)
        return None

def main():
    """Main test function"""
    print("🧪 Testing TSH ERP User Management API")
    print("=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot continue without authentication")
        return
    
    # Test getting users
    users = test_get_users(token)
    
    # Test getting roles
    roles = test_get_roles(token)
    
    # Test getting branches  
    branches = test_get_branches(token)
    
    # Test creating a new user
    new_user = test_create_user(token, roles, branches)
    
    print("\n" + "=" * 50)
    print("✅ User Management API tests completed!")
    
    if new_user:
        print(f"\n🔗 You can now login with the new test user:")
        print(f"   Email: test@tsh-erp.com")
        print(f"   Password: test123")

if __name__ == "__main__":
    main()
