#!/usr/bin/env python3
"""
Script to create Firebase Auth users for all bank admins.
This creates the authentication accounts that are prerequisites for the bank user documents.
"""

import sys
import os
import random
import string
from typing import List, Dict

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.config.firebase_config import initialize_firebase, get_auth_client, get_cmek_firestore_client
from datetime import datetime

# Bank list with domains and bank IDs
BANK_USERS = [
    {'email': 'admin@bice.cl', 'name': 'Banco BICE Admin', 'bankId': 'banco-bice', 'firstName': 'Admin', 'lastName': 'BICE'},
    {'email': 'admin@btgpactual.cl', 'name': 'Banco BTG Pactual Admin', 'bankId': 'banco-btg-pactual', 'firstName': 'Admin', 'lastName': 'BTG Pactual'},
    {'email': 'admin@bancoconsorcio.cl', 'name': 'Banco Consorcio Admin', 'bankId': 'banco-consorcio', 'firstName': 'Admin', 'lastName': 'Consorcio'},
    {'email': 'admin@bancochile.cl', 'name': 'Banco de Chile Admin', 'bankId': 'banco-de-chile', 'firstName': 'Admin', 'lastName': 'Banco de Chile'},
    {'email': 'admin@bancoestado.cl', 'name': 'Banco Estado Admin', 'bankId': 'banco-estado', 'firstName': 'Admin', 'lastName': 'Estado'},
    {'email': 'admin@bancofalabella.cl', 'name': 'Banco Falabella Admin', 'bankId': 'banco-falabella', 'firstName': 'Admin', 'lastName': 'Falabella'},
    {'email': 'admin@internacional.cl', 'name': 'Banco Internacional Admin', 'bankId': 'banco-internacional', 'firstName': 'Admin', 'lastName': 'Internacional'},
    {'email': 'admin@itau.cl', 'name': 'Banco Itaú Admin', 'bankId': 'banco-itau', 'firstName': 'Admin', 'lastName': 'Itaú'},
    {'email': 'admin@bancoripley.cl', 'name': 'Banco Ripley Admin', 'bankId': 'banco-ripley', 'firstName': 'Admin', 'lastName': 'Ripley'},
    {'email': 'admin@santander.cl', 'name': 'Banco Santander Admin', 'bankId': 'banco-santander', 'firstName': 'Admin', 'lastName': 'Santander'},
    {'email': 'admin@security.cl', 'name': 'Banco Security Admin', 'bankId': 'banco-security', 'firstName': 'Admin', 'lastName': 'Security'},
    {'email': 'admin@hsbc.cl', 'name': 'HSBC Admin', 'bankId': 'banco-hsbc', 'firstName': 'Admin', 'lastName': 'HSBC'},
    {'email': 'admin@scotiabank.cl', 'name': 'Scotiabank Admin', 'bankId': 'banco-scotiabank', 'firstName': 'Admin', 'lastName': 'Scotiabank'},
    {'email': 'admin@tanner.cl', 'name': 'Tanner Admin', 'bankId': 'banco-tanner', 'firstName': 'Admin', 'lastName': 'Tanner'}
]

def generate_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def check_firestore_user_exists(db, uid):
    """Check if Firestore user profile already exists"""
    try:
        user_ref = db.collection('users').document(uid)
        return user_ref.get().exists
    except Exception:
        return False

def delete_firestore_user_profile(db, uid):
    """Delete existing Firestore user profile"""
    try:
        user_ref = db.collection('users').document(uid)
        user_ref.delete()
        return True
    except Exception as e:
        print(f"❌ Failed to delete Firestore profile: {str(e)}")
        return False

async def create_firestore_user_profile(db, user_record, user_info):
    """Create complete Firestore user profile document"""
    try:
        user_data = {
            'createdAt': datetime.now(),
            'email': user_info['email'],
            'emailVerified': user_record.email_verified,
            'firstName': user_info['firstName'],
            'lastName': user_info['lastName'],
            'language': 'es',
            'lastUpdatedAt': datetime.now(),
            'lastUpdatedBy': db.collection('users').document(user_record.uid),
            'loginMetadata': {
                'lastLoginAt': None,
                'lastLoginIP': None,
                'loginCount': 0
            },
            'organizationId': db.collection('banks').document(user_info['bankId']),
            'organizationType': 'bank',
            'primaryRole': db.collection('roles').document('bank_admin'),
            'roles': [db.collection('roles').document('bank_admin')],
            'status': 'active',
            'timezone': 'America/Santiago',
            'twoFactorEnabled': False
        }
        
        # Create the user profile document
        user_ref = db.collection('users').document(user_record.uid)
        user_ref.set(user_data)
        
        return True
    except Exception as e:
        print(f"❌ Failed to create Firestore profile for {user_info['email']}: {str(e)}")
        return False

