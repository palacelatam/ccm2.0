"""
SMS Service for sending text messages via Twilio
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import asyncio

from config.settings import get_settings

logger = logging.getLogger(__name__)


class SmsService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client with credentials from settings"""
        # Get settings
        settings = get_settings()
        
        # Get Twilio credentials from settings
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_phone_number or '+12345678900'  # Default placeholder
        
        # Initialize Twilio client if credentials are available
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
        else:
            logger.warning("Twilio credentials not found in settings")
            self.client = None
            
        # Configuration
        self.rate_limit_per_minute = settings.sms_rate_limit_per_minute
        self.daily_limit_default = settings.sms_daily_limit_default
        
    async def send_sms(
        self,
        to_phone: str,
        message: str,
        client_id: Optional[str] = None,
        trade_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a single SMS message
        
        Args:
            to_phone: Recipient phone number in international format (e.g., +56912345678)
            message: SMS message content (max 160 characters for single SMS)
            client_id: Optional client ID for tracking
            trade_number: Optional trade number for tracking
            
        Returns:
            Dict containing delivery status and message details
        """
        if not self.client:
            error_msg = "SMS service not configured - Twilio credentials missing"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
        
        # Validate phone number format
        if not self._validate_phone_number(to_phone):
            error_msg = f"Invalid phone number format: {to_phone}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
        
        # Truncate message if too long (SMS limit is 160 characters)
        if len(message) > 160:
            logger.warning(f"Message truncated from {len(message)} to 160 characters")
            message = message[:157] + "..."
        
        try:
            # Send SMS via Twilio
            sms_message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_phone
                )
            )
            
            # Log successful send
            logger.info(f"SMS sent successfully to {to_phone} - SID: {sms_message.sid}")
            
            return {
                'success': True,
                'message_sid': sms_message.sid,
                'to_phone': to_phone,
                'from_phone': self.from_number,
                'message': message,
                'status': sms_message.status,
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'trade_number': trade_number
            }
            
        except TwilioException as e:
            error_msg = f"Twilio error sending SMS to {to_phone}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'to_phone': to_phone,
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'trade_number': trade_number
            }
        except Exception as e:
            error_msg = f"Unexpected error sending SMS to {to_phone}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'to_phone': to_phone,
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'trade_number': trade_number
            }
    
    async def send_bulk_sms(
        self,
        phone_list: List[str],
        message: str,
        client_id: Optional[str] = None,
        trade_number: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Send SMS to multiple recipients
        
        Args:
            phone_list: List of recipient phone numbers
            message: SMS message content
            client_id: Optional client ID for tracking
            trade_number: Optional trade number for tracking
            
        Returns:
            List of delivery results for each phone number
        """
        results = []
        
        # Remove duplicates from phone list
        unique_phones = list(set(phone_list))
        
        logger.info(f"Sending bulk SMS to {len(unique_phones)} recipients")
        
        # Send to each recipient with rate limiting
        for i, phone in enumerate(unique_phones):
            # Send SMS
            result = await self.send_sms(phone, message, client_id, trade_number)
            results.append(result)
            
            # Rate limiting: pause between messages if needed
            if i < len(unique_phones) - 1:  # Don't pause after last message
                await asyncio.sleep(60 / self.rate_limit_per_minute)  # Distribute sends across the minute
        
        # Calculate success rate
        successful = sum(1 for r in results if r.get('success'))
        logger.info(f"Bulk SMS complete: {successful}/{len(results)} successful")
        
        return results
    
    async def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get the delivery status of a sent SMS
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict containing message status details
        """
        if not self.client:
            logger.error("SMS service not configured")
            return None
        
        try:
            message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages(message_sid).fetch()
            )
            
            return {
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
            
        except TwilioException as e:
            logger.error(f"Error fetching message status for {message_sid}: {e}")
            return None
    
    def _validate_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - must start with + and contain only digits
        if not phone or not phone.startswith('+'):
            return False
        
        # Remove + and check if rest are digits
        digits = phone[1:].replace(' ', '').replace('-', '')
        if not digits.isdigit():
            return False
        
        # Check minimum length (typically at least 10 digits)
        if len(digits) < 10:
            return False
        
        # Check for Chilean numbers specifically (optional)
        if phone.startswith('+56'):
            # Chilean mobile numbers are +56 9 XXXX XXXX (11 digits total)
            if len(digits) != 11:
                logger.warning(f"Chilean phone number has unexpected length: {phone}")
        
        return True
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate SMS service configuration and connectivity
        
        Returns:
            Dict containing validation results
        """
        validation = {
            'configured': False,
            'credentials_present': False,
            'test_message': False,
            'errors': []
        }
        
        # Check credentials
        if self.account_sid and self.auth_token:
            validation['credentials_present'] = True
        else:
            validation['errors'].append("Twilio credentials not found in environment")
            return validation
        
        # Check client initialization
        if self.client:
            validation['configured'] = True
        else:
            validation['errors'].append("Twilio client not initialized")
            return validation
        
        # Try to fetch account info as a connectivity test
        try:
            account = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.api.accounts(self.account_sid).fetch()
            )
            validation['test_message'] = True
            validation['account_status'] = account.status
            logger.info(f"SMS service validation successful - Account status: {account.status}")
        except Exception as e:
            validation['errors'].append(f"Failed to connect to Twilio: {str(e)}")
            logger.error(f"SMS service validation failed: {e}")
        
        return validation


# Global instance
sms_service = SmsService()