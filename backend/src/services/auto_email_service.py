"""
Auto-email service for automated confirmation and dispute email sending
Uses the general-purpose task queue system for delayed email processing
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .task_queue_service import task_queue_service, TaskType, TaskQueue
from .client_service import ClientService

logger = logging.getLogger(__name__)

class AutoEmailService:
    """
    Service for scheduling automated confirmation and dispute emails
    
    Integrates with:
    - TaskQueueService for delayed execution
    - ClientService for configuration and mailback content generation
    - GmailService (via task execution) for actual email sending
    """
    
    def __init__(self):
        self.client_service = ClientService()
    
    async def schedule_confirmation_email(
        self,
        client_id: str,
        email_confirmation_data: Dict[str, Any],
        delay_minutes: int = 30
    ) -> Optional[str]:
        """
        Schedule a confirmation email to be sent after a delay
        
        Args:
            client_id: Client ID for configuration lookup
            email_confirmation_data: Email confirmation data from the grid
            delay_minutes: Minutes to wait before sending email
            
        Returns:
            str: Task ID for tracking, or None if not scheduled
        """
        try:
            # Get client settings to check if auto-confirmation is enabled
            settings_response = await self.client_service.get_client_settings(client_id)
            if not settings_response.get('success'):
                logger.warning(f"Could not retrieve client settings for {client_id}")
                return None
            
            settings = settings_response.get('data', {})
            auto_settings = settings.get('automation', {})
            matched_settings = auto_settings.get('autoConfirmMatched', {})
            
            # Check if auto-confirmation for matched trades is enabled
            if not matched_settings.get('enabled', False):
                logger.info(f"Auto-confirmation disabled for client {client_id}")
                return None
            
            # Use configured delay or fallback to provided delay
            configured_delay_minutes = matched_settings.get('delayMinutes', delay_minutes)
            delay_seconds = configured_delay_minutes * 60
            
            # Generate mailback content (confirmation email)
            email_content = await self._generate_confirmation_email_content(
                client_id=client_id,
                email_data=email_confirmation_data
            )
            
            if not email_content:
                logger.error(f"Failed to generate confirmation email content for {client_id}")
                return None
            
            # Create the email task
            task_name = await task_queue_service.create_email_task(
                email_data=email_content,
                delay_seconds=delay_seconds,
                is_urgent=False
            )
            
            logger.info(f"✅ Scheduled confirmation email for client {client_id}, "
                       f"trade {email_confirmation_data.get('BankTradeNumber', 'unknown')}, "
                       f"delay: {configured_delay_minutes} minutes")
            
            return task_name
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule confirmation email for client {client_id}: {e}")
            return None
    
    async def schedule_dispute_email(
        self,
        client_id: str,
        email_confirmation_data: Dict[str, Any],
        differing_fields: list,
        delay_minutes: int = 60
    ) -> Optional[str]:
        """
        Schedule a dispute email to be sent after a delay
        
        Args:
            client_id: Client ID for configuration lookup
            email_confirmation_data: Email confirmation data from the grid
            differing_fields: List of fields that differ between client and bank data
            delay_minutes: Minutes to wait before sending email
            
        Returns:
            str: Task ID for tracking, or None if not scheduled
        """
        try:
            # Get client settings to check if auto-dispute is enabled
            settings_response = await self.client_service.get_client_settings(client_id)
            if not settings_response.get('success'):
                logger.warning(f"Could not retrieve client settings for {client_id}")
                return None
            
            settings = settings_response.get('data', {})
            auto_settings = settings.get('automation', {})
            disputed_settings = auto_settings.get('autoConfirmDisputed', {})
            
            # Check if auto-confirmation for disputed trades is enabled
            if not disputed_settings.get('enabled', False):
                logger.info(f"Auto-dispute email disabled for client {client_id}")
                return None
            
            # Use configured delay or fallback to provided delay
            configured_delay_minutes = disputed_settings.get('delayMinutes', delay_minutes)
            delay_seconds = configured_delay_minutes * 60
            
            # Generate mailback content (dispute email with differing fields)
            email_content = await self._generate_dispute_email_content(
                client_id=client_id,
                email_data=email_confirmation_data,
                differing_fields=differing_fields
            )
            
            if not email_content:
                logger.error(f"Failed to generate dispute email content for client {client_id}")
                return None
            
            # Mark as dispute email in the task data
            email_content['is_dispute'] = True
            
            # Create the email task
            task_name = await task_queue_service.create_email_task(
                email_data=email_content,
                delay_seconds=delay_seconds,
                is_urgent=False
            )
            
            logger.info(f"✅ Scheduled dispute email for client {client_id}, "
                       f"trade {email_confirmation_data.get('BankTradeNumber', 'unknown')}, "
                       f"fields: {differing_fields}, delay: {configured_delay_minutes} minutes")
            
            return task_name
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule dispute email for client {client_id}: {e}")
            return None
    
    async def _generate_confirmation_email_content(
        self,
        client_id: str,
        email_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate confirmation email content using the same logic as the frontend mailback
        
        Args:
            client_id: Client ID for organization name lookup
            email_data: Email confirmation data
            
        Returns:
            Dict containing email content (to_email, subject, body, etc.)
        """
        try:
            # Get organization name from client data (simplified - could be enhanced)
            organization_name = "Your Organization"  # TODO: Get from client settings
            
            # Extract basic information
            counterparty_name = email_data.get('CounterpartyName', email_data.get('EmailSender', 'Counterparty'))
            trade_number = email_data.get('BankTradeNumber', email_data.get('id', 'Unknown'))
            to_email = email_data.get('EmailSender', '')
            cc_email = 'confirmaciones_dev@servicios.palace.cl'
            
            if not to_email:
                logger.error("No recipient email address found")
                return None
            
            # Generate confirmation email body (no discrepancies)
            subject = f"Confirmation of {trade_number}"
            
            body = f"""Dear {counterparty_name},

With regards to trade number {trade_number}, {organization_name} confirms the trade as informed by you.

Best regards,
{organization_name}"""
            
            return {
                'to_email': to_email,
                'subject': subject,
                'body': body,
                'cc_email': cc_email,
                'reply_to': 'noreply@servicios.palace.cl',
                'trade_number': trade_number,
                'counterparty_name': counterparty_name,
                'organization_name': organization_name
            }
            
        except Exception as e:
            logger.error(f"Failed to generate confirmation email content: {e}")
            return None
    
    async def _generate_dispute_email_content(
        self,
        client_id: str,
        email_data: Dict[str, Any],
        differing_fields: list
    ) -> Optional[Dict[str, Any]]:
        """
        Generate dispute email content highlighting specific field differences
        
        Args:
            client_id: Client ID for organization name lookup
            email_data: Email confirmation data
            differing_fields: List of fields that differ
            
        Returns:
            Dict containing email content (to_email, subject, body, etc.)
        """
        try:
            # Get organization name from client data
            organization_name = "Your Organization"  # TODO: Get from client settings
            
            # Extract basic information
            counterparty_name = email_data.get('CounterpartyName', email_data.get('EmailSender', 'Counterparty'))
            trade_number = email_data.get('BankTradeNumber', email_data.get('id', 'Unknown'))
            to_email = email_data.get('EmailSender', '')
            cc_email = 'confirmaciones_dev@servicios.palace.cl'
            
            if not to_email:
                logger.error("No recipient email address found")
                return None
            
            # Generate dispute email body with discrepancies
            subject = f"Confirmation of {trade_number} - Discrepancy Notice"
            
            body = f"""Dear {counterparty_name},

With regards to trade number {trade_number}, {organization_name} has the following observations:

"""
            
            # Add each discrepancy
            for field in differing_fields:
                email_value = email_data.get(field, 'N/A')
                client_value = email_data.get(f'client_{field}', 'N/A')  # Assuming client values are prefixed
                body += f"{field}:\n"
                body += f"Your value: {email_value}\n"
                body += f"Our value: {client_value}\n\n"
            
            body += f"""Please review and confirm the correct information.

Best regards,
{organization_name}"""
            
            return {
                'to_email': to_email,
                'subject': subject,
                'body': body,
                'cc_email': cc_email,
                'reply_to': 'noreply@servicios.palace.cl',
                'trade_number': trade_number,
                'counterparty_name': counterparty_name,
                'organization_name': organization_name,
                'differing_fields': differing_fields
            }
            
        except Exception as e:
            logger.error(f"Failed to generate dispute email content: {e}")
            return None
    
    async def cancel_scheduled_email(self, task_name: str) -> bool:
        """
        Cancel a scheduled email task (if supported by Cloud Tasks)
        
        Args:
            task_name: Task name returned from schedule_*_email methods
            
        Returns:
            bool: True if cancelled successfully
        """
        # Note: Cloud Tasks doesn't directly support task cancellation
        # This would require implementing a cancellation mechanism
        # For now, just log the request
        logger.info(f"Email cancellation requested for task: {task_name}")
        logger.warning("Task cancellation not yet implemented")
        return False
    
    async def get_scheduled_emails_for_client(self, client_id: str) -> list:
        """
        Get list of scheduled emails for a specific client
        
        Args:
            client_id: Client ID to get scheduled emails for
            
        Returns:
            List of scheduled email information
        """
        # This would require implementing task tracking by client
        # For now, return empty list
        logger.info(f"Scheduled emails requested for client: {client_id}")
        logger.warning("Scheduled email listing not yet implemented")
        return []

# Global instance
auto_email_service = AutoEmailService()