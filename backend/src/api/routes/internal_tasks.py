"""
Internal task execution endpoints for Cloud Tasks
Handles various types of background tasks in a secure, organized manner
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from services.task_queue_service import task_queue_service, TaskType
from services.gmail_service import gmail_service
from services.client_service import ClientService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/internal/tasks", tags=["internal-tasks"])

class TaskPayload(BaseModel):
    """Standard task payload structure"""
    task_type: str
    task_id: str
    data: Dict[str, Any]
    created_at: str
    queue_used: str

class TaskExecutionResult(BaseModel):
    """Standard task execution result"""
    task_id: str
    success: bool
    message: str
    execution_time_ms: int
    retry_count: int

def verify_cloud_tasks_request(request: Request) -> bool:
    """Dependency to verify request came from Cloud Tasks"""
    if not task_queue_service.verify_task_request(dict(request.headers)):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Cloud Tasks request")
    return True

@router.post("/email", response_model=TaskExecutionResult)
async def execute_email_task(
    payload: TaskPayload,
    request: Request,
    verified: bool = Depends(verify_cloud_tasks_request)
):
    """
    Execute email sending tasks (confirmations, disputes, notifications)
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"📧 Executing email task: {payload.task_id} ({payload.task_type})")
        
        task_data = payload.data
        retry_count = int(request.headers.get('X-CloudTasks-TaskRetryCount', '0'))
        
        # Validate required email data
        if not all(key in task_data for key in ['to_email', 'subject', 'body']):
            raise ValueError("Missing required email fields: to_email, subject, body")
        
        # Execute email sending  
        success = await gmail_service.send_email(
            to_email=task_data['to_email'],
            subject=task_data['subject'],
            body=task_data['body'],
            cc_email=task_data.get('cc_email'),
            reply_to=task_data.get('reply_to', 'noreply@servicios.palace.cl'),
            attachments=task_data.get('attachments')  # Pass attachments if present
        )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if success:
            logger.info(f"✅ Email task {payload.task_id} completed successfully in {execution_time}ms")
            task_queue_service._task_stats['executed'] += 1
            
            return TaskExecutionResult(
                task_id=payload.task_id,
                success=True,
                message="Email sent successfully",
                execution_time_ms=execution_time,
                retry_count=retry_count
            )
        else:
            logger.error(f"❌ Email task {payload.task_id} failed to send email")
            task_queue_service._task_stats['failed'] += 1
            
            # Return success=False to trigger Cloud Tasks retry
            return TaskExecutionResult(
                task_id=payload.task_id,
                success=False,
                message="Failed to send email",
                execution_time_ms=execution_time,
                retry_count=retry_count
            )
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Email task {payload.task_id} failed with exception: {e}")
        task_queue_service._task_stats['failed'] += 1
        
        # Raise HTTP exception to trigger Cloud Tasks retry
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )

@router.post("/general", response_model=TaskExecutionResult)
async def execute_general_task(
    payload: TaskPayload,
    request: Request,
    verified: bool = Depends(verify_cloud_tasks_request)
):
    """
    Execute general background tasks (data sync, cleanup, etc.)
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"⚙️ Executing general task: {payload.task_id} ({payload.task_type})")
        
        task_data = payload.data
        retry_count = int(request.headers.get('X-CloudTasks-TaskRetryCount', '0'))
        
        # Route to appropriate handler based on task type
        if payload.task_type == TaskType.DATA_SYNC.value:
            result = await _handle_data_sync_task(task_data)
        elif payload.task_type == TaskType.CLEANUP.value:
            result = await _handle_cleanup_task(task_data)
        elif payload.task_type == TaskType.REPORT_GENERATION.value:
            result = await _handle_report_generation_task(task_data)
        else:
            logger.warning(f"Unknown general task type: {payload.task_type}")
            result = {"success": True, "message": f"Unhandled task type: {payload.task_type}"}
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result.get('success', True):
            logger.info(f"✅ General task {payload.task_id} completed successfully in {execution_time}ms")
            task_queue_service._task_stats['executed'] += 1
        else:
            logger.error(f"❌ General task {payload.task_id} failed: {result.get('message', 'Unknown error')}")
            task_queue_service._task_stats['failed'] += 1
        
        return TaskExecutionResult(
            task_id=payload.task_id,
            success=result.get('success', True),
            message=result.get('message', 'Task completed'),
            execution_time_ms=execution_time,
            retry_count=retry_count
        )
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"❌ General task {payload.task_id} failed with exception: {e}")
        task_queue_service._task_stats['failed'] += 1
        
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )

@router.post("/priority", response_model=TaskExecutionResult)
async def execute_priority_task(
    payload: TaskPayload,
    request: Request,
    verified: bool = Depends(verify_cloud_tasks_request)
):
    """
    Execute high-priority tasks (urgent notifications, system alerts)
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"🔥 Executing priority task: {payload.task_id} ({payload.task_type})")
        
        task_data = payload.data
        retry_count = int(request.headers.get('X-CloudTasks-TaskRetryCount', '0'))
        
        # Handle notification tasks
        if payload.task_type == TaskType.NOTIFICATION.value:
            result = await _handle_notification_task(task_data)
        else:
            logger.warning(f"Unknown priority task type: {payload.task_type}")
            result = {"success": True, "message": f"Unhandled priority task type: {payload.task_type}"}
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result.get('success', True):
            logger.info(f"✅ Priority task {payload.task_id} completed successfully in {execution_time}ms")
            task_queue_service._task_stats['executed'] += 1
        else:
            logger.error(f"❌ Priority task {payload.task_id} failed: {result.get('message', 'Unknown error')}")
            task_queue_service._task_stats['failed'] += 1
        
        return TaskExecutionResult(
            task_id=payload.task_id,
            success=result.get('success', True),
            message=result.get('message', 'Task completed'),
            execution_time_ms=execution_time,
            retry_count=retry_count
        )
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Priority task {payload.task_id} failed with exception: {e}")
        task_queue_service._task_stats['failed'] += 1
        
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )

