"""
Email Parser Service for MSG/PDF Email Confirmation Processing
Handles parsing and LLM extraction of bank confirmation emails to v1.0 structure
"""

import os
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import extract_msg
import PyPDF2
from io import BytesIO
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class EmailParserService:
    """Service for parsing bank confirmation emails from MSG/PDF files"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def process_email_file(self, file_content: bytes, filename: str, client_name: str = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process MSG or PDF email file and extract confirmation data
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename for type detection
            client_name: Name of the client for context
            
        Returns:
            Tuple of (email_data, errors)
        """
        errors = []
        
        try:
            if filename.lower().endswith('.msg'):
                return self._process_msg_file(file_content, errors)
            elif filename.lower().endswith('.pdf'):
                return self._process_pdf_file(file_content, errors)
            else:
                errors.append(f"Unsupported file type: {filename}")
                return {}, errors
                
        except Exception as e:
            error_msg = f"Failed to process email file {filename}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return {}, errors
    
    def _process_msg_file(self, file_content: bytes, errors: List[str]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process MSG (Outlook) email file
        Priority: PDF attachments first, then email body
        
        Args:
            file_content: MSG file content as bytes
            errors: List to append errors to
            
        Returns:
            Tuple of (email_data, errors)
        """
        try:
            # Create temporary file for extract_msg to process
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.msg', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            msg = None
            try:
                # Extract email data using extract_msg
                msg = extract_msg.Message(temp_file_path)
                
                # Extract PDF attachments if available
                pdf_attachments = self._extract_pdf_attachments_from_msg(msg)
                
                # Determine what content to process with LLM
                # Priority: PDF attachments > email body
                content_to_process = ''
                processing_source = 'none'
                
                if pdf_attachments:
                    # Use PDF attachment text content
                    content_to_process = pdf_attachments
                    processing_source = 'pdf_attachment'
                    logger.info(f"Processing PDF attachment content ({len(content_to_process)} chars)")
                elif msg.body:
                    # Fallback to email body if no PDFs found
                    content_to_process = msg.body
                    processing_source = 'email_body'
                    logger.info(f"No PDF attachments found, processing email body ({len(content_to_process)} chars)")
                else:
                    errors.append("No content found in email (no body or PDF attachments)")
                    logger.warning("No processable content found in MSG file")
                
                # Extract sender email address
                sender_email = msg.sender or ''
                
                email_data = {
                    'sender_email': sender_email,
                    'subject': msg.subject or '',
                    'body_content': content_to_process,  # This will be either PDF text or email body
                    'date': msg.date.strftime('%d-%m-%Y') if msg.date else datetime.now().strftime('%d-%m-%Y'),
                    'time': msg.date.strftime('%H:%M:%S') if msg.date else datetime.now().strftime('%H:%M:%S'),
                    'attachments_text': '',  # We're already handling attachments above
                    'processing_source': processing_source  # Track where content came from
                }
                
                # Process with LLM to extract structured trade data
                llm_extracted_data = self._extract_trade_data_with_llm(email_data, client_name)
                
                result = {
                    'email_metadata': email_data,
                    'llm_extracted_data': llm_extracted_data,
                    'processed_at': datetime.now().isoformat(),
                    'processing_source': processing_source
                }
                
                return result, errors
                
            finally:
                # Close the message object to release file handle
                if msg is not None:
                    try:
                        msg.close()
                    except:
                        pass  # Ignore errors when closing
                
                # Clean up temporary file with retry logic
                try:
                    os.unlink(temp_file_path)
                except PermissionError:
                    # If file is still locked, try again after a short delay
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_file_path)
                    except:
                        # Log but don't fail if we can't delete temp file
                        logger.warning(f"Could not delete temporary file {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Error deleting temporary file {temp_file_path}: {e}")
                
        except Exception as e:
            error_msg = f"Error processing MSG file: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return {}, errors
    
    def _process_pdf_file(self, file_content: bytes, errors: List[str]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process PDF email file
        
        Args:
            file_content: PDF file content as bytes
            errors: List to append errors to
            
        Returns:
            Tuple of (email_data, errors)
        """
        try:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # For PDF files, we have limited metadata extraction capability
            # Extract what we can from the text content
            email_data = {
                'sender_email': self._extract_sender_from_text(text_content),
                'subject': self._extract_subject_from_text(text_content),
                'body_content': text_content,
                'date': datetime.now().strftime('%d-%m-%Y'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'attachments_text': ''
            }
            
            # Process with LLM to extract structured trade data
            llm_extracted_data = self._extract_trade_data_with_llm(email_data, client_name)
            
            return {
                'email_metadata': email_data,
                'llm_extracted_data': llm_extracted_data,
                'processed_at': datetime.now().isoformat()
            }, errors
            
        except Exception as e:
            error_msg = f"Error processing PDF file: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return {}, errors
    
    def _extract_pdf_attachments_from_msg(self, msg) -> str:
        """
        Extract text content from PDF attachments in MSG file
        
        Args:
            msg: extract_msg Message object
            
        Returns:
            Combined text from all PDF attachments
        """
        pdf_text = ""
        try:
            for attachment in msg.attachments:
                filename = attachment.longFilename or attachment.shortFilename or 'Unknown'
                if filename.lower().endswith('.pdf') and hasattr(attachment, 'data') and attachment.data:
                    try:
                        # Extract text from PDF attachment
                        pdf_reader = PyPDF2.PdfReader(BytesIO(attachment.data))
                        attachment_text = ""
                        for page in pdf_reader.pages:
                            attachment_text += page.extract_text() + "\n"
                        
                        if attachment_text.strip():
                            pdf_text += f"\n--- PDF Attachment: {filename} ---\n"
                            pdf_text += attachment_text + "\n"
                            logger.info(f"Extracted {len(attachment_text)} chars from PDF: {filename}")
                    except Exception as e:
                        logger.warning(f"Error extracting PDF {filename}: {str(e)}")
                        continue
        except Exception as e:
            logger.warning(f"Error processing attachments: {str(e)}")
        
        return pdf_text
    
    def _extract_attachments_text(self, msg) -> str:
        """
        Extract text content from MSG attachments
        
        Args:
            msg: extract_msg Message object
            
        Returns:
            Combined text from all attachments
        """
        attachments_text = ""
        try:
            for attachment in msg.attachments:
                if hasattr(attachment, 'data') and attachment.data:
                    # Try to decode as text
                    try:
                        attachment_text = attachment.data.decode('utf-8', errors='ignore')
                        attachments_text += f"\n--- Attachment: {attachment.longFilename or 'Unknown'} ---\n"
                        attachments_text += attachment_text + "\n"
                    except:
                        # Skip binary attachments
                        continue
        except Exception as e:
            logger.warning(f"Error extracting attachments: {str(e)}")
        
        return attachments_text
    
    def _extract_sender_from_text(self, text: str) -> str:
        """Extract sender email from PDF text content"""
        lines = text.split('\n')
        for line in lines:
            if '@' in line and ('from:' in line.lower() or 'de:' in line.lower()):
                # Extract email address pattern
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                matches = re.findall(email_pattern, line)
                if matches:
                    return matches[0]
        return ''
    
    def _extract_subject_from_text(self, text: str) -> str:
        """Extract subject from PDF text content"""
        lines = text.split('\n')
        for line in lines:
            if 'subject:' in line.lower() or 'asunto:' in line.lower():
                # Extract text after 'Subject:' or 'Asunto:'
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return ''
    
    def _extract_trade_data_with_llm(self, email_data: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Extract structured trade data using LLM
        
        Args:
            email_data: Raw email data
            client_name: Name of the client for context
            
        Returns:
            Structured trade data in v1.0 format
        """
        # Placeholder implementation - in real system, this would call the LLM service
        # For now, return mock data structure that matches the expected format
        
        formatted_email_data = {
            'subject': email_data.get('subject', ''),
            'body_content': email_data.get('body_content', ''),
            'sender_email': email_data.get('sender_email', ''),
            'attachments_text': email_data.get('attachments_text', '')
        }
        
        # Debug logging
        logger.info(f"EmailParserService: Calling LLM with client_name: {client_name}")
        
        # Call the actual LLM service
        llm_response = self.llm_service.process_email_data(formatted_email_data, client_name)
        
        return llm_response
    
    def get_llm_prompt(self) -> str:
        """
        Get the comprehensive LLM prompt for trade data extraction
        Based on the v1.0 prompt from feedback.md
        """
        return """You are receiving an email from a bank. This email is likely to be about a trade confirmation.
        
                Tell me if this email is requesting the confirmation of a trade(s) or not. It could feasibly be about something else.

                {formatted_data}

                If there is a reference to a trade confirmation, set the Confirmation field to Yes.
                If there is no reference to a trade confirmation, set the Confirmation field to No.

                The most likely type of emails that we will process are those that request the confirmation of a trade, and they come from banks.
                
                Typically (but not always), the subject line of an email about a trade confirmation will include the words "Confirmación" or "Confirmation" and the body will also probably refer to a confirmation.

                If this email is indeed about a trade confirmation, you need to extract the data as per the following instructions:
                
                Look for the trade number in the subject of the email and in the body. This is usually a number, e.g. "1234567890"). Can also be named as a reference and is one of the most important fields. It will always be present on a confirmation email.

                I also need you to extract some data from the email body. Data in the email body should also override data in the email subject, as it is possible that the conversation
                has moved on from the initial subject line.

                Remember that this email is written from the Bank's perspective, not you, the Client's. Therefore, the details of the trade are reversed. Specific consequences of this can include the following:
                - Counterparty: the bank could refer to you as the counterparty. However, from your perspective, the bank is the counterparty.
                - Currency 1: the bank could refer to the currency you pay as Currency 1. However, from your perspective, the currency you pay is Currency 2.
                - Currency 2: the bank could refer to the currency you receive as Currency 2. However, from your perspective, the currency you receive is Currency 1.
                - Direction: the bank could refer to the direction of the trade as "Buy" or "Sell". However, from your perspective, the direction of the trade is the opposite.
                - Counterparty Payment Method: the bank will refer to the payment method they use as "Forma de Pago Nuestra" or something similar. This should be saved in the field "Counterparty Payment Method".
                - Our Payment Method: the bank will refer to the payment method you use as "Forma de Pago Contraparte" or something similar. This should be saved in the field "Our Payment Method".
                
                The specific data you need to find is as follows:
                 
                - Trade Number, a number indicating the ID of the trade, can also be named as a reference. This is usually a number, e.g. "1234567890").
                - Counterparty ID, typically the bank's ID. It may not be present in the email, in which case you should leave it blank.
                - Counterparty Name, the bank's name
                - Product Type, if this says "Spot", save as "Spot". If it says "Seguro de Cambio", "Seguro de Inflación", "Arbitraje", "Forward", "NDF", save as "Forward".
                - Direction, from your perspective as the client, are you buying from the bank or selling to the bank? Save as "Buy" or "Sell".
                - Currency 1, an ISO 4217 currency code, the currency you are buying or selling according to the Direction field. Remember if the bank says "Buy", you are selling to the bank (and you should store it as "Sell"), and if the bank says "Sell", you are buying from the bank (and you should store it as "Buy").
                - Amount of Currency 1, a number, the amount of currency 1 you are buying or selling according to the Direction field.
                - Currency 2, an ISO 4217 currency code, the other currency of the trade.
                - Settlement Type, if it says "Compensación" or "Non-Deliverable", save as "Compensación". If it says "Entrega Física" or "Deliverable", save as "Entrega Física".
                - Settlement Currency, an ISO 4217 currency code. If the Settlement Type is "Entrega Física", this field is unlikely to exist or have a value, in which case set as "N/A".
                - Trade Date, a date, which can be in different formats
                - Value Date, a date, which can be in different formats
                - Maturity Date, a date, which can be in different formats
                - Payment Date, a date, which can be in different formats
                - Duration, an integer number, indicating the number of days between the value date and the maturity date
                - Forward Price, a number usually with decimal places
                - Fixing Reference, If you see anything such as "USD Obs", "Dolar Observado", "CLP10", "Dólar Observado", "CLP Obs", save as "USD Obs".
                - Counterparty Payment Method, look in fields labelled "Forma de Pago". Usually one of the following values: "Trans Alto Valor", "ComBanc", "SWIFT", "Cuenta Corriente".
                - Our Payment Method, look in fields labelled "Forma de Pago". Usually one of the following values: "Trans Alto Valor", "ComBanc", "SWIFT", "Cuenta Corriente"

                Return this in a JSON format, but do not include any markdown formatting such as ```json or ```. This causes errors so I really need you to return it without any markdown formatting.
                DO NOT return any other text than the JSON, as this causes errors.

                The required structured of the JSON file is as follows:

                {{
                    "Email": {{
                        "Email_subject": string,
                        "Email_sender": string,
                        "Email_date": date (dd-mm-yyyy),
                        "Email_time": time (hh:mm:ss),
                        "Confirmation": string (Yes or No)
                        "Num_trades": integer (the number of trades referred to in the email),
                    }},
                    "Trades": [
                        {{
                            "TradeNumber": string,
                            "CounterpartyName": string,
                            "ProductType": string,
                            "Direction": string ("Buy" or "Sell"),
                            "Currency1": string (ISO 4217 currency code),
                            "QuantityCurrency1": number to a minimum of two decimal places,
                            "Currency2": string (ISO 4217 currency code),
                            "SettlementType": string, ("Compensación" or "Entrega Física"),
                            "SettlementCurrency": string (ISO 4217 currency code),
                            "TradeDate": date in format dd-mm-yyyy,
                            "ValueDate": date in format dd-mm-yyyy,
                            "MaturityDate": date in format dd-mm-yyyy,
                            "PaymentDate": date in format dd-mm-yyyy,
                            "Price": number to a minimum of two decimal places,
                            "FixingReference": string,
                            "CounterpartyPaymentMethod": string,
                            "OurPaymentMethod": string
                        }}
                        // Repeat as many times as there are trades in the email
                    ]
                }}

                Now STOP for a minute, before you return the JSON. I need you to compare the data you have extracted into the Trades array in the JSON with the data in the email. If there is any difference on a specific field, overwrite the data in the JSON with the data you think is correct in the email.
                
                I repeat, the email body is the best source of truth.

                If the Direction field is "Buy", then QuantityCurrency1 is the amount of currency 1 you are buying from the bank. If the Direction field is "Sell", then QuantityCurrency1 is the amount of currency 1 you are selling to the bank.

                DO NOT return any other text than the JSON, as this causes errors. NO MARKDOWN.
            """