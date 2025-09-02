"""
Test Settlement Instructions with Real Trade Data from Database
This script pulls actual matched trade data from Firestore and generates settlement instructions
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')

from services.settlement_instruction_service import settlement_instruction_service
from config.firebase_config import get_cmek_firestore_client
from services.client_service import ClientService


async def get_real_trade_data(client_id: str = None, limit: int = 5):
    """
    Fetch real matched trade data from the database
    
    Args:
        client_id: Optional client ID to filter by
        limit: Maximum number of trades to fetch
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get list of clients first
        clients_ref = db.collection('clients')
        clients = clients_ref.limit(10).get()
        
        print(f"Found {len(clients)} clients in database")
        
        all_trades = []
        
        for client_doc in clients:
            client_id = client_doc.id
            client_data = client_doc.to_dict()
            client_name = client_data.get('name', client_id)
            
            print(f"\nChecking trades for client: {client_name} ({client_id})")
            
            # Look for matched trades in this client
            trades_ref = db.collection('clients').document(client_id).collection('trades')
            trades = trades_ref.limit(limit).get()
            
            print(f"  Found {len(trades)} trades")
            
            for trade_doc in trades:
                trade_data = trade_doc.to_dict()
                trade_data['id'] = trade_doc.id
                trade_data['client_id'] = client_id
                trade_data['client_name'] = client_name
                
                # Add to list if it has meaningful data
                if trade_data.get('TradeNumber') or trade_data.get('CounterpartyName'):
                    all_trades.append(trade_data)
                    print(f"    Trade: {trade_data.get('TradeNumber', 'No number')} - {trade_data.get('CounterpartyName', 'No counterparty')}")
        
        return all_trades[:limit]  # Return up to limit trades
        
    except Exception as e:
        print(f"Error fetching real trade data: {e}")
        return []


async def get_client_settlement_rules(client_id: str):
    """
    Get settlement rules for a client
    """
    try:
        # Create client service instance
        client_service = ClientService()
        response = await client_service.get_settlement_rules(client_id)
        if response.success and response.data:
            print(f"  Found {len(response.data)} settlement rules for client {client_id}")
            return response.data
        else:
            print(f"  No settlement rules found for client {client_id}")
            return []
    except Exception as e:
        print(f"  Error getting settlement rules: {e}")
        return []


async def get_client_bank_accounts(client_id: str):
    """
    Get bank accounts for a client
    """
    try:
        # Create client service instance
        client_service = ClientService()
        response = await client_service.get_bank_accounts(client_id)
        if response.success and response.data:
            print(f"  Found {len(response.data)} bank accounts for client {client_id}")
            return response.data
        else:
            print(f"  No bank accounts found for client {client_id}")
            return []
    except Exception as e:
        print(f"  Error getting bank accounts: {e}")
        return []


def find_matching_settlement_rule(trade_data, settlement_rules):
    """
    Find a settlement rule that matches the trade
    Simple matching logic - can be improved later
    """
    if not settlement_rules:
        return None
    
    trade_counterparty = trade_data.get('CounterpartyName', '').lower()
    trade_currency = trade_data.get('Currency1', '') or trade_data.get('Currency2', '')
    trade_product = trade_data.get('Product', '')
    
    # Try to find exact match first
    for rule in settlement_rules:
        rule_counterparty = rule.get('counterparty', '').lower()
        rule_currency = rule.get('cashflowCurrency', '')
        rule_product = rule.get('product', '')
        
        if (rule_counterparty in trade_counterparty or trade_counterparty in rule_counterparty) and \
           rule_currency == trade_currency:
            print(f"    Found matching rule: {rule.get('name', 'Unnamed rule')}")
            return rule
    
    # Return first rule as fallback
    if settlement_rules:
        print(f"    Using fallback rule: {settlement_rules[0].get('name', 'Unnamed rule')}")
        return settlement_rules[0]
    
    return None


def find_matching_bank_account(settlement_rule, bank_accounts):
    """
    Find bank account that matches the settlement rule
    """
    if not bank_accounts or not settlement_rule:
        return None
    
    rule_account_id = settlement_rule.get('bankAccountId', '')
    
    # Try to find account by ID first
    for account in bank_accounts:
        if account.get('id') == rule_account_id:
            print(f"    Found matching account: {account.get('accountName', 'Unnamed account')}")
            return account
    
    # Fallback to currency match
    rule_currency = settlement_rule.get('cashflowCurrency', '')
    for account in bank_accounts:
        if account.get('accountCurrency') == rule_currency:
            print(f"    Found currency-matching account: {account.get('accountName', 'Unnamed account')}")
            return account
    
    # Return first account as fallback
    if bank_accounts:
        print(f"    Using fallback account: {bank_accounts[0].get('accountName', 'Unnamed account')}")
        return bank_accounts[0]
    
    return None


