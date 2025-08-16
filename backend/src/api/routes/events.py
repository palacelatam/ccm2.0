"""
Events API Routes
Server-Sent Events (SSE) endpoint for real-time notifications
"""

import asyncio
import json
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.middleware.auth_middleware import get_auth_context
from api.routes.clients import validate_client_access
from models.events import EventSubscription, EventType, EventPriority
from services.event_service import event_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


class EventStreamRequest(BaseModel):
    """Request model for event stream subscription"""
    client_id: Optional[str] = None
    event_types: Optional[list[EventType]] = None
    priority_filter: Optional[list[EventPriority]] = None


@router.get("/stream")
async def stream_events(
    request: Request,
    client_id: Optional[str] = None,
    event_types: Optional[str] = None,
    priority_filter: Optional[str] = None,
    token: Optional[str] = None
):
    """
    Server-Sent Events endpoint for real-time notifications
    
    Query Parameters:
        client_id: Filter events for specific client
        event_types: Comma-separated list of event types to subscribe to
        priority_filter: Comma-separated list of priorities (high,medium,low)
        token: Authentication token (required for EventSource compatibility)
    """
    
    # Get authentication context
    # EventSource doesn't support custom headers, so we accept token as query param
    try:
        if token:
            # Manually verify token since middleware is bypassed
            from config.firebase_config import verify_firebase_token
            from services.user_service import UserService
            from models.user import AuthContext
            
            decoded_token = verify_firebase_token(token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")
            
            # Get user profile and permissions
            user_service = UserService()
            user_profile = await user_service.get_user_profile(uid)
            
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User profile not found"
                )
            
            # Get user permissions
            permissions = await user_service.get_user_permissions(uid)
            
            # Create auth context
            auth_context = AuthContext(
                uid=uid,
                email=email,
                user_profile=user_profile,
                permissions=permissions,
                organization_id=user_profile.organization.id if user_profile.organization else None,
                organization_type=user_profile.organization.type if user_profile.organization else None
            )
        else:
            # Try to get from Authorization header (if present)
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid token"
                )
            
            header_token = auth_header.split(" ")[1]
            # Use same token verification logic
            from config.firebase_config import verify_firebase_token
            from services.user_service import UserService
            from models.user import AuthContext
            
            decoded_token = verify_firebase_token(header_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")
            
            user_service = UserService()
            user_profile = await user_service.get_user_profile(uid)
            
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User profile not found"
                )
            
            permissions = await user_service.get_user_permissions(uid)
            
            auth_context = AuthContext(
                uid=uid,
                email=email,
                user_profile=user_profile,
                permissions=permissions,
                organization_id=user_profile.organization.id if user_profile.organization else None,
                organization_type=user_profile.organization.type if user_profile.organization else None
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Authentication error in events endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )
    
    # Parse query parameters
    parsed_event_types = None
    if event_types:
        parsed_event_types = [t.strip() for t in event_types.split(',')]
    
    parsed_priority_filter = None  
    if priority_filter:
        parsed_priority_filter = [p.strip() for p in priority_filter.split(',')]
    
    # If client_id provided, validate access
    if client_id:
        validate_client_access(auth_context, client_id)
    else:
        # Default to user's organization
        client_id = auth_context.organization_id or auth_context.uid
    
    # Create subscription
    subscription = EventSubscription(
        client_id=client_id,
        user_id=auth_context.uid,
        event_types=parsed_event_types,
        priority_filter=parsed_priority_filter
    )
    
    # Generate unique connection ID
    connection_id = str(uuid.uuid4())
    
    logger.info(f"📡 Starting SSE stream for user {auth_context.uid}, client {client_id}")
    
    async def event_stream():
        """Generate SSE stream"""
        event_queue = None
        try:
            logger.info(f"📡 Starting event stream setup for connection {connection_id}")
            
            # Subscribe to events
            event_queue = await event_service.subscribe(connection_id, subscription)
            logger.info(f"📡 Successfully subscribed to events")
            
            # Send initial connection event
            logger.info(f"📡 Sending initial connection message")
            yield _format_sse_data({
                'type': 'connection',
                'data': {
                    'status': 'connected',
                    'connection_id': connection_id,
                    'timestamp': str(asyncio.get_event_loop().time())
                }
            })
            
            logger.info(f"📡 Starting event loop with heartbeat interval 30s")
            
            # Send periodic heartbeats and events
            heartbeat_interval = 30  # seconds
            last_heartbeat = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # Wait for event with timeout for heartbeat
                    event = await asyncio.wait_for(event_queue.get(), timeout=heartbeat_interval)
                    
                    logger.info(f"📡 Received event: {event.type} - {event.data.title}")
                    
                    # Send the event
                    yield _format_sse_data({
                        'type': 'event',
                        'data': {
                            'id': event.id,
                            'type': event.type,
                            'timestamp': event.timestamp.isoformat(),
                            'priority': event.priority,
                            'client_id': event.client_id,
                            'title': event.data.title,
                            'message': event.data.message,
                            'action': event.data.action,
                            'payload': event.data.payload
                        }
                    })
                    
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_heartbeat >= heartbeat_interval:
                        logger.debug(f"📡 Sending heartbeat for connection {connection_id}")
                        yield _format_sse_data({
                            'type': 'heartbeat',
                            'data': {
                                'timestamp': str(current_time)
                            }
                        })
                        last_heartbeat = current_time
                        
                except Exception as e:
                    logger.error(f"📡 Error in event stream loop: {e}", exc_info=True)
                    break
                    
        except Exception as e:
            logger.error(f"📡 Failed to start event stream: {e}", exc_info=True)
            yield _format_sse_data({
                'type': 'error',
                'data': {
                    'message': f'Stream connection failed: {str(e)}'
                }
            })
        finally:
            # Cleanup subscription
            if event_queue is not None:
                try:
                    await event_service.unsubscribe(connection_id, subscription)
                    logger.info(f"📡 Successfully unsubscribed connection {connection_id}")
                except Exception as e:
                    logger.error(f"📡 Error during unsubscribe: {e}")
            logger.info(f"📡 Closed SSE stream for user {auth_context.uid}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "Access-Control-Allow-Methods": "GET",
        }
    )


