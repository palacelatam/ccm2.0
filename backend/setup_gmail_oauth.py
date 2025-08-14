#!/usr/bin/env python3
"""
Setup script for Gmail OAuth2 authentication
This script helps authenticate the Gmail account and save the refresh token
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the token file
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def setup_gmail_oauth():
    """Run OAuth2 flow to authenticate Gmail account"""
    
    print("=" * 60)
    print("Gmail OAuth2 Setup")
    print("=" * 60)
    
    creds = None
    token_path = 'gmail-token.json'
    credentials_path = 'gmail-credentials.json'
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"\n❌ OAuth2 credentials file not found: {credentials_path}")
        print("\nPlease follow these steps:")
        print("1. Go to Google Cloud Console")
        print("2. Create OAuth2 credentials (Desktop app type)")
        print("3. Download and save as 'gmail-credentials.json'")
        return
    
    # Check if token already exists
    if os.path.exists(token_path):
        print(f"\n⚠️  Token file already exists: {token_path}")
        response = input("Do you want to re-authenticate? (y/n): ")
        if response.lower() != 'y':
            print("Using existing token.")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\nRefreshing expired token...")
            creds.refresh(Request())
        else:
            print("\nStarting OAuth2 authentication flow...")
            print("A browser window will open for authentication.")
            print("\n⚠️  IMPORTANT: Log in as confirmaciones_dev@palace.cl")
            input("\nPress Enter to continue...")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        print("\nSaving authentication token...")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Token saved to {token_path}")
    
    # Test the connection
    print("\nTesting Gmail API connection...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile to confirm connection
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        
        print(f"✅ Successfully connected to Gmail account: {email}")
        
        # Get message count
        messages = service.users().messages().list(userId='me', maxResults=1).execute()
        total = messages.get('resultSizeEstimate', 0)
        print(f"📧 Total messages in inbox: ~{total}")
        
        print("\n✅ Setup completed successfully!")
        print("\nYou can now:")
        print("1. Run the backend server: python src/main.py")
        print("2. Test Gmail integration: python test_gmail_service.py")
        print("3. Use the API endpoints to control monitoring")
        
    except Exception as e:
        print(f"\n❌ Failed to connect to Gmail: {e}")
        print("\nPossible issues:")
        print("- Gmail API not enabled in GCP project")
        print("- Invalid credentials")
        print("- Network connectivity issues")

if __name__ == '__main__':
    setup_gmail_oauth()