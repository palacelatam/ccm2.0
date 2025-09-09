#!/usr/bin/env python3
"""
Script to create counterparty mappings for a specific client.
This creates aliases that map common bank name variations to standardized bank IDs.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.config.firebase_config import initialize_firebase, get_cmek_firestore_client

# Bank aliases mapping - common ways banks might be referred to in emails
# TODO: Review and update these aliases based on actual email variations
BANK_ALIASES = {
    'banco-abc': [
        'ABC', 'Banco ABC',
        '99.999.999-9', '99999999-9'  # RUT with and without dots
    ],
    'banco-bice': [
        'BICE', 'Banco BICE',
        '97.080.000-K', '97080000-K'
    ],
    'banco-btg-pactual': [
        'BTG', 'BTG Pactual', 'Banco BTG', 'BTG Pactual Chile', 'Banco BTG Pactual',
        '76.362.099-9', '763620999'
    ],
    'banco-consorcio': [
        'Consorcio', 'Banco Consorcio',
        '99.500.410-0', '99500410-0'
    ],
    'banco-de-chile': [
        'Banco Chile', 'Banco de Chile',
        '97.004.000-5', '97004000-5'
    ],
    'banco-bci': [
        'BCI', 'Banco BCI', 'Banco de Crédito', 'Banco de Crédito e Inversiones',
        '97.006.000-6', '97006000-6'
    ],
    'banco-estado': [
        'BancoEstado', 'Banco Estado', 'Banco del Estado', 'Banco del Estado de Chile',
        '97.030.000-7', '97030000-7'
    ],
    'banco-falabella': [
        'Falabella', 'Banco Falabella',
        '96.509.660-4', '96509660-4'
    ],
    'banco-internacional': [
        'Internacional', 'Banco Internacional',
        '97.011.000-3', '97011000-3'
    ],
    'banco-itau': [
        'Itaú', 'Itau', 'Banco Itaú', 'Banco Itau', 'Banco Itaú Chile', 'Itaú Corpbanca', 'Itau Corpbanca', 'Itaú-Corpbanca', 'Itau-Corpbanca',
        '97.023.000-9', '97023000-9'
    ],
    'banco-ripley': [
        'Ripley', 'Banco Ripley',
        '97.947.000-2', '97947000-2'
    ],
    'banco-santander': [
        'Santander', 'Banco Santander', 'Santander Chile', 'Banco Santander Chile', 'Banco Santander-Santiago', 'Banco Santander Santiago',
        '97.036.000-K', '97036000-K'
    ],
    'banco-security': [
        'Security', 'Banco Security',
        '97.053.000-2', '97053000-2'
    ],
    'banco-hsbc': [
        'HSBC', 'HSBC Chile', 'HSBC Bank Chile',
        '97.951.000-4', '97951000-4'
    ],
    'banco-scotiabank': [
        'Scotia', 'Scotiabank', 'Scotiabank Chile',
        '97.018.000-1', '97018000-1'
    ],
    'banco-tanner': [
        'Tanner', 'Tanner Digital', 'Banco Tanner', 'Tanner Banco Digital',
        '99.999.999-9', '99999999-9'  # Placeholder values
    ]
}

def create_counterparty_mappings(db, client_id: str) -> bool:
    """Create counterparty mappings for a client"""
    try:
        client_ref = db.collection('clients').document(client_id)
        
        # Check if client exists
        if not client_ref.get().exists:
            print(f"❌ Client '{client_id}' does not exist")
            return False
        
        print(f"Creating counterparty mappings for client: {client_id}")
        print()
        
        mappings_created = 0
        mappings_existing = 0
        
        # Create mappings for each bank
        for bank_id, aliases in BANK_ALIASES.items():
            for alias in aliases:
                try:
                    # Check if mapping already exists
                    existing_mappings = client_ref.collection('counterpartyMappings').where('counterpartyName', '==', alias).limit(1).get()
                    
                    if list(existing_mappings):
                        print(f"⚠️  Mapping already exists: '{alias}' → {bank_id}")
                        mappings_existing += 1
                        continue
                    
                    # Create new mapping
                    mapping_ref = client_ref.collection('counterpartyMappings').document()
                    mapping_data = {
                        'bankId': bank_id,
                        'counterpartyName': alias,
                        'createdAt': datetime.utcnow(),
                        'createdBy': 'counterparty-mapping-script'
                    }
                    
                    mapping_ref.set(mapping_data)
                    print(f"✅ Created mapping: '{alias}' → {bank_id}")
                    mappings_created += 1
                    
                except Exception as e:
                    print(f"❌ Failed to create mapping '{alias}' → {bank_id}: {str(e)}")
        
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✅ Mappings created: {mappings_created}")
        print(f"⚠️  Already existed: {mappings_existing}")
        print(f"📊 Total processed: {mappings_created + mappings_existing}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating mappings for client {client_id}: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("COUNTERPARTY MAPPINGS CREATION SCRIPT")
    print("=" * 60)
    print()
    
    # Get client ID from user
    if len(sys.argv) > 1:
        client_id = sys.argv[1]
    else:
        client_id = input("Enter client ID (e.g., xyz-corp): ").strip()
    
    if not client_id:
        print("❌ Client ID is required")
        return
    
    print(f"Client ID: {client_id}")
    print()
    
    # Show what will be created
    total_mappings = sum(len(aliases) for aliases in BANK_ALIASES.values())
    print(f"This script will create up to {total_mappings} counterparty mappings:")
    print()
    
    for bank_id, aliases in BANK_ALIASES.items():
        print(f"  {bank_id}:")
        for alias in aliases:
            print(f"    • '{alias}' → {bank_id}")
    print()
    
    print("💡 TIP: Review and edit BANK_ALIASES in the script before running if needed")
    print()
    
    # Confirm with user
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Operation cancelled")
        return
    
    print()
    print("🔧 Initializing Firebase...")
    initialize_firebase()
    db = get_cmek_firestore_client()
    print("✅ Firebase initialized")
    print()
    
    # Create mappings
    success = create_counterparty_mappings(db, client_id)
    
    if success:
        print()
        print("✅ Script completed successfully!")
        print()
        print("Next steps:")
        print("1. Test settlement rule matching with various bank name formats")
        print("2. Add more aliases if needed based on actual email variations")
        print("3. Update BANK_ALIASES in script for other clients if different patterns emerge")
    else:
        print()
        print("❌ Script completed with errors")

if __name__ == "__main__":
    main()