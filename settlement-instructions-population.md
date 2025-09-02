# Settlement Instructions Population Implementation

## Overview

This document outlines the implementation approach for automatically populating Settlement Instructions (Cartas de Instrucción) templates by merging bank-uploaded templates with client settlement rules and trade data. The system will generate populated settlement instruction documents for matched trades that can be attached to confirmation emails or stored separately.

## Current System State

### ✅ Bank Side - Template Management (COMPLETED)
- **Template Storage**: Banks upload .docx templates with placeholders
- **Rule Configuration**: Banks define template selection rules based on:
  - Client segments
  - Financial products (FX_SPOT, FX_FORWARD, FX_SWAP)
  - Counterparty matching criteria
  - Priority ordering system
- **Document Management**: Cloud Storage integration with preview functionality

### ✅ Client Side - Settlement Rules (COMPLETED)  
- **Settlement Rules Engine**: Clients configure settlement preferences by:
  - Counterparty (bank name)
  - Cashflow currency (USD, EUR, CLP, etc.)
  - Direction (IN/OUT)
  - Product type (FX_SPOT, FX_FORWARD, FX_SWAP)
- **Bank Account Management**: Client account details including:
  - Account numbers, SWIFT codes, bank names
  - Account currencies and settlement instructions
- **Rule Priority System**: Priority-based matching with drag-and-drop ordering

### ❌ Missing - Integration Layer
- **Template Selection Logic**: System to match trades → bank templates
- **Rule Matching Engine**: System to match trades → client settlement rules  
- **Document Population Service**: Merge trade data + templates → completed documents
- **Generation Trigger**: Integration with existing trade matching workflow

## Business Requirements

### Template Selection Criteria
**Bank Template Matching** (Trade → Bank Template):
1. **Counterparty**: Match trade counterparty with template rules
2. **Product**: Match trade product type (FX_SPOT, FX_FORWARD, etc.)
3. **Currencies**: Match trade currency pairs with template currency rules
4. **Client Segment**: Use client's assigned segment for template selection
5. **Priority**: Select highest priority template when multiple matches exist

### Settlement Rule Matching  
**Client Settlement Rule Matching** (Trade → Client Rule):
1. **Product**: Match trade product with settlement rule product
2. **Currencies**: Match trade currencies with settlement rule cashflow currency
3. **Counterparty/Bank**: Match trade counterparty with settlement rule counterparty
4. **Direction**: Match trade direction (IN/OUT) with settlement rule direction
5. **Priority**: Select highest priority rule when multiple matches exist

### Document Generation Trigger
- **Scope**: Only for **matched trades** (Confirmation OK status)
- **Timing**: ⚠️ **TBD** - Integration timing with confirmation email workflow needs discussion
- **Auto Carta Instrucción Toggle**: Respect client's `automation.auto_carta_instruccion` setting

## Data Mapping Specifications

### Trade Data Source
**Use Existing Trade Data Structure** from email parsing system:
- Trade data extracted from bank confirmation emails
- Matched trade data with comparison results
- Client internal trade records

### Template Variable Mapping
**Standard Settlement Instruction Variables**:
```
{client_name}           → Client organization name
{trade_number}          → Trade reference number  
{trade_date}            → Trade execution date
{value_date}            → Settlement/value date
{counterparty_name}     → Bank/counterparty name
{product_type}          → FX_SPOT, FX_FORWARD, FX_SWAP
{currency_1}            → First currency in pair (e.g., USD)
{currency_2}            → Second currency in pair (e.g., CLP)
{amount_currency_1}     → Notional amount in first currency
{amount_currency_2}     → Notional amount in second currency  
{exchange_rate}         → FX rate for the trade
{direction}             → BUY/SELL or IN/OUT
{account_number}        → Client settlement account number
{account_name}          → Client account name/description
{bank_name}             → Client's settlement bank name
{swift_code}            → Settlement bank SWIFT/BIC code
{special_instructions}  → Additional settlement instructions
{cutoff_time}           → Settlement cutoff time
```

