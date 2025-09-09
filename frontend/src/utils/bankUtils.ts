/**
 * Bank utilities for ID to display name conversion and other bank-related functions
 */

/**
 * Convert bank ID to user-friendly display name.
 * 
 * @param bankId Bank ID like 'banco-bci'
 * @returns Display name like 'Banco de Crédito e Inversiones'
 */
export function getBankDisplayName(bankId: string): string {
  if (!bankId) {
    return bankId;
  }
  
  // Bank ID to display name mapping
  const bankDisplayNames: Record<string, string> = {
    'banco-abc': 'Banco ABC',
    'banco-bice': 'Banco BICE',
    'banco-btg-pactual': 'BTG Pactual',
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
  };
  
  return bankDisplayNames[bankId.toLowerCase()] || bankId;
}

/**
 * Convert display name to bank ID (reverse lookup).
 * 
 * @param displayName Display name like 'Banco de Crédito e Inversiones'
 * @returns Bank ID like 'banco-bci'
 */
export function getBankIdFromDisplayName(displayName: string): string {
  if (!displayName) {
    return displayName;
  }
  
  // Reverse mapping for display name to bank ID
  const displayToId: Record<string, string> = {
    'Banco ABC': 'banco-abc',
    'Banco BICE': 'banco-bice', 
    'BTG Pactual': 'banco-btg-pactual',
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
  };
  
  return displayToId[displayName] || displayName.toLowerCase().replace(' ', '-').replace('ó', 'o');
}

/**
 * Get all banks as a list of {id, name} objects.
 * 
 * @returns List of bank objects with id and name fields
 */
export function getAllBanks(): Array<{id: string, name: string}> {
  return [
    {id: 'banco-abc', name: 'Banco ABC'},
    {id: 'banco-bice', name: 'Banco BICE'},
    {id: 'banco-btg-pactual', name: 'BTG Pactual'},
    {id: 'banco-consorcio', name: 'Banco Consorcio'},
    {id: 'banco-de-chile', name: 'Banco de Chile'},
    {id: 'banco-bci', name: 'Banco de Crédito e Inversiones'},
    {id: 'banco-estado', name: 'Banco del Estado de Chile'},
    {id: 'banco-falabella', name: 'Banco Falabella'},
    {id: 'banco-internacional', name: 'Banco Internacional'},
    {id: 'banco-itau', name: 'Banco Itaú Chile'},
    {id: 'banco-ripley', name: 'Banco Ripley'},
    {id: 'banco-santander', name: 'Banco Santander Chile'},
    {id: 'banco-security', name: 'Banco Security'},
    {id: 'banco-hsbc', name: 'HSBC Bank Chile'},
    {id: 'banco-scotiabank', name: 'Scotiabank Chile'},
    {id: 'banco-tanner', name: 'Tanner Banco Digital'}
  ];
}