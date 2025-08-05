"""
Firebase configuration and initialization
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import Client
import os
from typing import Optional

from .settings import get_settings


# Global Firebase instances
_db: Optional[Client] = None
_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> firebase_admin.App:
    """Initialize Firebase Admin SDK"""
    global _app, _db
    
    if _app is not None:
        return _app
    
    settings = get_settings()
    
    try:
        if settings.use_firebase_emulator:
            # Initialize for emulator
            print(f"🔧 Connecting to Firebase emulator at {settings.firebase_emulator_host}:{settings.firebase_emulator_port}")
            
            # Set environment variables for emulator
            os.environ["FIRESTORE_EMULATOR_HOST"] = f"{settings.firebase_emulator_host}:{settings.firebase_emulator_port}"
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = f"{settings.firebase_emulator_host}:9099"
            
            # Initialize with project ID only for emulator
            _app = firebase_admin.initialize_app(
                options={'projectId': settings.firebase_project_id}
            )
        else:
            # Initialize for production (with service account)
            cred = credentials.ApplicationDefault()
            _app = firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id
            })
        
        # Initialize Firestore client
        _db = firestore.client()
        
        print("✅ Firebase Admin SDK initialized successfully")
        return _app
        
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise


def get_firestore_client() -> Client:
    """Get Firestore client instance"""
    global _db
    
    if _db is None:
        initialize_firebase()
    
    return _db


def get_auth_client():
    """Get Firebase Auth client"""
    if _app is None:
        initialize_firebase()
    
    return auth


def verify_firebase_token(id_token: str) -> dict:
    """Verify Firebase ID token"""
    try:
        auth_client = get_auth_client()
        decoded_token = auth_client.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        raise ValueError(f"Invalid token: {e}")


def get_user_by_uid(uid: str) -> dict:
    """Get user record by UID"""
    try:
        auth_client = get_auth_client()
        user_record = auth_client.get_user(uid)
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'email_verified': user_record.email_verified,
            'display_name': user_record.display_name,
            'disabled': user_record.disabled
        }
    except Exception as e:
        print(f"❌ Failed to get user: {e}")
        raise ValueError(f"User not found: {e}")