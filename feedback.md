Compiled with problems:
×
ERROR in src/pages/admin/AdminDashboard.tsx:432:7
TS2345: Argument of type '{ active: true; priority: number; name: string; counterparty: string; cashflowCurrency: string; product: string; bankName: string; swiftCode: string; accountCurrency: string; accountNumber: string; }' is not assignable to parameter of type 'SetStateAction<Partial<SettlementRule>>'.
  Object literal may only specify known properties, and 'cashflowCurrency' does not exist in type 'SetStateAction<Partial<SettlementRule>>'.
    430 |       name: '',
    431 |       counterparty: '',
  > 432 |       cashflowCurrency: '',
        |       ^^^^^^^^^^^^^^^^^^^^
    433 |       product: '',
    434 |       bankName: '',
    435 |       swiftCode: '',
ERROR in src/pages/admin/AdminDashboard.tsx:449:22
TS2339: Property 'cashflowCurrency' does not exist on type 'SettlementRule'.
    447 |       return (
    448 |         existingRule.counterparty === rule.counterparty &&
  > 449 |         existingRule.cashflowCurrency === rule.cashflowCurrency &&
        |                      ^^^^^^^^^^^^^^^^
    450 |         existingRule.product === rule.product &&
    451 |         existingRule.bankName === rule.bankName &&
    452 |         existingRule.accountCurrency === rule.accountCurrency
ERROR in src/pages/admin/AdminDashboard.tsx:449:48
TS2339: Property 'cashflowCurrency' does not exist on type 'Partial<SettlementRule>'.
    447 |       return (
    448 |         existingRule.counterparty === rule.counterparty &&
  > 449 |         existingRule.cashflowCurrency === rule.cashflowCurrency &&
        |                                                ^^^^^^^^^^^^^^^^
    450 |         existingRule.product === rule.product &&
    451 |         existingRule.bankName === rule.bankName &&
    452 |         existingRule.accountCurrency === rule.accountCurrency
ERROR in src/pages/admin/AdminDashboard.tsx:451:22
TS2339: Property 'bankName' does not exist on type 'SettlementRule'.
    449 |         existingRule.cashflowCurrency === rule.cashflowCurrency &&
    450 |         existingRule.product === rule.product &&
  > 451 |         existingRule.bankName === rule.bankName &&
        |                      ^^^^^^^^
    452 |         existingRule.accountCurrency === rule.accountCurrency
    453 |       );
    454 |     });
ERROR in src/pages/admin/AdminDashboard.tsx:451:40
TS2339: Property 'bankName' does not exist on type 'Partial<SettlementRule>'.
    449 |         existingRule.cashflowCurrency === rule.cashflowCurrency &&
    450 |         existingRule.product === rule.product &&
  > 451 |         existingRule.bankName === rule.bankName &&
        |                                        ^^^^^^^^
    452 |         existingRule.accountCurrency === rule.accountCurrency
    453 |       );
    454 |     });
ERROR in src/pages/admin/AdminDashboard.tsx:452:22
TS2339: Property 'accountCurrency' does not exist on type 'SettlementRule'.
    450 |         existingRule.product === rule.product &&
    451 |         existingRule.bankName === rule.bankName &&
  > 452 |         existingRule.accountCurrency === rule.accountCurrency
        |                      ^^^^^^^^^^^^^^^
    453 |       );
    454 |     });
    455 |   };
ERROR in src/pages/admin/AdminDashboard.tsx:452:47
TS2339: Property 'accountCurrency' does not exist on type 'Partial<SettlementRule>'.
    450 |         existingRule.product === rule.product &&
    451 |         existingRule.bankName === rule.bankName &&
  > 452 |         existingRule.accountCurrency === rule.accountCurrency
        |                                               ^^^^^^^^^^^^^^^
    453 |       );
    454 |     });
    455 |   };
ERROR in src/pages/admin/AdminDashboard.tsx:1891:61
TS2339: Property 'cashflowCurrency' does not exist on type 'SettlementRule'.
    1889 |                           <div className="table-cell">{rule.name}</div>
    1890 |                           <div className="table-cell">{rule.counterparty || '-'}</div>
  > 1891 |                           <div className="table-cell">{rule.cashflowCurrency}</div>
         |                                                             ^^^^^^^^^^^^^^^^
    1892 |                           <div className="table-cell">{rule.product || '-'}</div>
    1893 |                           <div className="separator-cell"></div>
    1894 |                           <div className="table-cell">{rule.bankName}</div>
ERROR in src/pages/admin/AdminDashboard.tsx:1894:61
TS2339: Property 'bankName' does not exist on type 'SettlementRule'.
    1892 |                           <div className="table-cell">{rule.product || '-'}</div>
    1893 |                           <div className="separator-cell"></div>
  > 1894 |                           <div className="table-cell">{rule.bankName}</div>
         |                                                             ^^^^^^^^
    1895 |                           <div className="table-cell">{rule.accountNumber}</div>
    1896 |                           <div className="table-cell actions">
    1897 |                             <button className="edit-button" onClick={() => handleEditRule(rule)}>✏️</button>
ERROR in src/pages/admin/AdminDashboard.tsx:1895:61
TS2339: Property 'accountNumber' does not exist on type 'SettlementRule'.
    1893 |                           <div className="separator-cell"></div>
    1894 |                           <div className="table-cell">{rule.bankName}</div>
  > 1895 |                           <div className="table-cell">{rule.accountNumber}</div>
         |                                                             ^^^^^^^^^^^^^
    1896 |                           <div className="table-cell actions">
    1897 |                             <button className="edit-button" onClick={() => handleEditRule(rule)}>✏️</button>
    1898 |                             <button className="delete-button" onClick={() => handleDeleteRule(rule.id)}>🗑️</button>