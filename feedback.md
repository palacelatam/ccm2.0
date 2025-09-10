2025-09-10 17:10:40,876 - api.routes.clients - INFO - Settlement instruction generation requested for client xyz-corp, trade 32018
2025-09-10 17:10:40,941 - api.routes.clients - INFO - Trade found: 32018 - Banco ABC
2025-09-10 17:10:40,941 - api.routes.clients - INFO - Trade details: Product=Spot, Direction=Sell, Currencies=USD/CLP
2025-09-10 17:10:40,941 - api.routes.clients - INFO - Fetching settlement rules and bank accounts...
2025-09-10 17:10:40,995 - api.routes.clients - INFO - Found 8 settlement rules and 5 bank accounts
2025-09-10 17:10:41,016 - services.settlement_instruction_service - INFO - ✅ Resolved counterparty 'Banco ABC' → 'banco-abc' via client mapping
2025-09-10 17:10:41,019 - services.settlement_instruction_service - INFO - 🔍 Matching settlement rules - Type: Entrega Física, Currency: N/A
2025-09-10 17:10:41,021 - services.settlement_instruction_service - INFO -    Counterparty: 'banco-abc'
2025-09-10 17:10:41,021 - services.settlement_instruction_service - INFO -    Product: 'Spot'
2025-09-10 17:10:41,023 - services.settlement_instruction_service - INFO -    Direction: 'SELL'
2025-09-10 17:10:41,023 - services.settlement_instruction_service - INFO -    Currency1: 'USD'
2025-09-10 17:10:41,023 - services.settlement_instruction_service - INFO -    Currency2: 'CLP'
2025-09-10 17:10:41,023 - services.settlement_instruction_service - INFO -    Available rules: 8
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 1/8: name='Compra USD/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 2/8: name='Compra EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 3/8: name='Compra EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 4/8: name='Venta EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 5/8: name='Venta EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 6/8: name='Venta USD/CLP Spot', counterparty='banco-abc', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 17:10:41,025 - services.settlement_instruction_service - INFO -    Rule 7/8: name='Bci Compra USD/CLP Forward Comp CLP', counterparty='banco-bci', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -    Rule 8/8: name='Banco ABC Compra Divisas Forward USD/CLP Compensación', counterparty='banco-abc', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Compra USD/CLP Spot' (Entrega Física): counterparty=True ('' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=False (cargar='CLP'=='USD' AND abonar='USD'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/CLP Spot' (Entrega Física): counterparty=True ('' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=False (cargar='CLP'=='USD' AND abonar='EUR'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/USD Spot' (Entrega Física): counterparty=True ('' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=False (cargar='USD'=='USD' AND abonar='EUR'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/CLP Spot' (Entrega Física): counterparty=True ('' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=False (cargar='EUR'=='USD' AND abonar='CLP'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/USD Spot' (Entrega Física): counterparty=True ('' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=False (cargar='EUR'=='USD' AND abonar='USD'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Venta USD/CLP Spot' (Entrega Física): counterparty=True ('banco-abc' in 'banco-abc'), product=True ('Spot' in 'Spot'), modalidad=False ('entregaFisica' == 'Entrega Física'), currency=True (cargar='USD'=='USD' AND abonar='CLP'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Bci Compra USD/CLP Forward Comp CLP' (Entrega Física): counterparty=False ('banco-bci' in 'banco-abc'), product=False ('Forward' in 'Spot'), modalidad=False ('compensacion' == 'Entrega Física'), currency=False (cargar='CLP'=='USD' AND abonar='CLP'=='CLP')
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,027 - services.settlement_instruction_service - INFO -       Rule 'Banco ABC Compra Divisas Forward USD/CLP Compensación' (Entrega Física): counterparty=True ('banco-abc' in 'banco-abc'), product=False ('Forward' in 'Spot'), modalidad=False ('compensacion' == 'Entrega Física'), currency=False (cargar='CLP'=='USD' AND abonar='CLP'=='CLP')
2025-09-10 17:10:41,032 - services.settlement_instruction_service - INFO -       Trade direction: SELL, pay_currency: USD, receive_currency: CLP
2025-09-10 17:10:41,032 - services.settlement_instruction_service - ERROR - ❌ No matching settlement rules found for trade
2025-09-10 17:10:41,032 - api.routes.clients - ERROR - Error generating settlement instruction for client xyz-corp, trade 32018: No matching settlement rules found for this trade
INFO:     None:0 - "POST /api/v1/clients/xyz-corp/settlement-instructions/generate HTTP/1.1" 500 Internal Server Error