### Data Sources Priority
1. **Trade Data**: Core trade details from email parsing
2. **Client Settlement Rule**: Account and settlement preferences  
3. **Client Organization**: Company name and basic details
4. **Bank Template**: Template-specific formatting and structure

## Implementation Phases

### Phase 1: Simple Template Population (IMMEDIATE)
**Objective**: Test document generation with standard template and real trade data

**Scope**:
- Create basic settlement instruction template service
- Use existing matched trade data for variable population
- Generate populated documents as separate files (not attached to emails)
- Test with standard template format before bank-specific templates

**Deliverables**:
- `SettlementInstructionService` class with document generation
- Template variable substitution engine
- Basic .docx document generation capability
- Test script using actual matched trade data

### Phase 2: Template Selection Engine
**Objective**: Implement bank template matching and client rule matching

**Scope**:
- Template selection algorithm based on trade characteristics
- Client settlement rule matching engine
- Integration with existing bank template management
- Multi-template support with priority handling

**Deliverables**:
- Template matching service with rule evaluation
- Client settlement rule selection logic
- Template priority resolution system
- Comprehensive test suite for matching scenarios

### Phase 3: Full Integration
**Objective**: Integration with existing trade processing workflow

**Scope**:
- Integration with automated email confirmation system
- Document attachment to confirmation emails
- Document storage and retrieval system
- Performance optimization for high-volume processing

**Deliverables**:
- Full workflow integration
- Email attachment capability
- Document storage management
- Production-ready performance optimization

## Technical Architecture

### Service Design
```python
class SettlementInstructionService:
    async def generate_settlement_instruction(
        self,
        client_id: str,
        trade_data: Dict[str, Any],
        bank_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate populated settlement instruction document
        
        Returns:
            - document_url: Cloud Storage URL for generated document
            - template_info: Details about selected template
            - variables_used: List of populated variables
            - generation_status: Success/failure status
        """
        # 1. Find matching bank template
        template = await self._select_bank_template(client_id, trade_data)
        
        # 2. Find matching client settlement rule  
        settlement_rule = await self._select_settlement_rule(client_id, trade_data)
        
        # 3. Populate template variables
        populated_doc = await self._populate_template(template, settlement_rule, trade_data)
        
        # 4. Store generated document
        document_url = await self._store_document(populated_doc, client_id)
        
        return {
            'document_url': document_url,
            'template_info': template,
            'settlement_rule': settlement_rule,
            'generation_status': 'success'
        }
```

### Template Selection Algorithm
```python
async def _select_bank_template(self, client_id: str, trade_data: Dict) -> Optional[SettlementTemplate]:
    """
    Select best matching bank template based on trade characteristics
    
    Matching Priority:
    1. Exact match (counterparty + product + currencies + client segment)
    2. Partial match (counterparty + product + client segment)
    3. Generic match (product + client segment)
    4. Fallback (client segment only)
    """
    
    # Get client's assigned segment
    client_segment = await self._get_client_segment(client_id, trade_data['counterparty'])
    
    # Build matching criteria from trade data
    criteria = {
        'counterparty': trade_data['counterparty'],
        'product': trade_data['product_type'],
        'currencies': [trade_data['currency_1'], trade_data['currency_2']],
        'client_segment': client_segment
    }
    
    # Find templates with priority-based selection
    templates = await self._find_matching_templates(criteria)
    return self._select_highest_priority_template(templates)
```

