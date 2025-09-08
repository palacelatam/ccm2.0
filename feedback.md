2025-09-08 15:22:03,563 - services.settlement_instruction_service - INFO - ✅ Matched rule: Compra USD/CLP Forward Comp CLP for Compensación
2025-09-08 15:22:03,563 - api.routes.clients - INFO - Settlement data prepared with account: N/A / 2011234568
2025-09-08 15:22:03,564 - api.routes.clients - INFO - Generating document with bank_id=bci, segment_id=None
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO - 🔍 Starting settlement instruction generation:
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Bank ID: bci
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Client segment ID: None
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Settlement type: Compensación
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Product: Forward
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO - 🔍 Template search criteria:
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Bank ID: 'bci'
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Settlement type: 'Compensación'
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Product: 'Forward'
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO -    Client segment ID: 'None'
2025-09-08 15:22:03,564 - services.settlement_instruction_service - INFO - 🔍 Querying database: banks/bci/settlementInstructionLetters
2025-09-08 15:22:03,577 - services.settlement_instruction_service - ERROR - ❌ Bank document 'banks/bci' does not exist in database!
2025-09-08 15:22:03,577 - services.settlement_instruction_service - ERROR - ❌ No matching template found in database for bank_id='bci', settlement_type='Compensación', product='Forward'
2025-09-08 15:22:03,577 - api.routes.clients - ERROR - Document generation failed: ❌ No matching template found in database for bank_id='bci', settlement_type='Compensación', product='Forward'
2025-09-08 15:22:03,577 - api.routes.clients - ERROR - Error generating settlement instruction for client xyz-corp, trade 32010:
INFO:     None:0 - "POST /api/v1/clients/xyz-corp/settlement-instructions/generate HTTP/1.1" 500 Internal Server Error