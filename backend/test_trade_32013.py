"""
Test Settlement Instructions with Specific Trade 32013
This script fetches trade 32013 from Firestore and generates settlement instructions
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append('src')

from services.settlement_instruction_service import settlement_instruction_service
from config.firebase_config import get_cmek_firestore_client


async def get_specific_trade(trade_number: str = "32013"):
    """
    Fetch a specific trade by trade number from the database
    
    Args:
        trade_number: The trade number to search for
    """
    try:
        db = get_cmek_firestore_client()
        
        print(f"Searching for trade number: {trade_number}")
        print("=" * 60)
        
        # Get list of clients
        clients_ref = db.collection('clients')
        clients = clients_ref.get()
        
        print(f"Searching across {len(clients)} clients...")
        
        for client_doc in clients:
            client_id = client_doc.id
            client_data = client_doc.to_dict()
            client_name = client_data.get('name', client_id)
            
            # Look for the specific trade in this client's trades
            trades_ref = db.collection('clients').document(client_id).collection('trades')
            
            # Try to find by TradeNumber field
            trades_query = trades_ref.where('TradeNumber', '==', trade_number).limit(1)
            trades = trades_query.get()
            
            if trades:
                print(f"Found trade in client: {client_name} ({client_id})")
                trade_doc = trades[0]
                trade_data = trade_doc.to_dict()
                trade_data['id'] = trade_doc.id
                trade_data['client_id'] = client_id
                trade_data['client_name'] = client_name
                return trade_data
            
            # Also try searching all trades if field query didn't work
            all_trades = trades_ref.get()
            for trade_doc in all_trades:
                trade_data = trade_doc.to_dict()
                if str(trade_data.get('TradeNumber')) == str(trade_number):
                    print(f"Found trade in client: {client_name} ({client_id})")
                    trade_data['id'] = trade_doc.id
                    trade_data['client_id'] = client_id
                    trade_data['client_name'] = client_name
                    return trade_data
        
        print(f"Trade {trade_number} not found in any client!")
        return None
        
    except Exception as e:
        print(f"Error fetching trade data: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_client_settlement_rules(client_id: str):
    """
    Get settlement rules for a client directly from Firestore
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get settlement rules from Firestore
        rules_ref = db.collection('clients').document(client_id).collection('settlementRules')
        rules = rules_ref.order_by('priority').get()
        
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


async def get_client_bank_accounts(client_id: str):
    """
    Get bank accounts for a client directly from Firestore
    """
    try:
        db = get_cmek_firestore_client()
        
        # Get bank accounts from Firestore
        accounts_ref = db.collection('clients').document(client_id).collection('bankAccounts')
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


