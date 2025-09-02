"""
CSV Parser Service for Client Trade Data
Handles parsing and transformation of client CSV files to v1.0 structure
"""

import csv
import io
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CSVParserService:
    """Service for parsing client trade CSV files"""
    
    # Mapping from CSV headers to our v1.0 field names
    FIELD_MAPPING = {
        'Trade ID': 'TradeNumber',
        'Counterparty': 'CounterpartyName', 
        'Product Type': 'ProductType',
        'Trade Date': 'TradeDate',
        'Value Date': 'ValueDate',
        'Direction': 'Direction',
        'Currency 1': 'Currency1',
        'Currency 2': 'Currency2',
        'Amount': 'QuantityCurrency1',
        'Forward Price': 'Price',
        'Maturity Date': 'MaturityDate',
        'Fixing Reference': 'FixingReference',
        'Settlement Type': 'SettlementType',
        'Settlement Currency': 'SettlementCurrency',
        'Payment Date': 'PaymentDate',
        'Our Payment Method': 'OurPaymentMethod',
        'Counterparty Payment Method': 'CounterpartyPaymentMethod'
    }
    
    # Date fields that need format conversion
    DATE_FIELDS = ['TradeDate', 'ValueDate', 'MaturityDate', 'PaymentDate']
    
    # Numeric fields that need conversion
    NUMERIC_FIELDS = ['QuantityCurrency1', 'Price']
    
    def parse_csv_content(self, csv_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse CSV content and transform to v1.0 structure
        
        Args:
            csv_content: Raw CSV content as string
            
        Returns:
            Tuple of (parsed_trades, errors)
        """
        trades = []
        errors = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header
                try:
                    trade_data = self._transform_row(row)
                    trades.append(trade_data)
                except Exception as e:
                    error_msg = f"Row {row_num}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
            
            logger.info(f"Successfully parsed {len(trades)} trades with {len(errors)} errors")
            return trades, errors
            
        except Exception as e:
            error_msg = f"Failed to parse CSV: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return [], errors
    
    def _transform_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform a single CSV row to v1.0 structure
        
        Args:
            row: Dictionary representing one CSV row
            
        Returns:
            Transformed trade data
        """
        transformed = {}
        
        # Map fields using the field mapping
        for csv_field, v1_field in self.FIELD_MAPPING.items():
            if csv_field in row:
                value = row[csv_field].strip()
                
                # Handle empty values
                if not value or value.upper() in ['N/A', 'NULL', '']:
                    transformed[v1_field] = None if v1_field in self.DATE_FIELDS else value
                    continue
                
                # Convert dates from DD/MM/YYYY to DD-MM-YYYY
                if v1_field in self.DATE_FIELDS:
                    transformed[v1_field] = self._convert_date_format(value)
                
                # Convert numeric fields
                elif v1_field in self.NUMERIC_FIELDS:
                    transformed[v1_field] = self._convert_numeric(value)
                
                # Keep other fields as-is
                else:
                    transformed[v1_field] = value
            else:
                # Field not found in CSV
                if v1_field in self.DATE_FIELDS:
                    transformed[v1_field] = None
                elif v1_field in self.NUMERIC_FIELDS:
                    transformed[v1_field] = 0.0
                else:
                    transformed[v1_field] = ""
        
        # Add metadata
        transformed['status'] = 'unmatched'
        transformed['createdAt'] = datetime.now().isoformat()
        
        return transformed
    
    def _convert_date_format(self, date_str: str) -> str:
        """
        Convert date from DD/MM/YYYY to DD-MM-YYYY format
        
        Args:
            date_str: Date string in DD/MM/YYYY format
            
        Returns:
            Date string in DD-MM-YYYY format
        """
        try:
            if '/' in date_str:
                # Convert DD/MM/YYYY to DD-MM-YYYY
                return date_str.replace('/', '-')
            else:
                # Already in correct format or different format
                return date_str
        except Exception as e:
            raise ValueError(f"Invalid date format: {date_str}. Expected DD/MM/YYYY")
    
    def _convert_numeric(self, value_str: str) -> float:
        """
        Convert string to numeric value
        
        Args:
            value_str: String representation of number
            
        Returns:
            Float value
        """
        try:
            # Remove any comma separators and convert to float
            cleaned_value = value_str.replace(',', '')
            return float(cleaned_value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value: {value_str}")
    
    def validate_required_fields(self, trades: List[Dict[str, Any]]) -> List[str]:
        """
        Validate that required fields are present in parsed trades
        
        Args:
            trades: List of parsed trade dictionaries
            
        Returns:
            List of validation errors
        """
        required_fields = ['TradeNumber', 'CounterpartyName', 'ProductType']
        errors = []
        
        for i, trade in enumerate(trades, start=1):
            for field in required_fields:
                if not trade.get(field):
                    errors.append(f"Trade {i}: Missing required field '{field}'")
        
        return errors