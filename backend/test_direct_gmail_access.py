"""
Test direct Gmail API access without impersonation
"""

from google.auth import default
from googleapiclient.discovery import build

print("Testing direct Gmail API access...\n")

MONITORING_EMAIL = "confirmaciones_dev@servicios.palace.cl"
YOUR_EMAIL = "ben.clark@palace.cl"  # Update this if different

# Get default credentials with Gmail scope
print("1. Getting ADC credentials with Gmail scope...")
credentials, project = default(
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
print(f"   Project: {project}")
print(f"   Credentials type: {type(credentials).__name__}")

# Build Gmail service
print("\n2. Building Gmail service...")
service = build('gmail', 'v1', credentials=credentials)

# Test 1: Access your own email
print(f"\n3. Testing access to YOUR email ({YOUR_EMAIL})...")
try:
    profile = service.users().getProfile(userId=YOUR_EMAIL).execute()
    print(f"   ✓ Success! Can access {YOUR_EMAIL}")
    print(f"   Email: {profile.get('emailAddress')}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 2: Access monitoring email directly (if you have delegated access)
print(f"\n4. Testing access to monitoring email ({MONITORING_EMAIL})...")
try:
    profile = service.users().getProfile(userId=MONITORING_EMAIL).execute()
    print(f"   ✓ Success! Can access {MONITORING_EMAIL}")
    print(f"   Email: {profile.get('emailAddress')}")
    print(f"   History ID: {profile.get('historyId')}")
    
    # Try listing messages
    messages = service.users().messages().list(
        userId=MONITORING_EMAIL,
        maxResults=5
    ).execute()
    print(f"   Found {messages.get('resultSizeEstimate', 0)} messages")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n" + "="*60)
print("OPTIONS:")
print("\n1. If you can access the monitoring email directly:")
print("   → You have delegated access set up in Google Workspace")
print("   → We can use direct access without service account")
print("\n2. If you can't access the monitoring email:")
print("   → Option A: Set up delegated access in Gmail settings")
print("   → Option B: Use a shared credential approach")
print("   → Option C: Request org policy exception for service account keys")