def find_matching_settlement_rules(trade_data, settlement_rules):
    """
    Find settlement rules that match the trade based on SettlementType
    
    Returns:
        - For Compensación: Single rule or None
        - For Entrega Física: Dictionary with 'inflow' and 'outflow' rules or None
    """
    if not settlement_rules:
        print("    No settlement rules available")
        return None
    
    trade_counterparty = trade_data.get('CounterpartyName', '').lower()
    trade_currency1 = trade_data.get('Currency1', '')
    trade_currency2 = trade_data.get('Currency2', '')
    trade_product = trade_data.get('ProductType', '')
    trade_direction = trade_data.get('Direction', '').upper()
    settlement_type = trade_data.get('SettlementType', '')
    settlement_currency = trade_data.get('SettlementCurrency', '')
    
    print("\n  Matching logic for settlement rules:")
    print(f"    Trade counterparty: {trade_counterparty}")
    print(f"    Trade currencies: {trade_currency1}/{trade_currency2}")
    print(f"    Trade product: {trade_product}")
    print(f"    Trade direction: {trade_direction}")
    print(f"    Settlement type: {settlement_type}")
    
    if settlement_type == "Compensación":
        print(f"    Settlement currency: {settlement_currency}")
        print(f"\n    Looking for single rule matching settlement currency: {settlement_currency}")
        
        # For Compensación, match based on settlement currency
        for i, rule in enumerate(settlement_rules, 1):
            rule_name = rule.get('name', 'Unnamed')
            rule_counterparty = rule.get('counterparty', '').lower()
            rule_currency = rule.get('cashflowCurrency', '')
            rule_product = rule.get('product', '')
            rule_active = rule.get('active', True)
            
            print(f"\n    Rule {i}: {rule_name}")
            print(f"      Active: {rule_active}")
            print(f"      Counterparty: {rule_counterparty or 'ANY'}")
            print(f"      Currency: {rule_currency or 'ANY'}")
            print(f"      Product: {rule_product or 'ANY'}")
            
            if not rule_active:
                print(f"      → SKIPPED (inactive)")
                continue
                
            # Check if this rule matches
            counterparty_match = (not rule_counterparty or 
                                 rule_counterparty in trade_counterparty or 
                                 trade_counterparty in rule_counterparty)
            
            # For Compensación, match the settlement currency
            currency_match = (rule_currency == settlement_currency)
            
            product_match = (not rule_product or rule_product == trade_product)
            
            # For Compensación, direction is no longer relevant
            
            print(f"      Counterparty match: {counterparty_match}")
            print(f"      Currency match: {currency_match} (looking for {settlement_currency})")
            print(f"      Product match: {product_match}")
            
            if counterparty_match and currency_match and product_match:
                print(f"      → MATCHED! Using this rule for Compensación")
                return rule
            else:
                print(f"      → No match")
    
    elif settlement_type == "Entrega Física":
        print(f"\n    Looking for TWO rules for physical delivery:")
        print(f"    - Inflow currency: {trade_currency1 if trade_direction == 'BUY' else trade_currency2}")
        print(f"    - Outflow currency: {trade_currency2 if trade_direction == 'BUY' else trade_currency1}")
        
        # Determine inflow and outflow currencies based on direction
        if trade_direction == 'BUY':
            inflow_currency = trade_currency1   # Buying Currency1
            outflow_currency = trade_currency2  # Selling Currency2
        else:  # SELL
            inflow_currency = trade_currency2   # Selling Currency1, receiving Currency2
            outflow_currency = trade_currency1  # Selling Currency1
        
        matched_rules = {
            'inflow': None,
            'outflow': None
        }
        
        # Find rules for both currencies
        for i, rule in enumerate(settlement_rules, 1):
            rule_name = rule.get('name', 'Unnamed')
            rule_counterparty = rule.get('counterparty', '').lower()
            rule_currency = rule.get('cashflowCurrency', '')
            rule_product = rule.get('product', '')
            rule_active = rule.get('active', True)
            
            print(f"\n    Rule {i}: {rule_name}")
            print(f"      Active: {rule_active}")
            print(f"      Counterparty: {rule_counterparty or 'ANY'}")
            print(f"      Currency: {rule_currency or 'ANY'}")
            print(f"      Product: {rule_product or 'ANY'}")
            
            if not rule_active:
                print(f"      → SKIPPED (inactive)")
                continue
                
            # Check if this rule matches
            counterparty_match = (not rule_counterparty or 
                                 rule_counterparty in trade_counterparty or 
                                 trade_counterparty in rule_counterparty)
            
            product_match = (not rule_product or rule_product == trade_product)
            
            # Check if it matches inflow currency
            if rule_currency == inflow_currency and not matched_rules['inflow']:
                if counterparty_match and product_match:
                    # Direction no longer checked - all rules are valid
                    print(f"      → MATCHED for INFLOW ({inflow_currency})!")
                    matched_rules['inflow'] = rule
                    continue
            
            # Check if it matches outflow currency
            if rule_currency == outflow_currency and not matched_rules['outflow']:
                if counterparty_match and product_match:
                    # Direction no longer checked - all rules are valid
                    print(f"      → MATCHED for OUTFLOW ({outflow_currency})!")
                    matched_rules['outflow'] = rule
                    continue
            
            print(f"      → No match")
        
        # Check if we found both rules
        if matched_rules['inflow'] and matched_rules['outflow']:
            print(f"\n    ✓ Found both rules for physical delivery:")
            print(f"      Inflow: {matched_rules['inflow'].get('name', 'Unnamed')}")
            print(f"      Outflow: {matched_rules['outflow'].get('name', 'Unnamed')}")
            return matched_rules
        else:
            missing = []
            if not matched_rules['inflow']:
                missing.append(f"inflow ({inflow_currency})")
            if not matched_rules['outflow']:
                missing.append(f"outflow ({outflow_currency})")
            print(f"\n    ✗ Missing rules for: {', '.join(missing)}")
            return None
    
    else:
        print(f"\n    Unknown settlement type: {settlement_type}")
        return None
    
    print("\n    No applicable settlement rules found")
    return None


