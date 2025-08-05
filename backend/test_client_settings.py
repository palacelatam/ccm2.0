"""
Test script for client settings API endpoints
This script authenticates with Firebase and tests the client settings APIs
"""

import requests
import json
from datetime import datetime

# Firebase Auth endpoint for getting ID token
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIREBASE_API_KEY = "demo-key"  # This works with emulator

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token(email: str, password: str) -> str:
    """Get Firebase auth token for API calls"""
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # For Firebase emulator, we need to use the emulator endpoint
        emulator_url = "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        
        response = requests.post(
            emulator_url,
            params={"key": FIREBASE_API_KEY},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('idToken')
        else:
            print(f"Auth failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_client_settings_api(token: str):
    """Test client settings API endpoints"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    client_id = "xyz-corp"
    
    print(f"Testing Client Settings API for client: {client_id}")
    print("=" * 60)
    
    # Test 1: Get client settings
    print("\n1. Testing GET /api/v1/clients/{client_id}/settings")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/clients/{client_id}/settings", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Settings: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 2: Update client settings
    print(f"\n2. Testing PUT /api/v1/clients/{client_id}/settings")
    update_data = {
        "automation": {
            "dataSharing": True,
            "autoConfirmMatched": {
                "enabled": True,
                "delayMinutes": 30
            }
        },
        "preferences": {
            "language": "es",
            "timezone": "America/Santiago"
        }
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/clients/{client_id}/settings", 
            headers=headers,
            json=update_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Updated settings: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 3: Get bank accounts
    print(f"\n3. Testing GET /api/v1/clients/{client_id}/bank-accounts")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/clients/{client_id}/bank-accounts", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Bank accounts: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 4: Get settlement rules
    print(f"\n4. Testing GET /api/v1/clients/{client_id}/settlement-rules")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/clients/{client_id}/settlement-rules", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Settlement rules: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    print("Client Settings API Test")
    print("=" * 40)
    
    # Test credentials
    email = "admin@xyz.cl"
    password = "demo123"
    
    print(f"Getting auth token for {email}...")
    token = get_auth_token(email, password)
    
    if not token:
        print("Failed to get auth token. Make sure Firebase emulator is running.")
        return
    
    print("Got auth token successfully")
    print(f"Token: {token[:50]}...")
    
    # Test the APIs
    test_client_settings_api(token)

if __name__ == "__main__":
    main()