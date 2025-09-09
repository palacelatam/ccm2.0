# Trade Matching Algorithm Documentation

## Overview

The Trade Matching Algorithm is a core component of Client Confirmation Manager 2.0 that automatically matches trade confirmations received from banks via email with client trade data. This fuzzy matching system uses a sophisticated scoring algorithm to identify corresponding trades while minimizing false positives.

**Location:** `backend/src/services/matching_service.py`  
**Version:** 2.0 (Enhanced - September 2025)

## Algorithm Purpose

1. **Automated Reconciliation**: Match email-extracted trade data with client system trades
2. **Risk Management**: Identify discrepancies between bank confirmations and client records
3. **Operational Efficiency**: Reduce manual trade confirmation processing
4. **Audit Trail**: Maintain complete records of matching decisions and confidence levels

## Matching Process Flow

```
Email Processing → LLM Extraction → Trade Matching → Status Determination → Result Storage
     ↓                 ↓               ↓                ↓                    ↓
Bank Email       Structured      Scoring &       Confidence &        Matched/
Content          Trade Data      Validation      Status Assign       Unrecognized
```

## Enhanced Algorithm (v2.0) - Key Improvements

### 🚀 **Major Enhancements (September 2025)**

1. **MANDATORY Currency Matching**: Trades must have matching or reversed currency pairs
2. **Increased Currency Importance**: Higher scoring weights for currency pairs
3. **Higher Quality Thresholds**: More stringent matching requirements
4. **Critical Fields Requirement**: Must match 2 of 3 essential criteria
5. **Preserved Trading Tolerances**: Maintained appropriate amount tolerances

## Scoring System

### **Scoring Weights (Total: 90 points)**

| Criteria | Points | Description |
|----------|---------|-------------|
| **Counterparty Exact** | 25 | Exact counterparty name match (reduced from 30) |
| **Counterparty Partial** | 15 | Partial counterparty name match (reduced from 20) |
| **Trade Date** | 25 | Exact trade date match |
| **Currency Pair Exact** | 30 | Exact currency pair match (increased from 20) |
| **Currency Pair Reversed** | 25 | Reversed currency pair match (increased from 15) |
| **Amount Exact** | 15 | Exact amount match (0% tolerance) |
| **Amount Close** | 10 | Close amount match (0.1% tolerance) |

### **Matching Thresholds**

| Threshold | Value | Purpose |
|-----------|--------|----------|
| **Match Threshold** | 60/90 (67%) | Minimum score to be considered a match (raised from 40) |
| **Auto-Confirm Threshold** | 70/90 (78%) | Score above which status is auto-determined (raised from 60) |

## Matching Criteria Details

### **1. Counterparty Matching (25/15 points)**

**Data Sources:**
- Email sender domain mapping
- LLM-extracted counterparty name
- Client trade counterparty field

**Matching Logic:**
```python
# Exact match (25 points)
email_counterparty.lower() == client_counterparty.lower()

# Partial match (15 points) 
email_counterparty in client_counterparty OR client_counterparty in email_counterparty
```

**Domain Mappings:**
- `santander.cl` → "Santander"
- `bci.cl` → "BCI"  
- `scotiabank.cl` → "Scotiabank"
- `bancoestado.cl` → "BancoEstado"
- `banchile.cl` → "Banco de Chile"
- `itau.cl` → "Itaú"
- `security.cl` → "Banco Security"
- `bice.cl` → "BICE"

### **2. Trade Date Matching (25 points)**

**Requirements:**
- **Exact date match required** (no tolerance)
- Normalized to `dd-mm-yyyy` format
- Supports multiple input formats

**Supported Formats:**
- `dd-mm-yyyy`, `yyyy-mm-dd`
- `dd/mm/yyyy`, `yyyy/mm/dd` 
- `dd.mm.yyyy`, `yyyy.mm.dd`

### **3. 🔥 Currency Pair Matching (30/25 points) - MANDATORY**

**BREAKING CHANGE:** Currency matching is now **mandatory** - trades are automatically rejected if currencies don't match.

**Matching Logic:**
```python
# MANDATORY CHECK - Skip trade if no match
if NOT (ccy_exact_match OR ccy_reversed_match):
    SKIP_TRADE_ENTIRELY

# Exact match (30 points): USD/CLP = USD/CLP
# Reversed match (25 points): USD/CLP = CLP/USD
```

**Why This Matters:**
- Prevents false matches like EUR/CLP vs USD/CLP
- Currency is fundamental to trade identity
- Most critical field for financial accuracy

### **4. Amount Matching (15/10 points)**

**Tolerances (Unchanged - Appropriate for Trading):**
- **Exact**: 0% tolerance (15 points)
- **Close**: 0.1% tolerance (10 points)

**Purpose of Tolerances:**
- Catches rounding differences
- Handles minor data entry variations  
- Prevents major amount discrepancies (e.g., 34% difference)

**Calculation:**
```python
amount_difference = abs(email_amount - client_amount) / max(email_amount, client_amount)
```

## Critical Fields Requirement

### **Rule: Must Match 2 of 3 Critical Fields**

