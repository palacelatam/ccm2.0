"""
General-purpose task queue service using Google Cloud Tasks
Supports multiple queue types and task categories for reusable background processing
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from google.auth import default
import google.auth.impersonated_credentials

logger = logging.getLogger(__name__)

class TaskQueue(Enum):
    """Enum for available task queues with their configurations"""
    GENERAL = {
        'name': 'general-tasks',
        'max_delay_seconds': 3600,  # 1 hour
        'endpoint': '/api/internal/tasks/general'
    }
    EMAIL = {
        'name': 'email-tasks', 
        'max_delay_seconds': 86400,  # 24 hours
        'endpoint': '/api/internal/tasks/email'
    }
    PRIORITY = {
        'name': 'priority-tasks',
        'max_delay_seconds': 300,  # 5 minutes  
        'endpoint': '/api/internal/tasks/priority'
    }
    FILE_PROCESSING = {
        'name': 'general-tasks',  # Uses general queue but different endpoint
        'max_delay_seconds': 7200,  # 2 hours
        'endpoint': '/api/internal/tasks/file-processing'
    }
    DATA_PROCESSING = {
        'name': 'general-tasks',  # Uses general queue but different endpoint
        'max_delay_seconds': 3600,  # 1 hour
        'endpoint': '/api/internal/tasks/data-processing'
    }

class TaskType(Enum):
    """Enum for supported task types"""
    EMAIL_CONFIRMATION = 'email_confirmation'
    EMAIL_DISPUTE = 'email_dispute'
    FILE_UPLOAD = 'file_upload'
    DATA_SYNC = 'data_sync'
    NOTIFICATION = 'notification'
    CLEANUP = 'cleanup'
    REPORT_GENERATION = 'report_generation'

class TaskQueueService:
    """
    General-purpose task queue service for background processing
    
    Features:
    - Multiple queue support (general, email, priority)
    - Flexible task scheduling with delays
    - Automatic retry and error handling
    - Task authentication and security
    - Extensible for new task types
    """
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'ccm-dev-pool')
        self.location = os.getenv('CLOUD_TASKS_LOCATION', 'us-east4')
        self.cloud_run_url = os.getenv('CLOUD_RUN_URL', 'http://localhost:8000')
        
        # Initialize Cloud Tasks client
        self.client = None
        self.service_account_email = "cloud-tasks-manager@ccm-dev-pool.iam.gserviceaccount.com"
        
        # Task execution tracking
        self._task_stats = {
            'created': 0,
            'executed': 0,
            'failed': 0
        }
    
    async def initialize(self):
        """Initialize Cloud Tasks client with authentication"""
        try:
            # Try to use service account impersonation for Cloud Tasks access
            logger.info("Initializing Cloud Tasks client...")
            
            # Get default credentials (user or service account)
            source_credentials, _ = default()
            
            # Create impersonated credentials for Cloud Tasks service account
            target_scopes = [
                'https://www.googleapis.com/auth/cloud-tasks',
                'https://www.googleapis.com/auth/cloud-platform'
            ]
            
            impersonated_creds = google.auth.impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.service_account_email,
                target_scopes=target_scopes,
                delegates=[]
            )
            
            # Initialize Cloud Tasks client with impersonated credentials
            self.client = tasks_v2.CloudTasksClient(credentials=impersonated_creds)
            
            logger.info(f"✅ Cloud Tasks client initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloud Tasks client: {e}")
            raise
    
    async def create_task(
        self,
        task_type: TaskType,
        task_data: Dict[str, Any],
        queue: TaskQueue = TaskQueue.GENERAL,
        delay_seconds: int = 0,
        task_id: Optional[str] = None
    ) -> str:
        """
        Create a new task in the specified queue
        
        Args:
            task_type: Type of task to create
            task_data: Data payload for the task
            queue: Which queue to use for the task
            delay_seconds: Delay before task execution (0 for immediate)
            task_id: Optional custom task ID (auto-generated if not provided)
            
        Returns:
            str: Task name/ID for tracking
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Validate delay
            max_delay = queue.value['max_delay_seconds']
            if delay_seconds > max_delay:
                logger.warning(f"Delay {delay_seconds}s exceeds max {max_delay}s for {queue.name}, capping to max")
                delay_seconds = max_delay
            
            # Generate task ID if not provided
            if not task_id:
                timestamp = int(datetime.now(timezone.utc).timestamp())
                task_id = f"{task_type.value}_{timestamp}_{hash(str(task_data)) % 10000}"
            
            # Build task payload
            task_payload = {
                'task_type': task_type.value,
                'task_id': task_id,
                'data': task_data,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'queue_used': queue.name
            }
            
            # Create the task
            queue_path = self.client.queue_path(
                self.project_id, 
                self.location, 
                queue.value['name']
            )
            
            # Build HTTP request for Cloud Run endpoint
            http_request = {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': f"{self.cloud_run_url}{queue.value['endpoint']}",
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(task_payload).encode()
            }
            
            # Create the task object
            task_obj = {'http_request': http_request}
            
            # Add scheduling if delay is specified
            if delay_seconds > 0:
                schedule_time = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(schedule_time)
                task_obj['schedule_time'] = timestamp
                
                logger.info(f"📅 Task scheduled for: {schedule_time.isoformat()}")
            
            # Create the task
            response = self.client.create_task(
                parent=queue_path,
                task=task_obj
            )
            
            task_name = response.name
            self._task_stats['created'] += 1
            
            logger.info(f"✅ Created {task_type.value} task: {task_id} in {queue.name} queue")
            if delay_seconds > 0:
                logger.info(f"⏰ Task will execute in {delay_seconds} seconds")
            
            return task_name
            
        except Exception as e:
            logger.error(f"❌ Failed to create task {task_type.value}: {e}")
            raise
    
    async def create_email_task(
        self,
        email_data: Dict[str, Any],
        delay_seconds: int = 0,
        is_urgent: bool = False
    ) -> str:
        """
        Convenience method for creating email tasks
        
        Args:
            email_data: Email content and recipient information
            delay_seconds: Delay before sending email
            is_urgent: Whether to use priority queue
            
        Returns:
            str: Task name for tracking
        """
        queue = TaskQueue.PRIORITY if is_urgent else TaskQueue.EMAIL
        task_type = TaskType.EMAIL_CONFIRMATION
        
        # Determine task type from email data
        if email_data.get('is_dispute', False):
            task_type = TaskType.EMAIL_DISPUTE
        
        return await self.create_task(
            task_type=task_type,
            task_data=email_data,
            queue=queue,
            delay_seconds=delay_seconds
        )
    
    async def create_processing_task(
        self,
        task_type: TaskType,
        processing_data: Dict[str, Any],
        delay_seconds: int = 0
    ) -> str:
        """
        Convenience method for creating data/file processing tasks
        
        Args:
            task_type: Type of processing task
            processing_data: Data to be processed
            delay_seconds: Delay before processing
            
        Returns:
            str: Task name for tracking
        """
        if task_type == TaskType.FILE_UPLOAD:
            queue = TaskQueue.FILE_PROCESSING
        else:
            queue = TaskQueue.DATA_PROCESSING
        
        return await self.create_task(
            task_type=task_type,
            task_data=processing_data,
            queue=queue,
            delay_seconds=delay_seconds
        )
    
    async def create_notification_task(
        self,
        notification_data: Dict[str, Any],
        delay_seconds: int = 0
    ) -> str:
        """
        Convenience method for creating notification tasks
        
        Args:
            notification_data: Notification content and recipients
            delay_seconds: Delay before sending notification
            
        Returns:
            str: Task name for tracking
        """
        return await self.create_task(
            task_type=TaskType.NOTIFICATION,
            task_data=notification_data,
            queue=TaskQueue.PRIORITY,
            delay_seconds=delay_seconds
        )
    
    async def get_queue_info(self, queue: TaskQueue) -> Dict[str, Any]:
        """
        Get information about a specific queue
        
        Args:
            queue: Queue to get information about
            
        Returns:
            Dict containing queue statistics and configuration
        """
        try:
            if not self.client:
                await self.initialize()
            
            queue_path = self.client.queue_path(
                self.project_id,
                self.location, 
                queue.value['name']
            )
            
            queue_obj = self.client.get_queue(name=queue_path)
            
            return {
                'name': queue_obj.name,
                'state': queue_obj.state.name,
                'rate_limits': {
                    'max_dispatches_per_second': queue_obj.rate_limits.max_dispatches_per_second,
                    'max_concurrent_dispatches': queue_obj.rate_limits.max_concurrent_dispatches,
                },
                'retry_config': {
                    'max_attempts': queue_obj.retry_config.max_attempts,
                    'min_backoff': queue_obj.retry_config.min_backoff.seconds,
                    'max_backoff': queue_obj.retry_config.max_backoff.seconds,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue info for {queue.name}: {e}")
            return {}
    
    async def list_tasks(self, queue: TaskQueue, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List tasks in a specific queue
        
        Args:
            queue: Queue to list tasks from
            limit: Maximum number of tasks to return
            
        Returns:
            List of task information
        """
        try:
            if not self.client:
                await self.initialize()
            
            queue_path = self.client.queue_path(
                self.project_id,
                self.location,
                queue.value['name']
            )
            
            tasks = self.client.list_tasks(
                parent=queue_path,
                page_size=limit
            )
            
            task_list = []
            for task in tasks:
                task_info = {
                    'name': task.name,
                    'schedule_time': task.schedule_time.ToDatetime() if task.schedule_time else None,
                    'create_time': task.create_time.ToDatetime() if task.create_time else None,
                    'dispatch_count': task.dispatch_count,
                    'response_count': task.response_count,
                    'last_attempt_status': task.last_attempt.response_code if task.last_attempt else None
                }
                task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"Failed to list tasks for {queue.name}: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """Get task creation statistics"""
        return self._task_stats.copy()
    
    def verify_task_request(self, headers: Dict[str, str]) -> bool:
        """
        Verify that a request came from Cloud Tasks
        
        Args:
            headers: HTTP request headers
            
        Returns:
            bool: True if request is from Cloud Tasks
        """
        # DEBUG: Log all headers to see what Cloud Tasks actually sends
        logger.info(f"DEBUG: Received headers: {dict(headers)}")
        
        # Check for required Cloud Tasks headers (case-insensitive)
        queue_name = headers.get('x-cloudtasks-queuename', '') or headers.get('X-CloudTasks-QueueName', '')
        task_name = headers.get('x-cloudtasks-taskname', '') or headers.get('X-CloudTasks-TaskName', '')
        
        if not queue_name or not task_name:
            logger.warning("Missing required Cloud Tasks headers")
            logger.warning(f"DEBUG: queue_name='{queue_name}', task_name='{task_name}'")
            return False
        
        # Verify queue belongs to our project and is one of our queues
        expected_queues = [queue.value['name'] for queue in TaskQueue]
        queue_valid = any(queue == queue_name for queue in expected_queues)  # Exact match for queue name only
        
        if not queue_valid:
            logger.warning(f"Invalid queue in request: {queue_name}")
            logger.info(f"Expected one of: {expected_queues}")
            return False
        
        # Skip project ID verification for now since Cloud Tasks sends just the queue name
        # TODO: Add more sophisticated validation if needed
        
        logger.debug(f"✅ Verified Cloud Tasks request from queue: {queue_name}")
        return True

# Global instance
task_queue_service = TaskQueueService()