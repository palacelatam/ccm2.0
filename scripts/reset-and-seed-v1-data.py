"""
Script to reset database and seed with v1.0 structure data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from datetime import datetime, timedelta
import asyncio
from config.firebase_config import get_cmek_firestore_client

async def reset_and_seed():
    """Delete old data and create new with v1.0 structure"""
    
    print("Starting database reset and v1.0 data creation...")
    
    try:
        db = get_cmek_firestore_client()
        client_id = "xyz-corp"
        
        # Step 1: Delete all existing data
        print("Deleting existing data...")
        
        # Delete trades
        trades_ref = db.collection('clients').document(client_id).collection('trades')
        for doc in trades_ref.stream():
            doc.reference.delete()
        print("Deleted all trades")
        
        # Delete emails
        emails_ref = db.collection('clients').document(client_id).collection('emails')
        for doc in emails_ref.stream():
            doc.reference.delete()
        print("Deleted all emails")
        
        # Delete matches
        matches_ref = db.collection('clients').document(client_id).collection('matches')
        for doc in matches_ref.stream():
            doc.reference.delete()
        print("Deleted all matches")
        
        # Step 2: Create UNMATCHED trades with v1.0 structure
        print("\nCreating unmatched trades with v1.0 structure...")
        
        unmatched_trades = [
            {
                "TradeNumber": "32010",
                "CounterpartyName": "Bci",
                "ProductType": "Forward",
                "TradeDate": "2025-10-01",
                "ValueDate": "2025-10-01",
                "Direction": "Buy",
                "Currency1": "USD",
                "QuantityCurrency1": 330000.0,
                "ForwardPrice": 932.33,
                "Currency2": "CLP",
                "MaturityDate": "2026-10-01",
                "FixingReference": "USD Obs",
                "SettlementType": "Compensación",
                "SettlementCurrency": "CLP",
                "PaymentDate": "2026-10-03",
                "CounterpartyPaymentMethod": "SWIFT",
                "OurPaymentMethod": "SWIFT",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "TradeNumber": "32011",
                "CounterpartyName": "Banco Santander",
                "ProductType": "Spot",
                "TradeDate": "2025-08-11",
                "ValueDate": "2025-08-13",
                "Direction": "Sell",
                "Currency1": "EUR",
                "QuantityCurrency1": 250000.0,
                "ForwardPrice": 985.75,
                "Currency2": "CLP",
                "MaturityDate": "2025-08-13",
                "FixingReference": "EUR/CLP",
                "SettlementType": "Compensación",
                "SettlementCurrency": "EUR",
                "PaymentDate": "2025-08-13",
                "CounterpartyPaymentMethod": "LBTR",
                "OurPaymentMethod": "LBTR",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            }
        ]
        
        for trade in unmatched_trades:
            doc_ref = trades_ref.add(trade)
            print(f"Created unmatched trade: {trade['TradeNumber']}")
        
        # Step 3: Create MATCHED trade with v1.0 structure
        print("\nCreating matched trade with v1.0 structure...")
        
        matched_trade = {
            "TradeNumber": "32013",
            "CounterpartyName": "Banco ABC",
            "ProductType": "Forward",
            "TradeDate": "2025-09-29",
            "ValueDate": "2025-10-01",
            "Direction": "Buy",
            "Currency1": "USD",
            "QuantityCurrency1": 1000000.0,
            "ForwardPrice": 932.88,
            "Currency2": "CLP",
            "MaturityDate": "2025-10-30",
            "FixingReference": "USD Obs",
            "SettlementType": "Compensación",
            "SettlementCurrency": "CLP",
            "PaymentDate": "2025-11-01",
            "CounterpartyPaymentMethod": "LBTR",
            "OurPaymentMethod": "LBTR",
            "status": "matched",  # This one is matched
            "createdAt": datetime.now().isoformat()
        }
        
        matched_trade_ref = trades_ref.add(matched_trade)
        matched_trade_id = matched_trade_ref[1].id
        print(f"Created matched trade: {matched_trade['TradeNumber']} (ID: {matched_trade_id})")
        
        # Step 4: Create email confirmations with v1.0 structure
        print("\nCreating email confirmations with v1.0 structure...")
        
        emails = [
            {
                "EmailSender": "confirmacionesderivados@bancoabc.cl",
                "EmailDate": "2025-04-04",
                "EmailTime": "11:39:04",
                "EmailSubject": "Confirmación operación 9239834",
                "BankTradeNumber": "9239834",
                "CounterpartyID": "",
                "CounterpartyName": "Banco ABC",
                "ProductType": "Forward",
                "Direction": "Buy",
                "Trader": None,
                "Currency1": "USD",
                "QuantityCurrency1": 1000000.0,
                "Currency2": "CLP",
                "SettlementType": "Compensación",
                "SettlementCurrency": "CLP",
                "TradeDate": "2025-09-29",
                "ValueDate": "2025-10-01",
                "MaturityDate": "2025-10-30",
                "PaymentDate": "2025-11-01",
                "Duration": 0,
                "ForwardPrice": 932.98,
                "FixingReference": "USD Obs",
                "CounterpartyPaymentMethod": "SWIFT",
                "OurPaymentMethod": "SWIFT",
                "EmailBody": "Estimados señores,\nSe ha negociado entre Banco ABC y Empresas ABC Limitada la siguiente operación...",
                "status": "matched",
                "createdAt": datetime.now().isoformat()
            },
            {
                "EmailSender": "ops@santander.cl",
                "EmailDate": "2025-08-10",
                "EmailTime": "14:22:11",
                "EmailSubject": "FX Confirmation - Trade 445566",
                "BankTradeNumber": "445566",
                "CounterpartyName": "Banco Santander",
                "ProductType": "Spot",
                "Direction": "Sell",
                "Currency1": "EUR",
                "QuantityCurrency1": 150000.0,
                "Currency2": "CLP",
                "ForwardPrice": 985.50,
                "EmailBody": "Please confirm the following FX spot transaction...",
                "status": "unmatched",
                "createdAt": datetime.now().isoformat()
            }
        ]
        
        email_refs = []
        for email in emails:
            doc_ref = emails_ref.add(email)
            email_refs.append(doc_ref[1].id)
            print(f"Created email: {email['EmailSubject']}")
        
        # Step 5: Create match linking the matched trade and first email
        print("\nCreating match between trade and email...")
        
        match_data = {
            "tradeId": matched_trade_id,
            "emailId": email_refs[0],  # First email
            "confidenceScore": 0.89,  # 89%
            "matchReasons": ["Trade number match", "Amount match", "Currency match"],
            "discrepancies": [],
            "status": "confirmed",
            "match_id": "608d18e1-98cf-4230-b8a0-e20a5c1f153e",
            "identified_at": datetime.now().isoformat(),
            "createdAt": datetime.now().isoformat()
        }
        
        match_ref = matches_ref.add(match_data)
        print(f"Created match with confidence: {match_data['confidenceScore']*100}%")
        
        print("\n=== Database reset complete ===")
        print(f"Created:")
        print(f"  - 2 unmatched trades")
        print(f"  - 1 matched trade")
        print(f"  - 2 email confirmations (1 matched, 1 unmatched)")
        print(f"  - 1 match record")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reset_and_seed())