| Field | Importance | Why Critical |
|-------|------------|-------------|
| **Counterparty** | Essential | Identifies the trading partner |
| **Trade Date** | Essential | Temporal matching requirement |
| **Currency** | Essential | Fundamental trade characteristic |

**Implementation:**
```python
critical_matches = 0
if has_counterparty_match: critical_matches += 1
if has_date_match: critical_matches += 1  
if has_currency_match: critical_matches += 1

if critical_matches < 2:
    REJECT_TRADE  # Insufficient critical field matches
```

## Status Determination

### **Status Logic**

| Score | Discrepancies | Status |
|-------|---------------|--------|
| < 70 | Any | **Needs Review** |
| ≥ 70 | Yes | **Difference** |
| ≥ 70 | No | **Confirmation OK** |
| < 60 | N/A | **Unrecognized** |

### **Field Discrepancy Detection**

**Compared Fields (17 total):**
- ProductType, Direction, Currency1, Currency2
- QuantityCurrency1, Price, SettlementType, SettlementCurrency
- TradeDate, ValueDate, MaturityDate, PaymentDate  
- FixingReference, CounterpartyPaymentMethod, OurPaymentMethod

## Algorithm Performance

### **Before Enhancement (v1.0)**
- **False Match Example**: EUR/CLP 500K vs USD/CLP 330K = 55 points → ✅ MATCHED
- **Issues**: Currency mismatches scoring above threshold, weak validation

### **After Enhancement (v2.0)**  
- **Same Example**: EUR/CLP 500K vs USD/CLP 330K → 🚫 **REJECTED** (Mandatory currency check)
- **Improvements**: Eliminated false positives, higher precision, better risk management

## Integration Points

### **Input Data**
- **Email Trades**: LLM-extracted structured data from bank confirmations
- **Client Trades**: Uploaded CSV/Excel data from client systems  
- **Email Metadata**: Sender, date, subject, body content

### **Output Data**
- **Match Results**: Score, confidence, status, reasons
- **Discrepancies**: Field-by-field differences
- **Match ID**: Unique identifier for audit trail

### **Database Storage**
- Matched trades saved with full audit information
- Unrecognized trades preserved for manual review
- Historical matching decisions maintained

## Error Handling

### **Data Quality Issues**
- Missing currency data → Trade skipped
- Invalid amounts → Trade comparison skipped  
- Malformed dates → Normalization attempted

### **Edge Cases**
- Multiple email trades → Each processed independently
- Already matched trades → Duplicate detection warnings
- No client trades → All email trades marked unrecognized

## Debugging & Monitoring

### **Comprehensive Logging**
- Email trade raw data and normalized criteria
- Field-by-field comparison for each client trade
- Scoring breakdown with exact points awarded
- Threshold checks and rejection reasons
- Final results with confidence analysis

### **Debug Output Example**
```
🔍 MATCHING DEBUG - Email Trade Analysis
📋 NORMALIZED EMAIL CRITERIA:
  Date: 01-10-2025
  Currency1: EUR, Currency2: CLP  
  Amount: 500000.0, Counterparty: Bci

🏢 COUNTERPARTY MATCHING:
  ✅ EXACT MATCH: +25 points
💱 CURRENCY MATCHING:  
  🚫 MANDATORY CCY FAIL: EUR/CLP vs USD/CLP - SKIPPING TRADE
```

## Configuration

### **Tunable Parameters**
```python
# Scoring weights can be adjusted based on business requirements
SCORING_WEIGHTS = {
    'counterparty_exact': 25,      # Reduced from 30
    'counterparty_partial': 15,    # Reduced from 20  
    'trade_date': 25,              # Same
    'currency_pair_exact': 30,     # Increased from 20 - MORE IMPORTANT
    'currency_pair_reversed': 25,  # Increased from 15 - MORE IMPORTANT
    'amount_exact': 15,            # Same
    'amount_close': 10             # Same
}

# Thresholds can be modified for different risk tolerances  
MATCH_THRESHOLD = 60      # Increased from 40
AUTO_CONFIRM_THRESHOLD = 70  # Increased from 60

# Tolerances should remain conservative for trading
AMOUNT_EXACT_TOLERANCE = 0.0    # 0% - must be exactly the same
AMOUNT_CLOSE_TOLERANCE = 0.001  # 0.1% for close match
```

## Future Enhancements

### **Potential Improvements**
1. **Machine Learning**: Train models on historical matching decisions
2. **Dynamic Thresholds**: Adjust based on counterparty reliability
3. **Fuzzy String Matching**: Advanced counterparty name similarity
4. **Amount Range Validation**: Product-specific tolerance levels
5. **Multi-Currency Normalization**: Convert amounts to base currency

### **Business Rule Extensions**
1. **Product-Specific Rules**: Different criteria for Spot vs Forward
2. **Client-Specific Tolerances**: Customizable matching parameters
3. **Time-Based Validation**: Trade date business day validation
4. **Settlement Date Logic**: Value date consistency checking

---

**Document Version:** 1.0  
**Last Updated:** September 9, 2025  
**Author:** Enhanced Matching Algorithm Implementation  
**Review Schedule:** Quarterly or after significant algorithm changes