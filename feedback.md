2025-09-09 15:42:57,584 - services.matching_service - INFO - 🔍 Evaluating Client Trade #2: 32010
2025-09-09 15:42:57,584 - services.matching_service - INFO -   📋 Client Trade Data:
2025-09-09 15:42:57,584 - services.matching_service - INFO -     TradeNumber: 32010
2025-09-09 15:42:57,584 - services.matching_service - INFO -     CounterpartyName: Bci (normalized: bci)
2025-09-09 15:42:57,584 - services.matching_service - INFO -     TradeDate: 01-10-2025 (normalized: 01-10-2025)
2025-09-09 15:42:57,584 - services.matching_service - INFO -     Currency1: USD (normalized: USD)
2025-09-09 15:42:57,584 - services.matching_service - INFO -     Currency2: CLP (normalized: CLP)
2025-09-09 15:42:57,584 - services.matching_service - INFO -     QuantityCurrency1: 330000.0 (normalized: 330000.0)
2025-09-09 15:42:57,584 - services.matching_service - INFO -   🏢 COUNTERPARTY MATCHING:
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Email CP: 'Bci' (lower: 'bci')
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Client CP: 'Bci' (lower: 'bci')
2025-09-09 15:42:57,585 - services.matching_service - INFO -   📅 DATE MATCHING:
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Email Date: '01-10-2025'
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Client Date: '01-10-2025'
2025-09-09 15:42:57,585 - services.matching_service - INFO -   💱 CURRENCY MATCHING:
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Email Pair: EUR/CLP
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Client Pair: USD/CLP
2025-09-09 15:42:57,585 - services.matching_service - INFO -   💰 AMOUNT MATCHING:
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Email Amount: 500000.0
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Client Amount: 330000.0
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Amount difference: 0.340000 (34.0000%)
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Exact tolerance: 0.0 (0.0%)
2025-09-09 15:42:57,585 - services.matching_service - INFO -     Close tolerance: 0.001 (0.1%)
2025-09-09 15:42:57,585 - services.matching_service - INFO -     ✅ EXACT MATCH: +30 points - Counterparty exact: 'Bci'
2025-09-09 15:42:57,585 - services.matching_service - INFO -     ✅ DATE MATCH: +25 points - Trade date: 01-10-2025
2025-09-09 15:42:57,585 - services.matching_service - INFO -     ❌ CCY MISMATCH: EUR/CLP vs USD/CLP
2025-09-09 15:42:57,585 - services.matching_service - INFO -     ❌ AMOUNT MISMATCH: 500000.00 vs 330000.00 (diff: 34.0000%)
2025-09-09 15:42:57,585 - services.matching_service - INFO -   🏆 FINAL SCORE: 55/90 points
2025-09-09 15:42:57,586 - services.matching_service - INFO -   📊 THRESHOLD CHECK: 55 >= 40? ✅ YES
2025-09-09 15:42:57,586 - services.matching_service - INFO -   ✅ ADDED TO POTENTIAL MATCHES - Trade: 32010, Score: 55, Reasons: ["Counterparty exact: 'Bci'", 'Trade date: 01-10-2025']