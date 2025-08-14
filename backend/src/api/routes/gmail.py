"""
Gmail monitoring API endpoints
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any, List
import logging

from models.base import APIResponse
from api.middleware.auth_middleware import get_auth_context, require_permission
from services.gmail_service import gmail_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gmail")


@router.post("/check-now", response_model=APIResponse[List[Dict[str, Any]]])
@require_permission("manage_gmail")
async def check_gmail_now(request: Request):
    """
    Manually trigger Gmail check for new emails
    Admin only endpoint
    """
    try:
        auth_context = get_auth_context(request)
        logger.info(f"Admin {auth_context.uid} manually triggered Gmail check")
        
        # Check for new emails
        results = await gmail_service.check_for_new_emails()
        
        return APIResponse(
            status="success",
            data=results,
            message=f"Gmail check completed. Processed {len(results)} new emails."
        )
        
    except Exception as e:
        logger.error(f"Failed to check Gmail: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check Gmail: {str(e)}"
        )


@router.post("/start-monitoring", response_model=APIResponse[Dict[str, Any]])
@require_permission("manage_gmail")
async def start_gmail_monitoring(
    request: Request,
    background_tasks: BackgroundTasks,
    check_interval: int = 30
):
    """
    Start Gmail monitoring in background
    Admin only endpoint
    
    Args:
        check_interval: Seconds between checks (default: 30 seconds for near real-time)
    """
    try:
        auth_context = get_auth_context(request)
        
        # Validate interval
        if check_interval < 10:
            raise HTTPException(
                status_code=400,
                detail="Check interval must be at least 10 seconds"
            )
        
        if check_interval > 3600:
            raise HTTPException(
                status_code=400,
                detail="Check interval cannot exceed 3600 seconds (1 hour)"
            )
        
        logger.info(f"Admin {auth_context.uid} started Gmail monitoring with {check_interval}s interval")
        
        # Start monitoring in background
        background_tasks.add_task(
            gmail_service.start_monitoring,
            check_interval=check_interval
        )
        
        return APIResponse(
            status="success",
            data={"monitoring": "started", "interval_seconds": check_interval},
            message=f"Gmail monitoring started with {check_interval} second interval"
        )
        
    except Exception as e:
        logger.error(f"Failed to start Gmail monitoring: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Gmail monitoring: {str(e)}"
        )


@router.post("/stop-monitoring", response_model=APIResponse[Dict[str, Any]])
@require_permission("manage_gmail")
async def stop_gmail_monitoring(request: Request):
    """
    Stop Gmail monitoring
    Admin only endpoint
    """
    try:
        auth_context = get_auth_context(request)
        logger.info(f"Admin {auth_context.uid} stopping Gmail monitoring")
        
        await gmail_service.stop_monitoring()
        
        return APIResponse(
            status="success",
            data={"monitoring": "stopped"},
            message="Gmail monitoring stopped"
        )
        
    except Exception as e:
        logger.error(f"Failed to stop Gmail monitoring: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop Gmail monitoring: {str(e)}"
        )


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
@require_permission("manage_gmail")
async def get_gmail_status(request: Request):
    """
    Get Gmail service status
    Admin only endpoint
    """
    try:
        is_initialized = gmail_service.service is not None
        monitoring_email = gmail_service.monitoring_email
        last_history_id = gmail_service._last_history_id
        processed_count = len(gmail_service._processed_message_ids)
        monitoring_active = gmail_service._monitoring_active
        
        return APIResponse(
            status="success",
            data={
                "initialized": is_initialized,
                "monitoring_email": monitoring_email,
                "monitoring_active": monitoring_active,
                "last_history_id": last_history_id,
                "processed_message_count": processed_count
            },
            message="Gmail service status retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get Gmail status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Gmail status: {str(e)}"
        )


@router.post("/initialize", response_model=APIResponse[Dict[str, Any]])
@require_permission("manage_gmail")
async def initialize_gmail(request: Request):
    """
    Initialize Gmail service
    Admin only endpoint
    """
    try:
        auth_context = get_auth_context(request)
        logger.info(f"Admin {auth_context.uid} initializing Gmail service")
        
        await gmail_service.initialize()
        
        return APIResponse(
            status="success",
            data={"initialized": True},
            message="Gmail service initialized successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize Gmail: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Gmail: {str(e)}"
        )