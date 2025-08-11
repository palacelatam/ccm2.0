#!/usr/bin/env python3
"""
Test script for new trade-related endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test client ID (replace with actual client ID from your database)
CLIENT_ID = "test-client-id"

def test_endpoints():
    """Test the new trade-related endpoints"""
    
    print("Testing Trade-Related Endpoints")
    print("=" * 50)
    
    # Test get unmatched trades
    print("\n1. Testing GET /clients/{client_id}/unmatched-trades")
    try:
        response = requests.get(f"{BASE_URL}/clients/{CLIENT_ID}/unmatched-trades")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test get email confirmations
    print(f"\n2. Testing GET /clients/{CLIENT_ID}/email-confirmations")
    try:
        response = requests.get(f"{BASE_URL}/clients/{CLIENT_ID}/email-confirmations")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test get matches
    print(f"\n3. Testing GET /clients/{CLIENT_ID}/matches")
    try:
        response = requests.get(f"{BASE_URL}/clients/{CLIENT_ID}/matches")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test process matches
    print(f"\n4. Testing POST /clients/{CLIENT_ID}/process-matches")
    try:
        response = requests.post(f"{BASE_URL}/clients/{CLIENT_ID}/process-matches")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

def test_backend_running():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/../health")
        if response.status_code == 200:
            print("Backend is running")
            return True
    except:
        pass
    
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("Backend is running")
            return True
    except:
        pass
    
    print("Backend is not running or not accessible")
    print("Please make sure the backend is running on http://127.0.0.1:8000")
    return False

def main():
    print("Trade Endpoints Test Script")
    print("=" * 50)
    
    if not test_backend_running():
        return 1
    
    # Note: These endpoints require authentication
    print("\nNote: These endpoints require authentication.")
    print("You may see 401 Unauthorized errors, which is expected.")
    print("The important thing is that the endpoints exist and return proper error codes.\n")
    
    test_endpoints()
    
    print(f"\n" + "=" * 50)
    print("Test completed!")
    print("\nNext steps:")
    print("1. Start the backend with authentication")
    print("2. Test with proper authentication headers")
    print("3. Create sample trade and email data")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())