async def create_auth_users(auth, db) -> List[Dict]:
    """Create Firebase Auth users and return credentials"""
    print("=" * 60)
    print("CREATING FIREBASE AUTH USERS")
    print("=" * 60)
    print()
    
    credentials = []
    users_created = 0
    users_existing = 0
    users_failed = 0
    
    for user_info in BANK_USERS:
        email = user_info['email']
        name = user_info['name']
        
        try:
            # Check if user already exists in Firebase Auth
            existing_user = auth.get_user_by_email(email)
            print(f"⚠️  Firebase Auth user already exists: {email} (UID: {existing_user.uid})")
            
            # Check if Firestore profile also exists
            firestore_exists = check_firestore_user_exists(db, existing_user.uid)
            if firestore_exists:
                print(f"⚠️  Firestore profile also exists for: {email}")
                response = input(f"❓ Delete and recreate user {email}? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    # Delete Firestore profile
                    if delete_firestore_user_profile(db, existing_user.uid):
                        print(f"🗑️  Deleted existing Firestore profile for: {email}")
                        # Create new Firestore profile
                        profile_success = await create_firestore_user_profile(db, existing_user, user_info)
                        if profile_success:
                            print(f"✅ Recreated Firestore profile for: {email}")
                        else:
                            print(f"❌ Failed to recreate Firestore profile for: {email}")
                    else:
                        print(f"❌ Failed to delete existing profile for: {email}")
                else:
                    print(f"⏭️  Skipped: {email}")
            else:
                print(f"ℹ️  Creating missing Firestore profile for: {email}")
                # Create Firestore profile for existing Auth user
                profile_success = await create_firestore_user_profile(db, existing_user, user_info)
                if profile_success:
                    print(f"✅ Created Firestore profile for existing user: {email}")
                else:
                    print(f"❌ Failed to create Firestore profile for: {email}")
            
            users_existing += 1
            continue
        except:
            # User doesn't exist in Firebase Auth, create it
            pass
        
        try:
            # Generate secure password
            password = generate_password()
            
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name,
                email_verified=False  # Banks should verify their emails
            )
            
            # Create Firestore user profile
            profile_success = await create_firestore_user_profile(db, user, user_info)
            
            if profile_success:
                print(f"✅ Created: {email} (UID: {user.uid}) - Auth + Firestore profile")
                credentials.append({
                    'email': email,
                    'password': password,
                    'name': name,
                    'uid': user.uid
                })
                users_created += 1
            else:
                print(f"⚠️ Auth created but Firestore profile failed: {email}")
                # Still count as created since Auth user exists
                credentials.append({
                    'email': email,
                    'password': password,
                    'name': name,
                    'uid': user.uid,
                    'profile_error': True
                })
                users_created += 1
            
        except Exception as e:
            print(f"❌ Failed to create {email}: {str(e)}")
            users_failed += 1
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Created: {users_created}")
    print(f"⚠️  Already existed: {users_existing}")
    print(f"❌ Failed: {users_failed}")
    print(f"📊 Total: {len(BANK_USERS)}")
    
    return credentials

def save_credentials(credentials: List[Dict]):
    """Save credentials to a secure file"""
    if not credentials:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bank_credentials_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("BANK ADMIN CREDENTIALS\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write("⚠️  IMPORTANT: Store these credentials securely and share with banks!\n")
        f.write("⚠️  This file should be deleted after credentials are distributed.\n\n")
        
        for cred in credentials:
            f.write(f"Bank: {cred['name']}\n")
            f.write(f"Email: {cred['email']}\n")
            f.write(f"Password: {cred['password']}\n")
            f.write(f"UID: {cred['uid']}\n")
            f.write("-" * 40 + "\n\n")
    
    print()
    print(f"📄 Credentials saved to: {filename}")
    print("⚠️  IMPORTANT: Share these credentials securely with the banks!")
    print("⚠️  Delete this file after sharing the credentials!")

async def main():
    """Main function"""
    print("=" * 60)
    print("FIREBASE AUTH USER CREATION SCRIPT")
    print("=" * 60)
    print()
    print("This script will create complete Firebase users (Auth + Firestore profile) for all bank admins.")
    print(f"Total users to create: {len(BANK_USERS)}")
    print()
    
    # Show list of users
    print("Users to be created:")
    for user in BANK_USERS:
        print(f"  • {user['email']} ({user['name']}) → {user['bankId']}")
    print()
    
    # Confirm
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Cancelled")
        return
    
    print()
    print("🔧 Initializing Firebase...")
    initialize_firebase()
    auth = get_auth_client()
    db = get_cmek_firestore_client()
    print("✅ Firebase initialized (Auth + Firestore)")
    print()
    
    # Create users
    credentials = await create_auth_users(auth, db)
    
    # Save credentials if any were created
    if credentials:
        print()
        response = input("Save credentials to file? (yes/no): ").strip().lower()
        if response == 'yes':
            from datetime import datetime
            save_credentials(credentials)
    
    print()
    print("✅ Script complete!")
    print()
    print("Next steps:")
    print("1. Share credentials securely with each bank")
    print("2. Banks can now log in to the CCM system with their full profiles")
    print("3. Banks should change their passwords on first login")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())