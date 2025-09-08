"""
Bank utilities for ID to display name conversion and other bank-related functions
"""

def get_bank_display_name(bank_id: str) -> str:
    """
    Convert bank ID to user-friendly display name.
    
    Args:
        bank_id: Bank ID like 'banco-bci'
        
    Returns:
        Display name like 'Banco de Crédito e Inversiones'
    """
    if not bank_id:
        return bank_id
    
    # Bank ID to display name mapping
    bank_display_names = {
        'banco-abc': 'Banco ABC',
        'banco-bice': 'Banco BICE',
        'banco-btg-pactual': 'Banco BTG Pactual Chile',
        'banco-consorcio': 'Banco Consorcio',
        'banco-de-chile': 'Banco de Chile',
        'banco-bci': 'Banco de Crédito e Inversiones',
        'banco-estado': 'Banco del Estado de Chile',
        'banco-falabella': 'Banco Falabella',
        'banco-internacional': 'Banco Internacional',
        'banco-itau': 'Banco Itaú Chile',
        'banco-ripley': 'Banco Ripley',
        'banco-santander': 'Banco Santander Chile',
        'banco-security': 'Banco Security',
        'banco-hsbc': 'HSBC Bank Chile',
        'banco-scotiabank': 'Scotiabank Chile',
        'banco-tanner': 'Tanner Banco Digital'
    }
    
    return bank_display_names.get(bank_id.lower(), bank_id)


def get_bank_id_from_display_name(display_name: str) -> str:
    """
    Convert display name to bank ID (reverse lookup).
    
    Args:
        display_name: Display name like 'Banco de Crédito e Inversiones'
        
    Returns:
        Bank ID like 'banco-bci'
    """
    if not display_name:
        return display_name
    
    # Reverse mapping for display name to bank ID
    display_to_id = {
        'Banco ABC': 'banco-abc',
        'Banco BICE': 'banco-bice', 
        'Banco BTG Pactual Chile': 'banco-btg-pactual',
        'Banco Consorcio': 'banco-consorcio',
        'Banco de Chile': 'banco-de-chile',
        'Banco de Crédito e Inversiones': 'banco-bci',
        'Banco del Estado de Chile': 'banco-estado',
        'Banco Falabella': 'banco-falabella',
        'Banco Internacional': 'banco-internacional',
        'Banco Itaú Chile': 'banco-itau',
        'Banco Ripley': 'banco-ripley',
        'Banco Santander Chile': 'banco-santander',
        'Banco Security': 'banco-security',
        'HSBC Bank Chile': 'banco-hsbc',
        'Scotiabank Chile': 'banco-scotiabank',
        'Tanner Banco Digital': 'banco-tanner'
    }
    
    return display_to_id.get(display_name, display_name.lower().replace(' ', '-').replace('ó', 'o'))


def get_all_banks():
    """
    Get all banks as a list of {id, name} objects.
    
    Returns:
        List of bank objects with id and name fields
    """
    return [
        {'id': 'banco-abc', 'name': 'Banco ABC'},
        {'id': 'banco-bice', 'name': 'Banco BICE'},
        {'id': 'banco-btg-pactual', 'name': 'Banco BTG Pactual Chile'},
        {'id': 'banco-consorcio', 'name': 'Banco Consorcio'},
        {'id': 'banco-de-chile', 'name': 'Banco de Chile'},
        {'id': 'banco-bci', 'name': 'Banco de Crédito e Inversiones'},
        {'id': 'banco-estado', 'name': 'Banco del Estado de Chile'},
        {'id': 'banco-falabella', 'name': 'Banco Falabella'},
        {'id': 'banco-internacional', 'name': 'Banco Internacional'},
        {'id': 'banco-itau', 'name': 'Banco Itaú Chile'},
        {'id': 'banco-ripley', 'name': 'Banco Ripley'},
        {'id': 'banco-santander', 'name': 'Banco Santander Chile'},
        {'id': 'banco-security', 'name': 'Banco Security'},
        {'id': 'banco-hsbc', 'name': 'HSBC Bank Chile'},
        {'id': 'banco-scotiabank', 'name': 'Scotiabank Chile'},
        {'id': 'banco-tanner', 'name': 'Tanner Banco Digital'}
    ]