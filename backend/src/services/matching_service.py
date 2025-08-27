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
    """Service for matching email-extracted trades with client trades"""
    
    # Scoring weights (total up to ~90 points)
    SCORING_WEIGHTS = {
        'counterparty_exact': 30,
        'counterparty_partial': 20,
        'trade_date': 25,
        'currency_pair_exact': 20,
        'currency_pair_reversed': 15,
        'amount_exact': 15,
        'amount_close': 10
    }
    
    # Matching thresholds
    MATCH_THRESHOLD = 40  # Minimum score to be considered a match
    AUTO_CONFIRM_THRESHOLD = 60  # Score above which we auto-confirm
    
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
        
        for email_trade in email_trades:
            logger.info(f"Processing email trade: {email_trade.get('TradeNumber', 'Unknown')}")
            
            # Find potential matches for this email trade
            potential_matches = self._find_potential_matches(email_trade, client_trades, email_metadata)
            
            if potential_matches:
                # Get the best match (highest score)
                best_match = potential_matches[0]
                
                # Generate unique match_id for linking
                match_id = str(uuid.uuid4())
                
                # Check for field differences
                discrepancies = self._find_discrepancies(email_trade, best_match['trade'])
                
                # Determine status based on score and discrepancies
                status = self._determine_match_status(
                    best_match['score'], 
                    discrepancies
                )
                
                # Calculate confidence percentage
                confidence = round((best_match['score'] / 90) * 100)
                
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
                
                logger.info(f"Match found - Trade: {best_match['trade'].get('TradeNumber')}, "
                          f"Score: {best_match['score']}, Confidence: {confidence}%, "
                          f"Status: {status}, Match ID: {match_id}")
            else:
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
                
                logger.warning(f"No match found for email trade: {email_trade.get('TradeNumber', 'Unknown')}")
        
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
        
        logger.debug(f"Matching criteria - Date: {email_trade_date}, "
                    f"CCY1: {email_ccy1}, CCY2: {email_ccy2}, "
                    f"Amount: {email_amount}, Counterparty: {email_counterparty}")
        
        for client_trade in client_trades:
            score = 0
            reasons = []
            
            # 1. Counterparty match (30 points max)
            client_counterparty = str(client_trade.get('CounterpartyName', '')).lower()
            if email_counterparty and client_counterparty:
                email_cp_lower = email_counterparty.lower()
                if email_cp_lower == client_counterparty:
                    score += self.SCORING_WEIGHTS['counterparty_exact']
                    reasons.append(f"Counterparty exact: '{email_counterparty}'")
                elif email_cp_lower in client_counterparty or client_counterparty in email_cp_lower:
                    score += self.SCORING_WEIGHTS['counterparty_partial']
                    reasons.append(f"Counterparty partial: '{email_counterparty}' ~ '{client_trade.get('CounterpartyName')}'")
            
            # 2. Trade date match (25 points)
            client_trade_date = self._normalize_date(client_trade.get('TradeDate'))
            if email_trade_date and client_trade_date:
                if self._dates_match(email_trade_date, client_trade_date):
                    score += self.SCORING_WEIGHTS['trade_date']
                    reasons.append(f"Trade date: {email_trade_date}")
            
            # 3. Currency pair match (20 points max)
            client_ccy1 = str(client_trade.get('Currency1', '')).upper()
            client_ccy2 = str(client_trade.get('Currency2', '')).upper()
            if email_ccy1 and email_ccy2:
                if email_ccy1 == client_ccy1 and email_ccy2 == client_ccy2:
                    score += self.SCORING_WEIGHTS['currency_pair_exact']
                    reasons.append(f"Currency pair: {email_ccy1}/{email_ccy2}")
                elif email_ccy1 == client_ccy2 and email_ccy2 == client_ccy1:
                    score += self.SCORING_WEIGHTS['currency_pair_reversed']
                    reasons.append(f"Currency pair reversed: {email_ccy1}/{email_ccy2}")
            
            # 4. Amount match (15 points max)
            if email_amount is not None and email_amount > 0:
                client_amount = self._normalize_amount(client_trade.get('QuantityCurrency1'))
                if client_amount is not None and client_amount > 0:
                    amount_diff = abs(email_amount - client_amount) / max(email_amount, client_amount)
                    
                    if amount_diff <= self.AMOUNT_EXACT_TOLERANCE:
                        score += self.SCORING_WEIGHTS['amount_exact']
                        reasons.append(f"Amount exact: {email_amount:.2f}")
                    elif amount_diff <= self.AMOUNT_CLOSE_TOLERANCE:
                        score += self.SCORING_WEIGHTS['amount_close']
                        reasons.append(f"Amount close: {email_amount:.2f} ~ {client_amount:.2f}")
            
            # Add as potential match if score exceeds threshold
            if score >= self.MATCH_THRESHOLD:
                potential_matches.append({
                    'trade': client_trade,
                    'score': score,
                    'reasons': reasons
                })
                logger.debug(f"Potential match - Trade: {client_trade.get('TradeNumber')}, "
                           f"Score: {score}, Reasons: {reasons}")
        
        # Sort by score (highest first)
        return sorted(potential_matches, key=lambda x: x['score'], reverse=True)
    
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
            'QuantityCurrency1', 'ForwardPrice', 'SettlementType',
            'SettlementCurrency', 'TradeDate', 'ValueDate', 
            'MaturityDate', 'PaymentDate', 'FixingReference',
            'CounterpartyPaymentMethod', 'OurPaymentMethod'
        ]
        
        for field in fields_to_compare:
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
    
    def _is_valid_value(self, value: Any) -> bool:
        """Check if a value should be considered valid"""
        if value is None:
            return False
        
        if isinstance(value, str):
            cleaned = value.strip().upper()
            if cleaned in ('', 'N/A', 'NA', 'NULL'):
                return False
        
        return True