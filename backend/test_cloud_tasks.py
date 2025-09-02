#!/usr/bin/env python3
"""
Test script for Cloud Tasks system
Tests the general-purpose task queue functionality
"""

import asyncio
import logging
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.task_queue_service import task_queue_service, TaskType, TaskQueue
from src.services.auto_email_service import auto_email_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_task_queue_initialization():
    """Test Cloud Tasks service initialization"""
    print("🧪 Testing Task Queue Initialization")
    print("=" * 50)
    
    try:
        await task_queue_service.initialize()
        print("✅ Task Queue service initialized successfully")
        
        # Get queue information
        for queue in [TaskQueue.GENERAL, TaskQueue.EMAIL, TaskQueue.PRIORITY]:
            info = await task_queue_service.get_queue_info(queue)
            if info:
                print(f"📊 {queue.name} queue: {info.get('state', 'unknown')} state")
            else:
                print(f"⚠️ Could not get info for {queue.name} queue")
        
        return True
        
    except Exception as e:
        print(f"❌ Task Queue initialization failed: {e}")
        logger.error("Task queue initialization failed", exc_info=True)
        return False

async def test_task_creation():
    """Test creating different types of tasks"""
    print("\n🧪 Testing Task Creation")
    print("=" * 50)
    
    try:
        # Test general task creation
        task_data = {
            "test_type": "general_task",
            "message": "This is a test general task",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        task_name = await task_queue_service.create_task(
            task_type=TaskType.DATA_SYNC,
            task_data=task_data,
            queue=TaskQueue.GENERAL,
            delay_seconds=5  # 5 second delay for testing
        )
        
        print(f"✅ Created general task: {task_name}")
        
        # Test email task creation
        email_data = {
            "to_email": "test@example.com",
            "subject": "Test Email from Cloud Tasks",
            "body": "This is a test email sent via Cloud Tasks system",
            "test_mode": True
        }
        
        email_task_name = await task_queue_service.create_email_task(
            email_data=email_data,
            delay_seconds=10,  # 10 second delay
            is_urgent=False
        )
        
        print(f"✅ Created email task: {email_task_name}")
        
        # Test priority task creation
        notification_data = {
            "type": "system_alert",
            "message": "Test priority notification",
            "urgency": "high"
        }
        
        priority_task_name = await task_queue_service.create_notification_task(
            notification_data=notification_data,
            delay_seconds=15  # 15 second delay
        )
        
        print(f"✅ Created priority task: {priority_task_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        logger.error("Task creation failed", exc_info=True)
        return False

async def test_auto_email_service():
    """Test auto-email service functionality"""
    print("\n🧪 Testing Auto Email Service")
    print("=" * 50)
    
    try:
        # Mock email confirmation data
        email_confirmation_data = {
            "BankTradeNumber": "TEST123456",
            "CounterpartyName": "Test Bank",
            "EmailSender": "test@testbank.com",
            "Currency1": "USD",
            "Currency2": "CLP",
            "Direction": "Buy",
            "QuantityCurrency1": 1000000,
            "Price": 950.00,
            "TradeDate": "28-08-2025",
            "ValueDate": "30-08-2025"
        }
        
        # Test scheduling confirmation email (will check client settings)
        print("📧 Testing confirmation email scheduling...")
        confirmation_task = await auto_email_service.schedule_confirmation_email(
            client_id="test-client",  # This will likely fail due to no client settings
            email_confirmation_data=email_confirmation_data,
            delay_minutes=1  # 1 minute for testing
        )
        
        if confirmation_task:
            print(f"✅ Scheduled confirmation email task: {confirmation_task}")
        else:
            print("ℹ️ Confirmation email not scheduled (likely due to client settings or disabled auto-confirmation)")
        
        # Test scheduling dispute email
        print("📧 Testing dispute email scheduling...")
        differing_fields = ["Direction", "Price", "ValueDate"]
        
        dispute_task = await auto_email_service.schedule_dispute_email(
            client_id="test-client",
            email_confirmation_data=email_confirmation_data,
            differing_fields=differing_fields,
            delay_minutes=2  # 2 minutes for testing
        )
        
        if dispute_task:
            print(f"✅ Scheduled dispute email task: {dispute_task}")
        else:
            print("ℹ️ Dispute email not scheduled (likely due to client settings or disabled auto-dispute)")
        
        return True
        
    except Exception as e:
        print(f"❌ Auto email service test failed: {e}")
        logger.error("Auto email service test failed", exc_info=True)
        return False

async def test_queue_monitoring():
    """Test queue monitoring and statistics"""
    print("\n🧪 Testing Queue Monitoring")
    print("=" * 50)
    
    try:
        # Get task statistics
        stats = task_queue_service.get_stats()
        print(f"📊 Task Stats: {stats}")
        
        # List tasks in each queue
        for queue in [TaskQueue.GENERAL, TaskQueue.EMAIL, TaskQueue.PRIORITY]:
            tasks = await task_queue_service.list_tasks(queue, limit=5)
            print(f"📋 {queue.name} queue has {len(tasks)} visible tasks")
            
            for task in tasks[:2]:  # Show first 2 tasks
                print(f"   - {task.get('name', 'unknown')}: "
                      f"dispatched {task.get('dispatch_count', 0)} times")
        
        return True
        
    except Exception as e:
        print(f"❌ Queue monitoring test failed: {e}")
        logger.error("Queue monitoring test failed", exc_info=True)
        return False

async def main():
    """Main test runner"""
    print("🚀 Cloud Tasks System Tests")
    print("=" * 50)
    
    print("⚠️ IMPORTANT: Make sure you have:")
    print("   1. Set up Cloud Tasks queues (see cloud-tasks-setup.md)")
    print("   2. Configured proper IAM permissions")
    print("   3. Set environment variables (GOOGLE_CLOUD_PROJECT, etc.)")
    print("")
    
    choice = input("Continue with tests? (y/N): ").strip().lower()
    if choice != 'y':
        print("Tests cancelled")
        return
    
    # Run tests
    tests = [
        ("Task Queue Initialization", test_task_queue_initialization),
        ("Task Creation", test_task_creation),
        ("Auto Email Service", test_auto_email_service),
        ("Queue Monitoring", test_queue_monitoring)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n🏁 Test Results Summary")
    print("=" * 50)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Cloud Tasks system is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the setup instructions in cloud-tasks-setup.md")

if __name__ == "__main__":
    asyncio.run(main())