#!/usr/bin/env python3
"""
Test script for Gmail sending functionality
Tests the extended Gmail service with email sending capability
"""

import asyncio
import logging
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.gmail_service import gmail_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_gmail_sending():
    """Test Gmail sending functionality"""
    
    print("🧪 Testing Gmail Sending Functionality")
    print("=" * 50)
    
    try:
        # Initialize Gmail service
        print("1️⃣ Initializing Gmail service...")
        await gmail_service.initialize()
        print("✅ Gmail service initialized successfully")
        
        # Test email parameters
        test_email = input("Enter test recipient email address: ").strip()
        if not test_email or '@' not in test_email:
            print("❌ Invalid email address")
            return
        
        # Confirm sending test
        confirm = input(f"Send test email to {test_email}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Test cancelled")
            return
        
        print(f"2️⃣ Sending test email to {test_email}...")
        
        # Send test email
        success = await gmail_service.send_email(
            to_email=test_email,
            subject="CCM 2.0 - Gmail Service Test",
            body="""Hello!

This is a test email from the Client Confirmation Manager 2.0 automated email system.

If you received this email, the Gmail API sending functionality is working correctly.

Test Details:
- Sent from: confirmaciones_dev@servicios.palace.cl
- System: CCM 2.0 Auto-Email Service
- Test timestamp: {timestamp}

Best regards,
CCM 2.0 System""".format(timestamp=asyncio.get_event_loop().time()),
            cc_email=None,
            reply_to="noreply@servicios.palace.cl"
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📧 Check {test_email} for the test message")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error("Gmail sending test failed", exc_info=True)

async def test_email_formatting():
    """Test email message formatting without sending"""
    
    print("\n🧪 Testing Email Message Formatting")
    print("=" * 50)
    
    try:
        # Test message creation
        message = gmail_service._create_email_message(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body content",
            cc_email="cc@example.com",
            reply_to="reply@example.com"
        )
        
        print("✅ Email message formatting test passed")
        print(f"📝 Message structure: {list(message.keys())}")
        
        # Decode and show partial content (first 200 chars)
        import base64
        decoded = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
        print(f"📄 Message preview (first 200 chars):")
        print(decoded[:200] + "..." if len(decoded) > 200 else decoded)
        
    except Exception as e:
        print(f"❌ Email formatting test failed: {e}")
        logger.error("Email formatting test failed", exc_info=True)

async def test_service_initialization():
    """Test just the service initialization"""
    
    print("\n🧪 Testing Service Initialization")
    print("=" * 50)
    
    try:
        # Test initialization
        await gmail_service.initialize()
        
        # Check service properties
        print(f"✅ Service initialized")
        print(f"📧 Monitoring email: {gmail_service.monitoring_email}")
        print(f"🔑 Has credentials: {gmail_service.credentials is not None}")
        print(f"🌐 Has service: {gmail_service.service is not None}")
        print(f"👤 Use user ID: {gmail_service.use_user_id}")
        
        # Test API connection with a simple call
        profile = await gmail_service._execute_gmail_api(
            gmail_service.service.users().getProfile(
                userId=gmail_service.monitoring_email if gmail_service.use_user_id else 'me'
            )
        )
        
        print(f"📊 Gmail profile accessible: {profile.get('emailAddress')}")
        print("✅ All initialization tests passed!")
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        logger.error("Service initialization test failed", exc_info=True)

async def main():
    """Main test runner"""
    
    print("🚀 Gmail Service Sending Tests")
    print("=" * 50)
    print("Choose test to run:")
    print("1. Full sending test (sends actual email)")
    print("2. Email formatting test (no sending)")
    print("3. Service initialization test only")
    print("4. All tests")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        await test_gmail_sending()
    elif choice == '2':
        await test_email_formatting()
    elif choice == '3':
        await test_service_initialization()
    elif choice == '4':
        await test_service_initialization()
        await test_email_formatting()
        await test_gmail_sending()
    else:
        print("Invalid choice")
        return
    
    print("\n🏁 Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())