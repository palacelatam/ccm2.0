"""
Settlement Instruction Service for generating populated settlement instruction documents
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import logging
from docx import Document
from docx.shared import Inches
import tempfile
import uuid

logger = logging.getLogger(__name__)


class SettlementInstructionService:
    """Service for generating populated settlement instruction documents"""
    
    def __init__(self):
        """Initialize the service"""
        # Get templates directory path
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'templates'
        )
        
        # Ensure templates directory exists
        os.makedirs(self.templates_dir, exist_ok=True)
        
        logger.info(f"Settlement Instruction Service initialized with templates dir: {self.templates_dir}")
    
    def create_standard_template(self) -> str:
        """
        Create a standard settlement instruction template for testing
        
        Returns:
            Path to created template file
        """
        template_path = os.path.join(self.templates_dir, 'standard_settlement_instruction.docx')
        
        # Create document
        doc = Document()
        
        # Add title
        title = doc.add_heading('SETTLEMENT INSTRUCTIONS', 0)
        title.alignment = 1  # Center alignment
        
        # Add document content with placeholders
        doc.add_paragraph('')  # Blank line
        
        # Client information section
        doc.add_heading('Client Information', level=1)
        p1 = doc.add_paragraph()
        p1.add_run('Client Name: ').bold = True
        p1.add_run('{client_name}')
        
        # Trade information section
        doc.add_heading('Trade Details', level=1)
        
        trade_info = [
            ('Trade Number:', '{trade_number}'),
            ('Trade Date:', '{trade_date}'),
            ('Value Date:', '{value_date}'),
            ('Counterparty:', '{counterparty_name}'),
            ('Product:', '{product_type}'),
            ('Currency Pair:', '{currency_1}/{currency_2}'),
            ('Amount:', '{amount_currency_1} {currency_1}'),
            ('Counter Amount:', '{amount_currency_2} {currency_2}'),
            ('Exchange Rate:', '{exchange_rate}'),
            ('Direction:', '{direction}')
        ]
        
        for label, placeholder in trade_info:
            p = doc.add_paragraph()
            p.add_run(label + ' ').bold = True
            p.add_run(placeholder)
        
        # Settlement information section
        doc.add_heading('Settlement Instructions', level=1)
        
        settlement_info = [
            ('Account Name:', '{account_name}'),
            ('Account Number:', '{account_number}'),
            ('Bank Name:', '{bank_name}'),
            ('SWIFT Code:', '{swift_code}'),
            ('Cutoff Time:', '{cutoff_time}'),
        ]
        
        for label, placeholder in settlement_info:
            p = doc.add_paragraph()
            p.add_run(label + ' ').bold = True
            p.add_run(placeholder)
        
        # Special instructions section
        doc.add_heading('Special Instructions', level=1)
        doc.add_paragraph('{special_instructions}')
        
        # Footer
        doc.add_paragraph('')
        footer_p = doc.add_paragraph('Generated automatically by Client Confirmation Manager 2.0')
        footer_p.alignment = 1  # Center alignment
        
        # Save template
        doc.save(template_path)
        logger.info(f"Standard template created at: {template_path}")
        
        return template_path
    
    def populate_template(
        self, 
        template_path: str, 
        trade_data: Dict[str, Any],
        settlement_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Populate a template with trade and settlement data
        
        Args:
            template_path: Path to the template document
            trade_data: Dictionary containing trade information
            settlement_data: Optional dictionary containing settlement account information
            
        Returns:
            Path to the populated document
        """
        try:
            # Load template
            doc = Document(template_path)
            
            # Prepare variable mapping (pass template name for language detection)
            template_name = os.path.basename(template_path)
            variables = self._prepare_variables(trade_data, settlement_data, template_name)
            
            # Replace placeholders in all paragraphs
            for paragraph in doc.paragraphs:
                self._replace_placeholders_in_paragraph(paragraph, variables)
            
            # Replace placeholders in tables (if any)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            self._replace_placeholders_in_paragraph(paragraph, variables)
            
            # Generate unique filename for populated document
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trade_id = trade_data.get('trade_number', 'unknown')
            filename = f"settlement_instruction_{trade_id}_{timestamp}.docx"
            output_path = os.path.join(self.templates_dir, 'generated', filename)
            
            # Ensure generated directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save populated document
            doc.save(output_path)
            
            logger.info(f"Settlement instruction generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error populating template: {e}")
            raise
    
    def _prepare_variables(
        self, 
        trade_data: Dict[str, Any], 
        settlement_data: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Prepare variable mapping from trade and settlement data
        
        Args:
            trade_data: Trade information
            settlement_data: Settlement account information
            template_name: Template filename to detect language
            
        Returns:
            Dictionary mapping placeholder names to values
        """
        variables = {}
        
        # Detect language from template name (default to Spanish)
        language = 'es'  # Default Spanish
        if template_name:
            template_lower = template_name.lower()
            if 'english' in template_lower or '_en' in template_lower or '-en' in template_lower:
                language = 'en'
            elif 'portuguese' in template_lower or 'portugues' in template_lower or '_pt' in template_lower or '-pt' in template_lower:
                language = 'pt'
        
        # Localization dictionaries
        direction_translations = {
            'en': {'BUY': 'Buy', 'SELL': 'Sell'},
            'es': {'BUY': 'Compra', 'SELL': 'Venta'},
            'pt': {'BUY': 'Compra', 'SELL': 'Venda'}
        }
        
        action_translations = {
            'en': {'credit': 'credit', 'debit': 'debit'},
            'es': {'credit': 'abonar', 'debit': 'cargar'},
            'pt': {'credit': 'creditar', 'debit': 'debitar'}
        }
        
        # Trade data variables
        trade_direction = str(trade_data.get('Direction', trade_data.get('direction', ''))).upper()
        
        # Get localized direction
        localized_direction = direction_translations[language].get(trade_direction, trade_direction)
        
        # Determine action words for Entrega Física based on trade direction
        # If Buy: we receive (credit) currency1 and pay (debit) currency2
        # If Sell: we pay (debit) currency1 and receive (credit) currency2
        if trade_direction == 'BUY':
            action_currency_1 = action_translations[language]['credit']  # receiving currency1
            action_currency_2 = action_translations[language]['debit']   # paying currency2
        else:  # SELL
            action_currency_1 = action_translations[language]['debit']   # paying currency1
            action_currency_2 = action_translations[language]['credit']  # receiving currency2
        
        variables.update({
            'client_name': str(trade_data.get('client_name', 'N/A')),
            'trade_number': str(trade_data.get('TradeNumber', trade_data.get('trade_number', 'N/A'))),
            'trade_date': self._format_date(trade_data.get('TradeDate', trade_data.get('trade_date'))),
            'value_date': self._format_date(trade_data.get('MaturityDate', trade_data.get('value_date'))),
            'counterparty_name': str(trade_data.get('CounterpartyName', trade_data.get('counterparty', 'N/A'))),
            'product_type': str(trade_data.get('Product', trade_data.get('product_type', 'N/A'))),
            'currency_1': str(trade_data.get('Currency1', trade_data.get('currency_1', 'N/A'))),
            'currency_2': str(trade_data.get('Currency2', trade_data.get('currency_2', 'N/A'))),
            'amount_currency_1': self._format_amount(trade_data.get('QuantityCurrency1', trade_data.get('amount_currency_1'))),
            'amount_currency_2': self._format_amount(trade_data.get('QuantityCurrency2', trade_data.get('amount_currency_2'))),
            'price': str(trade_data.get('Price', trade_data.get('exchange_rate', 'N/A'))),
            'direction': localized_direction,  # Use localized direction
            'direction_original': str(trade_data.get('Direction', trade_data.get('direction', 'N/A'))),  # Keep original for reference
            'action_currency_1': action_currency_1,
            'action_currency_2': action_currency_2,
            'client_name': str(trade_data.get('client_name', 'N/A')),
            'todays_date': datetime.now().strftime('%d/%m/%Y')
        })
        
        # Settlement data variables (if provided)
        if settlement_data:
            # Check if this is physical delivery (has inflow/outflow accounts) or compensación (single account)
            if 'inflow_account_number' in settlement_data:
                # Physical delivery - we have two accounts (inflow and outflow)
                # Map inflow/outflow to currency1/currency2 based on trade direction
                
                # Determine which currency is inflow and which is outflow
                currency_1 = str(trade_data.get('Currency1', 'N/A'))
                currency_2 = str(trade_data.get('Currency2', 'N/A'))
                
                if trade_direction == 'BUY':
                    # Buy: inflow is currency1, outflow is currency2
                    variables.update({
                        # Currency 1 account (inflow - receiving)
                        'account_number_currency_1': str(settlement_data.get('inflow_account_number', 'N/A')),
                        'account_bank_currency_1': str(settlement_data.get('inflow_bank_name', 'N/A')),
                        'account_name_currency_1': str(settlement_data.get('inflow_account_name', 'N/A')),
                        'swift_code_currency_1': str(settlement_data.get('inflow_swift_code', 'N/A')),
                        
                        # Currency 2 account (outflow - paying)
                        'account_number_currency_2': str(settlement_data.get('outflow_account_number', 'N/A')),
                        'account_bank_currency_2': str(settlement_data.get('outflow_bank_name', 'N/A')),
                        'account_name_currency_2': str(settlement_data.get('outflow_account_name', 'N/A')),
                        'swift_code_currency_2': str(settlement_data.get('outflow_swift_code', 'N/A')),
                    })
                else:  # SELL
                    # Sell: outflow is currency1, inflow is currency2
                    variables.update({
                        # Currency 1 account (outflow - paying)
                        'account_number_currency_1': str(settlement_data.get('outflow_account_number', 'N/A')),
                        'account_bank_currency_1': str(settlement_data.get('outflow_bank_name', 'N/A')),
                        'account_name_currency_1': str(settlement_data.get('outflow_account_name', 'N/A')),
                        'swift_code_currency_1': str(settlement_data.get('outflow_swift_code', 'N/A')),
                        
                        # Currency 2 account (inflow - receiving)
                        'account_number_currency_2': str(settlement_data.get('inflow_account_number', 'N/A')),
                        'account_bank_currency_2': str(settlement_data.get('inflow_bank_name', 'N/A')),
                        'account_name_currency_2': str(settlement_data.get('inflow_account_name', 'N/A')),
                        'swift_code_currency_2': str(settlement_data.get('inflow_swift_code', 'N/A')),
                    })
                
                # Also add generic fields for backwards compatibility
                variables.update({
                    'cutoff_time': str(settlement_data.get('cutoff_time', 'N/A')),
                    'special_instructions': str(settlement_data.get('special_instructions', 'Standard settlement instructions apply.'))
                })
            else:
                # Compensación - single account
                variables.update({
                    'account_name': str(settlement_data.get('account_name', 'N/A')),
                    'account_number': str(settlement_data.get('account_number', 'N/A')),
                    'account_bank': str(settlement_data.get('bank_name', 'N/A')),
                    'swift_code': str(settlement_data.get('swift_code', 'N/A')),
                    'cutoff_time': str(settlement_data.get('cutoff_time', 'N/A')),
                    'special_instructions': str(settlement_data.get('special_instructions', 'Standard settlement instructions apply.'))
                })
        else:
            # Default settlement data
            variables.update({
                'account_name': 'N/A',
                'account_number': 'N/A',
                'bank_name': 'N/A',
                'swift_code': 'N/A',
                'account_number_currency_1': 'N/A',
                'account_bank_currency_1': 'N/A',
                'account_number_currency_2': 'N/A',
                'account_bank_currency_2': 'N/A',
                'cutoff_time': 'N/A',
                'special_instructions': 'Standard settlement instructions apply.'
            })
        
        return variables
    
    def _replace_placeholders_in_paragraph(self, paragraph, variables: Dict[str, str]):
        """Replace placeholders in a paragraph with actual values"""
        full_text = paragraph.text
        
        for placeholder, value in variables.items():
            placeholder_with_braces = '{' + placeholder + '}'
            if placeholder_with_braces in full_text:
                full_text = full_text.replace(placeholder_with_braces, value)
        
        # Only update if text changed
        if full_text != paragraph.text:
            # Try to preserve formatting from the first run
            if paragraph.runs:
                first_run = paragraph.runs[0]
                font_name = first_run.font.name
                font_size = first_run.font.size
                bold = first_run.font.bold
                italic = first_run.font.italic
                underline = first_run.font.underline
                
                # Clear and update text
                paragraph.clear()
                new_run = paragraph.add_run(full_text)
                
                # Apply the preserved formatting
                if font_name:
                    new_run.font.name = font_name
                if font_size:
                    new_run.font.size = font_size
                if bold:
                    new_run.font.bold = bold
                if italic:
                    new_run.font.italic = italic
                if underline:
                    new_run.font.underline = underline
            else:
                # No existing runs, just update
                paragraph.clear()
                paragraph.add_run(full_text)
    
    def _format_date(self, date_value: Any) -> str:
        """Format date value for display"""
        if not date_value:
            return 'N/A'
        
        if isinstance(date_value, str):
            # Try to parse common date formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    return parsed_date.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return str(date_value)  # Return as-is if parsing fails
        
        if isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        
        return str(date_value)
    
    def _format_amount(self, amount_value: Any) -> str:
        """Format amount value for display"""
        if not amount_value:
            return 'N/A'
        
        try:
            # Try to format as number with thousands separator
            if isinstance(amount_value, (int, float)):
                return f"{amount_value:,.2f}"
            
            # Try to parse string as number
            if isinstance(amount_value, str):
                # Remove common separators and try parsing
                cleaned = amount_value.replace(',', '').replace(' ', '')
                if cleaned.replace('.', '').replace('-', '').isdigit():
                    num_value = float(cleaned)
                    return f"{num_value:,.2f}"
            
            return str(amount_value)
        except (ValueError, TypeError):
            return str(amount_value)
    
    async def generate_settlement_instruction(
        self,
        trade_data: Dict[str, Any],
        #template_name: str = 'standard_settlement_instruction.docx',
        template_name: str = 'Template Carta Instrucción Banco ABC.docx',
        settlement_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main method to generate a settlement instruction document
        
        Args:
            trade_data: Trade information dictionary
            template_name: Name of template file to use
            settlement_data: Optional settlement account information
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Get template path
            template_path = os.path.join(self.templates_dir, template_name)
            
            # Create standard template if it doesn't exist
            if not os.path.exists(template_path):
                logger.info(f"Template {template_name} not found, creating standard template")
                template_path = self.create_standard_template()
            
            # Populate template
            populated_doc_path = self.populate_template(template_path, trade_data, settlement_data)
            
            return {
                'success': True,
                'document_path': populated_doc_path,
                'template_used': template_name,
                'variables_populated': len(self._prepare_variables(trade_data, settlement_data)),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate settlement instruction: {e}")
            return {
                'success': False,
                'error': str(e),
                'template_used': template_name,
                'generated_at': datetime.now().isoformat()
            }


# Global instance
settlement_instruction_service = SettlementInstructionService()