def find_matching_bank_accounts(settlement_rules, bank_accounts):
    """
    Find bank accounts that match the settlement rules
    
    Args:
        settlement_rules: Either a single rule or dict with 'inflow' and 'outflow' rules
        bank_accounts: List of available bank accounts
    
    Returns:
        - For single rule: Single account or None
        - For dict of rules: Dict with 'inflow' and 'outflow' accounts or None
    """
    if not bank_accounts:
        print("    No bank accounts available")
        return None
    
    if not settlement_rules:
        print("    No settlement rules to match against")
        return None
    
    # Check if we have a dictionary of rules (Entrega Física) or single rule (Compensación)
    # For Entrega Física, we get a dict with 'inflow' and 'outflow' keys
    # For Compensación, we get a single rule dict (from Firestore)
    if isinstance(settlement_rules, dict) and 'inflow' in settlement_rules and 'outflow' in settlement_rules:
        # Physical delivery - need two accounts
        print(f"\n  Matching bank accounts for physical delivery:")
        
        matched_accounts = {
            'inflow': None,
            'outflow': None
        }
        
        # Find account for inflow rule
        if settlement_rules.get('inflow'):
            inflow_rule = settlement_rules['inflow']
            rule_account_id = inflow_rule.get('bankAccountId', '')
            rule_currency = inflow_rule.get('cashflowCurrency', '')
            
            print(f"\n    Looking for INFLOW account:")
            print(f"      Rule: {inflow_rule.get('name', 'Unnamed')}")
            print(f"      Account ID: {rule_account_id or 'Not specified'}")
            print(f"      Currency: {rule_currency}")
            
            for account in bank_accounts:
                account_id = account.get('id', '')
                account_name = account.get('accountName', 'Unnamed')
                account_currency = account.get('accountCurrency', '')
                
                # Check ID match first (highest priority)
                if rule_account_id and account_id == rule_account_id:
                    print(f"      → MATCHED by ID: {account_name}")
                    matched_accounts['inflow'] = account
                    break
                
                # Check currency match as secondary criteria
                if not rule_account_id and account_currency == rule_currency:
                    print(f"      → MATCHED by currency: {account_name}")
                    matched_accounts['inflow'] = account
                    break
            
            if not matched_accounts['inflow']:
                print(f"      → No matching account found for inflow")
        
        # Find account for outflow rule
        if settlement_rules.get('outflow'):
            outflow_rule = settlement_rules['outflow']
            rule_account_id = outflow_rule.get('bankAccountId', '')
            rule_currency = outflow_rule.get('cashflowCurrency', '')
            
            print(f"\n    Looking for OUTFLOW account:")
            print(f"      Rule: {outflow_rule.get('name', 'Unnamed')}")
            print(f"      Account ID: {rule_account_id or 'Not specified'}")
            print(f"      Currency: {rule_currency}")
            
            for account in bank_accounts:
                account_id = account.get('id', '')
                account_name = account.get('accountName', 'Unnamed')
                account_currency = account.get('accountCurrency', '')
                
                # Check ID match first (highest priority)
                if rule_account_id and account_id == rule_account_id:
                    print(f"      → MATCHED by ID: {account_name}")
                    matched_accounts['outflow'] = account
                    break
                
                # Check currency match as secondary criteria
                if not rule_account_id and account_currency == rule_currency:
                    print(f"      → MATCHED by currency: {account_name}")
                    matched_accounts['outflow'] = account
                    break
            
            if not matched_accounts['outflow']:
                print(f"      → No matching account found for outflow")
        
        # Check if we found both accounts
        if matched_accounts['inflow'] and matched_accounts['outflow']:
            print(f"\n    ✓ Found both accounts for physical delivery")
            return matched_accounts
        else:
            print(f"\n    ✗ Missing accounts for physical delivery")
            return None
    
    else:
        # Single rule (Compensación)
        rule_account_id = settlement_rules.get('bankAccountId', '')
        rule_currency = settlement_rules.get('cashflowCurrency', '')
        
        print(f"\n  Matching bank account for Compensación:")
        print(f"    Rule: {settlement_rules.get('name', 'Unnamed')}")
        print(f"    Looking for account ID: {rule_account_id or 'Not specified'}")
        print(f"    Settlement currency: {rule_currency}")
        print(f"\n    Checking {len(bank_accounts)} accounts:")
        
        # Try to find account
        for i, account in enumerate(bank_accounts, 1):
            account_id = account.get('id', '')
            account_name = account.get('accountName', 'Unnamed')
            account_currency = account.get('accountCurrency', '')
            account_bank = account.get('bankName', 'Unnamed')
            
            print(f"\n    Account {i}: {account_name}")
            print(f"      Bank: {account_bank}")
            print(f"      ID: {account_id}")
            print(f"      Currency: {account_currency}")
            
            # Check ID match first (highest priority)
            if rule_account_id and account_id == rule_account_id:
                print(f"      → MATCHED by ID! Using this account")
                return account
            
            # Check currency match as secondary criteria
            if not rule_account_id and account_currency == rule_currency:
                print(f"      → MATCHED by currency! Using this account")
                return account
            
            print(f"      → No match")
        
        print("\n    No matching bank account found")
        return None


