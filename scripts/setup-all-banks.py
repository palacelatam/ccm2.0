#!/usr/bin/env python3
"""
Batch script to create all Chilean banks and their admin users.
This script reads the bank list and creates each bank with an admin user.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.config.firebase_config import initialize_firebase, get_cmek_firestore_client, get_auth_client

# Bank list with all Chilean banks (matching bankUtils.ts) with real RUT and SWIFT codes
CHILEAN_BANKS = [
    {'id': 'banco-abc', 'name': 'Banco ABC', 'domain': 'bancoabc.cl', 'rut': '99.999.999-9', 'swift': 'TESTCLRM'},  # Test bank - placeholder values
    {'id': 'banco-bice', 'name': 'Banco BICE', 'domain': 'bice.cl', 'rut': '97.080.000-K', 'swift': 'BICECLRM'},
    {'id': 'banco-btg-pactual', 'name': 'Banco BTG Pactual Chile', 'domain': 'btgpactual.cl', 'rut': '76.362.099-9', 'swift': 'BPABCLRM'},
    {'id': 'banco-consorcio', 'name': 'Banco Consorcio', 'domain': 'bancoconsorcio.cl', 'rut': '99.500.410-0', 'swift': 'MNEXCLRM'},
    {'id': 'banco-de-chile', 'name': 'Banco de Chile', 'domain': 'bancochile.cl', 'rut': '97.004.000-5', 'swift': 'BCHICLRM'},
    {'id': 'banco-bci', 'name': 'Banco de Crédito e Inversiones', 'domain': 'bci.cl', 'rut': '97.006.000-6', 'swift': 'CREDCLRM'},
    {'id': 'banco-estado', 'name': 'Banco del Estado de Chile', 'domain': 'bancoestado.cl', 'rut': '97.030.000-7', 'swift': 'BECHCLRM'},
    {'id': 'banco-falabella', 'name': 'Banco Falabella', 'domain': 'bancofalabella.cl', 'rut': '96.509.660-4', 'swift': 'FALACLRM'},
    {'id': 'banco-internacional', 'name': 'Banco Internacional', 'domain': 'internacional.cl', 'rut': '97.011.000-3', 'swift': 'BICHCLRM'},
    {'id': 'banco-itau', 'name': 'Banco Itaú Chile', 'domain': 'itau.cl', 'rut': '97.023.000-9', 'swift': 'ITAUCLRM'},
    {'id': 'banco-ripley', 'name': 'Banco Ripley', 'domain': 'bancoripley.cl', 'rut': '97.947.000-2', 'swift': 'RPLYCLRM'},
    {'id': 'banco-santander', 'name': 'Banco Santander Chile', 'domain': 'santander.cl', 'rut': '97.036.000-K', 'swift': 'BSCHCLRM'},
    {'id': 'banco-security', 'name': 'Banco Security', 'domain': 'security.cl', 'rut': '97.053.000-2', 'swift': 'BSCLCLRM'},
    {'id': 'banco-hsbc', 'name': 'HSBC Bank Chile', 'domain': 'hsbc.cl', 'rut': '97.951.000-4', 'swift': 'BLICCLRM'},
    {'id': 'banco-scotiabank', 'name': 'Scotiabank Chile', 'domain': 'scotiabank.cl', 'rut': '97.018.000-1', 'swift': 'BKSACLRM'},
    {'id': 'banco-tanner', 'name': 'Tanner Banco Digital', 'domain': 'tanner.cl', 'rut': '99.999.999-9', 'swift': 'TANNCLRM'}  # Tanner - placeholder values (not in provided list)
]

def create_bank(db, bank: Dict) -> bool:
    """Create a bank in Firestore"""
    try:
        bank_id = bank['id']
        bank_name = bank['name']
        
        # Check if bank already exists
        bank_ref = db.collection('banks').document(bank_id)
        if bank_ref.get().exists:
            print(f"⚠️  Bank {bank_id} already exists, skipping...")
            return True
        
        # Create bank document with only root fields
        bank_data = {
            'name': bank_name,
            'status': 'active',
            'swiftCode': bank.get('swift', 'XXXXCLRM'),  # Use real SWIFT from bank data
            'taxId': bank.get('rut', '99.999.999-9'),  # Use real RUT from bank data
            'createdAt': datetime.utcnow(),
            'lastUpdatedAt': datetime.utcnow(),
            'lastUpdatedBy': 'setup-script'
        }
        
        bank_ref.set(bank_data)
        
        # Don't create any subcollections - keep it minimal
        
        print(f"✅ Created bank: {bank_name} ({bank_id})")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bank {bank['name']}: {str(e)}")
        return False

def create_bank_user(db, auth, bank: Dict) -> bool:
    """Create admin user for a bank"""
    try:
        bank_id = bank['id']
        bank_name = bank['name']
        email = f"admin@{bank['domain']}"
        
        # Check if user already exists in Firestore
        users_ref = db.collection('users')
        existing_user = users_ref.where('email', '==', email).limit(1).get()
        if list(existing_user):
            print(f"⚠️  User {email} already exists, skipping...")
            return True
        
        # Note: We cannot create Firebase Auth users programmatically without their password
        # The user must be created manually in Firebase Auth first
        print(f"ℹ️  Please ensure Firebase Auth user exists for: {email}")
        
        # Try to get the user from Firebase Auth to get their UID
        try:
            user = auth.get_user_by_email(email)
            uid = user.uid
            
            # Create user document in Firestore
            user_ref = db.collection('users').document(uid)
            user_data = {
                'email': email,
                'name': f"{bank_name} Admin",
                'role': 'bank_admin',
                'organization': {
                    'id': bank_id,
                    'name': bank_name,
                    'type': 'bank'
                },
                'is_active': True,
                'created_at': datetime.utcnow(),
                'created_by': 'setup-script',
                'last_login': None,
                'preferences': {
                    'language': 'es',
                    'notifications': True,
                    'theme': 'light'
                }
            }
            
            user_ref.set(user_data)
            print(f"✅ Created user document for: {email} (Bank: {bank_name})")
            return True
            
        except Exception as auth_error:
            print(f"⚠️  Firebase Auth user not found for {email}. Please create it manually first.")
            print(f"    Instructions: Go to Firebase Console > Authentication > Add User")
            print(f"    Email: {email}")
            print(f"    Password: Set a secure password and share with the bank")
            return False
        
    except Exception as e:
        print(f"❌ Error creating user for {bank['name']}: {str(e)}")
        return False

def main():
    """Main function to set up all banks and users"""
    print("=" * 60)
    print("CHILEAN BANKS SETUP SCRIPT")
    print("=" * 60)
    print()
    
    # Initialize Firebase
    print("🔧 Initializing Firebase...")
    initialize_firebase()
    db = get_cmek_firestore_client()
    auth = get_auth_client()
    print("✅ Firebase initialized")
    print()
    
    # Show what will be created
    print(f"This script will create {len(CHILEAN_BANKS)} banks and their admin users:")
    print()
    for bank in CHILEAN_BANKS:
        print(f"  • {bank['name']} ({bank['id']})")
        print(f"    Admin email: admin@{bank['domain']}")
    print()
    
    # Confirm with user
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Setup cancelled")
        return
    
    print()
    print("=" * 60)
    print("CREATING BANKS")
    print("=" * 60)
    print()
    
    # Create banks
    banks_created = 0
    for bank in CHILEAN_BANKS:
        if create_bank(db, bank):
            banks_created += 1
    
    print()
    print(f"📊 Banks created: {banks_created}/{len(CHILEAN_BANKS)}")
    print()
    
    print("=" * 60)
    print("CREATING BANK ADMIN USERS")
    print("=" * 60)
    print()
    
    # Important notice about Firebase Auth
    print("⚠️  IMPORTANT: Bank admin users must be created in Firebase Auth FIRST!")
    print("   The script will only create Firestore user documents for existing Auth users.")
    print()
    
    response = input("Have you created the Firebase Auth users? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Please create Firebase Auth users first, then run this script again.")
        print()
        print("To create users in Firebase Auth:")
        print("1. Go to Firebase Console")
        print("2. Select your project")
        print("3. Go to Authentication > Users")
        print("4. Click 'Add User' for each bank admin")
        print()
        print("Users to create:")
        for bank in CHILEAN_BANKS:
            print(f"  • admin@{bank['domain']}")
        return
    
    print()
    
    # Create bank users
    users_created = 0
    for bank in CHILEAN_BANKS:
        if create_bank_user(db, auth, bank):
            users_created += 1
    
    print()
    print("=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print()
    print(f"📊 Summary:")
    print(f"   Banks created/existing: {banks_created}/{len(CHILEAN_BANKS)}")
    print(f"   Users created/existing: {users_created}/{len(CHILEAN_BANKS)}")
    print()
    
    if users_created < len(CHILEAN_BANKS):
        print("⚠️  Some users could not be created.")
        print("   Please ensure all Firebase Auth users exist and run the script again.")
    else:
        print("✅ All banks and users have been set up successfully!")

if __name__ == "__main__":
    main()