### Settlement Rule Selection Algorithm  
```python
async def _select_settlement_rule(self, client_id: str, trade_data: Dict) -> Optional[SettlementRule]:
    """
    Select client settlement rule based on trade characteristics
    
    Matching Priority:
    1. Exact match (counterparty + product + currency + direction)
    2. Partial match (counterparty + currency + direction)  
    3. Currency match (currency + direction)
    4. Generic match (product + direction)
    """
    
    criteria = {
        'counterparty': trade_data['counterparty'],
        'product': trade_data['product_type'], 
        'cashflow_currency': self._determine_settlement_currency(trade_data),
        'direction': self._determine_direction(trade_data)
    }
    
    rules = await self._find_matching_settlement_rules(client_id, criteria)
    return self._select_highest_priority_rule(rules)
```

## Document Generation Technical Approach

### Template Processing Options
**Option 1: python-docx Library**
- Direct manipulation of .docx documents
- Variable substitution in document content
- Maintains document formatting and structure
- Good for simple variable replacement

**Option 2: Document Generation Service**
- External service for complex document processing
- Better handling of complex templates
- More robust formatting preservation
- Higher implementation complexity

### Variable Substitution Strategy
- **Placeholder Format**: `{variable_name}` (consistent with existing system)
- **Case Handling**: Convert all variables to consistent case for matching
- **Missing Data**: Define fallback values or leave placeholders empty
- **Data Formatting**: Format dates, currencies, numbers according to client preferences

## Testing Strategy

### Phase 1 Testing (Simple Population)
**Test Data Sources**:
- Use existing matched trade data from development database
- Create sample settlement instruction template with common variables
- Test with multiple trade types (Spot, Forward, Swap)

**Test Cases**:
1. **Basic Variable Substitution**: All standard variables populated correctly
2. **Missing Data Handling**: Graceful handling of missing trade data
3. **Multiple Currency Pairs**: USD/CLP, EUR/CLP, USD/EUR combinations
4. **Document Format Preservation**: Ensure generated documents maintain formatting

### Integration Testing
**End-to-End Scenarios**:
1. **Complete Match**: Trade matches both bank template and client settlement rule
2. **Partial Match**: Trade matches template but no specific settlement rule
3. **No Template Match**: Trade has no matching bank template
4. **Multiple Matches**: Multiple templates/rules match - priority selection works

## Open Questions & Implementation Notes

### Template Matching Specificity
- **Question**: How specific should template matching be?
- **Current Approach**: Most specific rule match
- **Implementation Note**: Start with exact matching, add fuzzy matching later

### Currency Direction Logic
- **Question**: How to determine settlement direction (IN/OUT) from trade data?
- **Implementation Note**: May need to analyze trade structure and client position

### Template Variable Standardization  
- **Question**: Should we enforce standard variable names across all bank templates?
- **Implementation Note**: Start with flexible mapping, consider standardization later

### Performance Considerations
- **Question**: How to handle high-volume document generation?
- **Implementation Note**: Consider async generation with queue system for production

### Error Handling Strategy
- **Question**: What happens when template matching fails?
- **Implementation Note**: Define fallback templates or graceful failure modes

## Success Metrics

### Phase 1 Success Criteria
- ✅ Generate populated settlement instruction documents from trade data
- ✅ Variable substitution works correctly for all standard fields
- ✅ Documents maintain proper formatting and structure
- ✅ Test with real matched trade data from existing system

### Long-term Success Metrics
- **Template Match Rate**: Percentage of trades that find matching templates
- **Rule Match Rate**: Percentage of trades that find matching settlement rules  
- **Generation Success Rate**: Percentage of successful document generations
- **Processing Speed**: Average time to generate populated document
- **Error Rate**: Rate of generation failures or data mapping errors

---

## Next Steps

1. **Document Review**: Review and iterate on specifications with stakeholders
2. **Simple Implementation**: Create basic template population service for testing
3. **Template Creation**: Create standard settlement instruction template for initial testing
4. **Data Integration**: Test with actual matched trade data from existing system
5. **Iterative Development**: Refine matching algorithms based on real-world testing results

This approach allows us to start simple, test the core concept, and gradually build complexity as we better understand the requirements through practical implementation.