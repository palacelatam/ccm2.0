"""
Gmail API service for monitoring and processing emails
"""

import os
import base64
import email
import io
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import PyPDF2
import extract_msg

from .client_service import ClientService

logger = logging.getLogger(__name__)

class GmailService:
    """Service for monitoring Gmail inbox and processing trade confirmation emails"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.client_service = ClientService()
        self.monitoring_email = "confirmaciones_dev@palace.cl"
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.use_user_id = False  # Flag to determine if we need to use userId parameter
        
        # Email processing state
        self._last_history_id = None
        self._processed_message_ids = set()
        
        # Monitoring control
        self._monitoring_task = None
        self._monitoring_active = False
        
    async def initialize(self):
        """Initialize Gmail API service with authentication"""
        try:
            # Try to use service account key if it exists
            # Check both relative and absolute paths
            creds_filename = os.getenv('GMAIL_SERVICE_ACCOUNT_PATH', 'gmail-service-account.json')
            
            # Try to find the credentials file
            if os.path.isabs(creds_filename):
                creds_path = creds_filename
            else:
                # Check in backend directory first
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                creds_path = os.path.join(backend_dir, creds_filename)
                if not os.path.exists(creds_path):
                    # Fall back to current directory
                    creds_path = creds_filename
            
            logger.info(f"Looking for Gmail service account key at: {creds_path}")
            if os.path.exists(creds_path):
                # Use service account key file if available
                logger.info("Using service account key file for Gmail API")
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                self.credentials = ServiceAccountCredentials.from_service_account_file(
                    creds_path, 
                    scopes=['https://www.googleapis.com/auth/gmail.readonly']
                )
                # Apply domain-wide delegation for service account key
                delegated_credentials = self.credentials.with_subject(self.monitoring_email)
            else:
                # Use Application Default Credentials with service account impersonation
                logger.info("Using Application Default Credentials for Gmail API")
                from google.auth import default
                import google.auth.impersonated_credentials
                import google.auth.transport.requests
                
                # Get the default credentials (your user account)
                source_credentials, project = default()
                
                # Define the service account to impersonate
                service_account_email = "gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com"
                
                # Create impersonated credentials
                logger.info(f"Impersonating service account: {service_account_email}")
                
                # First, impersonate the service account
                target_scopes = ['https://www.googleapis.com/auth/gmail.readonly']
                
                impersonated_creds = google.auth.impersonated_credentials.Credentials(
                    source_credentials=source_credentials,
                    target_principal=service_account_email,
                    target_scopes=target_scopes,
                    delegates=[]
                )
                
                # Refresh the impersonated credentials to get an access token
                request = google.auth.transport.requests.Request()
                impersonated_creds.refresh(request)
                
                # Now we need to use the service account to access Gmail with domain delegation
                # Since we can't use .with_subject() on impersonated credentials,
                # we'll use the Gmail API with the 'userId' parameter set to the monitoring email
                logger.info(f"Will access Gmail as: {self.monitoring_email}")
                delegated_credentials = impersonated_creds
                
                # Store this for later use in API calls
                self.use_user_id = True  # Flag to use userId parameter instead of 'me'
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=delegated_credentials)
            
            # Test connection and get initial state
            await self._initialize_monitoring_state()
            
            logger.info(f"Gmail service initialized for {self.monitoring_email}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise
    
    async def _initialize_monitoring_state(self):
        """Initialize monitoring state with current inbox state"""
        try:
            # Get current history ID for future monitoring
            profile = await self._execute_gmail_api(
                self.service.users().getProfile(userId=self.monitoring_email if self.use_user_id else 'me')
            )
            self._last_history_id = profile.get('historyId')
            
            logger.info(f"Initialized monitoring state with history ID: {self._last_history_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring state: {e}")
            raise
    
    async def _execute_gmail_api(self, request):
        """Execute Gmail API request in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, request.execute)
    
    async def check_for_new_emails(self) -> List[Dict[str, Any]]:
        """
        Check for new emails since last check
        Returns list of processed email results
        """
        try:
            if not self.service:
                await self.initialize()
            
            # Get new messages using history
            new_messages = await self._get_new_messages()
            
            if not new_messages:
                logger.debug("No new emails found")
                return []
            
            logger.info(f"Found {len(new_messages)} new emails to process")
            
            # Process each new email
            results = []
            for message in new_messages:
                try:
                    result = await self._process_email_message(message)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Failed to process message {message.get('id')}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to check for new emails: {e}")
            return []
    
    async def _get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages since last history ID"""
        try:
            # If no history ID, get recent messages (last 24 hours)
            if not self._last_history_id:
                return await self._get_recent_messages()
            
            # Get history changes since last check
            history = await self._execute_gmail_api(
                self.service.users().history().list(
                    userId=self.monitoring_email if self.use_user_id else 'me',
                    startHistoryId=self._last_history_id
                )
            )
            
            # Update history ID
            self._last_history_id = history.get('historyId')
            
            # Extract new messages from history
            new_messages = []
            for history_record in history.get('history', []):
                for message in history_record.get('messagesAdded', []):
                    message_id = message['message']['id']
                    if message_id not in self._processed_message_ids:
                        # Get full message details
                        full_message = await self._execute_gmail_api(
                            self.service.users().messages().get(
                                userId=self.monitoring_email if self.use_user_id else 'me', 
                                id=message_id, 
                                format='full'
                            )
                        )
                        new_messages.append(full_message)
                        
            return new_messages
            
        except HttpError as e:
            if e.resp.status == 404:
                # History ID expired, get recent messages instead
                logger.warning("History ID expired, falling back to recent messages")
                return await self._get_recent_messages()
            raise
    
    async def _get_recent_messages(self) -> List[Dict[str, Any]]:
        """Get messages from last 24 hours as fallback"""
        try:
            # Calculate timestamp for 24 hours ago
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            query = f'after:{int(yesterday.timestamp())}'
            
            # Search for recent messages
            messages = await self._execute_gmail_api(
                self.service.users().messages().list(
                    userId=self.monitoring_email if self.use_user_id else 'me',
                    q=query,
                    maxResults=50
                )
            )
            
            # Get full details for each message
            full_messages = []
            for message in messages.get('messages', []):
                message_id = message['id']
                if message_id not in self._processed_message_ids:
                    full_message = await self._execute_gmail_api(
                        self.service.users().messages().get(
                            userId=self.monitoring_email if self.use_user_id else 'me', 
                            id=message_id, 
                            format='full'
                        )
                    )
                    full_messages.append(full_message)
            
            return full_messages
            
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []
    
    async def _process_email_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single email message and extract trade confirmations"""
        try:
            message_id = message['id']
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extract email metadata
            sender = headers.get('From', '')
            subject = headers.get('Subject', '')
            date_str = headers.get('Date', '')
            to_addresses = headers.get('To', '') + ',' + headers.get('Cc', '')
            
            # Check if this email is for our monitoring address
            if self.monitoring_email not in to_addresses:
                logger.debug(f"Email {message_id} not sent to monitoring address, skipping")
                return None
            
            # Determine client ID from To: field or other logic
            client_id = await self._determine_client_id(headers)
            if not client_id:
                logger.warning(f"Could not determine client ID for email {message_id}")
                return None
            
            # Extract email body and attachments
            email_body = await self._extract_email_body(message)
            attachments = await self._extract_pdf_attachments(message)
            
            if not attachments:
                logger.debug(f"No PDF attachments found in email {message_id}")
                return None
            
            logger.info(f"Processing email {message_id} from {sender} with {len(attachments)} PDF attachments")
            
            # Process each PDF attachment
            processing_results = []
            for attachment_name, pdf_content in attachments:
                try:
                    # Create temporary file-like object for processing
                    pdf_file = io.BytesIO(pdf_content)
                    pdf_file.name = attachment_name
                    
                    # Create Gmail email data structure
                    gmail_email_data = {
                        'sender': sender,
                        'subject': subject,
                        'date': date_str,
                        'body': email_body
                    }
                    
                    # Use existing email processing pipeline via ClientService adapter
                    result = await self.client_service.process_gmail_attachment(
                        client_id=client_id,
                        gmail_email_data=gmail_email_data,
                        attachment_data=pdf_content,
                        filename=attachment_name
                    )
                    
                    if result:
                        processing_results.append(result)
                        
                except Exception as e:
                    logger.error(f"Failed to process PDF attachment {attachment_name}: {e}")
                    continue
            
            # Mark message as processed
            self._processed_message_ids.add(message_id)
            
            # Return processing summary
            if processing_results:
                total_trades = sum(r.get('trades_extracted', 0) for r in processing_results)
                total_matches = sum(r.get('matches_found', 0) for r in processing_results)
                total_duplicates = sum(r.get('duplicates_found', 0) for r in processing_results)
                
                return {
                    'message_id': message_id,
                    'sender': sender,
                    'subject': subject,
                    'client_id': client_id,
                    'attachments_processed': len(processing_results),
                    'total_trades_extracted': total_trades,
                    'total_matches_found': total_matches,
                    'total_duplicates_found': total_duplicates,
                    'processing_results': processing_results
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to process email message: {e}")
            return None
    
    async def _determine_client_id(self, headers: Dict[str, str]) -> Optional[str]:
        """Determine client ID from email headers"""
        try:
            # Get To: field and extract client email addresses
            to_field = headers.get('To', '')
            cc_field = headers.get('Cc', '')
            
            # Combine and parse email addresses
            all_recipients = f"{to_field},{cc_field}"
            
            # Extract email addresses (simple regex for email extraction)
            import re
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            email_addresses = re.findall(email_pattern, all_recipients)
            
            # Filter out our monitoring email
            client_emails = [
                email for email in email_addresses 
                if email.lower() != self.monitoring_email.lower()
            ]
            
            if not client_emails:
                logger.warning("No client email addresses found in To/Cc fields")
                return None
            
            # For now, use the first non-monitoring email as client identifier
            # In production, this would look up the client by email in the database
            primary_client_email = client_emails[0]
            
            # TODO: Implement actual database lookup to map email to client_id
            # For development, we'll use a simple mapping
            logger.info(f"Client email identified: {primary_client_email}")
            
            # For development purposes, return a test client ID
            # This should be replaced with actual database lookup:
            # client = await self.client_service.get_client_by_email(primary_client_email)
            # return client.id if client else None
            
            return "dev-client-001"  # Temporary until client email mapping is implemented
            
        except Exception as e:
            logger.error(f"Error determining client ID from headers: {e}")
            return None
    
    async def _extract_email_body(self, message: Dict[str, Any]) -> str:
        """Extract plain text body from email message"""
        try:
            def extract_text_from_part(part):
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                for subpart in part.get('parts', []):
                    text = extract_text_from_part(subpart)
                    if text:
                        return text
                
                return ''
            
            return extract_text_from_part(message['payload'])
            
        except Exception as e:
            logger.error(f"Failed to extract email body: {e}")
            return ''
    
    async def _extract_pdf_attachments(self, message: Dict[str, Any]) -> List[Tuple[str, bytes]]:
        """Extract PDF attachments from email message"""
        try:
            attachments = []
            
            def process_part(part):
                filename = None
                # Check for filename in headers
                for header in part.get('headers', []):
                    if header['name'].lower() == 'content-disposition':
                        value = header['value']
                        if 'filename=' in value:
                            filename = value.split('filename=')[1].strip('"\'')
                
                # Check if it's a PDF attachment
                if (filename and filename.lower().endswith('.pdf') and 
                    part.get('body', {}).get('attachmentId')):
                    
                    attachment_id = part['body']['attachmentId']
                    return (filename, attachment_id)
                
                # Process sub-parts
                results = []
                for subpart in part.get('parts', []):
                    result = process_part(subpart)
                    if result:
                        results.append(result)
                return results
            
            # Find all PDF attachments
            pdf_attachments = process_part(message['payload'])
            if isinstance(pdf_attachments, tuple):
                pdf_attachments = [pdf_attachments]
            elif not isinstance(pdf_attachments, list):
                pdf_attachments = []
            
            # Download attachment content
            for filename, attachment_id in pdf_attachments:
                try:
                    attachment = await self._execute_gmail_api(
                        self.service.users().messages().attachments().get(
                            userId=self.monitoring_email if self.use_user_id else 'me',
                            messageId=message['id'],
                            id=attachment_id
                        )
                    )
                    
                    data = attachment.get('data')
                    if data:
                        content = base64.urlsafe_b64decode(data)
                        attachments.append((filename, content))
                        
                except Exception as e:
                    logger.error(f"Failed to download attachment {filename}: {e}")
                    continue
            
            return attachments
            
        except Exception as e:
            logger.error(f"Failed to extract PDF attachments: {e}")
            return []
    
    
    async def start_monitoring(self, check_interval: int = 30):
        """
        Start continuous email monitoring
        
        Args:
            check_interval: Seconds between checks (default: 30 seconds for near real-time)
        """
        # Check if monitoring is already active
        if self._monitoring_active:
            logger.warning("Gmail monitoring is already active")
            return
        
        self._monitoring_active = True
        logger.info(f"Starting Gmail monitoring with {check_interval}s interval")
        
        while self._monitoring_active:
            try:
                results = await self.check_for_new_emails()
                
                if results:
                    logger.info(f"Processed {len(results)} emails in this check")
                    for result in results:
                        logger.info(
                            f"Email from {result['sender']}: "
                            f"{result['total_trades_extracted']} trades, "
                            f"{result['total_matches_found']} matches, "
                            f"{result['total_duplicates_found']} duplicates"
                        )
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                logger.info("Gmail monitoring task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in email monitoring loop: {e}")
                # Wait before retrying
                await asyncio.sleep(min(60, check_interval))
        
        self._monitoring_active = False
        logger.info("Gmail monitoring stopped")
    
    async def stop_monitoring(self):
        """Stop the monitoring task"""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        logger.info("Gmail monitoring stop requested")

# Global instance
gmail_service = GmailService()