"""
Test script for Settlement Instruction Service
Run this to test basic document generation functionality
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')

from services.settlement_instruction_service import settlement_instruction_service


async def test_basic_generation():
    """Test basic settlement instruction generation"""
    print("=" * 60)
    print("Settlement Instructions Service Test")
    print("=" * 60)
    
    # Sample trade data (based on your existing trade structure)
    sample_trade_data = {
        'client_name': 'XYZ Corporation',
        'TradeNumber': 'FX-2024-001234',
        'TradeDate': '15-08-2024',
        'MaturityDate': '17-08-2024',
        'CounterpartyName': 'Banco Santander Chile',
        'Product': 'FX_SPOT',
        'Currency1': 'USD',
        'Currency2': 'CLP',
        'QuantityCurrency1': 1000000,
        'QuantityCurrency2': 950000000,
        'Price': '950.00',
        'Direction': 'BUY'
    }
    
    # Sample settlement data
    sample_settlement_data = {
        'account_name': 'XYZ Corp USD Account',
        'account_number': '12345678901',
        'bank_name': 'Banco de Chile',
        'swift_code': 'BCHICLRM',
        'cutoff_time': '15:00',
        'special_instructions': 'Please confirm receipt of funds via email to treasury@xyzcorp.cl'
    }
    
    print("Sample Trade Data:")
    for key, value in sample_trade_data.items():
        print(f"  {key}: {value}")
    
    print("\nSample Settlement Data:")
    for key, value in sample_settlement_data.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Generating Settlement Instruction Document...")
    print("=" * 60)
    
    # Test 1: Generate with settlement data
    result1 = await settlement_instruction_service.generate_settlement_instruction(
        trade_data=sample_trade_data,
        settlement_data=sample_settlement_data
    )
    
    if result1['success']:
        print("✅ Test 1: Generation with settlement data - SUCCESS")
        print(f"   Document: {result1['document_path']}")
        print(f"   Variables: {result1['variables_populated']}")
        print(f"   Template: {result1['template_used']}")
    else:
        print("❌ Test 1: Generation with settlement data - FAILED")
        print(f"   Error: {result1['error']}")
    
    print()
    
    # Test 2: Generate without settlement data (should use defaults)
    result2 = await settlement_instruction_service.generate_settlement_instruction(
        trade_data=sample_trade_data
    )
    
    if result2['success']:
        print("✅ Test 2: Generation without settlement data - SUCCESS")
        print(f"   Document: {result2['document_path']}")
        print(f"   Variables: {result2['variables_populated']}")
        print(f"   Template: {result2['template_used']}")
    else:
        print("❌ Test 2: Generation without settlement data - FAILED")
        print(f"   Error: {result2['error']}")
    
    print()
    
    # Test 3: Different trade type (Forward)
    forward_trade_data = {
        'client_name': 'ABC Industries',
        'TradeNumber': 'FX-2024-005678',
        'TradeDate': '20-08-2024',
        'MaturityDate': '20-11-2024',  # 3 months forward
        'CounterpartyName': 'Banco BCI',
        'Product': 'FX_FORWARD',
        'Currency1': 'EUR',
        'Currency2': 'CLP',
        'QuantityCurrency1': 500000,
        'QuantityCurrency2': 550000000,
        'Price': '1100.00',
        'Direction': 'SELL'
    }
    
    forward_settlement_data = {
        'account_name': 'ABC Industries EUR Account',
        'account_number': '98765432101',
        'bank_name': 'Banco Estado',
        'swift_code': 'BESCCLRR',
        'cutoff_time': '14:30',
        'special_instructions': 'Forward settlement - please coordinate with treasury department.'
    }
    
    result3 = await settlement_instruction_service.generate_settlement_instruction(
        trade_data=forward_trade_data,
        settlement_data=forward_settlement_data
    )
    
    if result3['success']:
        print("✅ Test 3: Forward trade generation - SUCCESS")
        print(f"   Document: {result3['document_path']}")
        print(f"   Variables: {result3['variables_populated']}")
        print(f"   Template: {result3['template_used']}")
    else:
        print("❌ Test 3: Forward trade generation - FAILED")
        print(f"   Error: {result3['error']}")
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    success_count = sum([result1['success'], result2['success'], result3['success']])
    print(f"Tests passed: {success_count}/3")
    
    if success_count == 3:
        print("🎉 All tests passed! Settlement instruction generation is working correctly.")
        print("\nGenerated documents are available in:")
        print("   backend/templates/generated/")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")


async def test_with_minimal_data():
    """Test with minimal trade data to verify error handling"""
    print("\n" + "=" * 60)
    print("Testing with Minimal Data")
    print("=" * 60)
    
    minimal_trade_data = {
        'TradeNumber': 'TEST-MIN-001',
        'CounterpartyName': 'Test Bank'
    }
    
    result = await settlement_instruction_service.generate_settlement_instruction(
        trade_data=minimal_trade_data
    )
    
    if result['success']:
        print("✅ Minimal data test - SUCCESS")
        print(f"   Document: {result['document_path']}")
        print("   Service handled missing data gracefully")
    else:
        print("❌ Minimal data test - FAILED")
        print(f"   Error: {result['error']}")


async def main():
    """Main test function"""
    await test_basic_generation()
    await test_with_minimal_data()
    
    print("\n" + "=" * 60)
    print("Settlement Instructions Service Testing Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())