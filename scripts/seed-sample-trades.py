#!/usr/bin/env python3
"""
Script to seed sample trade data directly to Firestore for testing
"""

import os
import sys
from datetime import datetime, timedelta
import uuid

# Add the backend src to Python path
backend_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'src')
sys.path.append(backend_src)

from google.cloud import firestore as gcp_firestore

def create_sample_data():
    """Create sample trade data for testing"""
    
    # Sample unmatched trades
    sample_trades = [
        {
            "tradeNumber": "T001",
            "counterpartyName": "Banco ABC",
            "productType": "Forward",
            "tradeDate": "2024-01-15",
            "valueDate": "2024-02-15",
            "direction": "Buy",
            "currency1": "USD",
            "quantityCurrency1": 100000.00,
            "currency2": "CLP",
            "forwardPrice": 950.50,
            "maturityDate": "2024-02-15",
            "fixingReference": "USD Obs",
            "settlementType": "Compensación",
            "settlementCurrency": "CLP",
            "paymentDate": "2024-02-17",
            "counterpartyPaymentMethod": "SWIFT",
            "ourPaymentMethod": "SWIFT",
            "status": "unmatched",
            "organizationId": "test-client",
            "createdAt": datetime.now()
        },
        {
            "tradeNumber": "T002",
            "counterpartyName": "Banco XYZ",
            "productType": "Spot",
            "tradeDate": "2024-01-16",
            "valueDate": "2024-01-18",
            "direction": "Sell",
            "currency1": "EUR",
            "quantityCurrency1": 50000.00,
            "currency2": "CLP",
            "forwardPrice": 1020.75,
            "maturityDate": "2024-01-18",
            "fixingReference": "EUR Obs",
            "settlementType": "Entrega Física",
            "settlementCurrency": "N/A",
            "paymentDate": "2024-01-20",
            "counterpartyPaymentMethod": "LBTR",
            "ourPaymentMethod": "LBTR",
            "status": "unmatched",
            "organizationId": "test-client",
            "createdAt": datetime.now()
        }
    ]
    
    # Sample email confirmations
    sample_emails = [
        {
            "emailSender": "confirmaciones@bancoabc.cl",
            "emailDate": "2024-01-15",
            "emailTime": "10:30:00",
            "emailSubject": "Confirmación Operación T001",
            "emailBody": "Estimados, confirmamos la operación Forward por USD 100,000 vs CLP...",
            "bankTradeNumber": "T001-ABC",
            "status": "unmatched",
            "organizationId": "test-client",
            "createdAt": datetime.now(),
            "llmExtractedData": {
                "tradeNumber": "T001",
                "amount": 100000.00,
                "currency": "USD",
                "counterparty": "Banco ABC"
            }
        },
        {
            "emailSender": "ops@bancoxyz.cl",
            "emailDate": "2024-01-16",
            "emailTime": "14:45:00",
            "emailSubject": "Confirmación Spot EUR/CLP",
            "emailBody": "Confirmamos operación spot EUR 50,000 vs CLP...",
            "bankTradeNumber": "T002-XYZ",
            "status": "unmatched",
            "organizationId": "test-client",
            "createdAt": datetime.now(),
            "llmExtractedData": {
                "tradeNumber": "T002",
                "amount": 50000.00,
                "currency": "EUR",
                "counterparty": "Banco XYZ"
            }
        }
    ]
    
    return sample_trades, sample_emails

def seed_data():
    """Seed sample data to Firestore"""
    try:
        # Connect to CMEK database
        db = gcp_firestore.Client(
            project='ccm-dev-pool',
            database='ccm-development'
        )
        
        print("Connected to CMEK Firestore database")
        
        # Create sample data
        sample_trades, sample_emails = create_sample_data()
        
        # Use existing client ID from your database
        client_id = "uhhjERSGmvNMq0SpER0u2M1IWGp2"  # admin@bancoabc.cl user's org
        
        print(f"Seeding data for client: {client_id}")
        
        # Seed trades
        trades_ref = db.collection('clients').document(client_id).collection('trades')
        for i, trade in enumerate(sample_trades):
            doc_ref = trades_ref.add(trade)[1]
            print(f"Created trade: {doc_ref.id} - {trade['tradeNumber']}")
        
        # Seed email confirmations
        emails_ref = db.collection('clients').document(client_id).collection('emails')
        for i, email in enumerate(sample_emails):
            doc_ref = emails_ref.add(email)[1]
            print(f"Created email: {doc_ref.id} - {email['emailSubject']}")
        
        # Create a sample upload session
        sessions_ref = db.collection('clients').document(client_id).collection('uploadSessions')
        session_doc = {
            "fileName": "sample_trades.xlsx",
            "fileType": "trades",
            "fileSize": 15420,
            "recordsProcessed": len(sample_trades),
            "recordsFailed": 0,
            "status": "completed",
            "uploadedBy": client_id,
            "organizationId": client_id,
            "createdAt": datetime.now()
        }
        session_ref = sessions_ref.add(session_doc)[1]
        print(f"Created upload session: {session_ref.id}")
        
        print(f"\nSeeded successfully:")
        print(f"- {len(sample_trades)} trades")
        print(f"- {len(sample_emails)} emails")
        print(f"- 1 upload session")
        
        return True
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        return False

def main():
    print("Trade Data Seeding Script")
    print("=" * 50)
    
    success = seed_data()
    
    if success:
        print("\nSample data seeded successfully!")
        print("\nYou can now test the endpoints with actual data:")
        print("1. GET /api/v1/clients/{client_id}/unmatched-trades")
        print("2. GET /api/v1/clients/{client_id}/email-confirmations")
        print("3. GET /api/v1/clients/{client_id}/matches")
        print("\nNote: You'll need proper authentication headers to access the data.")
    else:
        print("\nFailed to seed data")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())