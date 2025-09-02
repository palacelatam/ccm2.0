"""
Test script for SMS service functionality
Run this after setting up Twilio credentials
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')

# Set test environment variables (replace with your actual values)
# os.environ['TWILIO_ACCOUNT_SID'] = 'your_account_sid_here'
# os.environ['TWILIO_AUTH_TOKEN'] = 'your_auth_token_here'  
# os.environ['TWILIO_PHONE_NUMBER'] = '+1234567890'  # Your Twilio phone number

from services.sms_service import sms_service
from services.auto_sms_service import auto_sms_service
from config.firebase_config import get_cmek_firestore_client


async def test_sms_configuration():
    """Test SMS service configuration"""
    print("\n=== Testing SMS Configuration ===")
    
    validation = await sms_service.validate_configuration()
    
    print(f"Configuration valid: {validation.get('configured', False)}")
    print(f"Credentials present: {validation.get('credentials_present', False)}")
    
    if validation.get('errors'):
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    return validation.get('configured', False)


async def test_single_sms(phone_number: str):
    """Test sending a single SMS"""
    print(f"\n=== Testing Single SMS to {phone_number} ===")
    
    result = await sms_service.send_sms(
        to_phone=phone_number,
        message="Test SMS from CCM2.0 - Single message test",
        client_id="test-client",
        trade_number="TEST-001"
    )
    
    if result.get('success'):
        print(f"✅ SMS sent successfully!")
        print(f"   Message SID: {result.get('message_sid')}")
        print(f"   Status: {result.get('status')}")
    else:
        print(f"❌ Failed to send SMS: {result.get('error')}")
    
    return result


async def test_bulk_sms(phone_numbers: list):
    """Test sending bulk SMS"""
    print(f"\n=== Testing Bulk SMS to {len(phone_numbers)} numbers ===")
    
    results = await sms_service.send_bulk_sms(
        phone_list=phone_numbers,
        message="Test SMS from CCM2.0 - Bulk message test",
        client_id="test-client",
        trade_number="TEST-002"
    )
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"Results: {successful}/{len(results)} successful")
    
    for i, result in enumerate(results):
        if result.get('success'):
            print(f"  ✅ {phone_numbers[i]}: Success (SID: {result.get('message_sid')})")
        else:
            print(f"  ❌ {phone_numbers[i]}: Failed - {result.get('error')}")
    
    return results


async def test_trade_notifications(client_id: str = "xyz-corp"):
    """Test trade notification SMS using real client configuration"""
    print(f"\n=== Testing Trade Notification SMS for {client_id} ===")
    
    # Test confirmed trade
    print("\n--- Confirmed Trade SMS ---")
    confirmed_trade_data = {
        "TradeNumber": "TEST-CONFIRM-001",
        "CounterpartyName": "Banco Santander",
        "QuantityCurrency1": 150000,
        "Currency1": "USD",
        "Currency2": "CLP",
        "TradeDate": datetime.now().strftime("%d-%m-%Y")
    }
    
    result = await auto_sms_service.process_trade_sms_notifications(
        client_id=client_id,
        trade_status="Confirmation OK",
        trade_data=confirmed_trade_data,
        discrepancies=None
    )
    
    if result.get('sms_sent'):
        print(f"✅ Confirmed trade SMS sent")
        if result.get('confirmed_sms'):
            for sms in result['confirmed_sms']:
                if sms.get('success'):
                    print(f"   ✅ {sms.get('to_phone')}: Success")
                else:
                    print(f"   ❌ {sms.get('to_phone')}: {sms.get('error')}")
    else:
        print(f"❌ No SMS sent - may be disabled or no phones configured")
        if result.get('errors'):
            for error in result['errors']:
                print(f"   Error: {error}")
    
    # Test disputed trade
    print("\n--- Disputed Trade SMS ---")
    disputed_trade_data = {
        "TradeNumber": "TEST-DISPUTE-001",
        "CounterpartyName": "Banco BCI",
        "QuantityCurrency1": 250000,
        "Currency1": "EUR",
        "Currency2": "CLP",
        "TradeDate": datetime.now().strftime("%d-%m-%Y")
    }
    
    discrepancies = [
        {"field": "Price", "email_value": "932.50", "client_value": "931.75"},
        {"field": "MaturityDate", "email_value": "01-10-2026", "client_value": "30-09-2026"}
    ]
    
    result = await auto_sms_service.process_trade_sms_notifications(
        client_id=client_id,
        trade_status="Difference",
        trade_data=disputed_trade_data,
        discrepancies=discrepancies
    )
    
    if result.get('sms_sent'):
        print(f"✅ Disputed trade SMS sent")
        if result.get('disputed_sms'):
            for sms in result['disputed_sms']:
                if sms.get('success'):
                    print(f"   ✅ {sms.get('to_phone')}: Success")
                else:
                    print(f"   ❌ {sms.get('to_phone')}: {sms.get('error')}")
    else:
        print(f"❌ No SMS sent - may be disabled or no phones configured")
        if result.get('errors'):
            for error in result['errors']:
                print(f"   Error: {error}")
    
    return result


async def test_message_status(message_sid: str):
    """Test getting SMS delivery status"""
    print(f"\n=== Testing Message Status for {message_sid} ===")
    
    status = await sms_service.get_message_status(message_sid)
    
    if status:
        print(f"Message Status: {status.get('status')}")
        print(f"To: {status.get('to')}")
        print(f"From: {status.get('from')}")
        if status.get('error_code'):
            print(f"Error: {status.get('error_code')} - {status.get('error_message')}")
    else:
        print("Could not retrieve message status")
    
    return status


async def main():
    """Main test function"""
    print("=" * 50)
    print("SMS Service Test Suite")
    print("=" * 50)
    
    # Test configuration
    configured = await test_sms_configuration()
    
    if not configured:
        print("\n⚠️  SMS service not configured. Please set up Twilio credentials:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_PHONE_NUMBER")
        return
    
    # Get test phone number from user
    print("\n" + "=" * 50)
    test_phone = input("Enter test phone number (e.g., +56912345678): ").strip()
    
    if not test_phone:
        print("No phone number provided, using default test number")
        test_phone = "+56912345678"  # Default test number
    
    # Run tests
    print("\n" + "=" * 50)
    print("Running SMS Tests")
    print("=" * 50)
    
    # Test 1: Single SMS
    single_result = await test_single_sms(test_phone)
    
    # Test 2: Bulk SMS (if you want to test with multiple numbers)
    # bulk_phones = [test_phone, "+56987654321"]  # Add more test numbers
    # await test_bulk_sms(bulk_phones)
    
    # Test 3: Trade notifications using real client config
    await test_trade_notifications("xyz-corp")
    
    # Test 4: Check message status (if we have a message SID)
    if single_result.get('success') and single_result.get('message_sid'):
        await asyncio.sleep(2)  # Wait a bit for status to update
        await test_message_status(single_result['message_sid'])
    
    print("\n" + "=" * 50)
    print("SMS Tests Complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())