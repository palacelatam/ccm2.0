"""
Test script to check ADC credentials type
"""

from google.auth import default
import json

# Get default credentials
credentials, project = default(
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

print(f"Project: {project}")
print(f"Credentials type: {type(credentials)}")
print(f"Credentials class: {credentials.__class__.__name__}")

# Check attributes
attrs = ['service_account_email', 'signer', 'token_uri', 'with_subject', '_service_account_email']
for attr in attrs:
    if hasattr(credentials, attr):
        value = getattr(credentials, attr)
        if callable(value):
            print(f"Has method: {attr}")
        else:
            print(f"Has attribute {attr}: {value}")

# Check if it's impersonated credentials
if hasattr(credentials, '_source_credentials'):
    print("\nThis appears to be impersonated credentials")
    source = credentials._source_credentials
    print(f"Source credentials type: {type(source)}")
    if hasattr(source, 'service_account_email'):
        print(f"Source service account: {source.service_account_email}")

# Try to get service account email
if hasattr(credentials, '_service_account_email'):
    print(f"\nService account email: {credentials._service_account_email}")
elif hasattr(credentials, 'service_account_email'):
    print(f"\nService account email: {credentials.service_account_email}")