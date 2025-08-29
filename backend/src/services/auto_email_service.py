"""
Auto-email service for automated confirmation and dispute email sending
Uses the general-purpose task queue system for delayed email processing
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .task_queue_service import task_queue_service, TaskType, TaskQueue

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
        # Remove circular import - client data will be passed as parameters
        pass

    async def schedule_trade_email(self, email_data: Dict[str, Any], delay_seconds: int = 0) -> Optional[str]:
        """
        Schedule a trade-related email (confirmation or dispute) based on provided data
        
        Args:
            email_data: Complete email information including client_id, trade details, etc.
            delay_seconds: How many seconds to delay the email
            
        Returns:
            Task name if scheduled successfully, None otherwise
        """
        try:
            email_type = email_data.get("email_type", "unknown")
            client_id = email_data.get("client_id", "")
            
            logger.info(f"📧 Scheduling {email_type} email for client {client_id} with {delay_seconds}s delay")
            
            # Generate the actual email content based on email type
            if email_type == "confirmation":
                email_content = await self._generate_confirmation_email_content(
                    client_id=client_id,
                    email_data=email_data
                )
            elif email_type == "dispute":
                email_content = await self._generate_dispute_email_content(
                    client_id=client_id,
                    email_data=email_data,
                    differing_fields=email_data.get("differing_fields", [])
                )
            else:
                logger.error(f"Unknown email type: {email_type}")
                return None
                
            if not email_content:
                logger.error(f"Failed to generate {email_type} email content for client {client_id}")
                return None
            
            # Add metadata from original email_data to the email content
            email_content.update({
                'client_id': client_id,
                'match_id': email_data.get('match_id', ''),
                'trade_id': email_data.get('trade_id', ''),
                'email_id': email_data.get('email_id', ''),
                'email_type': email_type,
                'comparison_status': email_data.get('comparison_status', ''),
                'differing_fields': email_data.get('differing_fields', []),
                'confidence_score': email_data.get('confidence_score', 0),
                'scheduled_at': email_data.get('scheduled_at', '')
            })
            
            # Create the email task using task queue service
            # Both confirmation and dispute emails should use the email queue
            task_name = await task_queue_service.create_email_task(
                email_data=email_content,  # Now contains to_email, subject, body
                delay_seconds=delay_seconds,
                is_urgent=False  # Always use email queue for email tasks
            )
            
            if task_name:
                logger.info(f"✅ Successfully scheduled {email_type} email task: {task_name}")
                return task_name
            else:
                logger.error(f"❌ Failed to schedule {email_type} email task")
                return None
                
        except Exception as e:
            logger.error(f"Error scheduling trade email: {e}")
            return None
    
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
            # Extract basic information using the correct field names from client_service
            counterparty_name = email_data.get('counterparty_name', 'Counterparty')
            trade_number = email_data.get('bank_trade_number', 'Unknown')
            email_id = email_data.get('email_id', '')
            
            # Get the email address from the original email document
            # We need to fetch this from Firestore since it's not included in the match data
            if not email_id:
                logger.error("No email_id provided to fetch recipient email address")
                return None
            
            # Import here to avoid circular imports
            from config.firebase_config import get_cmek_firestore_client
            db = get_cmek_firestore_client()
            
            # Get the original email document to extract sender email
            email_ref = db.collection('clients').document(client_id).collection('emails').document(email_id)
            email_doc = email_ref.get()
            
            if not email_doc.exists:
                logger.error(f"Email document {email_id} not found for client {client_id}")
                return None
            
            email_doc_data = email_doc.to_dict()
            
            # Get sender email from programmatically extracted email metadata (not LLM data)
            # Try multiple possible locations for the sender email
            email_metadata = email_doc_data.get('email_metadata', {})
            
            to_email = (email_metadata.get('sender_email') or 
                       email_doc_data.get('senderEmail') or
                       email_doc_data.get('from') or 
                       email_doc_data.get('sender') or '')
            
            # Validate email address
            if not to_email or '@' not in to_email:
                logger.error(f"No valid email address found for automated email. Sender: '{to_email}'")
                return None
            
            # Get client's confirmation email and organization name
            client_ref = db.collection('clients').document(client_id)
            client_doc = client_ref.get()
            
            if not client_doc.exists:
                logger.error(f"Client document {client_id} not found")
                return None
                
            client_data = client_doc.to_dict()
            cc_email = client_data.get('confirmationEmail', 'confirmaciones_dev@servicios.palace.cl')  # Fallback to default
            organization_name = client_data.get('name', client_data.get('organizationName', 'Your Organization'))  # Get organization name
            
            # Get language preference (default to Spanish)
            preferences = client_data.get('preferences', {})
            language = preferences.get('language', 'es')
            
            # Generate confirmation email body based on language
            if language == 'es':
                subject = f"Confirmación de {trade_number}"
                body = f"""Estimado {counterparty_name},

