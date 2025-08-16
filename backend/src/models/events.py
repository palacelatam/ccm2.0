"""
Event System Models
Defines the structure for system-wide events and notifications
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel
import uuid


EventType = Literal[
    'gmail_processed',
    'trade_matched', 
    'upload_complete',
    'system_alert',
    'match_created',
    'duplicate_detected'
]

EventPriority = Literal['high', 'medium', 'low']

EventAction = Literal[
    'refresh_grids',
    'show_toast', 
    'redirect',
    'update_status'
]


class EventData(BaseModel):
    """Event payload data"""
    title: str
    message: str
    action: Optional[EventAction] = None
    payload: Optional[Dict[str, Any]] = None


class SystemEvent(BaseModel):
    """System event model for real-time notifications"""
    id: str
    type: EventType
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime
    priority: EventPriority = 'medium'
    data: EventData
    
    @classmethod
    def create(cls, 
              event_type: EventType,
              title: str, 
              message: str,
              client_id: Optional[str] = None,
              user_id: Optional[str] = None,
              priority: EventPriority = 'medium',
              action: Optional[EventAction] = None,
              payload: Optional[Dict[str, Any]] = None) -> 'SystemEvent':
        """Factory method to create system events"""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            client_id=client_id,
            user_id=user_id,
            timestamp=datetime.now(),
            priority=priority,
            data=EventData(
                title=title,
                message=message,
                action=action,
                payload=payload or {}
            )
        )


class EventSubscription(BaseModel):
    """Event subscription filter"""
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    event_types: Optional[List[EventType]] = None
    priority_filter: Optional[List[EventPriority]] = None