Compiled with problems:
×
ERROR in src/components/grids/ConfirmationsGrid.tsx:125:34
TS18048: 'result.matched_trade_numbers.length' is possibly 'undefined'.
    123 |       // Use the enhanced data from the backend response
    124 |       const counterpartyName = result.counterparty_name || 'Unknown';
  > 125 |       const clientTradeNumbers = result.matched_trade_numbers?.length > 0 ? 
        |                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    126 |         ` (${result.matched_trade_numbers.join(', ')})` : '';
    127 |       
    128 |       const message = `Successfully processed email file from ${counterpartyName} with ${tradesCount} trades extracted and ${matchesCount} matches found${clientTradeNumbers}`;
ERROR in src/components/grids/ConfirmationsGrid.tsx:126:14
TS18048: 'result.matched_trade_numbers' is possibly 'undefined'.
    124 |       const counterpartyName = result.counterparty_name || 'Unknown';
    125 |       const clientTradeNumbers = result.matched_trade_numbers?.length > 0 ? 
  > 126 |         ` (${result.matched_trade_numbers.join(', ')})` : '';
        |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    127 |       
    128 |       const message = `Successfully processed email file from ${counterpartyName} with ${tradesCount} trades extracted and ${matchesCount} matches found${clientTradeNumbers}`;
    129 |       showToastNotification(message, 'success');