2025-09-10 15:19:51,256 - services.settlement_instruction_service - INFO - ✅ Resolved counterparty 'Bci' → 'banco-bci' via client mapping
2025-09-10 15:19:51,256 - services.settlement_instruction_service - INFO - 🔍 Matching settlement rules - Type: Compensación, Currency: CLP
2025-09-10 15:19:51,257 - services.settlement_instruction_service - INFO -    Counterparty: 'banco-bci'
2025-09-10 15:19:51,257 - services.settlement_instruction_service - INFO -    Product: 'Forward'
2025-09-10 15:19:51,257 - services.settlement_instruction_service - INFO -    Direction: 'BUY'
2025-09-10 15:19:51,257 - services.settlement_instruction_service - INFO -    Currency1: 'USD'
2025-09-10 15:19:51,257 - services.settlement_instruction_service - INFO -    Currency2: 'CLP'
2025-09-10 15:19:51,258 - services.settlement_instruction_service - INFO -    Available rules: 8
2025-09-10 15:19:51,258 - services.settlement_instruction_service - INFO -    Rule 1/8: name='Compra USD/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,258 - services.settlement_instruction_service - INFO -    Rule 2/8: name='Compra EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 3/8: name='Compra EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 4/8: name='Venta EUR/CLP Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 5/8: name='Venta EUR/USD Spot', counterparty='', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 6/8: name='Venta USD/CLP Spot', counterparty='banco-abc', product='Spot', modalidad='entregaFisica', settlementCurrency='', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 7/8: name='Bci Compra USD/CLP Forward Comp CLP', counterparty='banco-bci', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-10 15:19:51,259 - services.settlement_instruction_service - INFO -    Rule 8/8: name='Banco ABC Compra Divisas Forward USD/CLP Compensación', counterparty='banco-abc', product='Forward', modalidad='compensacion', settlementCurrency='CLP', active=True
2025-09-10 15:19:51,260 - services.settlement_instruction_service - INFO -       Rule 'Compra USD/CLP Spot': counterparty=True ( in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,260 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/CLP Spot': counterparty=True ( in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,260 - services.settlement_instruction_service - INFO -       Rule 'Compra EUR/USD Spot': counterparty=True ( in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,260 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/CLP Spot': counterparty=True ( in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,261 - services.settlement_instruction_service - INFO -       Rule 'Venta EUR/USD Spot': counterparty=True ( in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,261 - services.settlement_instruction_service - INFO -       Rule 'Venta USD/CLP Spot': counterparty=False (banco-abc in banco-bci), product=False (Spot in Forward), modalidad=False (entregaFisica == Compensación), currency=True ( == CLP)
2025-09-10 15:19:51,261 - services.settlement_instruction_service - INFO -       Rule 'Bci Compra USD/CLP Forward Comp CLP': counterparty=True (banco-bci in banco-bci), product=True (Forward in Forward), modalidad=True (compensacion == Compensación), currency=True (CLP == CLP)
2025-09-10 15:19:51,261 - services.settlement_instruction_service - INFO - ✅ Matched rule: Bci Compra USD/CLP Forward Comp CLP for Compensación
2025-09-10 15:19:51,262 - services.auto_email_service - INFO - 💰 Settlement data prepared: N/A / 2011234568
2025-09-10 15:19:51,262 - services.settlement_instruction_service - INFO - 🔍 Starting settlement instruction generation:
2025-09-10 15:19:51,262 - services.settlement_instruction_service - INFO -    Bank ID: banco-bci
2025-09-10 15:19:51,262 - services.settlement_instruction_service - INFO -    Client segment ID: xyz-corp
2025-09-10 15:19:51,262 - services.settlement_instruction_service - INFO -    Settlement type: Compensación
2025-09-10 15:19:51,263 - services.settlement_instruction_service - INFO -    Product: Forward
2025-09-10 15:19:51,263 - services.settlement_instruction_service - INFO - 🔍 Template search criteria:
2025-09-10 15:19:51,263 - services.settlement_instruction_service - INFO -    Bank ID: 'banco-bci'
2025-09-10 15:19:51,263 - services.settlement_instruction_service - INFO -    Settlement type: 'Compensación'
2025-09-10 15:19:51,263 - services.settlement_instruction_service - INFO -    Product: 'Forward'
2025-09-10 15:19:51,264 - services.settlement_instruction_service - INFO -    Client segment ID: 'xyz-corp'
2025-09-10 15:19:51,264 - services.settlement_instruction_service - INFO - 🔍 Querying database: banks/banco-bci/settlementInstructionLetters
2025-09-10 15:19:51,308 - services.settlement_instruction_service - INFO - ✅ Bank document exists: {'taxId': '97.004.000-5', 'lastUpdatedAt': DatetimeWithNanoseconds(2025, 9, 8, 14, 0, 33, 152930, tzinfo=datetime.timezone.utc), 'country': 'CL', 'createdAt': DatetimeWithNanoseconds(2025, 9, 8, 14, 0, 33, 152930, tzinfo=datetime.timezone.utc), 'lastUpdatedBy': None, 'status': 'active', 'swiftCode': 'BCHCCLRM', 'name': 'BCI'}
2025-09-10 15:19:51,374 - services.settlement_instruction_service - INFO - 🔍 Total settlement instruction letters in banks/banco-bci/settlementInstructionLetters: 3
2025-09-10 15:19:51,374 - services.settlement_instruction_service - INFO - 📋 Available templates for bank 'banco-bci':
2025-09-10 15:19:51,375 - services.settlement_instruction_service - INFO -    1. ID: Bk87Ktdvrbdc33EQHxKU
2025-09-10 15:19:51,375 - services.settlement_instruction_service - INFO -       Rule name: Template Forward Carta Instrucción (Entrega Física)
2025-09-10 15:19:51,376 - services.settlement_instruction_service - INFO -       Settlement type: Entrega Física
2025-09-10 15:19:51,376 - services.settlement_instruction_service - INFO -       Product: Forward
2025-09-10 15:19:51,376 - services.settlement_instruction_service - INFO -       Client segment: None
2025-09-10 15:19:51,376 - services.settlement_instruction_service - INFO -       Active: True
2025-09-10 15:19:51,377 - services.settlement_instruction_service - INFO -       Priority: 2
2025-09-10 15:19:51,377 - services.settlement_instruction_service - INFO -       Storage path: banco-bci/default/Template Forward Carta Instrucción Bci (Entrega Física)_20250908_141229_74cdae22.docx
2025-09-10 15:19:51,377 - services.settlement_instruction_service - INFO -    2. ID: DPai8qSVOiKcQXH1rIgA
2025-09-10 15:19:51,377 - services.settlement_instruction_service - INFO -       Rule name: Template Carta Instrucción Spot
2025-09-10 15:19:51,377 - services.settlement_instruction_service - INFO -       Settlement type: Entrega Física
2025-09-10 15:19:51,378 - services.settlement_instruction_service - INFO -       Product: Spot
2025-09-10 15:19:51,378 - services.settlement_instruction_service - INFO -       Client segment: None
2025-09-10 15:19:51,379 - services.settlement_instruction_service - INFO -       Active: True
2025-09-10 15:19:51,379 - services.settlement_instruction_service - INFO -       Priority: 1
2025-09-10 15:19:51,379 - services.settlement_instruction_service - INFO -       Storage path: banco-bci/default/Template Spot Carta Instrucción Bci (Entrega Física)_20250908_141142_68333305.docx
2025-09-10 15:19:51,379 - services.settlement_instruction_service - INFO -    3. ID: JbbzInUQC08FklapNgo2
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Rule name: Template Forward Carta Instrucción (Compensación)
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Settlement type: Compensación
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Product: Forward
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Client segment: None
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Active: True
2025-09-10 15:19:51,380 - services.settlement_instruction_service - INFO -       Priority: 3
2025-09-10 15:19:51,381 - services.settlement_instruction_service - INFO -       Storage path: banco-bci/default/Template Forward Carta Instrucción Bci (Compensación)_20250908_141257_3ccdf4db.docx
2025-09-10 15:19:51,381 - services.settlement_instruction_service - INFO - 🔍 Filtering by active=True...
2025-09-10 15:19:51,425 - services.settlement_instruction_service - INFO -    Found 3 active templates
2025-09-10 15:19:51,426 - services.settlement_instruction_service - INFO - 🔍 Filtering by settlement_type='Compensación'...
C:\Users\bencl\Proyectos\ccm2.0\backend\src\services\settlement_instruction_service.py:238: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  query = query.where('settlement_type', '==', settlement_type)
2025-09-10 15:19:51,473 - services.settlement_instruction_service - INFO -    Found 1 templates matching settlement_type
2025-09-10 15:19:51,530 - services.settlement_instruction_service - INFO - 🧮 Scoring template 'Template Forward Carta Instrucción (Compensación)':
2025-09-10 15:19:51,530 - services.settlement_instruction_service - INFO -    Settlement type match: +100 ('Compensación' == 'Compensación')
2025-09-10 15:19:51,531 - services.settlement_instruction_service - INFO -    Product partial match: +50 ('Forward' in 'Forward')
2025-09-10 15:19:51,531 - services.settlement_instruction_service - INFO -    Default template (no client segment): +10
2025-09-10 15:19:51,531 - services.settlement_instruction_service - INFO -    Priority bonus: +997 (priority 3)
2025-09-10 15:19:51,531 - services.settlement_instruction_service - INFO -    Total score: 1157
2025-09-10 15:19:51,532 - services.settlement_instruction_service - INFO - 🏆 Final template ranking:
2025-09-10 15:19:51,532 - services.settlement_instruction_service - INFO -    1. Template Forward Carta Instrucción (Compensación) (score: 1157)
2025-09-10 15:19:51,532 - services.settlement_instruction_service - INFO - ✅ Selected best template: Template Forward Carta Instrucción (Compensación) (score: 1157)
2025-09-10 15:19:51,532 - services.settlement_instruction_service - INFO - ✅ Found matching template: Template Forward Carta Instrucción (Compensación) (ID: JbbzInUQC08FklapNgo2, Score: 1157)