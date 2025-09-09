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

from src.config.firebase_config import initialize_firebase, get_auth_client

# Bank list with domains
BANK_USERS = [
    {'email': 'admin@bice.cl', 'name': 'Banco BICE Admin'},
    {'email': 'admin@btgpactual.cl', 'name': 'Banco BTG Pactual Admin'},
    {'email': 'admin@bancoconsorcio.cl', 'name': 'Banco Consorcio Admin'},
    {'email': 'admin@bancochile.cl', 'name': 'Banco de Chile Admin'},
    {'email': 'admin@bancoestado.cl', 'name': 'Banco Estado Admin'},
    {'email': 'admin@bancofalabella.cl', 'name': 'Banco Falabella Admin'},
    {'email': 'admin@internacional.cl', 'name': 'Banco Internacional Admin'},
    {'email': 'admin@itau.cl', 'name': 'Banco Itaú Admin'},
    {'email': 'admin@bancoripley.cl', 'name': 'Banco Ripley Admin'},
    {'email': 'admin@santander.cl', 'name': 'Banco Santander Admin'},
    {'email': 'admin@security.cl', 'name': 'Banco Security Admin'},
    {'email': 'admin@hsbc.cl', 'name': 'HSBC Admin'},
    {'email': 'admin@scotiabank.cl', 'name': 'Scotiabank Admin'},
    {'email': 'admin@tanner.cl', 'name': 'Tanner Admin'}
]

def generate_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def create_auth_users(auth) -> List[Dict]:
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
            # Check if user already exists
            existing_user = auth.get_user_by_email(email)
            print(f"⚠️  User already exists: {email} (UID: {existing_user.uid})")
            users_existing += 1
            continue
        except:
            # User doesn't exist, create it
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
            
            print(f"✅ Created: {email} (UID: {user.uid})")
            credentials.append({
                'email': email,
                'password': password,
                'name': name,
                'uid': user.uid
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

def main():
    """Main function"""
    print("=" * 60)
    print("FIREBASE AUTH USER CREATION SCRIPT")
    print("=" * 60)
    print()
    print("This script will create Firebase Authentication users for all bank admins.")
    print(f"Total users to create: {len(BANK_USERS)}")
    print()
    
    # Show list of users
    print("Users to be created:")
    for user in BANK_USERS:
        print(f"  • {user['email']} ({user['name']})")
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
    print("✅ Firebase initialized")
    print()
    
    # Create users
    credentials = create_auth_users(auth)
    
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
    print("2. Run setup-all-banks.py to create bank documents and user profiles")
    print("3. Banks should change their passwords on first login")

if __name__ == "__main__":
    main()