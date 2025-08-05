"""
Test script to create a Firebase token for testing
"""

import firebase_admin
from firebase_admin import auth
import requests

# This script creates a custom token for testing
def create_test_token():
    try:
        # Create a custom token for our test user
        custom_token = auth.create_custom_token('admin@bancoabc.cl', {
            'email': 'admin@bancoabc.cl',
            'email_verified': True
        })
        
        print("Custom token created:")
        print(custom_token.decode('utf-8'))
        print("\nUse this in your curl command:")
        print(f"curl -H \"Authorization: Bearer {custom_token.decode('utf-8')}\" http://127.0.0.1:8000/api/v1/users/me")
        
    except Exception as e:
        print(f"Error creating token: {e}")

if __name__ == "__main__":
    create_test_token()