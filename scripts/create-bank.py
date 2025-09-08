#!/usr/bin/env python3
"""
Interactive script to create a new bank in the CCM system.
"""

import sys
import os
import re
from datetime import datetime

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from config.firebase_config import get_cmek_firestore_client

# Default system settings for all banks
DEFAULT_BANK_SETTINGS = {
    'defaultCurrency': 'CLP',
    'supportedCurrencies': ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS'],
    'supportedProducts': ['Spot', 'Forward']
}

def validate_rut(rut):
    """Validate Chilean RUT format"""
    rut_pattern = r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'
    return re.match(rut_pattern, rut) is not None

def validate_swift(swift):
    """Validate SWIFT code format"""
    swift_pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'
    return re.match(swift_pattern, swift.upper()) is not None

def validate_bank_id(bank_id):
    """Validate bank ID format"""
    return re.match(r'^[a-z0-9-]+$', bank_id) is not None

def ask_question(question, validator=None, error_msg=None):
    """Ask a question with optional validation"""
    while True:
        answer = input(question).strip()
        if not answer:
            continue
        if validator and not validator(answer):
            print(f"❌ {error_msg or 'Invalid input'}")
            continue
        return answer

def ask_optional(question, default=None):
    """Ask an optional question with default value"""
    answer = input(question).strip()
    return answer if answer else default

def confirm_action(message):
    """Ask for confirmation"""
    answer = input(message).strip().lower()
    return answer in ['y', 'yes']

async def create_bank():
    """Main function to create a new bank"""
    print('🏛️ Bank Creation Script')
    print('========================')
    print('This script will create a new bank in the CCM system.')
    print('')

    try:
        # Initialize Firestore client
        db = get_cmek_firestore_client()
        
        # Collect bank information
        bank_id = ask_question(
            '? Bank ID (e.g., banco-bci): ',
            validate_bank_id,
            'Bank ID must contain only lowercase letters, numbers, and hyphens'
        )

        # Check if bank already exists
        bank_ref = db.collection('banks').document(bank_id)
        if bank_ref.get().exists:
            raise ValueError(f'Bank with ID "{bank_id}" already exists')

        name = ask_question('? Bank Name (e.g., BCI): ')

        tax_id = ask_question(
            '? Tax ID/RUT (format: XX.XXX.XXX-X): ',
            validate_rut,
            'Invalid RUT format. Please use format: XX.XXX.XXX-X'
        )

        swift_code = ask_question(
            '? SWIFT Code (e.g., BCHCCLRM): ',
            validate_swift,
            'Invalid SWIFT code format. Please use 8 or 11 character SWIFT/BIC code'
        )

        country = ask_optional('? Country Code (default: CL): ', 'CL').upper()
        if not re.match(r'^[A-Z]{2}$', country):
            raise ValueError('Country code must be 2 uppercase letters (ISO 3166-1 alpha-2)')

        print('')
        print('📋 Bank Information Summary:')
        print(f'   Bank ID: {bank_id}')
        print(f'   Name: {name}')
        print(f'   Tax ID: {tax_id}')
        print(f'   SWIFT: {swift_code.upper()}')
        print(f'   Country: {country}')
        print('')

        if not confirm_action('✅ Create this bank? (y/N): '):
            print('❌ Bank creation cancelled')
            return

        print('')
        print('🔨 Creating bank...')

        # Create main bank document
        bank_data = {
            'name': name,
            'taxId': tax_id,
            'country': country,
            'swiftCode': swift_code.upper(),
            'status': 'active',
            'createdAt': datetime.now(),
            'lastUpdatedAt': datetime.now(),
            'lastUpdatedBy': None  # Will be set when we have a user context
        }
        
        bank_ref.set(bank_data)
        print('✅ Bank document created')

        # Create bank system settings
        settings_data = {
            **DEFAULT_BANK_SETTINGS,
            'lastUpdatedAt': datetime.now(),
            'lastUpdatedBy': None  # Will be set when we have a user context
        }
        
        bank_ref.collection('systemSettings').document('configuration').set(settings_data)
        print('✅ Bank system settings created')

        print('')
        print('🎉 Bank creation completed successfully!')
        print('')
        print('📝 Next Steps:')
        print('1. Create a bank admin user with: python scripts/create-bank-user.py')
        print('2. The admin user email should match the bank domain (e.g., admin@bci.cl)')
        print('3. Make sure the user exists in Firebase Auth first')
        print('')

    except Exception as error:
        print(f'❌ Error creating bank: {error}')
        print('')
        print('💡 Tips:')
        print('- Make sure you have proper Firebase Admin permissions')
        print('- Check that the bank ID is unique')
        print('- Verify input formats (RUT, SWIFT code)')

if __name__ == '__main__':
    import asyncio
    asyncio.run(create_bank())