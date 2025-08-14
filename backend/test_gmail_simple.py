"""
Simple test to check Gmail API access
"""

from google.auth import default
from googleapiclient.discovery import build

print("Testing Gmail API access...\n")

# Get default credentials
print("1. Getting credentials...")
credentials, project = default(
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
print(f"   Project: {project}")
print(f"   Credentials type: {type(credentials).__name__}")

# Try to access Gmail API without delegation
print("\n2. Building Gmail service...")
service = build('gmail', 'v1', credentials=credentials)

print("\n3. Testing API access (getting profile)...")
try:
    # Try to get the profile of the service account itself
    profile = service.users().getProfile(userId='me').execute()
    print(f"   Success! Profile: {profile}")
except Exception as e:
    print(f"   Failed: {e}")
    
print("\n4. Testing with specific email...")
# Try with the monitoring email
monitoring_email = "confirmaciones_dev@palace.cl"
try:
    profile = service.users().getProfile(userId=monitoring_email).execute()
    print(f"   Success! Can access {monitoring_email}")
except Exception as e:
    print(f"   Failed to access {monitoring_email}: {e}")

print("\n5. Testing with your email...")
# Try with your email
your_email = "ben.clark@palace.cl"
try:
    profile = service.users().getProfile(userId=your_email).execute() 
    print(f"   Success! Can access {your_email}")
except Exception as e:
    print(f"   Failed to access {your_email}: {e}")

print("\nNote: If all tests fail, the issue might be:")
print("- Domain-wide delegation not properly configured in Google Workspace Admin")
print("- The email address doesn't exist or isn't a Google Workspace account")
print("- The service account doesn't have the necessary permissions")