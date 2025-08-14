"""
Test Gmail API access with service account key
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

print("Testing Gmail API with service account key...\n")

MONITORING_EMAIL = "confirmaciones_dev@palace.cl"
KEY_FILE = "gmail-service-account.json"

# Check if key file exists
if not os.path.exists(KEY_FILE):
    print(f"❌ Key file not found: {KEY_FILE}")
    exit(1)

print(f"✅ Found key file: {KEY_FILE}")

# Load service account credentials
print("\n1. Loading service account credentials...")
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE,
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

# Apply domain-wide delegation
print(f"2. Applying domain-wide delegation for: {MONITORING_EMAIL}")
delegated_credentials = credentials.with_subject(MONITORING_EMAIL)

# Build Gmail service
print("3. Building Gmail service...")
service = build('gmail', 'v1', credentials=delegated_credentials)

# Test access
print(f"\n4. Testing access to {MONITORING_EMAIL}...")
try:
    # Get profile
    profile = service.users().getProfile(userId='me').execute()
    print(f"   ✅ SUCCESS! Connected to Gmail")
    print(f"   Email: {profile.get('emailAddress')}")
    print(f"   Total messages: {profile.get('messagesTotal')}")
    print(f"   History ID: {profile.get('historyId')}")
    
    # List recent messages
    print("\n5. Checking for recent messages...")
    messages = service.users().messages().list(
        userId='me',
        maxResults=5
    ).execute()
    
    message_count = messages.get('resultSizeEstimate', 0)
    print(f"   Found {message_count} messages")
    
    if messages.get('messages'):
        print(f"   Latest message ID: {messages['messages'][0]['id']}")
    
    print("\n✅ Gmail service is working correctly!")
    
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    print("\nPossible issues:")
    print("- Domain-wide delegation not configured in Google Workspace Admin")
    print("- The service account doesn't have the correct OAuth scopes")
    print("- The monitoring email doesn't exist")