@router.post("/test")
async def test_event(
    title: str = "Test Event",
    message: str = "This is a test event", 
    client_id: str = "xyz-corp"
):
    """Test endpoint to trigger a sample event (no auth required for testing)"""
    
    # Emit test event using a subscribed event type
    event = await event_service.emit_event(
        event_type='gmail_processed',  # Use subscribed event type
        title=title,
        message=message,
        client_id=client_id,
        priority='medium',
        action='show_toast'
    )
    
    return {
        'success': True,
        'event_id': event.id,
        'message': 'Test event emitted',
        'client_id': client_id
    }


@router.get("/test-stream")
async def test_stream_events(request: Request):
    """
    Test SSE endpoint without authentication
    FOR TESTING PURPOSES ONLY - Remove in production
    """
    
    # Create a test subscription
    subscription = EventSubscription(
        client_id="xyz-corp",
        user_id="test-user",
        event_types=['gmail_processed', 'trade_matched', 'match_created', 'duplicate_detected'],
        priority_filter=None
    )
    
    # Generate unique connection ID
    connection_id = str(uuid.uuid4())
    
    logger.info(f"📡 Starting TEST SSE stream for connection {connection_id}")
    
    async def event_stream():
        """Generate SSE stream"""
        event_queue = None
        try:
            # Subscribe to events
            event_queue = await event_service.subscribe(connection_id, subscription)
            
            # Send initial connection event
            yield _format_sse_data({
                'type': 'connection',
                'data': {
                    'status': 'connected',
                    'connection_id': connection_id,
                    'timestamp': str(asyncio.get_event_loop().time()),
                    'test_mode': True
                }
            })
            
            # Send periodic heartbeats and events
            heartbeat_interval = 30  # seconds
            last_heartbeat = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # Wait for event with timeout for heartbeat
                    event = await asyncio.wait_for(event_queue.get(), timeout=heartbeat_interval)
                    
                    logger.info(f"📡 TEST: Received event: {event.type} - {event.data.title}")
                    
                    # Send the event
                    yield _format_sse_data({
                        'type': 'event',
                        'data': {
                            'id': event.id,
                            'type': event.type,
                            'timestamp': event.timestamp.isoformat(),
                            'priority': event.priority,
                            'client_id': event.client_id,
                            'title': event.data.title,
                            'message': event.data.message,
                            'action': event.data.action,
                            'payload': event.data.payload
                        }
                    })
                    
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_heartbeat >= heartbeat_interval:
                        logger.debug(f"📡 TEST: Sending heartbeat for connection {connection_id}")
                        yield _format_sse_data({
                            'type': 'heartbeat',
                            'data': {
                                'timestamp': str(current_time)
                            }
                        })
                        last_heartbeat = current_time
                        
                except Exception as e:
                    logger.error(f"📡 TEST: Error in event stream loop: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"📡 TEST: Failed to start event stream: {e}")
            yield _format_sse_data({
                'type': 'error',
                'data': {
                    'message': f'Stream connection failed: {str(e)}'
                }
            })
        finally:
            # Cleanup subscription
            if event_queue is not None:
                await event_service.unsubscribe(connection_id, subscription)
            logger.info(f"📡 TEST: Closed SSE stream for connection {connection_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "Access-Control-Allow-Methods": "GET",
        }
    )


@router.get("/stats")
async def get_event_stats(request: Request):
    """Get event service statistics (admin only)"""
    
    auth_context = get_auth_context(request)
    
    # Simple admin check - you might want more sophisticated role checking
    if not auth_context.uid or 'admin' not in auth_context.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stats = event_service.get_connection_stats()
    return {
        'success': True,
        'stats': stats
    }


def _format_sse_data(data: dict) -> str:
    """Format data for Server-Sent Events"""
    json_data = json.dumps(data)
    return f"data: {json_data}\n\n"