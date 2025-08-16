"""
Script to add confirmationEmail field to client documents
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.config.firebase_config import get_cmek_firestore_client

def add_confirmation_email():
    """Add confirmationEmail field to xyz-corp client"""
    
    print("Adding confirmationEmail field to client documents...")
    
    try:
        # Initialize Firestore client
        db = get_cmek_firestore_client()
        
        # Update xyz-corp client
        client_id = "xyz-corp"
        confirmation_email = "admin@xyz.cl"
        
        print(f"Updating client {client_id} with confirmationEmail: {confirmation_email}")
        
        # Update the document
        client_ref = db.collection('clients').document(client_id)
        client_ref.update({
            'confirmationEmail': confirmation_email
        })
        
        print(f"✅ Successfully updated {client_id} with confirmationEmail")
        
        # Verify the update
        doc = client_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"Verification: confirmationEmail = {data.get('confirmationEmail')}")
        
    except Exception as e:
        print(f"❌ Error updating client: {e}")
        return False
    
    return True

if __name__ == "__main__":
    add_confirmation_email()