@router.post("/file-processing", response_model=TaskExecutionResult)
async def execute_file_processing_task(
    payload: TaskPayload,
    request: Request,
    verified: bool = Depends(verify_cloud_tasks_request)
):
    """
    Execute file processing tasks (uploads, conversions, analysis)
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"📁 Executing file processing task: {payload.task_id} ({payload.task_type})")
        
        task_data = payload.data
        retry_count = int(request.headers.get('X-CloudTasks-TaskRetryCount', '0'))
        
        # Handle file upload tasks
        if payload.task_type == TaskType.FILE_UPLOAD.value:
            result = await _handle_file_upload_task(task_data)
        else:
            logger.warning(f"Unknown file processing task type: {payload.task_type}")
            result = {"success": True, "message": f"Unhandled file processing task type: {payload.task_type}"}
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result.get('success', True):
            logger.info(f"✅ File processing task {payload.task_id} completed successfully in {execution_time}ms")
            task_queue_service._task_stats['executed'] += 1
        else:
            logger.error(f"❌ File processing task {payload.task_id} failed: {result.get('message', 'Unknown error')}")
            task_queue_service._task_stats['failed'] += 1
        
        return TaskExecutionResult(
            task_id=payload.task_id,
            success=result.get('success', True),
            message=result.get('message', 'Task completed'),
            execution_time_ms=execution_time,
            retry_count=retry_count
        )
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"❌ File processing task {payload.task_id} failed with exception: {e}")
        task_queue_service._task_stats['failed'] += 1
        
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )

# Task handler functions (to be implemented based on specific needs)

async def _handle_data_sync_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle data synchronization tasks"""
    logger.info("Executing data sync task")
    
    # Implement data sync logic here
    # Example: sync data between systems, update caches, etc.
    
    return {"success": True, "message": "Data sync completed"}

async def _handle_cleanup_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cleanup tasks"""
    logger.info("Executing cleanup task")
    
    # Implement cleanup logic here
    # Example: delete old files, clean up database records, etc.
    
    return {"success": True, "message": "Cleanup completed"}

async def _handle_report_generation_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle report generation tasks"""
    logger.info("Executing report generation task")
    
    # Implement report generation logic here
    # Example: generate PDF reports, compile statistics, etc.
    
    return {"success": True, "message": "Report generation completed"}

async def _handle_notification_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle notification tasks"""
    logger.info("Executing notification task")
    
    # Implement notification logic here
    # Example: send system alerts, update dashboards, etc.
    
    return {"success": True, "message": "Notification sent"}

async def _handle_file_upload_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle file upload processing tasks"""
    logger.info("Executing file upload task")
    
    # Implement file processing logic here
    # Example: process uploaded files, extract data, move to permanent storage, etc.
    
    return {"success": True, "message": "File processing completed"}

# Management endpoints (for monitoring and debugging)

@router.get("/stats")
async def get_task_stats():
    """Get task execution statistics"""
    return {
        "stats": task_queue_service.get_stats(),
        "queues": {
            "general": await task_queue_service.get_queue_info(task_queue_service.TaskQueue.GENERAL),
            "email": await task_queue_service.get_queue_info(task_queue_service.TaskQueue.EMAIL),
            "priority": await task_queue_service.get_queue_info(task_queue_service.TaskQueue.PRIORITY)
        }
    }