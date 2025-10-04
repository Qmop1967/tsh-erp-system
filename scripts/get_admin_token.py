"""
Generate an admin token for testing
"""
import requests
import json

def get_admin_token():
    """Login as admin and get token"""
    url = "http://localhost:8000/api/auth/login"
    credentials = {
        "email": "admin@tsh.sale",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=credentials)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user = data.get('user')
            
            print("✅ Login successful!")
            print(f"   User: {user.get('name')} ({user.get('email')})")
            print(f"   Token: {token}")
            print("\n📋 Copy this token to use in your frontend:")
            print(f"   {token}")
            
            # Create localStorage format
            auth_data = {
                "state": {
                    "user": user,
                    "token": token,
                    "isLoading": False,
                    "error": None
                },
                "version": 0
            }
            
            print("\n📋 Or copy this to localStorage (key: 'tsh-erp-auth'):")
            print(json.dumps(auth_data, indent=2))
            
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_admin_token()
