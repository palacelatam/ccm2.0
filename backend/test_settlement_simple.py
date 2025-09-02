"""
Simple Settlement Instructions Test with Real Trade Data
This version avoids importing services that initialize external dependencies
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')

from services.settlement_instruction_service import settlement_instruction_service
from config.firebase_config import get_cmek_firestore_client


async def get_real_trade_data(limit: int = 3):
    """
    Fetch real matched trade data directly from Firestore
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get clients
        clients_ref = db.collection('clients')
        clients = clients_ref.limit(5).get()
        
        print(f"Found {len(clients)} clients in database")
        
        all_trades = []
        
        for client_doc in clients:
            client_id = client_doc.id
            client_data = client_doc.to_dict()
            client_name = client_data.get('name', client_id)
            
            print(f"\nChecking client: {client_name} ({client_id})")
            
            # Get trades directly from Firestore
            trades_ref = db.collection('clients').document(client_id).collection('trades')
            trades = trades_ref.limit(5).get()
            
            print(f"  Found {len(trades)} trades")
            
            for trade_doc in trades:
                trade_data = trade_doc.to_dict()
                trade_data['id'] = trade_doc.id
                trade_data['client_id'] = client_id
                trade_data['client_name'] = client_name
                
                # Only include trades with meaningful data
                if trade_data.get('TradeNumber') or trade_data.get('CounterpartyName'):
                    all_trades.append(trade_data)
                    
                    trade_num = trade_data.get('TradeNumber', 'No number')
                    counterparty = trade_data.get('CounterpartyName', 'No counterparty')
                    currency1 = trade_data.get('Currency1', 'N/A')
                    currency2 = trade_data.get('Currency2', 'N/A')
                    amount = trade_data.get('QuantityCurrency1', 'N/A')
                    
                    print(f"    • {trade_num} | {counterparty} | {currency1}/{currency2} | {amount}")
        
        return all_trades[:limit]
        
    except Exception as e:
        print(f"Error fetching trade data: {e}")
        return []


async def get_settlement_rules_direct(client_id: str):
    """
    Get settlement rules directly from Firestore
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get settlement rules directly
        rules_ref = db.collection('clients').document(client_id).collection('settlement_rules')
        rules = rules_ref.get()
        
        settlement_rules = []
        for rule_doc in rules:
            rule_data = rule_doc.to_dict()
            rule_data['id'] = rule_doc.id
            settlement_rules.append(rule_data)
        
        print(f"  Found {len(settlement_rules)} settlement rules")
        return settlement_rules
        
    except Exception as e:
        print(f"  Error getting settlement rules: {e}")
        return []


async def get_bank_accounts_direct(client_id: str):
    """
    Get bank accounts directly from Firestore
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get bank accounts directly
        accounts_ref = db.collection('clients').document(client_id).collection('bank_accounts')
        accounts = accounts_ref.get()
        
        bank_accounts = []
        for account_doc in accounts:
            account_data = account_doc.to_dict()
            account_data['id'] = account_doc.id
            bank_accounts.append(account_data)
        
        print(f"  Found {len(bank_accounts)} bank accounts")
        return bank_accounts
        
    except Exception as e:
        print(f"  Error getting bank accounts: {e}")
        return []


def find_matching_data(trade_data, settlement_rules, bank_accounts):
    """
    Simple matching logic to find settlement rule and bank account for a trade
    """
    # Extract trade info
    trade_counterparty = str(trade_data.get('CounterpartyName', '')).lower()
    trade_currency1 = trade_data.get('Currency1', '')
    trade_currency2 = trade_data.get('Currency2', '')
    
    print(f"    Looking for rules matching: {trade_counterparty}, {trade_currency1}/{trade_currency2}")
    
    # Try to find matching settlement rule
    matching_rule = None
    for rule in settlement_rules:
        rule_counterparty = str(rule.get('counterparty', '')).lower()
        rule_currency = rule.get('cashflowCurrency', '')
        
        # Simple matching logic
        if (rule_counterparty in trade_counterparty or trade_counterparty in rule_counterparty) and \
           (rule_currency in [trade_currency1, trade_currency2]):
            matching_rule = rule
            print(f"    ✅ Found matching rule: {rule.get('name', 'Unnamed')}")
            break
    
    if not matching_rule and settlement_rules:
        matching_rule = settlement_rules[0]  # Use first rule as fallback
        print(f"    ⚠️ Using fallback rule: {matching_rule.get('name', 'Unnamed')}")
    
    # Find matching bank account
    matching_account = None
    if matching_rule and bank_accounts:
        rule_account_id = matching_rule.get('bankAccountId', '')
        
        # Try to match by account ID
        for account in bank_accounts:
            if account.get('id') == rule_account_id:
                matching_account = account
                print(f"    ✅ Found matching account: {account.get('accountName', 'Unnamed')}")
                break
        
        # Fallback to first account
        if not matching_account:
            matching_account = bank_accounts[0]
            print(f"    ⚠️ Using fallback account: {matching_account.get('accountName', 'Unnamed')}")
    
    return matching_rule, matching_account


