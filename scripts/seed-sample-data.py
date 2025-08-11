"""
Script to seed sample data for xyz-corp client
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from datetime import datetime, timedelta
import asyncio
from config.firebase_config import get_cmek_firestore_client
from models.client import UnmatchedTrade, EmailConfirmation, TradeMatch

async def seed_sample_data():
    """Create sample data for xyz-corp client"""
    
    print("Starting sample data creation...")
    
    try:
        # Initialize Firestore client
        db = get_cmek_firestore_client()
        client_id = "xyz-corp"
        
        # Create sample unmatched trades
        trades_ref = db.collection('clients').document(client_id).collection('trades')
        
        sample_trades = [
            {
                "tradeNumber": "XYZ-2024-001",
                "counterpartyName": "Banco Santander Chile",
                "productType": "FX SPOT",
                "tradeDate": (datetime.now() - timedelta(days=2)).isoformat(),
                "valueDate": datetime.now().isoformat(),
                "direction": "BUY",
                "currency1": "USD",
                "quantityCurrency1": 100000,
                "currency2": "CLP",
                "forwardPrice": 890.50,
                "maturityDate": datetime.now().isoformat(),
                "fixingReference": "SPOT",
                "settlementType": "DVP",
                "settlementCurrency": "CLP",
                "paymentDate": datetime.now().isoformat(),
                "counterpartyPaymentMethod": "SWIFT",
                "ourPaymentMethod": "ACH",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "tradeNumber": "XYZ-2024-002",
                "counterpartyName": "Banco de Chile",
                "productType": "FX FORWARD",
                "tradeDate": (datetime.now() - timedelta(days=1)).isoformat(),
                "valueDate": (datetime.now() + timedelta(days=30)).isoformat(),
                "direction": "SELL",
                "currency1": "EUR",
                "quantityCurrency1": 50000,
                "currency2": "CLP",
                "forwardPrice": 950.25,
                "maturityDate": (datetime.now() + timedelta(days=30)).isoformat(),
                "fixingReference": "EUR/CLP-BCCH",
                "settlementType": "NET",
                "settlementCurrency": "EUR",
                "paymentDate": (datetime.now() + timedelta(days=30)).isoformat(),
                "counterpartyPaymentMethod": "WIRE",
                "ourPaymentMethod": "SWIFT",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "tradeNumber": "XYZ-2024-003",
                "counterpartyName": "BCI",
                "productType": "FX SWAP",
                "tradeDate": datetime.now().isoformat(),
                "valueDate": (datetime.now() + timedelta(days=2)).isoformat(),
                "direction": "BUY",
                "currency1": "USD",
                "quantityCurrency1": 75000,
                "currency2": "CLP",
                "forwardPrice": 891.75,
                "maturityDate": (datetime.now() + timedelta(days=90)).isoformat(),
                "fixingReference": "USD/CLP-BCCH",
                "settlementType": "DVP",
                "settlementCurrency": "USD",
                "paymentDate": (datetime.now() + timedelta(days=2)).isoformat(),
                "counterpartyPaymentMethod": "ACH",
                "ourPaymentMethod": "WIRE",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            }
        ]
        
        for trade in sample_trades:
            doc_ref = trades_ref.add(trade)
            print(f"Created trade: {trade['tradeNumber']}")
        
        # Create sample email confirmations
        emails_ref = db.collection('clients').document(client_id).collection('emails')
        
        sample_emails = [
            {
                "emailSender": "confirmations@santander.cl",
                "emailDate": (datetime.now() - timedelta(days=2)).isoformat(),
                "emailTime": "14:30:00",
                "emailSubject": "FX Trade Confirmation - XYZ-2024-001",
                "emailBody": "We confirm the following FX SPOT trade: Buy USD 100,000 @ 890.50 CLP",
                "bankTradeNumber": "SANT-FX-78901",
                "llmExtractedData": {
                    "tradeType": "FX SPOT",
                    "direction": "BUY",
                    "amount": 100000,
                    "rate": 890.50
                },
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "emailSender": "ops@bancochile.cl",
                "emailDate": (datetime.now() - timedelta(days=1)).isoformat(),
                "emailTime": "10:15:00",
                "emailSubject": "Trade Confirmation FWD EUR/CLP",
                "emailBody": "Forward trade confirmation: Sell EUR 50,000 for delivery on value date",
                "bankTradeNumber": "BCH-FWD-45678",
                "llmExtractedData": {
                    "tradeType": "FX FORWARD",
                    "direction": "SELL",
                    "amount": 50000,
                    "currency": "EUR"
                },
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "emailSender": "treasury@bci.cl",
                "emailDate": datetime.now().isoformat(),
                "emailTime": "16:45:00",
                "emailSubject": "FX SWAP Confirmation",
                "emailBody": "Please find attached the confirmation for FX SWAP USD/CLP",
                "bankTradeNumber": "BCI-SWP-12345",
                "llmExtractedData": {
                    "tradeType": "FX SWAP",
                    "currencies": ["USD", "CLP"]
                },
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            }
        ]
        
        for email in sample_emails:
            doc_ref = emails_ref.add(email)
            print(f"Created email: {email['emailSubject']}")
        
        # Create sample matches (matching first trade with first email)
        matches_ref = db.collection('clients').document(client_id).collection('matches')
        
        # Get the first trade and email IDs for creating a match
        first_trade = list(trades_ref.limit(1).stream())[0]
        first_email = list(emails_ref.limit(1).stream())[0]
        
        sample_match = {
            "tradeId": first_trade.id,
            "emailId": first_email.id,
            "confidenceScore": 0.92,
            "matchReasons": [
                "Trade number matches",
                "Amount matches",
                "Counterparty matches",
                "Trade date within tolerance"
            ],
            "discrepancies": [],
            "status": "matched",
            "createdAt": datetime.now().isoformat()
        }
        
        match_ref = matches_ref.add(sample_match)
        print(f"Created match between trade {first_trade.id} and email {first_email.id}")
        
        print("\nSample data creation completed successfully!")
        print(f"Created: 3 trades, 3 emails, 1 match for client {client_id}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_sample_data())