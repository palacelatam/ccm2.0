"""
Simple test script to verify FastAPI backend is working
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoints():
    """Test health check endpoints"""
    print("Testing health endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_auth_without_token():
    """Test auth endpoints without token (should fail)"""
    print("\nTesting protected endpoints without token...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/me")
        print(f"GET /api/v1/users/me - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_docs_endpoint():
    """Test if API docs are accessible"""
    print("\nTesting API documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"GET /docs - Status: {response.status_code}")
        if response.status_code == 200:
            print("API docs are accessible")
        else:
            print(f"Error accessing docs: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Testing FastAPI backend at {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    test_health_endpoints()
    test_auth_without_token()
    test_docs_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")