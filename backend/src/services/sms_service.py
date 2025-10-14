"""
SMS Service for sending text messages via Bird API
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)


class SmsService:
    """Service for sending SMS messages via Bird API"""

    def __init__(self):
        """Initialize Bird API client with credentials from settings"""
        # Get settings
        settings = get_settings()

        # Get Bird credentials from settings
        self.api_key = settings.bird_api_key
        self.workspace_id = settings.bird_workspace_id
        self.channel_id = settings.bird_channel_id

        # Validate credentials
        if self.api_key and self.workspace_id and self.channel_id:
            logger.info("Bird SMS service initialized successfully")
            self.configured = True
        else:
            logger.warning("Bird credentials not found in settings")
            self.configured = False

        # Configuration
        self.rate_limit_per_minute = settings.sms_rate_limit_per_minute
        self.daily_limit_default = settings.sms_daily_limit_default

        # Bird API endpoint
        self.api_url = f"https://api.bird.com/workspaces/{self.workspace_id}/channels/{self.channel_id}/messages"

    async def send_sms(
        self,
        to_phone: str,
        message: str,
        client_id: Optional[str] = None,
        trade_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a single SMS message via Bird API

        Args:
            to_phone: Recipient phone number in international format (e.g., +56912345678)
            message: SMS message content (max 160 characters for single SMS)
            client_id: Optional client ID for tracking
            trade_number: Optional trade number for tracking

        Returns:
            Dict containing delivery status and message details
        """
        if not self.configured:
            error_msg = "SMS service not configured - Bird credentials missing"
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

        # Prepare Bird API request
        headers = {
            "Authorization": f"AccessKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }

        payload = {
            "receiver": {
                "contacts": [
                    {
                        "identifierValue": to_phone
                    }
                ]
            },
            "body": {
                "type": "text",
                "text": {
                    "text": message
                }
            }
        }

        try:
            # Send SMS via Bird API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                response_data = response.json()

            # Log successful send
            logger.info(f"SMS sent successfully to {to_phone} via Bird API")

            return {
                'success': True,
                'message_id': response_data.get('id'),
                'to_phone': to_phone,
                'message': message,
                'status': response_data.get('status'),
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'trade_number': trade_number,
                'response': response_data
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"Bird API error sending SMS to {to_phone}: HTTP {e.response.status_code}"
            logger.error(f"{error_msg} - {e.response.text}")
            return {
                'success': False,
                'error': error_msg,
                'error_details': e.response.text,
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
            'connectivity_test': False,
            'errors': []
        }

        # Check credentials
        if self.api_key and self.workspace_id and self.channel_id:
            validation['credentials_present'] = True
            validation['configured'] = True
        else:
            validation['errors'].append("Bird credentials not found in environment")
            return validation

        # Test connectivity by validating the API endpoint is reachable
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Simple HEAD request to check if endpoint is accessible
                response = await client.head(
                    f"https://api.bird.com/workspaces/{self.workspace_id}",
                    headers={"Authorization": f"AccessKey {self.api_key}"}
                )
                validation['connectivity_test'] = True
                logger.info("SMS service validation successful - Bird API accessible")
        except Exception as e:
            validation['errors'].append(f"Failed to connect to Bird API: {str(e)}")
            logger.error(f"SMS service validation failed: {e}")

        return validation


# Global instance
sms_service = SmsService()
