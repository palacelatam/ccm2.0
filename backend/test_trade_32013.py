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
    
    Uses the new settlement rule structure with cargarCurrency/abonarCurrency
    
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
    
    print("\n  Matching logic for settlement rules (NEW STRUCTURE):")
    print(f"    Trade counterparty: {trade_counterparty}")
    print(f"    Trade currencies: {trade_currency1}/{trade_currency2}")
    print(f"    Trade product: {trade_product}")
    print(f"    Trade direction: {trade_direction}")
    print(f"    Settlement type: {settlement_type}")
    
    if settlement_type == "Compensación":
        print(f"    Settlement currency: {settlement_currency}")
        print(f"\n    Looking for single rule with modalidad=compensacion and settlementCurrency={settlement_currency}")
        
        # For Compensación, match based on modalidad and settlementCurrency
        for i, rule in enumerate(settlement_rules, 1):
            rule_name = rule.get('name', 'Unnamed')
            rule_counterparty = rule.get('counterparty', '').lower()
            rule_product = rule.get('product', '')
            rule_modalidad = rule.get('modalidad', '')
            rule_settlement_currency = rule.get('settlementCurrency', '')
            rule_active = rule.get('active', True)
            
            print(f"\n    Rule {i}: {rule_name}")
            print(f"      Active: {rule_active}")
            
            # Skip inactive rules
            if not rule_active:
                print(f"      → SKIPPED (inactive rule)")
                continue
            print(f"      Counterparty: {rule_counterparty or 'ANY'}")
            print(f"      Product: {rule_product or 'ANY'}")
            print(f"      Modalidad: {rule_modalidad}")
            print(f"      Settlement Currency: {rule_settlement_currency or 'None'}")
            
            if not rule_active:
                print(f"      → SKIPPED (inactive)")
                continue
                
            # Check if this rule matches
            counterparty_match = (not rule_counterparty or 
                                 rule_counterparty in trade_counterparty or 
                                 trade_counterparty in rule_counterparty)
            
            product_match = (not rule_product or rule_product == trade_product)
            modalidad_match = (rule_modalidad == 'compensacion')
            currency_match = (rule_settlement_currency == settlement_currency)
            
            print(f"      Counterparty match: {counterparty_match}")
            print(f"      Product match: {product_match}")
            print(f"      Modalidad match: {modalidad_match}")
            print(f"      Settlement currency match: {currency_match}")
            
            if counterparty_match and product_match and modalidad_match and currency_match:
                print(f"      → MATCHED! Using this rule for Compensación")
                return rule
            else:
                print(f"      → No match")
    
    elif settlement_type == "Entrega Física":
        print(f"\n    Looking for ONE rule with modalidad=entregaFisica that matches currencies:")
        
        # Determine what we're paying (cargar) and receiving (abonar) based on direction
        if trade_direction == 'BUY':
            # Buy USD/CLP means: pay CLP (cargar), receive USD (abonar)
            pay_currency = trade_currency2    # Paying CLP
            receive_currency = trade_currency1  # Receiving USD
        else:  # SELL
            # Sell USD/CLP means: pay USD (cargar), receive CLP (abonar)
            pay_currency = trade_currency1    # Paying USD
            receive_currency = trade_currency2  # Receiving CLP
        
        print(f"    - Pay currency (cargar): {pay_currency}")
        print(f"    - Receive currency (abonar): {receive_currency}")
        
        # Find a single rule that matches both currencies
        for i, rule in enumerate(settlement_rules, 1):
            rule_name = rule.get('name', 'Unnamed')
            rule_counterparty = rule.get('counterparty', '').lower()
            rule_product = rule.get('product', '')
            rule_modalidad = rule.get('modalidad', '')
            rule_cargar_currency = rule.get('cargarCurrency', '')
            rule_abonar_currency = rule.get('abonarCurrency', '')
            rule_active = rule.get('active', True)
            
            print(f"\n    Rule {i}: {rule_name}")
            print(f"      Active: {rule_active}")
            
            # Skip inactive rules
            if not rule_active:
                print(f"      → SKIPPED (inactive rule)")
                continue
            print(f"      Counterparty: {rule_counterparty or 'ANY'}")
            print(f"      Product: {rule_product or 'ANY'}")
            print(f"      Modalidad: {rule_modalidad}")
            print(f"      Cargar Currency: {rule_cargar_currency or 'None'}")
            print(f"      Abonar Currency: {rule_abonar_currency or 'None'}")
            
            if not rule_active:
                print(f"      → SKIPPED (inactive)")
                continue
                
            # Check if this rule matches
            counterparty_match = (not rule_counterparty or 
                                 rule_counterparty in trade_counterparty or 
                                 trade_counterparty in rule_counterparty)
            
            product_match = (not rule_product or rule_product == trade_product)
            modalidad_match = (rule_modalidad == 'entregaFisica')
            cargar_match = (rule_cargar_currency == pay_currency)
            abonar_match = (rule_abonar_currency == receive_currency)
            
            print(f"      Counterparty match: {counterparty_match}")
            print(f"      Product match: {product_match}")
            print(f"      Modalidad match: {modalidad_match}")
            print(f"      Cargar currency match: {cargar_match} (need {pay_currency})")
            print(f"      Abonar currency match: {abonar_match} (need {receive_currency})")
            
            if (counterparty_match and product_match and modalidad_match and 
                cargar_match and abonar_match):
                print(f"      → MATCHED! Using this rule for Entrega Física")
                return {
                    'matched_rule': rule,
                    'pay_currency': pay_currency,
                    'receive_currency': receive_currency
                }
            else:
                print(f"      → No match")
        
        print(f"\n    ✗ No rule found for physical delivery ({trade_direction} {trade_currency1}/{trade_currency2})")
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
        settlement_rules: Either a single rule dict or dict with matched_rule for Entrega Física
        bank_accounts: List of available bank accounts
    
    Returns:
        - For Compensación: Single account or None
        - For Entrega Física: Dict with 'cargar' and 'abonar' accounts or None
    """
    if not bank_accounts:
        print("    No bank accounts available")
        return None
    
    if not settlement_rules:
        print("    No settlement rules to match against")
        return None
    
    # Check if we have Entrega Física result (dict with matched_rule) or Compensación (single rule)
    if isinstance(settlement_rules, dict) and 'matched_rule' in settlement_rules:
        # Physical delivery - need two accounts based on cargar/abonar from the rule
        rule = settlement_rules['matched_rule']
        pay_currency = settlement_rules['pay_currency']
        receive_currency = settlement_rules['receive_currency']
        
        print(f"\n  Matching bank accounts for physical delivery:")
        print(f"    Rule: {rule.get('name', 'Unnamed')}")
        print(f"    Pay currency (cargar): {pay_currency}")
        print(f"    Receive currency (abonar): {receive_currency}")
        
        matched_accounts = {
            'cargar': None,  # Account for paying (outflow)
            'abonar': None   # Account for receiving (inflow)
        }
        
        # Find account for cargar (pay/outflow) - look for cargarBankName and cargarAccountNumber
        cargar_bank_name = rule.get('cargarBankName', '')
        cargar_account_number = rule.get('cargarAccountNumber', '')
        
        print(f"\n    Looking for CARGAR account (pay {pay_currency}):")
        print(f"      Bank: {cargar_bank_name or 'Not specified'}")
        print(f"      Account: {cargar_account_number or 'Not specified'}")
        
        for account in bank_accounts:
            account_name = account.get('accountName', 'Unnamed')
            account_bank = account.get('bankName', '')
            account_number = account.get('accountNumber', '')
            account_currency = account.get('accountCurrency', '')
            
            # Check bank name and account number match
            bank_match = (cargar_bank_name and account_bank == cargar_bank_name)
            account_match = (cargar_account_number and account_number == cargar_account_number)
            currency_match = (account_currency == pay_currency)
            
            if bank_match and account_match:
                print(f"      → MATCHED by bank & account: {account_name}")
                matched_accounts['cargar'] = account
                break
            elif currency_match and not cargar_bank_name:
                print(f"      → MATCHED by currency: {account_name}")
                matched_accounts['cargar'] = account
                break
        
        if not matched_accounts['cargar']:
            print(f"      → No matching account found for cargar ({pay_currency})")
        
        # Find account for abonar (receive/inflow) - look for abonarBankName and abonarAccountNumber
        abonar_bank_name = rule.get('abonarBankName', '')
        abonar_account_number = rule.get('abonarAccountNumber', '')
        
        print(f"\n    Looking for ABONAR account (receive {receive_currency}):")
        print(f"      Bank: {abonar_bank_name or 'Not specified'}")
        print(f"      Account: {abonar_account_number or 'Not specified'}")
        
        for account in bank_accounts:
            account_name = account.get('accountName', 'Unnamed')
            account_bank = account.get('bankName', '')
            account_number = account.get('accountNumber', '')
            account_currency = account.get('accountCurrency', '')
            
            # Check bank name and account number match
            bank_match = (abonar_bank_name and account_bank == abonar_bank_name)
            account_match = (abonar_account_number and account_number == abonar_account_number)
            currency_match = (account_currency == receive_currency)
            
            if bank_match and account_match:
                print(f"      → MATCHED by bank & account: {account_name}")
                matched_accounts['abonar'] = account
                break
            elif currency_match and not abonar_bank_name:
                print(f"      → MATCHED by currency: {account_name}")
                matched_accounts['abonar'] = account
                break
        
        if not matched_accounts['abonar']:
            print(f"      → No matching account found for abonar ({receive_currency})")
        
        # Check if we found both accounts
        if matched_accounts['cargar'] and matched_accounts['abonar']:
            print(f"\n    ✓ Found both accounts for physical delivery")
            return matched_accounts
        else:
            print(f"\n    ✗ Missing accounts for physical delivery")
            return None
    
    else:
        # Single rule (Compensación)
        settlement_currency = settlement_rules.get('settlementCurrency', '')
        
        print(f"\n  Matching bank account for Compensación:")
        print(f"    Rule: {settlement_rules.get('name', 'Unnamed')}")
        print(f"    Settlement currency: {settlement_currency}")
        print(f"\n    Checking {len(bank_accounts)} accounts:")
        
        # For Compensación, we need an account that matches the settlement currency
        for i, account in enumerate(bank_accounts, 1):
            account_name = account.get('accountName', 'Unnamed')
            account_currency = account.get('accountCurrency', '')
            account_bank = account.get('bankName', 'Unnamed')
            account_active = account.get('active', True)
            
            print(f"\n    Account {i}: {account_name}")
            print(f"      Bank: {account_bank}")
            print(f"      Currency: {account_currency}")
            print(f"      Active: {account_active}")
            
            # Check currency match and account is active
            if account_currency == settlement_currency and account_active:
                print(f"      → MATCHED by settlement currency! Using this account")
                return account
            elif account_currency == settlement_currency and not account_active:
                print(f"      → Currency matches but account is inactive")
            else:
                print(f"      → No match (need {settlement_currency})")
        
        print("\n    No matching active bank account found for settlement currency")
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
    
    # Debug: Show what we got from settlement rule matching
    print(f"\n  DEBUG: Settlement rules matching result:")
    if settlement_rules_matched:
        print(f"    Type: {type(settlement_rules_matched)}")
        if isinstance(settlement_rules_matched, dict):
            for key, value in settlement_rules_matched.items():
                if key == 'matched_rule' and isinstance(value, dict):
                    print(f"    {key}: (dict with {len(value)} keys)")
                    print(f"      centralBankTradeCode: {value.get('centralBankTradeCode', 'NOT FOUND')}")
                else:
                    print(f"    {key}: {value}")
        else:
            print(f"    Data: {settlement_rules_matched}")
            if hasattr(settlement_rules_matched, 'get'):
                print(f"    centralBankTradeCode: {settlement_rules_matched.get('centralBankTradeCode', 'NOT FOUND')}")
    else:
        print(f"    Result: None")
    
    # Check if settlement rules were found
    if not settlement_rules_matched:
        print("❌ ERROR: No applicable settlement rules found for this trade!")
        print("   Please check the settlement rules configuration for this client.")
        print("   Trade details:")
        print(f"     Counterparty: {trade.get('CounterpartyName', 'N/A')}")
        print(f"     Product: {trade.get('Product', 'N/A')}")
        print(f"     Currencies: {trade.get('Currency1', 'N/A')}/{trade.get('Currency2', 'N/A')}")
        print(f"     Direction: {trade.get('Direction', 'N/A')}")
        print(f"     Settlement Type: {trade.get('SettlementType', 'N/A')}")
        return
    
    bank_accounts_matched = find_matching_bank_accounts(settlement_rules_matched, bank_accounts)
    
    # Check if bank accounts were found
    if not bank_accounts_matched:
        print("❌ ERROR: No applicable bank accounts found for the matched settlement rule!")
        print("   The settlement rule was found but no matching bank accounts could be located.")
        print("   Please check the bank account configuration for this client.")
        return
    
    # Prepare settlement data from matched rules and accounts
    settlement_data = None
    
    if bank_accounts_matched:
        # Check if we have a dictionary with cargar/abonar (physical delivery) or single account (compensación)
        if isinstance(bank_accounts_matched, dict) and 'cargar' in bank_accounts_matched:
            # Physical delivery - combine both accounts into settlement data
            print("\nSettlement Data Prepared (Physical Delivery - Two Accounts):")
            
            # Prepare cargar and abonar account data
            cargar_account = bank_accounts_matched.get('cargar')  # Pay/outflow account
            abonar_account = bank_accounts_matched.get('abonar')  # Receive/inflow account
            
            if cargar_account and abonar_account:
                settlement_data = {
                    # Cargar (pay/outflow) account details
                    'cargar_account_name': cargar_account.get('accountName', 'N/A'),
                    'cargar_account_number': cargar_account.get('accountNumber', 'N/A'),
                    'cargar_bank_name': cargar_account.get('bankName', 'N/A'),
                    'cargar_swift_code': cargar_account.get('swiftCode', 'N/A'),
                    'cargar_currency': cargar_account.get('accountCurrency', 'N/A'),
                    
                    # Abonar (receive/inflow) account details
                    'abonar_account_name': abonar_account.get('accountName', 'N/A'),
                    'abonar_account_number': abonar_account.get('accountNumber', 'N/A'),
                    'abonar_bank_name': abonar_account.get('bankName', 'N/A'),
                    'abonar_swift_code': abonar_account.get('swiftCode', 'N/A'),
                    'abonar_currency': abonar_account.get('accountCurrency', 'N/A'),
                    
                    # Common fields
                    'cutoff_time': '15:00 Santiago Time',
                    'special_instructions': 'Physical delivery settlement - two-way transfer',
                    'central_bank_trade_code': settlement_rules_matched.get('matched_rule', {}).get('centralBankTradeCode', 'N/A') if settlement_rules_matched else 'N/A',
                    
                    # For backward compatibility, also include single account fields using abonar as primary (receiving)
                    'account_name': abonar_account.get('accountName', 'N/A'),
                    'account_number': abonar_account.get('accountNumber', 'N/A'),
                    'bank_name': abonar_account.get('bankName', 'N/A'),
                    'swift_code': abonar_account.get('swiftCode', 'N/A'),
                }
                
                print("  Cargar Account (Pay/Outflow):")
                print(f"    Name: {settlement_data['cargar_account_name']}")
                print(f"    Number: {settlement_data['cargar_account_number']}")
                print(f"    Bank: {settlement_data['cargar_bank_name']}")
                print(f"    SWIFT: {settlement_data['cargar_swift_code']}")
                print(f"    Currency: {settlement_data['cargar_currency']}")
                
                print("  Abonar Account (Receive/Inflow):")
                print(f"    Name: {settlement_data['abonar_account_name']}")
                print(f"    Number: {settlement_data['abonar_account_number']}")
                print(f"    Bank: {settlement_data['abonar_bank_name']}")
                print(f"    SWIFT: {settlement_data['abonar_swift_code']}")
                print(f"    Currency: {settlement_data['abonar_currency']}")
        else:
            # Single account (Compensación)
            print("\nSettlement Data Prepared (Compensación - Single Account):")
            settlement_data = {
                'account_name': bank_accounts_matched.get('accountName', 'N/A'),
                'account_number': bank_accounts_matched.get('accountNumber', 'N/A'),
                'bank_name': bank_accounts_matched.get('bankName', 'N/A'),
                'swift_code': bank_accounts_matched.get('swiftCode', 'N/A'),
                'cutoff_time': '15:00 Santiago Time',
                'special_instructions': settlement_rules_matched.get('specialInstructions', 'Standard settlement instructions apply.') if settlement_rules_matched else 'Standard settlement instructions apply.',
                'central_bank_trade_code': settlement_rules_matched.get('centralBankTradeCode', 'N/A') if settlement_rules_matched else 'N/A'
            }
            
            for key, value in settlement_data.items():
                print(f"  {key}: {value}")
    else:
        print("  WARNING: No matching settlement rules or accounts found")
    
    # Generate settlement instruction
    print("\nGenerating Settlement Instruction Document...")
    print("-" * 60)
    
    # Get client segment ID from trade data if available
    client_segment_id = trade.get('client_segment_id')
    counterparty = trade.get('CounterpartyName', '')
    
    # Map counterparty to bank ID - "Banco ABC" -> "banco-abc"
    if 'banco abc' in counterparty.lower():
        bank_id = "banco-abc"
    else:
        # Default mapping - convert to lowercase and replace spaces with hyphens
        bank_id = counterparty.lower().replace(' ', '-').replace('ó', 'o')
    
    # Get the correct product field
    product = trade.get('ProductType', trade.get('Product', 'N/A'))
    
    print(f"  Counterparty: {counterparty}")
    print(f"  Bank ID (mapped): {bank_id}")
    print(f"  Client segment ID: {client_segment_id or 'None'}")
    print(f"  Settlement type: {trade.get('SettlementType', 'N/A')}")
    print(f"  Product: {product}")
    print(f"  System will query database for best matching template...")
    
    # Ensure trade_data has the Product field for template matching
    trade_data_with_product = trade.copy()
    if 'Product' not in trade_data_with_product and 'ProductType' in trade_data_with_product:
        trade_data_with_product['Product'] = trade_data_with_product['ProductType']
    
    # Debug: Show exactly what data we're sending to the template population
    print(f"\n  DEBUG: Template Population Data:")
    print(f"    Trade Data Keys: {list(trade_data_with_product.keys())}")
    if settlement_data:
        print(f"    Settlement Data Keys: {list(settlement_data.keys())}")
        print(f"    Settlement Data Values:")
        for key, value in settlement_data.items():
            print(f"      {key}: {value}")
    else:
        print(f"    Settlement Data: None")
    
    # Generate the document with error handling
    try:
        result = await settlement_instruction_service.generate_settlement_instruction(
            trade_data=trade_data_with_product,
            bank_id=bank_id,
            client_segment_id=client_segment_id,
            settlement_data=settlement_data
        )
        
        if not result['success']:
            print("❌ ERROR: Failed to generate settlement instruction document!")
            print(f"   Error details: {result.get('error', 'Unknown error')}")
            if 'No matching template found' in result.get('error', ''):
                print("   This means no suitable document template exists in the database for:")
                print(f"     Bank: {bank_id}")
                print(f"     Settlement Type: {trade_data_with_product.get('SettlementType', 'N/A')}")
                print(f"     Product: {product}")
                print("   Please check the settlement instruction templates configuration.")
            print("=" * 80)
            return
            
    except Exception as e:
        print("❌ ERROR: Exception occurred during document generation!")
        print(f"   Exception: {str(e)}")
        print("=" * 80)
        return
    
    if result['success']:
        print("SUCCESS: Document generated!")
        print(f"  Path: {result['document_path']}")
        print(f"  Template: {result['template_used']}")
        print(f"  Template ID: {result.get('template_id', 'N/A')}")
        print(f"  Match score: {result.get('match_score', 'N/A')}")
        print(f"  Variables populated: {result['variables_populated']}")
        
        # Debug: Show what variables were actually used
        if 'debug_variables' in result:
            print(f"\n  DEBUG: All Template Variables Used:")
            debug_vars = result['debug_variables']
            for key in sorted(debug_vars.keys()):
                value = debug_vars[key]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"    {key}: {value}")
        
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