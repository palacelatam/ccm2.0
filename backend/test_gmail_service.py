"""
Test script for Gmail service integration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
import sys
sys.path.append('./src')

from services.gmail_service import gmail_service
from config.firebase_config import initialize_firebase

async def test_gmail_service():
    """Test Gmail service functionality"""
    
    print("=" * 60)
    print("Gmail Service Integration Test")
    print("=" * 60)
    
    # Initialize Firebase first
    print("\n1. Initializing Firebase...")
    try:
        initialize_firebase()
        print("   [OK] Firebase initialized")
    except Exception as e:
        print(f"   [ERROR] Firebase initialization failed: {e}")
        return
    
    # Check if service account is configured
    service_account_path = os.getenv('GMAIL_SERVICE_ACCOUNT_PATH', 'gmail-service-account.json')
    if not os.path.exists(service_account_path):
        print(f"\n[INFO] Service account file not found: {service_account_path}")
        print("   Using Application Default Credentials (ADC) instead")
        # ADC is configured, so we can continue
    
    # Initialize Gmail service
    print("\n2. Initializing Gmail service...")
    try:
        await gmail_service.initialize()
        print(f"   [OK] Gmail service initialized")
        print(f"   Monitoring email: {gmail_service.monitoring_email}")
    except Exception as e:
        print(f"   [ERROR] Gmail initialization failed: {e}")
        print("\n   Possible issues:")
        print("   - Service account not properly configured")
        print("   - Access not granted to specific user (see setup-gmail-api.md)")
        print("   - Gmail API not enabled in GCP project")
        return
    
    # Check for new emails
    print("\n3. Checking for new emails...")
    try:
        results = await gmail_service.check_for_new_emails()
        
        if results:
            print(f"   [OK] Found {len(results)} new emails")
            for result in results:
                print(f"\n   Email Details:")
                print(f"   - From: {result.get('sender', 'Unknown')}")
                print(f"   - Subject: {result.get('subject', 'No subject')}")
                print(f"   - Client ID: {result.get('client_id', 'Unknown')}")
                print(f"   - Attachments: {result.get('attachments_processed', 0)}")
                print(f"   - Trades extracted: {result.get('total_trades_extracted', 0)}")
                print(f"   - Matches found: {result.get('total_matches_found', 0)}")
        else:
            print("   [INFO] No new emails found")
    except Exception as e:
        print(f"   [ERROR] Email check failed: {e}")
    
    # Test monitoring (for 30 seconds)
    print("\n4. Testing monitoring (30 seconds)...")
    print("   Starting monitoring with 10-second intervals...")
    
    # Create monitoring task
    monitoring_task = asyncio.create_task(
        gmail_service.start_monitoring(check_interval=10)
    )
    
    # Wait for 30 seconds
    await asyncio.sleep(30)
    
    # Stop monitoring
    print("   Stopping monitoring...")
    await gmail_service.stop_monitoring()
    
    print("\n[OK] Test completed!")
    print("\nNext steps:")
    print("1. Send a test email to confirmaciones_dev@palace.cl")
    print("2. Run this test again to see if it's detected")
    print("3. Use the API endpoints to control monitoring:")
    print("   - POST /api/v1/gmail/check-now - Manual check")
    print("   - POST /api/v1/gmail/start-monitoring - Start monitoring")
    print("   - POST /api/v1/gmail/stop-monitoring - Stop monitoring")
    print("   - GET /api/v1/gmail/status - Get status")

if __name__ == "__main__":
    asyncio.run(test_gmail_service())