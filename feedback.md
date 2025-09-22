Compiled with problems:
×
ERROR in src/pages/client/Reports.tsx:479:46
TS2339: Property 'emailsSent' does not exist on type '{ total: number; fullyMatched: number; unmatched: number; portal: number; confirmationOK: number; differences: number; matchRate: string; confirmationEmailsSent: number; disputeEmailsSent: number; settlementsSent: number; }'.
    477 |         </div>
    478 |         <div className="summary-card">
  > 479 |           <div className="card-value">{stats.emailsSent}</div>
        |                                              ^^^^^^^^^^
    480 |           <div className="card-label">{t('reports.emailsSent', 'Emails Sent')}</div>
    481 |         </div>
    482 |         <div className="summary-card">
ERROR in src/pages/client/Reports.tsx:522:52
TS2552: Cannot find name 'getStatusBadgeClass'. Did you mean 'getMatchStatusBadgeClass'?
    520 |                 </div>
    521 |                 <div className="table-cell">
  > 522 |                   <span className={`status-badge ${getStatusBadgeClass(trade['Match Status'])}`}>
        |                                                    ^^^^^^^^^^^^^^^^^^^
    523 |                     {trade['Match Status']}
    524 |                   </span>
    525 |                 </div>
ERROR in src/pages/client/Reports.tsx:550:53
TS7053: Element implicitly has an 'any' type because expression of type '"Fields Match"' can't be used to index type 'ReportData'.
  Property 'Fields Match' does not exist on type 'ReportData'.
    548 |                   <div className="detail-row">
    549 |                     <span className="detail-label">Fields Match:</span>
  > 550 |                     <span className="detail-value">{trade['Fields Match']}</span>
        |                                                     ^^^^^^^^^^^^^^^^^^^^^
    551 |                   </div>
    552 |                   <div className="detail-row">
    553 |                     <span className="detail-label">Email Sent:</span>
ERROR in src/pages/client/Reports.tsx:554:53
TS7053: Element implicitly has an 'any' type because expression of type '"Email Sent"' can't be used to index type 'ReportData'.
  Property 'Email Sent' does not exist on type 'ReportData'.
    552 |                   <div className="detail-row">
    553 |                     <span className="detail-label">Email Sent:</span>
  > 554 |                     <span className="detail-value">{trade['Email Sent']}</span>
        |                                                     ^^^^^^^^^^^^^^^^^^^
    555 |                   </div>
    556 |                   <div className="detail-row">
    557 |                     <span className="detail-label">Settlement Instruction Sent:</span>
ERROR in src/pages/client/Reports.tsx:558:53
TS7053: Element implicitly has an 'any' type because expression of type '"Settlement Sent"' can't be used to index type 'ReportData'.
  Property 'Settlement Sent' does not exist on type 'ReportData'.
    556 |                   <div className="detail-row">
    557 |                     <span className="detail-label">Settlement Instruction Sent:</span>
  > 558 |                     <span className="detail-value">{trade['Settlement Sent']}</span>
        |                                                     ^^^^^^^^^^^^^^^^^^^^^^^^
    559 |                   </div>
    560 |                   <div className="detail-row">
    561 |                     <span className="detail-label">Confirmation Source:</span>
ERROR in src/pages/client/Reports.tsx:562:53
TS7053: Element implicitly has an 'any' type because expression of type '"Confirmation Source"' can't be used to index type 'ReportData'.
  Property 'Confirmation Source' does not exist on type 'ReportData'.
    560 |                   <div className="detail-row">
    561 |                     <span className="detail-label">Confirmation Source:</span>
  > 562 |                     <span className="detail-value">{trade['Confirmation Source']}</span>
        |                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    563 |                   </div>
    564 |                 </div>
    565 |               )}