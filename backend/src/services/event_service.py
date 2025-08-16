"""
Event Service
Generic system for real-time events and notifications using Server-Sent Events (SSE)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict

from models.events import SystemEvent, EventType, EventPriority, EventAction, EventSubscription

logger = logging.getLogger(__name__)


class EventService:
    """
    Generic event service for real-time notifications
    Uses Server-Sent Events (SSE) to push events to connected clients
    """
    
    def __init__(self):
        # Store active SSE connections by client_id and user_id
        self._connections: Dict[str, Dict[str, asyncio.Queue]] = defaultdict(dict)
        # Store recent events for new connections
        self._recent_events: List[SystemEvent] = []
        # Maximum events to keep in memory
        self._max_recent_events = 100
        # Event retention time
        self._event_retention_hours = 24
        
        logger.info("EventService initialized")

    async def emit_event(self,
                        event_type: EventType,
                        title: str,
                        message: str,
                        client_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        priority: EventPriority = 'medium',
                        action: Optional[EventAction] = None,
                        payload: Optional[Dict] = None) -> SystemEvent:
        """
        Emit a system event to all relevant subscribers
        
        Args:
            event_type: Type of event
            title: Event title
            message: Event message
            client_id: Optional client ID filter
            user_id: Optional user ID filter  
            priority: Event priority
            action: Optional action for frontend
            payload: Additional event data
            
        Returns:
            The created SystemEvent
        """
        
        # Create the event
        event = SystemEvent.create(
            event_type=event_type,
            title=title,
            message=message,
            client_id=client_id,
            user_id=user_id,
            priority=priority,
            action=action,
            payload=payload
        )
        
        # Store in recent events
        self._recent_events.append(event)
        self._cleanup_old_events()
        
        # Send to all matching subscribers
        await self._broadcast_event(event)
        
        logger.info(f"📡 Emitted event: {event_type} - {title} (client: {client_id}, priority: {priority})")
        
        return event

    async def subscribe(self, 
                       connection_id: str,
                       subscription: EventSubscription) -> asyncio.Queue:
        """
        Subscribe to events with filtering
        
        Args:
            connection_id: Unique connection identifier
            subscription: Event subscription filters
            
        Returns:
            Queue for receiving events
        """
        
        # Create event queue for this connection
        event_queue = asyncio.Queue()
        
        # Store connection with subscription info
        key = self._get_subscription_key(subscription)
        self._connections[key][connection_id] = {
            'queue': event_queue,
            'subscription': subscription,
            'connected_at': datetime.now()
        }
        
        logger.info(f"📡 New event subscription: {connection_id} (client: {subscription.client_id}, user: {subscription.user_id})")
        
        # Send recent events to new subscriber
        await self._send_recent_events(event_queue, subscription)
        
        return event_queue

    async def unsubscribe(self, connection_id: str, subscription: EventSubscription):
        """Remove event subscription"""
        key = self._get_subscription_key(subscription)
        if key in self._connections and connection_id in self._connections[key]:
            del self._connections[key][connection_id]
            logger.info(f"📡 Unsubscribed: {connection_id}")
            
            # Clean up empty subscription groups
            if not self._connections[key]:
                del self._connections[key]

    async def _broadcast_event(self, event: SystemEvent):
        """Broadcast event to matching subscribers"""
        disconnected_connections = []
        
        logger.info(f"📡 Broadcasting event {event.type} to {len(self._connections)} subscription groups")
        
        for key, connections in self._connections.items():
            logger.debug(f"📡 Checking subscription group {key} with {len(connections)} connections")
            for connection_id, connection_info in connections.items():
                subscription = connection_info['subscription']
                
                # Check if event matches subscription
                matches = self._event_matches_subscription(event, subscription)
                logger.debug(f"📡 Event {event.type} matches subscription {connection_id}: {matches}")
                logger.debug(f"   - Event client_id: {event.client_id}, Subscription client_id: {subscription.client_id}")
                logger.debug(f"   - Event user_id: {event.user_id}, Subscription user_id: {subscription.user_id}")
                logger.debug(f"   - Event type: {event.type}, Subscription types: {subscription.event_types}")
                logger.debug(f"   - Event priority: {event.priority}, Subscription priority_filter: {subscription.priority_filter}")
                
                if matches:
                    try:
                        # Add event to connection queue (non-blocking)
                        connection_info['queue'].put_nowait(event)
                        logger.info(f"📡 Event queued for connection {connection_id}")
                    except asyncio.QueueFull:
                        logger.warning(f"📡 Event queue full for connection {connection_id}, dropping event")
                    except Exception as e:
                        logger.error(f"📡 Failed to send event to {connection_id}: {e}")
                        disconnected_connections.append((key, connection_id))
        
        # Clean up disconnected connections
        for key, connection_id in disconnected_connections:
            if key in self._connections and connection_id in self._connections[key]:
                del self._connections[key][connection_id]

    def _event_matches_subscription(self, event: SystemEvent, subscription: EventSubscription) -> bool:
        """Check if event matches subscription filters"""
        
        # Client ID filter
        if subscription.client_id and event.client_id != subscription.client_id:
            logger.debug(f"   - FAILED client_id check: subscription={subscription.client_id}, event={event.client_id}")
            return False
            
        # User ID filter - only filter if event has a specific user_id
        if event.user_id and subscription.user_id and event.user_id != subscription.user_id:
            logger.debug(f"   - FAILED user_id check: subscription={subscription.user_id}, event={event.user_id}")
            return False
            
        # Event type filter
        if subscription.event_types and event.type not in subscription.event_types:
            logger.debug(f"   - FAILED event_type check: subscription={subscription.event_types}, event={event.type}")
            return False
            
        # Priority filter
        if subscription.priority_filter and event.priority not in subscription.priority_filter:
            logger.debug(f"   - FAILED priority check: subscription={subscription.priority_filter}, event={event.priority}")
            return False
        
        logger.debug(f"   - PASSED all checks")
        return True

    async def _send_recent_events(self, queue: asyncio.Queue, subscription: EventSubscription):
        """Send recent events to new subscriber"""
        for event in self._recent_events:
            if self._event_matches_subscription(event, subscription):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning("📡 Queue full when sending recent events")
                    break

    def _get_subscription_key(self, subscription: EventSubscription) -> str:
        """Generate key for grouping similar subscriptions"""
        return f"{subscription.client_id}:{subscription.user_id}"

    def _cleanup_old_events(self):
        """Remove old events from memory"""
        # Remove events older than retention time
        cutoff_time = datetime.now() - timedelta(hours=self._event_retention_hours)
        self._recent_events = [
            event for event in self._recent_events 
            if event.timestamp > cutoff_time
        ]
        
        # Limit total number of events
        if len(self._recent_events) > self._max_recent_events:
            self._recent_events = self._recent_events[-self._max_recent_events:]

    def get_connection_stats(self) -> Dict:
        """Get statistics about active connections"""
        total_connections = sum(len(connections) for connections in self._connections.values())
        return {
            'total_connections': total_connections,
            'subscription_groups': len(self._connections),
            'recent_events': len(self._recent_events)
        }


# Global event service instance
event_service = EventService()