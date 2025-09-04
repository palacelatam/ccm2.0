Compiled with problems:
×
ERROR in src/pages/admin/AdminDashboard.tsx:2087:31
TS2322: Type 'string | false | undefined' is not assignable to type 'boolean | undefined'.
  Type 'string' is not assignable to type 'boolean | undefined'.
    2085 |                               value={ruleForm.cargarCurrency || ''}
    2086 |                               onChange={(e) => updateRuleForm('cargarCurrency', e.target.value)}
  > 2087 |                               disabled={ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency}
         |                               ^^^^^^^^
    2088 |                             >
    2089 |                               <option value="">{t('admin.settlement.placeholders.currency')}</option>
    2090 |                               {ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency ? (
ERROR in src/pages/admin/AdminDashboard.tsx:2258:31
TS2322: Type 'string | false | undefined' is not assignable to type 'boolean | undefined'.
    2256 |                               value={ruleForm.abonarCurrency || ''}
    2257 |                               onChange={(e) => updateRuleForm('abonarCurrency', e.target.value)}
  > 2258 |                               disabled={ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency}
         |                               ^^^^^^^^
    2259 |                             >
    2260 |                               <option value="">{t('admin.settlement.placeholders.currency')}</option>
    2261 |                               {ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency ? (