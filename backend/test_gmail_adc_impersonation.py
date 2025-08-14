"""
Test Gmail API access with ADC and impersonation
"""

from google.auth import default
import google.auth.impersonated_credentials
import google.auth.transport.requests
from googleapiclient.discovery import build

print("Testing Gmail API with ADC and impersonation...\n")

# Configuration
SERVICE_ACCOUNT = "gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com"
MONITORING_EMAIL = "confirmaciones_dev@palace.cl"

# Step 1: Get default credentials
print("1. Getting default ADC credentials...")
source_credentials, project = default()
print(f"   Project: {project}")
print(f"   Credentials type: {type(source_credentials).__name__}")

# Step 2: Impersonate the service account
print(f"\n2. Impersonating service account: {SERVICE_ACCOUNT}")
target_scopes = ['https://www.googleapis.com/auth/gmail.readonly']

impersonated_creds = google.auth.impersonated_credentials.Credentials(
    source_credentials=source_credentials,
    target_principal=SERVICE_ACCOUNT,
    target_scopes=target_scopes,
    delegates=[]
)

# Step 3: Refresh to get access token
print("\n3. Getting access token...")
request = google.auth.transport.requests.Request()
impersonated_creds.refresh(request)
print("   Access token obtained!")

# Step 4: Build Gmail service
print("\n4. Building Gmail service...")
service = build('gmail', 'v1', credentials=impersonated_creds)

# Step 5: Test access
print("\n5. Testing API access...")

# Test 1: Try 'me' (this should fail for service account)
print("\n   Test A: Using userId='me'")
try:
    profile = service.users().getProfile(userId='me').execute()
    print(f"      Success! Profile: {profile}")
except Exception as e:
    print(f"      Failed: {e}")

# Test 2: Try with monitoring email directly
print(f"\n   Test B: Using userId='{MONITORING_EMAIL}'")
try:
    profile = service.users().getProfile(userId=MONITORING_EMAIL).execute()
    print(f"      Success! Can access {MONITORING_EMAIL}")
    print(f"      Email: {profile.get('emailAddress')}")
    print(f"      History ID: {profile.get('historyId')}")
except Exception as e:
    print(f"      Failed: {e}")

# Test 3: Try to list messages
print(f"\n   Test C: Listing messages from {MONITORING_EMAIL}")
try:
    messages = service.users().messages().list(
        userId=MONITORING_EMAIL,
        maxResults=5
    ).execute()
    print(f"      Success! Found {messages.get('resultSizeEstimate', 0)} messages")
    if messages.get('messages'):
        print(f"      First message ID: {messages['messages'][0]['id']}")
except Exception as e:
    print(f"      Failed: {e}")

print("\n" + "="*60)
print("SUMMARY:")
print("- If Test B and C work: Domain-wide delegation is properly configured!")
print("- If they fail with 'Delegation denied': Check Google Workspace Admin settings")
print("- If they fail with '400 Bad Request': The email might not exist")