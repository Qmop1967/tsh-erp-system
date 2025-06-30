"""
Test Frontend-Backend Connection
اختبار الاتصال بين الواجهة الأمامية والخلفية
"""

import requests
import json

def test_backend_connection():
    """Test if backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint specifically"""
    try:
        login_data = {
            "email": "admin@tsh-erp.com",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/login", 
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login endpoint working correctly")
            print(f"Response keys: {list(data.keys())}")
            print(f"User info: {data.get('user', {})}")
            return data.get("access_token")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_users_endpoint(token):
    """Test the users endpoint"""
    if not token:
        print("❌ No token available for users test")
        return
        
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:8000/api/users/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users endpoint working - got {len(users)} users")
            if users:
                print(f"Sample user fields: {list(users[0].keys())}")
            return True
        else:
            print(f"❌ Users endpoint failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Users request failed: {e}")
        return False

def main():
    print("🔍 Testing Frontend-Backend Connection")
    print("=" * 50)
    
    # Test 1: Backend connectivity
    print("\n1. Testing backend connectivity...")
    if not test_backend_connection():
        print("❌ Cannot proceed - backend not accessible")
        return
    
    # Test 2: Login endpoint
    print("\n2. Testing login endpoint...")
    token = test_login_endpoint()
    
    # Test 3: Users endpoint
    print("\n3. Testing users endpoint...")
    test_users_endpoint(token)
    
    print("\n" + "=" * 50)
    print("✅ Connection tests completed!")
    
    if token:
        print("\n🌐 Frontend should now be able to connect to backend")
        print("💡 Try logging in with: admin@tsh-erp.com / admin123")
    else:
        print("\n❌ Authentication issues detected")

if __name__ == "__main__":
    main()
