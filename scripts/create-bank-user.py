#!/usr/bin/env python3
"""
Interactive script to create a new bank user in the CCM system.
"""

import sys
import os
import re
from datetime import datetime

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from config.firebase_config import get_cmek_firestore_client, initialize_firebase, get_auth_client

# Available roles
AVAILABLE_ROLES = {
    'bank_admin': 'Bank Administrator - Full administrative access for bank operations',
    'client_admin': 'Client Administrator - Administrative access for client organization',
    'client_user': 'Client User - Standard user access for viewing trades and confirmations'
}

# Email domain to bank mapping
EMAIL_TO_BANK_MAPPING = {
    '@bancoabc.cl': 'banco-abc',
    '@bci.cl': 'banco-bci', 
    '@itau.cl': 'banco-itau'
}

def validate_email(email):
    """Validate email format"""
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_pattern, email) is not None

def get_bank_from_email(email):
    """Get bank ID from email domain"""
    for domain, bank_id in EMAIL_TO_BANK_MAPPING.items():
        if domain in email:
            return bank_id
    return None

def get_user_by_email(email):
    """Get user from Firebase Auth by email"""
    try:
        auth_client = get_auth_client()
        user_record = auth_client.get_user_by_email(email)
        return user_record
    except Exception as e:
        if 'auth/user-not-found' in str(e) or 'UserNotFoundError' in str(e):
            return None
        raise e

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

def select_role():
    """Interactive role selection"""
    print('')
    print('📋 Available Roles:')
    role_list = list(AVAILABLE_ROLES.keys())
    for i, (role_id, description) in enumerate(AVAILABLE_ROLES.items(), 1):
        print(f'   {i}. {role_id} - {description}')
    print('')
    
    while True:
        choice = input('? Select role (1-3) or enter role name: ').strip()
        
        if choice in ['1', '2', '3']:
            return role_list[int(choice) - 1]
        elif choice.lower() in AVAILABLE_ROLES:
            return choice.lower()
        else:
            print('❌ Invalid role selection. Please choose 1-3 or enter a valid role name.')

async def create_bank_user():
    """Main function to create a new bank user"""
    print('👤 Bank User Creation Script')
    print('============================')
    print('')
    print('⚠️  IMPORTANT PREREQUISITE:')
    print('   The user MUST already exist in Firebase Auth before running this script.')
    print('   This script only creates the user profile in Firestore, not the Firebase Auth user.')
    print('')
    print('📋 To create a Firebase Auth user:')
    print('   1. Go to Firebase Console > Authentication > Users')
    print('   2. Click "Add user" and enter email/password')
    print('   3. Or use Firebase Admin SDK to create the user programmatically')
    print('')
    print('✅ Once the Firebase Auth user exists, this script will:')
    print('   - Verify the user exists in Firebase Auth')
    print('   - Create their user profile in Firestore')  
    print('   - Link them to a bank organization with proper role')
    print('')
    
    if not confirm_action('🔥 Have you already created the user in Firebase Auth? (y/N): '):
        print('❌ Please create the user in Firebase Auth first, then run this script again.')
        print('')
        print('💡 Firebase Console: https://console.firebase.google.com/')
        return

    try:
        # Initialize Firebase (needed for Auth operations)
        initialize_firebase()
        
        # Initialize Firestore client
        db = get_cmek_firestore_client()
        
        # Collect user information
        email = None
        user_record = None
        
        while True:
            email = ask_question(
                '? User Email (e.g., admin@bci.cl): ',
                validate_email,
                'Invalid email format'
            ).lower()
            
            # Check if user exists in Firebase Auth
            user_record = get_user_by_email(email)
            if not user_record:
                print('❌ User not found in Firebase Auth. Please create the user in Firebase Auth first.')
                print('   You can do this through the Firebase Console or using Firebase Admin SDK.')
                continue
            
            print('✅ User found in Firebase Auth')
            break

        first_name = ask_question('? First Name: ')
        last_name = ask_question('? Last Name: ')

        # Auto-detect bank from email or ask user
        bank_id = get_bank_from_email(email)
        if bank_id:
            print(f'🏛️ Auto-detected bank: {bank_id} (from email domain)')
            if not confirm_action(f'✅ Use bank "{bank_id}"? (Y/n): '):
                bank_id = None

        if not bank_id:
            bank_id = ask_question('? Bank ID (e.g., banco-bci): ')

        # Check if bank exists
        bank_ref = db.collection('banks').document(bank_id)
        if not bank_ref.get().exists:
            raise ValueError(f'Bank "{bank_id}" does not exist. Please create the bank first using: python scripts/create-bank.py')

        # Select role
        role = select_role()

        # Check if user profile already exists
        user_ref = db.collection('users').document(user_record.uid)
        if user_ref.get().exists:
            raise ValueError(f'User profile already exists for {email} (UID: {user_record.uid})')

        print('')
        print('📋 User Information Summary:')
        print(f'   Email: {email}')
        print(f'   Name: {first_name} {last_name}')
        print(f'   Bank: {bank_id}')
        print(f'   Role: {role}')
        print(f'   Firebase UID: {user_record.uid}')
        print('')

        if not confirm_action('✅ Create this user profile? (y/N): '):
            print('❌ User creation cancelled')
            return

        print('')
        print('🔨 Creating user profile...')

        # Create user profile
        user_data = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'roles': [db.collection('roles').document(role)],
            'primaryRole': db.collection('roles').document(role),
            'organizationId': db.collection('banks').document(bank_id),
            'organizationType': 'bank',
            'language': 'es',
            'timezone': 'America/Santiago',
            'loginMetadata': {
                'lastLoginAt': None,
                'lastLoginIP': None,
                'loginCount': 0
            },
            'status': 'active',
            'emailVerified': user_record.email_verified,
            'twoFactorEnabled': False,
            'createdAt': datetime.now(),
            'lastUpdatedAt': datetime.now(),
            'lastUpdatedBy': db.collection('users').document(user_record.uid)
        }

        user_ref.set(user_data)
        print('✅ User profile created')

        print('')
        print('🎉 Bank user creation completed successfully!')
        print('')
        print('📝 User Details:')
        print(f'   Firebase UID: {user_record.uid}')
        print(f'   Email: {email}')
        print(f'   Organization: {bank_id} (bank)')
        print(f'   Role: {role}')
        print('')
        print('💡 Next Steps:')
        print('1. The user can now log in to the CCM system')
        print('2. They will have access based on their assigned role')
        print('3. To create clients for this bank, use: python scripts/create-client.py')
        print('')

    except Exception as error:
        print(f'❌ Error creating bank user: {error}')
        print('')
        print('💡 Tips:')
        print('- Make sure the user exists in Firebase Auth first')
        print('- Verify the bank exists (create with create-bank.py if needed)')
        print('- Check that you have proper Firebase Admin permissions')

if __name__ == '__main__':
    import asyncio
    asyncio.run(create_bank_user())