async def test_with_real_data():
    """
    Main test function using real database data
    """
    print("=" * 80)
    print("Settlement Instructions Test with Real Database Data")
    print("=" * 80)
    
    # Fetch real trade data
    print("Fetching real trade data from database...")
    trades = await get_real_trade_data(limit=3)
    
    if not trades:
        print("❌ No trade data found in database!")
        print("Make sure you have trade data in your Firestore database.")
        return
    
    print(f"\n✅ Found {len(trades)} trades to process")
    
    generated_docs = []
    
    for i, trade in enumerate(trades, 1):
        print(f"\n" + "=" * 60)
        print(f"Processing Trade {i}/{len(trades)}")
        print("=" * 60)
        
        client_id = trade['client_id']
        client_name = trade['client_name']
        trade_number = trade.get('TradeNumber', 'Unknown')
        counterparty = trade.get('CounterpartyName', 'Unknown')
        
        print(f"Client: {client_name}")
        print(f"Trade: {trade_number}")
        print(f"Counterparty: {counterparty}")
        
        # Get client's settlement rules and bank accounts
        print(f"\nFetching client data...")
        settlement_rules = await get_client_settlement_rules(client_id)
        bank_accounts = await get_client_bank_accounts(client_id)
        
        # Find matching rule and account
        settlement_rule = find_matching_settlement_rule(trade, settlement_rules)
        bank_account = find_matching_bank_account(settlement_rule, bank_accounts)
        
        # Prepare settlement data from matched rule and account
        settlement_data = None
        if settlement_rule and bank_account:
            settlement_data = {
                'account_name': bank_account.get('accountName', 'N/A'),
                'account_number': bank_account.get('accountNumber', 'N/A'),
                'bank_name': bank_account.get('bankName', 'N/A'),
                'swift_code': bank_account.get('swiftCode', 'N/A'),
                'cutoff_time': '15:00',  # Default - could come from rule
                'special_instructions': settlement_rule.get('specialInstructions', 'Standard settlement instructions apply.')
            }
            
            print(f"Settlement Data Prepared:")
            for key, value in settlement_data.items():
                print(f"  {key}: {value}")
        else:
            print("⚠️  No matching settlement rule or bank account found - using defaults")
        
        # Generate settlement instruction
        print(f"\nGenerating settlement instruction document...")
        
        result = await settlement_instruction_service.generate_settlement_instruction(
            trade_data=trade,
            settlement_data=settlement_data
        )
        
        if result['success']:
            print(f"✅ Document generated successfully!")
            print(f"   Path: {result['document_path']}")
            print(f"   Variables populated: {result['variables_populated']}")
            generated_docs.append(result['document_path'])
        else:
            print(f"❌ Document generation failed!")
            print(f"   Error: {result['error']}")
    
    print(f"\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Trades processed: {len(trades)}")
    print(f"Documents generated: {len(generated_docs)}")
    
    if generated_docs:
        print(f"\n🎉 Settlement instruction documents generated:")
        for doc_path in generated_docs:
            print(f"   • {os.path.basename(doc_path)}")
        print(f"\nAll documents saved in: backend/templates/generated/")
        print("Open them to verify the real trade data was populated correctly!")
    else:
        print("⚠️  No documents were generated successfully.")


async def list_available_data():
    """
    Helper function to show what data is available in the database
    """
    print("=" * 60)
    print("Available Data in Database")
    print("=" * 60)
    
    try:
        db = get_cmek_firestore_client()
        
        # List clients
        clients_ref = db.collection('clients')
        clients = clients_ref.limit(5).get()
        
        print(f"Clients found: {len(clients)}")
        
        for client_doc in clients:
            client_id = client_doc.id
            client_data = client_doc.to_dict()
            client_name = client_data.get('name', 'Unknown')
            
            print(f"\nClient: {client_name} ({client_id})")
            
            # Check trades
            trades_ref = db.collection('clients').document(client_id).collection('trades')
            trades = trades_ref.limit(3).get()
            print(f"  Trades: {len(trades)}")
            
            for trade_doc in trades:
                trade_data = trade_doc.to_dict()
                trade_number = trade_data.get('TradeNumber', 'No number')
                counterparty = trade_data.get('CounterpartyName', 'No counterparty')
                print(f"    • {trade_number} - {counterparty}")
        
    except Exception as e:
        print(f"Error accessing database: {e}")


async def main():
    """
    Main function with options
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        await list_available_data()
    else:
        await test_with_real_data()


if __name__ == "__main__":
    asyncio.run(main())