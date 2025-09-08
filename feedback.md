2025-09-08 17:51:13,196 - api.routes.clients - INFO - Settlement instruction generation requested for client xyz-corp, trade 32019
2025-09-08 17:51:13,242 - api.routes.clients - INFO - Trade found: 32019 - Banco ABC
2025-09-08 17:51:13,242 - api.routes.clients - INFO - Trade details: Product=Forward, Direction=Buy, Currencies=USD/CLP
2025-09-08 17:51:13,243 - api.routes.clients - INFO - Fetching settlement rules and bank accounts...
2025-09-08 17:51:13,286 - api.routes.clients - INFO - Found 8 settlement rules and 5 bank accounts
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO - ✅ Resolved counterparty 'Banco ABC' → 'banco-abc' via client mapping
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO - 🔍 Matching settlement rules - Type: Compensación, Currency: CLP
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Counterparty: 'banco-abc'
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Product: 'Forward'
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Direction: 'BUY'
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Currency1: 'USD'
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Currency2: 'CLP'
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Available rules: 8
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Rule 1/8: name='Compra USD/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Rule 2/8: name='Compra EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Rule 3/8: name='Compra EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,302 - services.settlement_instruction_service - INFO -    Rule 4/8: name='Venta USD/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -    Rule 5/8: name='Venta EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -    Rule 6/8: name='Venta EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -    Rule 7/8: name='Bci Compra USD/CLP Forward Comp CLP', counterparty='banco-bci', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -    Rule 8/8: name='Banco ABC Compra Divisas Forward USD/CLP Compensación', counterparty='banco-estado', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Compra USD/CLP Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/CLP Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/USD Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Venta USD/CLP Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/CLP Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/USD Spot': counterparty=True ( in banco-abc), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Bci Compra USD/CLP Forward Comp CLP': counterparty=False (banco-bci in banco-abc), product=True (Forward in Forward), modalidad=True (compensacion == Compensación), currency=True (CLP == CLP)
2025-09-08 17:51:13,304 - services.settlement_instruction_service - INFO -       Rule 'Banco ABC Compra Divisas Forward USD/CLP Compensación': counterparty=False (banco-estado in banco-abc), product=True (Forward in Forward), modalidad=True (compensacion == Compensación), currency=True (CLP == CLP)
2025-09-08 17:51:13,304 - api.routes.clients - ERROR - No matching settlement rules found for trade 32019
2025-09-08 17:51:13,304 - api.routes.clients - ERROR - Error generating settlement instruction for client xyz-corp, trade 32019:
INFO:     None:0 - "POST /api/v1/clients/xyz-corp/settlement-instructions/generate HTTP/1.1" 500 Internal Server Error