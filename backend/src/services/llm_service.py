"""
LLM Service for processing email confirmations and extracting trade data
Supports multiple LLM providers: Anthropic Claude, GCP Vertex AI, OpenAI
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based email processing and trade data extraction"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on configuration"""
        try:
            if self.settings.llm_provider == "anthropic":
                self._initialize_anthropic()
            elif self.settings.llm_provider == "vertex":
                self._initialize_vertex()
            else:
                logger.warning(f"Unsupported LLM provider: {self.settings.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
    def _initialize_anthropic(self):
        """Initialize Anthropic Claude client"""
        if not self.settings.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not found in environment variables")
            return
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
            
            # Debug: Check available methods
            available_methods = [method for method in dir(self.client) if not method.startswith('_')]
            logger.info(f"Anthropic client methods: {available_methods}")
            
            logger.info("Anthropic Claude client initialized successfully")
        except ImportError:
            logger.error("Anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def _initialize_vertex(self):
        """Initialize GCP Vertex AI client (for future implementation)"""
        logger.info("Vertex AI initialization - TODO: Implement when needed")
        # TODO: Implement Vertex AI initialization
    
    def process_email_data(self, formatted_email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email data using LLM to extract structured trade information
        
        Args:
            formatted_email_data: Dictionary containing email content and metadata
            
        Returns:
            Structured trade data extracted by LLM
        """
        try:
            # Get the comprehensive prompt
            prompt = self._get_email_processing_prompt()
            
            # Format the prompt with email data
            formatted_prompt = prompt.format(formatted_data=self._format_email_for_llm(formatted_email_data))
            
            # Call LLM service (placeholder implementation)
            llm_response = self._call_llm_service(formatted_prompt)
            
            # Parse JSON response
            parsed_response = self._parse_llm_response(llm_response)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error processing email with LLM: {e}")
            # Return a fallback response
            return self._get_fallback_response(formatted_email_data)
    
    def _format_email_for_llm(self, email_data: Dict[str, Any]) -> str:
        """Format email data for LLM processing"""
        formatted_text = f"""
Email Subject: {email_data.get('subject', '')}
Email Sender: {email_data.get('sender_email', '')}
Email Body:
{email_data.get('body_content', '')}
        """
        
        if email_data.get('attachments_text'):
            formatted_text += f"\n\nAttachments:\n{email_data['attachments_text']}"
        
        return formatted_text
    
    def _call_llm_service(self, prompt: str) -> str:
        """Call the configured LLM service"""
        if not self.client:
            logger.warning("No LLM client available, using fallback")
            return self._get_mock_response()
        
        try:
            if self.settings.llm_provider == "anthropic":
                return self._call_anthropic(prompt)
            elif self.settings.llm_provider == "vertex":
                return self._call_vertex(prompt)
            else:
                logger.warning(f"Unsupported provider {self.settings.llm_provider}, using fallback")
                return self._get_mock_response()
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._get_mock_response()
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        try:
            logger.info(f"Calling Anthropic Claude model: {self.settings.anthropic_model}")
            
            # Check if client has messages attribute (newer SDK)
            if hasattr(self.client, 'messages'):
                logger.info("Using Anthropic Messages API")
                response = self.client.messages.create(
                    model=self.settings.anthropic_model,
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                response_text = response.content[0].text
            else:
                # Use completions API (available in the client)
                logger.info("Using Anthropic Completions API")
                
                # The completions API needs the model to be compatible
                # For Claude Sonnet 4, we need to try a different approach
                # Let's check if this is an older SDK version
                if hasattr(self.client, 'completions'):
                    # Format prompt for completions API
                    formatted_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
                    
                    response = self.client.completions.create(
                        model="claude-2.1",  # Use a model that works with completions API
                        prompt=formatted_prompt,
                        max_tokens_to_sample=4000,
                        temperature=0.1,
                        stop_sequences=["\n\nHuman:"]
                    )
                    response_text = response.completion
                else:
                    raise AttributeError("Cannot find appropriate API method on Anthropic client")
            
            logger.info("Anthropic API call successful")
            return response_text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            # Log more details about the client
            logger.error(f"Client type: {type(self.client)}")
            logger.error(f"Client attributes: {[attr for attr in dir(self.client) if not attr.startswith('_')]}")
            raise
    
    def _call_vertex(self, prompt: str) -> str:
        """Call GCP Vertex AI API (future implementation)"""
        # TODO: Implement Vertex AI call
        logger.info("Vertex AI call - TODO: Implement")
        raise NotImplementedError("Vertex AI implementation coming soon")
    
    def _get_mock_response(self) -> str:
        """Get mock response for fallback scenarios"""
        mock_response = {
            "Email": {
                "EmailSubject": "Trade Confirmation - Mock Response",
                "EmailSender": "mock@bank.com",
                "EmailDate": datetime.now().strftime('%d-%m-%Y'),
                "EmailTime": datetime.now().strftime('%H:%M:%S'),
                "Confirmation": "Yes",
                "Num_trades": 1
            },
            "Trades": [
                {
                    "BankTradeNumber": "MOCK001",
                    "CounterpartyName": "Mock Bank",
                    "ProductType": "Forward",
                    "Direction": "Buy",
                    "Currency1": "USD",
                    "QuantityCurrency1": 100000.00,
                    "Currency2": "CLP",
                    "SettlementType": "Entrega Física",
                    "SettlementCurrency": "N/A",
                    "TradeDate": datetime.now().strftime('%d-%m-%Y'),
                    "ValueDate": datetime.now().strftime('%d-%m-%Y'),
                    "MaturityDate": datetime.now().strftime('%d-%m-%Y'),
                    "PaymentDate": datetime.now().strftime('%d-%m-%Y'),
                    "ForwardPrice": 850.25,
                    "FixingReference": "USD Obs",
                    "CounterpartyPaymentMethod": "SWIFT",
                    "OurPaymentMethod": "SWIFT"
                }
            ]
        }
        
        return json.dumps(mock_response)
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse the LLM JSON response"""
        try:
            # The LLM should return clean JSON without markdown formatting
            cleaned_response = llm_response.strip()
            
            # Remove any potential markdown formatting
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            parsed_data = json.loads(cleaned_response.strip())
            
            # Validate the response structure
            if not self._validate_llm_response(parsed_data):
                raise ValueError("Invalid LLM response structure")
            
            return parsed_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.error(f"Raw response: {llm_response}")
            raise e
    
    def _validate_llm_response(self, response: Dict[str, Any]) -> bool:
        """Validate that the LLM response has the expected structure"""
        try:
            # Check for required top-level keys
            if 'Email' not in response or 'Trades' not in response:
                return False
            
            # Check Email section
            email_section = response['Email']
            required_email_fields = ['EmailSubject', 'EmailSender', 'EmailDate', 'EmailTime', 'Confirmation']
            for field in required_email_fields:
                if field not in email_section:
                    return False
            
            # Check Trades section
            trades_section = response['Trades']
            if not isinstance(trades_section, list):
                return False
            
            # Validate each trade
            for trade in trades_section:
                required_trade_fields = [
                    'BankTradeNumber', 'CounterpartyName', 'ProductType', 'Direction',
                    'Currency1', 'QuantityCurrency1', 'Currency2'
                ]
                for field in required_trade_fields:
                    if field not in trade:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating LLM response: {e}")
            return False
    
    def _get_fallback_response(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback response when LLM processing fails"""
        return {
            "Email": {
                "EmailSubject": email_data.get('subject', 'Unknown'),
                "EmailSender": email_data.get('sender_email', 'Unknown'),
                "EmailDate": datetime.now().strftime('%d-%m-%Y'),
                "EmailTime": datetime.now().strftime('%H:%M:%S'),
                "Confirmation": "Unknown",
                "Num_trades": 0
            },
            "Trades": []
        }
    
    def _get_email_processing_prompt(self) -> str:
        """
        Get the comprehensive LLM prompt for trade data extraction
        Based on the v1.0 specification from feedback.md
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
                        "EmailSubject": string,
                        "EmailSender": string,
                        "EmailDate": date (dd-mm-yyyy),
                        "EmailTime": time (hh:mm:ss),
                        "Confirmation": string (Yes or No)
                        "Num_trades": integer (the number of trades referred to in the email),
                    }},
                    "Trades": [
                        {{
                            "BankTradeNumber": string,
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
                            "ForwardPrice": number to a minimum of two decimal places,
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