Con respecto a la operación número {trade_number}, {organization_name} confirma la operación según nos informó.

Saludos cordiales,
{organization_name}"""
            elif language == 'pt':
                subject = f"Confirmação de {trade_number}"
                body = f"""Caro {counterparty_name},

Com relação à operação número {trade_number}, {organization_name} confirma a operação conforme informado por você.

Atenciosamente,
{organization_name}"""
            else:  # English
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
            # Extract basic information using the correct field names from client_service
            counterparty_name = email_data.get('counterparty_name', 'Counterparty')
            trade_number = email_data.get('bank_trade_number', 'Unknown')
            email_id = email_data.get('email_id', '')
            
            # Get the email address from the original email document
            if not email_id:
                logger.error("No email_id provided to fetch recipient email address")
                return None
            
            # Import here to avoid circular imports
            from config.firebase_config import get_cmek_firestore_client
            db = get_cmek_firestore_client()
            
            # Get the original email document to extract sender email
            email_ref = db.collection('clients').document(client_id).collection('emails').document(email_id)
            email_doc = email_ref.get()
            
            if not email_doc.exists:
                logger.error(f"Email document {email_id} not found for client {client_id}")
                return None
            
            email_doc_data = email_doc.to_dict()
            
            # Get sender email from programmatically extracted email metadata (not LLM data)
            # Try multiple possible locations for the sender email
            email_metadata = email_doc_data.get('email_metadata', {})
            
            to_email = (email_metadata.get('sender_email') or 
                       email_doc_data.get('senderEmail') or
                       email_doc_data.get('from') or 
                       email_doc_data.get('sender') or '')
            
            # Validate email address
            if not to_email or '@' not in to_email:
                logger.error(f"No valid email address found for automated email. Sender: '{to_email}'")
                return None
            
            # Get client's confirmation email and organization name
            client_ref = db.collection('clients').document(client_id)
            client_doc = client_ref.get()
            
            if not client_doc.exists:
                logger.error(f"Client document {client_id} not found")
                return None
                
            client_data = client_doc.to_dict()
            cc_email = client_data.get('confirmationEmail', 'confirmaciones_dev@servicios.palace.cl')  # Fallback to default
            organization_name = client_data.get('name', client_data.get('organizationName', 'Your Organization'))  # Get organization name
            
            # Get language preference (default to Spanish)
            preferences = client_data.get('preferences', {})
            language = preferences.get('language', 'es')
            
            # Generate dispute email body with discrepancies based on language
            if language == 'es':
                subject = f"Confirmación de {trade_number} - Aviso de Discrepancia"
                body = f"""Estimado {counterparty_name},

Con respecto a la operación número {trade_number}, {organization_name} tiene las siguientes observaciones:

"""
                # Add each discrepancy with actual values - now each item is a dict with field, email_value, client_value
                # Debug logging
                logger.info(f"DEBUG: differing_fields = {differing_fields}")
                
                for discrepancy in differing_fields:
                    field_name = discrepancy.get('field', 'Unknown')
                    email_value = discrepancy.get('email_value', 'N/A')
                    client_value = discrepancy.get('client_value', 'N/A')
                    
                    body += f"{field_name}:\n"
                    body += f"Su valor: {email_value}\n"
                    body += f"Nuestro valor: {client_value}\n\n"
                
                body += f"""Por favor revise y confirme la información correcta.

Saludos cordiales,
{organization_name}"""
            elif language == 'pt':
                subject = f"Confirmação de {trade_number} - Aviso de Discrepância"
                body = f"""Caro {counterparty_name},

Com relação à operação número {trade_number}, {organization_name} tem as seguintes observações:

"""
                # Add each discrepancy with actual values
                for discrepancy in differing_fields:
                    field_name = discrepancy.get('field', 'Unknown')
                    email_value = discrepancy.get('email_value', 'N/A')
                    client_value = discrepancy.get('client_value', 'N/A')
                    
                    body += f"{field_name}:\n"
                    body += f"Seu valor: {email_value}\n"
                    body += f"Nosso valor: {client_value}\n\n"
                
                body += f"""Por favor, revise e confirme as informações corretas.

Atenciosamente,
{organization_name}"""
            else:  # English
                subject = f"Confirmation of {trade_number} - Discrepancy Notice"
                body = f"""Dear {counterparty_name},

With regards to trade number {trade_number}, {organization_name} has the following observations:

"""
                # Add each discrepancy with actual values
                for discrepancy in differing_fields:
                    field_name = discrepancy.get('field', 'Unknown')
                    email_value = discrepancy.get('email_value', 'N/A')
                    client_value = discrepancy.get('client_value', 'N/A')
                    
                    body += f"{field_name}:\n"
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