#!/usr/bin/env python3
"""
Quick Firestore connectivity test for startup script
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from database.firebase_client import db
    
    # Simple connectivity test - just try to get a collection reference
    test_ref = db.collection('_health_check')
    
    # Try to perform a simple operation that doesn't modify data
    # This will fail if authentication or connectivity is broken
    list(test_ref.limit(1).stream())
    
    print("Firestore connection: OK")
    sys.exit(0)
    
except Exception as e:
    print(f"Firestore connection failed: {e}")
    sys.exit(1)