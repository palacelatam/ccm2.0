#!/usr/bin/env python3
"""
Script to update user document IDs in CMEK Firestore database to match Firebase Auth UIDs
"""

import os
import sys
import json
from datetime import datetime

# Add the backend src to Python path
backend_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'src')
sys.path.append(backend_src)

from google.cloud import firestore as gcp_firestore

def main():
    # Firebase Auth UID to email mappings
    uid_email_mappings = {
        'uhhjERSGmvNMq0SpER0u2M1IWGp2': 'admin@bancoabc.cl',
        'D5HgqZfogqM3FyyH3zeJdu2Gt1F2': 'admin@xyz.cl',
        'cvXuhvcG61PjlRo7Ez4EHHV942k1': 'usuario@xyz.cl'
    }
    
    try:
        # Connect to CMEK database
        db = gcp_firestore.Client(
            project='ccm-dev-pool',
            database='ccm-development'
        )
        
        print("Connected to CMEK Firestore database")
        
        # Get all current users
        users_collection = db.collection('users')
        users_docs = users_collection.stream()
        
        current_users = []
        for doc in users_docs:
            user_data = doc.to_dict()
            user_data['current_id'] = doc.id
            current_users.append(user_data)
            print(f"Found user: {doc.id} - {user_data.get('email', 'No email')}")
        
        print(f"\nFound {len(current_users)} existing users")
        
        if not current_users:
            print("No existing users found. Creating new user documents...")
            
            # Create new user documents with correct UIDs
            for uid, email in uid_email_mappings.items():
                user_data = {
                    'email': email,
                    'firstName': email.split('@')[0].title(),
                    'lastName': 'User',
                    'status': 'active',
                    'language': 'es',
                    'timezone': 'America/Santiago',
                    'createdAt': datetime.now(),
                    'lastUpdatedAt': datetime.now()
                }
                
                # Create document with Firebase Auth UID as document ID
                user_ref = users_collection.document(uid)
                user_ref.set(user_data)
                
                print(f"Created user document: {uid} -> {email}")
        
        else:
            # Update existing users by matching email addresses
            for user in current_users:
                user_email = user.get('email', '')
                matching_uid = None
                
                # Find matching UID for this email
                for uid, email in uid_email_mappings.items():
                    if user_email == email:
                        matching_uid = uid
                        break
                
                if matching_uid and user['current_id'] != matching_uid:
                    print(f"Updating user {user_email}: {user['current_id']} -> {matching_uid}")
                    
                    # Create new document with correct UID
                    new_user_ref = users_collection.document(matching_uid)
                    
                    # Copy data (excluding current_id)
                    user_data = {k: v for k, v in user.items() if k != 'current_id'}
                    user_data['lastUpdatedAt'] = datetime.now()
                    
                    new_user_ref.set(user_data)
                    
                    # Delete old document
                    old_user_ref = users_collection.document(user['current_id'])
                    old_user_ref.delete()
                    
                    print(f"Updated user: {user_email}")
                    
                elif matching_uid and user['current_id'] == matching_uid:
                    print(f"User {user_email} already has correct UID: {matching_uid}")
                    
                else:
                    print(f"No matching UID found for email: {user_email}")
        
        print("\nUser ID update completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())