async def test_with_real_data():
    """
    Test settlement instructions with real database data
    """
    print("=" * 80)
    print("Settlement Instructions Test with Real Database Data")
    print("=" * 80)
    
    # Get real trade data
    print("Fetching real trade data...")
    trades = await get_real_trade_data(limit=3)
    
    if not trades:
        print("❌ No trades found in database!")
        print("\nMake sure you have trade data in your Firestore collections:")
        print("  /clients/{client_id}/trades")
        return
    
    print(f"\n✅ Processing {len(trades)} trades")
    generated_docs = []
    
    # Process each trade
    for i, trade in enumerate(trades, 1):
        print(f"\n" + "=" * 60)
        print(f"Processing Trade {i}/{len(trades)}")
        print("=" * 60)
        
        client_id = trade['client_id']
        client_name = trade['client_name']
        trade_number = trade.get('TradeNumber', 'No number')
        counterparty = trade.get('CounterpartyName', 'No counterparty')
        
        print(f"Client: {client_name}")
        print(f"Trade: {trade_number}")
        print(f"Counterparty: {counterparty}")
        
        # Get client data
        print(f"\nFetching client settlement data...")
        settlement_rules = await get_settlement_rules_direct(client_id)
        bank_accounts = await get_bank_accounts_direct(client_id)
        
        # Find matching data
        matching_rule, matching_account = find_matching_data(trade, settlement_rules, bank_accounts)
        
        # Prepare settlement data
        settlement_data = None
        if matching_rule and matching_account:
            settlement_data = {
                'account_name': matching_account.get('accountName', 'N/A'),
                'account_number': matching_account.get('accountNumber', 'N/A'), 
                'bank_name': matching_account.get('bankName', 'N/A'),
                'swift_code': matching_account.get('swiftCode', 'N/A'),
                'cutoff_time': '15:00',
                'special_instructions': f"Settlement via {matching_rule.get('name', 'standard rule')}"
            }
            
            print(f"\n✅ Settlement data prepared:")
            print(f"    Account: {settlement_data['account_name']}")
            print(f"    Bank: {settlement_data['bank_name']}")
            print(f"    SWIFT: {settlement_data['swift_code']}")
        else:
            print(f"\n⚠️  No settlement data found - using defaults")
        
        # Generate document
        print(f"\nGenerating settlement instruction...")
        result = await settlement_instruction_service.generate_settlement_instruction(
            trade_data=trade,
            settlement_data=settlement_data
        )
        
        if result['success']:
            print(f"✅ Document generated: {os.path.basename(result['document_path'])}")
            generated_docs.append(result['document_path'])
        else:
            print(f"❌ Generation failed: {result['error']}")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("Test Results")
    print("=" * 80)
    print(f"Trades processed: {len(trades)}")
    print(f"Documents generated: {len(generated_docs)}")
    
    if generated_docs:
        print(f"\n🎉 Generated settlement instruction documents:")
        for doc in generated_docs:
            print(f"   • {os.path.basename(doc)}")
        print(f"\nLocation: backend/templates/generated/")
        print("Open these documents to see the real trade data populated!")
    else:
        print("❌ No documents generated successfully")


async def main():
    """Main function"""
    await test_with_real_data()


if __name__ == "__main__":
    asyncio.run(main())