Compiled with problems:
×
ERROR in src/components/settings/SettlementRulesSettings.tsx:94:25
TS2551: Property 'centralBankTradeCode' does not exist on type 'SettlementRule'. Did you mean 'centralBankTradeCodeIn'?
    92 |                     <span className="detail-value">{rule.bankAccountId}</span>
    93 |                   </div>
  > 94 |                   {rule.centralBankTradeCode && (
       |                         ^^^^^^^^^^^^^^^^^^^^
    95 |                     <div className="detail-row">
    96 |                       <span className="detail-label">Central Bank Code:</span>
    97 |                       <span className="detail-value">{rule.centralBankTradeCode}</span>
ERROR in src/components/settings/SettlementRulesSettings.tsx:97:60
TS2551: Property 'centralBankTradeCode' does not exist on type 'SettlementRule'. Did you mean 'centralBankTradeCodeIn'?
     95 |                     <div className="detail-row">
     96 |                       <span className="detail-label">Central Bank Code:</span>
  >  97 |                       <span className="detail-value">{rule.centralBankTradeCode}</span>
        |                                                            ^^^^^^^^^^^^^^^^^^^^
     98 |                     </div>
     99 |                   )}
    100 |                 </div>