"""
Trade Matching Service
Implements the fuzzy matching algorithm to match email confirmations with client trades
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Service for matching email-extracted trades with client trades
    
    ENHANCED MATCHING ALGORITHM (v2.0):
    1. MANDATORY currency pair matching - trades must have matching or reversed currency pairs
    2. INCREASED currency pair scoring weights (30/25 vs 20/15) 
    3. REDUCED counterparty scoring weights (25/15 vs 30/20)
    4. HIGHER score thresholds (60 vs 40 for match, 70 vs 60 for auto-confirm)
    5. CRITICAL FIELDS requirement - must match 2 of 3: counterparty, date, currency
    6. PRESERVED amount tolerances (0% exact, 0.1% close) - appropriate for trading
    """
    
    # Scoring weights (total up to ~95 points) - UPDATED for better currency matching + product type
    SCORING_WEIGHTS = {
        'counterparty_exact': 25,      # Reduced from 30
        'counterparty_partial': 15,    # Reduced from 20  
        'trade_date': 25,              # Same
        'currency_pair_exact': 30,     # Increased from 20 - MORE IMPORTANT
        'currency_pair_reversed': 25,  # Increased from 15 - MORE IMPORTANT
        'amount_exact': 15,            # Same
        'amount_close': 10,            # Same
        'product_type': 5              # NEW - differentiate spot vs forward
    }
    
    # Matching thresholds - TIGHTENED for better precision
    MATCH_THRESHOLD = 60  # Increased from 40 - Minimum score to be considered a match
    AUTO_CONFIRM_THRESHOLD = 70  # Increased from 60 - Score above which we auto-confirm
    
    # Tolerances
    AMOUNT_EXACT_TOLERANCE = 0.0    # 0% - must be exactly the same
    AMOUNT_CLOSE_TOLERANCE = 0.001  # 0.1% for close match
    DATE_TOLERANCE_DAYS = 0  # No tolerance - exact date match required
    
    def __init__(self):
        """Initialize the matching service"""
        logger.info("MatchingService initialized")
    
    def match_email_trades_with_client_trades(
        self, 
        email_trades: List[Dict[str, Any]], 
        client_trades: List[Dict[str, Any]],
        email_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Match trades extracted from email with client trades
        
        Args:
            email_trades: List of trades extracted from email by LLM
            client_trades: List of unmatched client trades
            email_metadata: Email metadata (sender, date, subject, etc.)
            
        Returns:
            List of match results with match_id, confidence, status, etc.
        """
        match_results = []
        
        # DEBUGGING: Log initial setup
        logger.info("🚀 STARTING MATCHING PROCESS")
        logger.info(f"📧 Email trades to process: {len(email_trades)}")
        logger.info(f"📊 Client trades available: {len(client_trades)}")
        
        # DEBUGGING: Check for already matched trades
        already_matched_trade_numbers = set()
        for client_trade in client_trades:
            if client_trade.get('matched', False) or client_trade.get('status') in ['Matched', 'Confirmed']:
                already_matched_trade_numbers.add(client_trade.get('TradeNumber'))
        
        if already_matched_trade_numbers:
            logger.warning(f"⚠️  FOUND ALREADY MATCHED TRADES: {already_matched_trade_numbers}")
            logger.warning("These should have been filtered out before matching!")
        
        for idx, email_trade in enumerate(email_trades):
            email_trade_num = email_trade.get('TradeNumber', 'Unknown')
            
            logger.info("🔄" * 20)
            logger.info(f"🔄 PROCESSING EMAIL TRADE #{idx+1}/{len(email_trades)}: {email_trade_num}")
            logger.info("🔄" * 20)
            
            # DEBUGGING: Check if this email trade might be a duplicate
            if email_trade_num in already_matched_trade_numbers:
                logger.error(f"🚨 POTENTIAL DUPLICATE DETECTED!")
                logger.error(f"Email trade {email_trade_num} appears to already be matched!")
                logger.error(f"This might explain why you're getting duplicate instead of unrecognized!")
            
            # Find potential matches for this email trade
            potential_matches = self._find_potential_matches(email_trade, client_trades, email_metadata)
            
            if potential_matches:
                # Get the best match (highest score)
                best_match = potential_matches[0]
                
                logger.info(f"✅ MATCH FOUND!")
                logger.info(f"Best matching client trade: {best_match['trade'].get('TradeNumber')}")
                logger.info(f"Match score: {best_match['score']}/90 points")
                logger.info(f"Match reasons: {best_match['reasons']}")
                
                # Generate unique match_id for linking
                match_id = str(uuid.uuid4())
                
                # Check for field differences
                logger.info(f"🔍 Checking for field discrepancies...")
                discrepancies = self._find_discrepancies(email_trade, best_match['trade'])
                
                if discrepancies:
                    logger.warning(f"⚠️  Found {len(discrepancies)} field discrepancies:")
                    for disc in discrepancies:
                        logger.warning(f"  - {disc['field']}: Email='{disc['email_value']}' vs Client='{disc['client_value']}'")
                else:
                    logger.info(f"✅ No field discrepancies found")
                
                # Determine status based on score and discrepancies
                status = self._determine_match_status(
                    best_match['score'], 
                    discrepancies
                )
                
                logger.info(f"📊 Status determination:")
                logger.info(f"  Score: {best_match['score']} (threshold for auto-confirm: {self.AUTO_CONFIRM_THRESHOLD})")
                logger.info(f"  Discrepancies: {len(discrepancies)}")
                logger.info(f"  Final Status: {status}")
                
                # Calculate confidence percentage
                # Maximum possible score is 100 (counterparty: 25, date: 25, currency: 30, amount: 15, product: 5)
                confidence = round((best_match['score'] / 100) * 100)
                
                # DEBUGGING: Check if this might be a duplicate match
                matched_trade_num = best_match['trade'].get('TradeNumber')
                if best_match['trade'].get('matched', False):
                    logger.error(f"🚨 DUPLICATE MATCH DETECTED!")
                    logger.error(f"Client trade {matched_trade_num} appears to already be matched!")
                    logger.error(f"This explains why you got a duplicate instead of unrecognized!")
                    logger.error(f"Trade status/flags: {best_match['trade'].get('status', 'No status')} | Matched: {best_match['trade'].get('matched', False)}")
                
                match_result = {
                    'match_id': match_id,
                    'email_trade': email_trade,
                    'matched_client_trade': best_match['trade'],
                    'score': best_match['score'],
                    'confidence': confidence,
                    'status': status,
                    'match_reasons': best_match['reasons'],
                    'discrepancies': discrepancies,
                    'email_metadata': email_metadata
                }
                
                match_results.append(match_result)
                
                logger.info(f"✅ FINAL MATCH RESULT:")
                logger.info(f"  Email Trade: {email_trade_num}")
                logger.info(f"  Matched to Client Trade: {matched_trade_num}")
                logger.info(f"  Score: {best_match['score']}/100 ({confidence}%)")
                logger.info(f"  Status: {status}")
                logger.info(f"  Match ID: {match_id}")
                
            else:
                logger.warning(f"❌ NO MATCH FOUND!")
                logger.warning(f"Email trade {email_trade_num} will be marked as UNRECOGNIZED")
                
                # No match found - create unrecognized entry
                match_id = str(uuid.uuid4())
                
                match_result = {
                    'match_id': match_id,
                    'email_trade': email_trade,
                    'matched_client_trade': None,
                    'score': 0,
                    'confidence': 0,
                    'status': 'Unrecognized',
                    'match_reasons': [],
                    'discrepancies': [],
                    'email_metadata': email_metadata
                }
                
                match_results.append(match_result)
                
                logger.warning(f"❌ FINAL UNRECOGNIZED RESULT:")
                logger.warning(f"  Email Trade: {email_trade_num}")
                logger.warning(f"  Status: Unrecognized")
                logger.warning(f"  Match ID: {match_id}")
        
        return match_results
    
    def _find_potential_matches(
        self, 
        email_trade: Dict[str, Any], 
        client_trades: List[Dict[str, Any]],
        email_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find potential matching trades using scoring algorithm
        
        Returns list of matches sorted by score (highest first)
        """
        potential_matches = []
        
        # Extract email trade data for matching
        email_trade_date = self._normalize_date(email_trade.get('TradeDate'))
        email_ccy1 = str(email_trade.get('Currency1', '')).upper()
        email_ccy2 = str(email_trade.get('Currency2', '')).upper()
        email_amount = self._normalize_amount(email_trade.get('QuantityCurrency1'))
        email_counterparty = self._extract_counterparty_from_email(email_trade, email_metadata)
        
        # DEBUGGING: Enhanced logging for email trade
        logger.info("=" * 80)
        logger.info(f"🔍 MATCHING DEBUG - Email Trade Analysis")
        logger.info(f"Email Trade Number: {email_trade.get('TradeNumber', 'Unknown')}")
        logger.info(f"Email Raw Data:")
        for key, value in email_trade.items():
            logger.info(f"  {key}: {value}")
        logger.info(f"Email Metadata:")
        for key, value in email_metadata.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 80)
        
        logger.info(f"📋 NORMALIZED EMAIL CRITERIA:")
        logger.info(f"  Date: {email_trade_date}")
        logger.info(f"  Currency1: {email_ccy1}")
        logger.info(f"  Currency2: {email_ccy2}")
        logger.info(f"  Amount: {email_amount}")
        logger.info(f"  Counterparty: {email_counterparty}")
        logger.info(f"📊 CLIENT TRADES TO COMPARE: {len(client_trades)}")
        logger.info("-" * 80)
        
        for idx, client_trade in enumerate(client_trades):
            score = 0
            reasons = []
            debug_info = []
            
            # DEBUGGING: Log each client trade being evaluated
            client_trade_number = client_trade.get('TradeNumber', f'Unknown-{idx}')
            logger.info(f"🔍 Evaluating Client Trade #{idx+1}: {client_trade_number}")
            
            # Extract client trade data for comparison
            client_counterparty = str(client_trade.get('CounterpartyName', '')).lower()
            client_trade_date = self._normalize_date(client_trade.get('TradeDate'))
            client_ccy1 = str(client_trade.get('Currency1', '')).upper()
            client_ccy2 = str(client_trade.get('Currency2', '')).upper()
            client_amount = self._normalize_amount(client_trade.get('QuantityCurrency1'))
            
            logger.info(f"  📋 Client Trade Data:")
            logger.info(f"    TradeNumber: {client_trade.get('TradeNumber')}")
            logger.info(f"    CounterpartyName: {client_trade.get('CounterpartyName')} (normalized: {client_counterparty})")
            logger.info(f"    TradeDate: {client_trade.get('TradeDate')} (normalized: {client_trade_date})")
            logger.info(f"    Currency1: {client_trade.get('Currency1')} (normalized: {client_ccy1})")
            logger.info(f"    Currency2: {client_trade.get('Currency2')} (normalized: {client_ccy2})")
            logger.info(f"    QuantityCurrency1: {client_trade.get('QuantityCurrency1')} (normalized: {client_amount})")
            
            # 1. Counterparty match (30 points max)
            logger.info(f"  🏢 COUNTERPARTY MATCHING:")
            logger.info(f"    Email CP: '{email_counterparty}' (lower: '{email_counterparty.lower() if email_counterparty else None}')")
            logger.info(f"    Client CP: '{client_trade.get('CounterpartyName')}' (lower: '{client_counterparty}')")
            
            if email_counterparty and client_counterparty:
                email_cp_lower = email_counterparty.lower()
                if email_cp_lower == client_counterparty:
                    score += self.SCORING_WEIGHTS['counterparty_exact']
                    reason = f"Counterparty exact: '{email_counterparty}'"
                    reasons.append(reason)
                    debug_info.append(f"✅ EXACT MATCH: +{self.SCORING_WEIGHTS['counterparty_exact']} points - {reason}")
                elif email_cp_lower in client_counterparty or client_counterparty in email_cp_lower:
                    score += self.SCORING_WEIGHTS['counterparty_partial']
                    reason = f"Counterparty partial: '{email_counterparty}' ~ '{client_trade.get('CounterpartyName')}'"
                    reasons.append(reason)
                    debug_info.append(f"✅ PARTIAL MATCH: +{self.SCORING_WEIGHTS['counterparty_partial']} points - {reason}")
                else:
                    debug_info.append(f"❌ NO COUNTERPARTY MATCH: '{email_counterparty}' vs '{client_trade.get('CounterpartyName')}'")
            else:
                debug_info.append(f"⚠️  MISSING COUNTERPARTY DATA: Email='{email_counterparty}', Client='{client_counterparty}'")
            
            # 2. Trade date match (25 points)
            logger.info(f"  📅 DATE MATCHING:")
            logger.info(f"    Email Date: '{email_trade_date}'")
            logger.info(f"    Client Date: '{client_trade_date}'")
            
            if email_trade_date and client_trade_date:
                if self._dates_match(email_trade_date, client_trade_date):
                    score += self.SCORING_WEIGHTS['trade_date']
                    reason = f"Trade date: {email_trade_date}"
                    reasons.append(reason)
                    debug_info.append(f"✅ DATE MATCH: +{self.SCORING_WEIGHTS['trade_date']} points - {reason}")
                else:
                    debug_info.append(f"❌ DATE MISMATCH: '{email_trade_date}' vs '{client_trade_date}'")
            else:
                debug_info.append(f"⚠️  MISSING DATE DATA: Email='{email_trade_date}', Client='{client_trade_date}'")
            
            # 3. Currency pair match (30 points max) - MANDATORY CHECK
            logger.info(f"  💱 CURRENCY MATCHING:")
            logger.info(f"    Email Pair: {email_ccy1}/{email_ccy2}")
            logger.info(f"    Client Pair: {client_ccy1}/{client_ccy2}")
            
            # MANDATORY CURRENCY CHECK - Skip trade if currencies don't match at all
            if email_ccy1 and email_ccy2 and client_ccy1 and client_ccy2:
                ccy_exact_match = (email_ccy1 == client_ccy1 and email_ccy2 == client_ccy2)
                ccy_reversed_match = (email_ccy1 == client_ccy2 and email_ccy2 == client_ccy1)
                
                if not (ccy_exact_match or ccy_reversed_match):
                    debug_info.append(f"🚫 MANDATORY CCY FAIL: {email_ccy1}/{email_ccy2} vs {client_ccy1}/{client_ccy2} - SKIPPING TRADE")
                    logger.info(f"    🚫 MANDATORY CURRENCY CHECK FAILED - SKIPPING THIS TRADE")
                    logger.info(f"  ❌ REJECTED (currency mismatch) - Trade: {client_trade_number}")
                    logger.info("-" * 40)
                    continue  # Skip this client trade entirely
            elif email_ccy1 and email_ccy2:
                # If client trade is missing currency data, also skip
                debug_info.append(f"🚫 MISSING CLIENT CCY DATA - SKIPPING TRADE")
                logger.info(f"    🚫 CLIENT MISSING CURRENCY DATA - SKIPPING THIS TRADE")
                logger.info(f"  ❌ REJECTED (missing client currency) - Trade: {client_trade_number}")
                logger.info("-" * 40)
                continue
            
            if email_ccy1 and email_ccy2:
                if email_ccy1 == client_ccy1 and email_ccy2 == client_ccy2:
                    score += self.SCORING_WEIGHTS['currency_pair_exact']
                    reason = f"Currency pair: {email_ccy1}/{email_ccy2}"
                    reasons.append(reason)
                    debug_info.append(f"✅ EXACT CCY MATCH: +{self.SCORING_WEIGHTS['currency_pair_exact']} points - {reason}")
                elif email_ccy1 == client_ccy2 and email_ccy2 == client_ccy1:
                    score += self.SCORING_WEIGHTS['currency_pair_reversed']
                    reason = f"Currency pair reversed: {email_ccy1}/{email_ccy2}"
                    reasons.append(reason)
                    debug_info.append(f"✅ REVERSED CCY MATCH: +{self.SCORING_WEIGHTS['currency_pair_reversed']} points - {reason}")
                else:
                    debug_info.append(f"❌ CCY MISMATCH: {email_ccy1}/{email_ccy2} vs {client_ccy1}/{client_ccy2}")
            else:
                debug_info.append(f"⚠️  MISSING CCY DATA: Email={email_ccy1}/{email_ccy2}, Client={client_ccy1}/{client_ccy2}")
            
            # 4. Amount match (15 points max)
            logger.info(f"  💰 AMOUNT MATCHING:")
            logger.info(f"    Email Amount: {email_amount}")
            logger.info(f"    Client Amount: {client_amount}")
            
            if email_amount is not None and email_amount > 0:
                if client_amount is not None and client_amount > 0:
                    amount_diff = abs(email_amount - client_amount) / max(email_amount, client_amount)
                    amount_diff_pct = amount_diff * 100
                    
                    logger.info(f"    Amount difference: {amount_diff:.6f} ({amount_diff_pct:.4f}%)")
                    logger.info(f"    Exact tolerance: {self.AMOUNT_EXACT_TOLERANCE} ({self.AMOUNT_EXACT_TOLERANCE*100}%)")
                    logger.info(f"    Close tolerance: {self.AMOUNT_CLOSE_TOLERANCE} ({self.AMOUNT_CLOSE_TOLERANCE*100}%)")
                    
                    if amount_diff <= self.AMOUNT_EXACT_TOLERANCE:
                        score += self.SCORING_WEIGHTS['amount_exact']
                        reason = f"Amount exact: {email_amount:.2f}"
                        reasons.append(reason)
                        debug_info.append(f"✅ EXACT AMOUNT: +{self.SCORING_WEIGHTS['amount_exact']} points - {reason}")
                    elif amount_diff <= self.AMOUNT_CLOSE_TOLERANCE:
                        score += self.SCORING_WEIGHTS['amount_close']
                        reason = f"Amount close: {email_amount:.2f} ~ {client_amount:.2f}"
                        reasons.append(reason)
                        debug_info.append(f"✅ CLOSE AMOUNT: +{self.SCORING_WEIGHTS['amount_close']} points - {reason} (diff: {amount_diff_pct:.4f}%)")
                    else:
                        debug_info.append(f"❌ AMOUNT MISMATCH: {email_amount:.2f} vs {client_amount:.2f} (diff: {amount_diff_pct:.4f}%)")
                else:
                    debug_info.append(f"⚠️  CLIENT AMOUNT INVALID: {client_trade.get('QuantityCurrency1')} (normalized: {client_amount})")
            else:
                debug_info.append(f"⚠️  EMAIL AMOUNT INVALID: {email_trade.get('QuantityCurrency1')} (normalized: {email_amount})")
            
            # 5. Product type match (5 points)
            logger.info(f"  📋 PRODUCT TYPE MATCHING:")
            email_product_type = self._normalize_product_type(email_trade.get('ProductType'))
            client_product_type = self._normalize_product_type(client_trade.get('ProductType'))
            logger.info(f"    Email Product: '{email_trade.get('ProductType')}' (normalized: '{email_product_type}')")
            logger.info(f"    Client Product: '{client_trade.get('ProductType')}' (normalized: '{client_product_type}')")
            
            if email_product_type and client_product_type:
                if email_product_type == client_product_type:
                    score += self.SCORING_WEIGHTS['product_type']
                    reason = f"Product type: {email_product_type}"
                    reasons.append(reason)
                    debug_info.append(f"✅ PRODUCT TYPE MATCH: +{self.SCORING_WEIGHTS['product_type']} points - {reason}")
                else:
                    debug_info.append(f"❌ PRODUCT TYPE MISMATCH: '{email_product_type}' vs '{client_product_type}'")
            else:
                debug_info.append(f"⚠️  MISSING PRODUCT TYPE DATA: Email='{email_product_type}', Client='{client_product_type}'")
            
            # Log all debug info for this trade comparison
            for info in debug_info:
                logger.info(f"    {info}")
            
            # CRITICAL FIELDS CHECK - Must have at least 2 of 3 critical matches
            critical_matches = 0
            has_counterparty = any('CP Exact' in reason or 'CP Partial' in reason for reason in debug_info)
            has_date = any('DATE MATCH' in reason for reason in debug_info)
            has_currency = any('CCY MATCH' in reason for reason in debug_info)
            
            if has_counterparty: critical_matches += 1
            if has_date: critical_matches += 1 
            if has_currency: critical_matches += 1
            
            logger.info(f"  🎯 CRITICAL FIELDS: CP={has_counterparty}, Date={has_date}, CCY={has_currency} ({critical_matches}/3)")
            
            if critical_matches < 2:
                logger.info(f"  ❌ REJECTED (insufficient critical matches: {critical_matches}/3 minimum required)")
                logger.info(f"  📊 Need at least 2 of: Counterparty, Date, Currency")
                logger.info("-" * 40)
                continue
            
            # Final score summary for this client trade
            logger.info(f"  🏆 FINAL SCORE: {score}/100 points")
            logger.info(f"  📊 THRESHOLD CHECK: {score} >= {self.MATCH_THRESHOLD}? {'✅ YES' if score >= self.MATCH_THRESHOLD else '❌ NO'}")
            logger.info(f"  ✅ CRITICAL FIELDS: {critical_matches}/3 critical matches (passed)")
            
            # Add as potential match if score exceeds threshold AND critical fields
            if score >= self.MATCH_THRESHOLD:
                potential_matches.append({
                    'trade': client_trade,
                    'score': score,
                    'reasons': reasons
                })
                logger.info(f"  ✅ ADDED TO POTENTIAL MATCHES - Trade: {client_trade_number}, Score: {score}, Reasons: {reasons}")
            else:
                logger.info(f"  ❌ REJECTED (below threshold) - Trade: {client_trade_number}, Score: {score}")
                
            logger.info("-" * 40)
        
        # Sort by score (highest first)
        sorted_matches = sorted(potential_matches, key=lambda x: x['score'], reverse=True)
        
        # DEBUGGING: Final summary
        logger.info("=" * 80)
        logger.info(f"🎯 MATCHING RESULTS SUMMARY")
        logger.info(f"Total potential matches found: {len(sorted_matches)}")
        
        if sorted_matches:
            logger.info(f"📋 RANKED MATCHES:")
            for i, match in enumerate(sorted_matches):
                trade_num = match['trade'].get('TradeNumber', 'Unknown')
                logger.info(f"  #{i+1}: Trade {trade_num} - Score: {match['score']}/100 ({(match['score']/100*100):.1f}%)")
                logger.info(f"       Reasons: {', '.join(match['reasons'])}")
            
            best_match = sorted_matches[0]
            logger.info(f"🏆 BEST MATCH: Trade {best_match['trade'].get('TradeNumber')} with {best_match['score']}/100 points")
        else:
            logger.info(f"❌ NO MATCHES FOUND - All client trades failed requirements:")
            logger.info(f"   • Score threshold: {self.MATCH_THRESHOLD}/100 points")
            logger.info(f"   • Critical fields: 2/3 (Counterparty, Date, Currency)")
            logger.info(f"   • Mandatory currency matching")
            
        logger.info("=" * 80)
        
        return sorted_matches
    
    def _find_discrepancies(
        self, 
        email_trade: Dict[str, Any], 
        client_trade: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find field discrepancies between email trade and client trade
        
        Returns list of discrepancies with field name and both values
        """
        discrepancies = []
        
        # Fields to compare (excluding match fields and IDs)
        fields_to_compare = [
            'ProductType', 'Direction', 'Currency1', 'Currency2',
            'QuantityCurrency1', 'Price', 'SettlementType',
            'SettlementCurrency', 'TradeDate', 'ValueDate', 
            'MaturityDate', 'PaymentDate', 'FixingReference',
            'CounterpartyPaymentMethod', 'OurPaymentMethod'
        ]
        
        for field in fields_to_compare:_is_valid_value
            email_value = email_trade.get(field)
            client_value = client_trade.get(field)
            
            # Normalize values for comparison
            norm_email = self._normalize_value(email_value)
            norm_client = self._normalize_value(client_value)
            
            # Check if values differ (and email value is valid)
            if norm_email != norm_client and self._is_valid_value(email_value):
                discrepancies.append({
                    'field': field,
                    'email_value': email_value,
                    'client_value': client_value
                })
                logger.debug(f"Discrepancy in {field}: Email='{email_value}' vs Client='{client_value}'")
        
        return discrepancies
    
    def _determine_match_status(self, score: int, discrepancies: List[Dict]) -> str:
        """
        Determine match status based on score and discrepancies
        
        Returns: 'Confirmation OK', 'Difference', 'Needs Review', or 'Unrecognized'
        """
        if score < self.AUTO_CONFIRM_THRESHOLD:
            return 'Needs Review'
        elif discrepancies:
            return 'Difference'
        else:
            return 'Confirmation OK'
    
    def _extract_counterparty_from_email(
        self, 
        email_trade: Dict[str, Any], 
        email_metadata: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extract counterparty name from email trade or metadata
        """
        # First try from LLM extracted trade data
        counterparty = email_trade.get('CounterpartyName')
        if counterparty:
            return counterparty
        
        # Try to extract from email sender domain
        sender = email_metadata.get('senderEmail', '')
        if '@' in sender:
            domain = sender.split('@')[1].lower()
            # Map common bank domains to names (you can expand this)
            domain_mappings = {
                'santander.cl': 'Santander',
                'bci.cl': 'BCI',
                'scotiabank.cl': 'Scotiabank',
                'bancoestado.cl': 'BancoEstado',
                'banchile.cl': 'Banco de Chile',
                'itau.cl': 'Itaú',
                'security.cl': 'Banco Security',
                'bice.cl': 'BICE',
            }
            
            for key, name in domain_mappings.items():
                if key in domain:
                    return name
        
        return None
    
    def _normalize_date(self, date_value: Any) -> Optional[str]:
        """Normalize date to dd-mm-yyyy format"""
        if not date_value:
            return None
        
        date_str = str(date_value).strip()
        
        # Already in correct format?
        if re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
            return date_str
        
        # Try different date formats
        date_formats = [
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%d.%m.%Y',
            '%Y.%m.%d'
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%d-%m-%Y')
            except ValueError:
                continue
        
        return date_str  # Return as-is if can't parse
    
    def _dates_match(self, date1: str, date2: str, tolerance_days: int = None) -> bool:
        """
        Check if two dates match within tolerance
        
        Args:
            date1: First date in dd-mm-yyyy format
            date2: Second date in dd-mm-yyyy format
            tolerance_days: Number of days tolerance (uses class default if not specified)
        """
        if tolerance_days is None:
            tolerance_days = self.DATE_TOLERANCE_DAYS
            
        if date1 == date2:
            return True
        
        # If no tolerance allowed, dates must be exactly the same
        if tolerance_days == 0:
            return False
        
        try:
            # Parse dates
            d1 = datetime.strptime(date1, '%d-%m-%Y')
            d2 = datetime.strptime(date2, '%d-%m-%Y')
            
            # Check if within tolerance
            diff = abs((d1 - d2).days)
            return diff <= tolerance_days
            
        except (ValueError, TypeError):
            return False
    
    def _normalize_amount(self, amount_value: Any) -> Optional[float]:
        """Normalize amount to float"""
        if amount_value is None:
            return None
        
        try:
            # Handle string amounts with commas
            if isinstance(amount_value, str):
                amount_str = amount_value.replace(',', '').strip()
                return float(amount_str)
            return float(amount_value)
        except (ValueError, TypeError):
            return None
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize value for comparison"""
        if value is None:
            return None
        
        if isinstance(value, str):
            normalized = value.strip().upper()
            if normalized in ('', 'N/A', 'NA', 'NULL'):
                return None
            return normalized
        
        if isinstance(value, (int, float)):
            return round(float(value), 4)  # Round to 4 decimal places
        
        return str(value).strip().upper()
    
    def _normalize_product_type(self, product_type: Any) -> Optional[str]:
        """
        Normalize product type for comparison
        Maps various product type names to standardized values
        """
        if not product_type:
            return None
        
        product_str = str(product_type).strip().upper()
        
        # Map to standard values
        if product_str in ['SPOT']:
            return 'SPOT'
        elif product_str in ['FORWARD', 'SEGURO DE CAMBIO', 'SEGURO DE INFLACION', 'ARBITRAJE', 'NDF']:
            return 'FORWARD'
        
        return product_str  # Return as-is if no mapping found
    
    def _is_valid_value(self, value: Any) -> bool:
        """Check if a value should be considered valid"""
        if value is None:
            return False
        
        if isinstance(value, str):
            cleaned = value.strip().upper()
            if cleaned in ('', 'N/A', 'NA', 'NULL'):
                return False
        
        return True