async def test_specific_trade():
    """
    Main test function for trade 32013
    """
    print("=" * 80)
    print("Settlement Instructions Test for Trade 32013")
    print("=" * 80)
    
    # Fetch the specific trade
    print("\nFetching trade 32013 from database...")
    trade = await get_specific_trade("32013")
    
    if not trade:
        print("ERROR: Trade 32013 not found in database!")
        return
    
    print("\nTrade Details:")
    print("-" * 60)
    
    # Display trade information
    client_id = trade['client_id']
    client_name = trade['client_name']
    
    print(f"Client: {client_name}")
    print(f"Trade Number: {trade.get('TradeNumber', 'N/A')}")
    print(f"Counterparty: {trade.get('CounterpartyName', 'N/A')}")
    print(f"Product: {trade.get('ProductType', 'N/A')}")
    print(f"Direction: {trade.get('Direction', 'N/A')}")
    print(f"Currencies: {trade.get('Currency1', 'N/A')}/{trade.get('Currency2', 'N/A')}")
    print(f"Amount: {trade.get('QuantityCurrency1', 'N/A')} {trade.get('Currency1', '')}")
    print(f"Counter Amount: {trade.get('QuantityCurrency2', 'N/A')} {trade.get('Currency2', '')}")
    print(f"Rate: {trade.get('Price', 'N/A')}")
    print(f"Trade Date: {trade.get('TradeDate', 'N/A')}")
    print(f"Value Date: {trade.get('MaturityDate', 'N/A')}")
    
    # Get client's settlement rules and bank accounts
    print(f"\nFetching client configuration...")
    print("-" * 60)
    settlement_rules = await get_client_settlement_rules(client_id)
    bank_accounts = await get_client_bank_accounts(client_id)
    
    # Display settlement rules
    if settlement_rules:
        print("\n  Settlement Rules:")
        for rule in settlement_rules[:3]:  # Show first 3
            print(f"    - {rule.get('name', 'Unnamed')} (Priority: {rule.get('priority', 999)}, Active: {rule.get('active', False)})")
    
    # Display bank accounts  
    if bank_accounts:
        print("\n  Bank Accounts:")
        for account in bank_accounts[:3]:  # Show first 3
            print(f"    - {account.get('accountName', 'Unnamed')} ({account.get('accountCurrency', 'N/A')}, Active: {account.get('active', False)})")
    
    # Find matching rules and accounts
    print("\nMatching Settlement Configuration...")
    print("-" * 60)
    settlement_rules_matched = find_matching_settlement_rules(trade, settlement_rules)
    bank_accounts_matched = find_matching_bank_accounts(settlement_rules_matched, bank_accounts)
    
    # Prepare settlement data from matched rules and accounts
    settlement_data = None
    
    if bank_accounts_matched:
        # Check if we have a dictionary with inflow/outflow (physical delivery) or single account (compensación)
        if isinstance(bank_accounts_matched, dict) and 'inflow' in bank_accounts_matched:
            # Physical delivery - combine both accounts into settlement data
            print("\nSettlement Data Prepared (Physical Delivery - Two Accounts):")
            
            # Prepare inflow account data
            inflow_account = bank_accounts_matched.get('inflow')
            outflow_account = bank_accounts_matched.get('outflow')
            
            if inflow_account and outflow_account:
                settlement_data = {
                    # Inflow account details
                    'inflow_account_name': inflow_account.get('accountName', 'N/A'),
                    'inflow_account_number': inflow_account.get('accountNumber', 'N/A'),
                    'inflow_bank_name': inflow_account.get('bankName', 'N/A'),
                    'inflow_swift_code': inflow_account.get('swiftCode', 'N/A'),
                    'inflow_currency': inflow_account.get('accountCurrency', 'N/A'),
                    
                    # Outflow account details
                    'outflow_account_name': outflow_account.get('accountName', 'N/A'),
                    'outflow_account_number': outflow_account.get('accountNumber', 'N/A'),
                    'outflow_bank_name': outflow_account.get('bankName', 'N/A'),
                    'outflow_swift_code': outflow_account.get('swiftCode', 'N/A'),
                    'outflow_currency': outflow_account.get('accountCurrency', 'N/A'),
                    
                    # Common fields
                    'cutoff_time': '15:00 Santiago Time',
                    'special_instructions': 'Physical delivery settlement - two-way transfer',
                    
                    # For backward compatibility, also include single account fields using inflow as primary
                    'account_name': inflow_account.get('accountName', 'N/A'),
                    'account_number': inflow_account.get('accountNumber', 'N/A'),
                    'bank_name': inflow_account.get('bankName', 'N/A'),
                    'swift_code': inflow_account.get('swiftCode', 'N/A'),
                }
                
                print("  Inflow Account:")
                print(f"    Name: {settlement_data['inflow_account_name']}")
                print(f"    Number: {settlement_data['inflow_account_number']}")
                print(f"    Bank: {settlement_data['inflow_bank_name']}")
                print(f"    SWIFT: {settlement_data['inflow_swift_code']}")
                print(f"    Currency: {settlement_data['inflow_currency']}")
                
                print("  Outflow Account:")
                print(f"    Name: {settlement_data['outflow_account_name']}")
                print(f"    Number: {settlement_data['outflow_account_number']}")
                print(f"    Bank: {settlement_data['outflow_bank_name']}")
                print(f"    SWIFT: {settlement_data['outflow_swift_code']}")
                print(f"    Currency: {settlement_data['outflow_currency']}")
        else:
            # Single account (Compensación)
            print("\nSettlement Data Prepared (Compensación - Single Account):")
            settlement_data = {
                'account_name': bank_accounts_matched.get('accountName', 'N/A'),
                'account_number': bank_accounts_matched.get('accountNumber', 'N/A'),
                'bank_name': bank_accounts_matched.get('bankName', 'N/A'),
                'swift_code': bank_accounts_matched.get('swiftCode', 'N/A'),
                'cutoff_time': '15:00 Santiago Time',
                'special_instructions': settlement_rules_matched.get('specialInstructions', 'Standard settlement instructions apply.') if settlement_rules_matched else 'Standard settlement instructions apply.'
            }
            
            for key, value in settlement_data.items():
                print(f"  {key}: {value}")
    else:
        print("  WARNING: No matching settlement rules or accounts found")
    
    # Generate settlement instruction
    print("\nGenerating Settlement Instruction Document...")
    print("-" * 60)
    
    # Select template based on settlement type
    settlement_type = trade.get('SettlementType', '')
    if settlement_type == 'Compensación':
        template_name = 'Template Carta Instrucción Banco ABC (Compensación).docx'
    else:  # Entrega Física
        template_name = 'Template Carta Instrucción Banco ABC (Entrega Física).docx'
    
    print(f"  Using template: {template_name}")
    
    result = await settlement_instruction_service.generate_settlement_instruction(
        trade_data=trade,
        template_name=template_name,
        settlement_data=settlement_data
    )
    
    if result['success']:
        print("SUCCESS: Document generated!")
        print(f"  Path: {result['document_path']}")
        print(f"  Template: {result['template_used']}")
        print(f"  Variables populated: {result['variables_populated']}")
        
        filename = os.path.basename(result['document_path'])
        print(f"\nDocument saved as:")
        print(f"  backend/templates/generated/{filename}")
        print("\nOpen this document to verify the settlement instructions for trade 32013")
    else:
        print("ERROR: Document generation failed!")
        print(f"  Error: {result['error']}")
    
    print("\n" + "=" * 80)


async def main():
    """
    Main function
    """
    await test_specific_trade()


if __name__ == "__main__":
    asyncio.run(main())