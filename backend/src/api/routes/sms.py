"""
SMS API endpoints for testing and management
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from api.middleware.auth_middleware import verify_firebase_token
from services.sms_service import sms_service
from services.auto_sms_service import auto_sms_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sms", tags=["SMS"])


class TestSmsRequest(BaseModel):
    """Request model for sending test SMS"""
    phone_number: str
    client_id: str = None


@router.post("/test")
async def send_test_sms(
    request: TestSmsRequest,
    current_user: dict = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """
    Send a test SMS message
    
    Args:
        request: Test SMS request with phone number
        current_user: Authenticated user
        
    Returns:
        SMS sending result
    """
    try:
        logger.info(f"User {current_user['uid']} sending test SMS to {request.phone_number}")
        
        result = await auto_sms_service.send_test_sms(
            phone_number=request.phone_number,
            client_id=request.client_id
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': 'Test SMS sent successfully',
                'message_id': result.get('message_id'),
                'details': result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to send SMS: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate")
async def validate_sms_configuration(
    current_user: dict = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """
    Validate SMS service configuration
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Validation results
    """
    try:
        logger.info(f"User {current_user['uid']} validating SMS configuration")
        
        validation = await sms_service.validate_configuration()
        
        return {
            'success': validation.get('configured', False),
            'validation': validation
        }
        
    except Exception as e:
        logger.error(f"Error validating SMS configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-trade-notification")
async def send_trade_sms_notification(
    client_id: str,
    trade_status: str,
    trade_data: Dict[str, Any],
    current_user: dict = Depends(verify_firebase_token)
) -> Dict[str, Any]:
    """
    Manually trigger SMS notifications for a trade (for testing)
    
    Args:
        client_id: Client ID
        trade_status: Trade status (Confirmation OK, Difference, Needs Review)
        trade_data: Trade information
        current_user: Authenticated user
        
    Returns:
        SMS sending results
    """
    try:
        logger.info(f"User {current_user['uid']} manually triggering SMS for client {client_id}, status {trade_status}")
        
        result = await auto_sms_service.process_trade_sms_notifications(
            client_id=client_id,
            trade_status=trade_status,
            trade_data=trade_data,
            discrepancies=trade_data.get('discrepancies', [])
        )
        
        return {
            'success': result.get('sms_sent', False),
            'results': result
        }
        
    except Exception as e:
        logger.error(f"Error sending trade SMS notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))