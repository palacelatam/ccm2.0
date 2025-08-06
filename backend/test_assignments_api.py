#!/usr/bin/env python3
"""Test script for bank assignments API"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.bank_service import BankService

async def test_assignments():
    """Test the bank assignments API"""
    print("Testing Bank Assignments API...")
    
    bank_service = BankService()
    bank_id = 'banco-abc'
    
    try:
        # Test 1: Get client segment assignments
        print(f"\nGetting client segment assignments for bank {bank_id}...")
        assignments = await bank_service.get_client_segment_assignments(bank_id)
        print(f"Assignments: {assignments}")
        
        # Test 2: Get client segments
        print(f"\nGetting client segments for bank {bank_id}...")
        segments = await bank_service.get_client_segments(bank_id)
        print(f"Found {len(segments)} segments:")
        for segment in segments:
            print(f"  - {segment.id}: {segment.name}")
        
        # Test 3: Test assign client to segment
        print(f"\nTesting client assignment...")
        test_client_id = 'test-client-123'
        test_segment_id = 'premium'
        
        success = await bank_service.assign_client_to_segment(
            bank_id, test_client_id, test_segment_id, 'test-user'
        )
        print(f"Assignment successful: {success}")
        
        # Test 4: Verify the assignment
        if success:
            print(f"\nVerifying assignment...")
            updated_assignments = await bank_service.get_client_segment_assignments(bank_id)
            print(f"Updated assignments: {updated_assignments}")
            
            if test_client_id in updated_assignments.get(test_segment_id, []):
                print(f"SUCCESS: Client {test_client_id} successfully assigned to {test_segment_id}")
            else:
                print(f"ERROR: Client {test_client_id} NOT found in {test_segment_id}")
        
    except Exception as e:
        print(f"ERROR testing assignments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_assignments())