/**
 * useEventStream Hook
 * React hook for connecting to the real-time event stream using Server-Sent Events (SSE)
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { auth } from '../config/firebase';

export type EventType = 
  | 'gmail_processed' 
  | 'trade_matched' 
  | 'upload_complete' 
  | 'system_alert' 
  | 'match_created' 
  | 'duplicate_detected';

export type EventPriority = 'high' | 'medium' | 'low';

export type EventAction = 
  | 'refresh_grids' 
  | 'show_toast' 
  | 'redirect' 
  | 'update_status';

export interface SystemEvent {
  id: string;
  type: EventType;
  timestamp: string;
  priority: EventPriority;
  client_id?: string;
  title: string;
  message: string;
  action?: EventAction;
  payload?: Record<string, any>;
}

export interface EventStreamOptions {
  clientId?: string;
  eventTypes?: EventType[];
  priorityFilter?: EventPriority[];
  onEvent?: (event: SystemEvent) => void;
  onToast?: (title: string, message: string, type: 'success' | 'warning' | 'error' | 'info') => void;
  onRefreshGrids?: () => void;
  autoConnect?: boolean;
}

export interface EventStreamState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  connectionId: string | null;
}

export const useEventStream = (options: EventStreamOptions = {}) => {
  const [state, setState] = useState<EventStreamState>({
    connected: false,
    connecting: false,
    error: null,
    connectionId: null
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const {
    clientId,
    eventTypes,
    priorityFilter,
    onEvent,
    onToast,
    onRefreshGrids,
    autoConnect = true
  } = options;

  const connect = useCallback(async () => {
    // Don't connect if component is unmounted
    if (!mountedRef.current) return;
    
    // Clean up any existing connection first
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setState(prev => ({ ...prev, connecting: true, error: null }));
    
    try {
      // Get Firebase auth token
      const user = auth.currentUser;
      if (!user) {
        throw new Error('No authenticated user');
      }
      
      const token = await user.getIdToken();
      if (!token) {
        throw new Error('No authentication token available');
      }

      // Build query parameters
      const params = new URLSearchParams();
      if (clientId) params.append('client_id', clientId);
      if (eventTypes?.length) params.append('event_types', eventTypes.join(','));
      if (priorityFilter?.length) params.append('priority_filter', priorityFilter.join(','));
      params.append('token', token);

      // Create EventSource URL
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const url = `${baseUrl}/api/v1/events/stream?${params.toString()}`;
      
      console.log('📡 Connecting to event stream...');

      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        if (!mountedRef.current) return;
        console.log('📡 EventStream connected successfully');
        setState(prev => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null
        }));
      };

      eventSource.onmessage = (event) => {
        if (!mountedRef.current) return;
        
        try {
          const data = JSON.parse(event.data);
          console.log('📡 Received event:', data);

          if (data.type === 'connection') {
            setState(prev => ({
              ...prev,
              connectionId: data.data.connection_id
            }));
            return;
          }

          if (data.type === 'event') {
            const systemEvent: SystemEvent = {
              id: data.data.id,
              type: data.data.type,
              timestamp: data.data.timestamp,
              priority: data.data.priority,
              client_id: data.data.client_id,
              title: data.data.title,
              message: data.data.message,
              action: data.data.action,
              payload: data.data.payload
            };

            // Call custom event handler
            if (onEvent) {
              onEvent(systemEvent);
            }

            // Handle built-in actions
            handleEventAction(systemEvent);
          }

          if (data.type === 'heartbeat') {
            console.log('💓 EventStream heartbeat received');
          }

        } catch (error) {
          console.error('📡 Error parsing event data:', error);
        }
      };

      eventSource.onerror = (event) => {
        if (!mountedRef.current) return;
        
        console.error('📡 EventStream error:', event);
        setState(prev => ({
          ...prev,
          connected: false,
          connecting: false,
          error: 'Connection error'
        }));

        // Close the failed connection
        eventSource.close();
        eventSourceRef.current = null;

        // Schedule reconnection after a short delay
        reconnectTimeoutRef.current = setTimeout(() => {
          if (mountedRef.current) {
            console.log('📡 Attempting to reconnect...');
            connect();
          }
        }, 3000);
      };

    } catch (error) {
      console.error('📡 Failed to connect to event stream:', error);
      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          connecting: false,
          error: error instanceof Error ? error.message : 'Connection failed'
        }));
      }
    }
  }, [clientId, eventTypes, priorityFilter, onEvent]);

  const disconnect = useCallback(() => {
    console.log('📡 Disconnecting from event stream');
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setState({
      connected: false,
      connecting: false,
      error: null,
      connectionId: null
    });
  }, []);

  const handleEventAction = useCallback((event: SystemEvent) => {
    switch (event.action) {
      case 'refresh_grids':
        console.log('📡 Triggering grid refresh');
        if (onRefreshGrids) {
          onRefreshGrids();
        }
        break;

      case 'show_toast':
        console.log('📡 Showing toast notification');
        if (onToast) {
          // Determine toast type based on event type and priority
          let toastType: 'success' | 'warning' | 'error' | 'info' = 'info';
          
          if (event.type === 'gmail_processed' || event.type === 'match_created') {
            toastType = 'success';
          } else if (event.type === 'duplicate_detected') {
            toastType = 'warning';
          } else if (event.priority === 'high') {
            toastType = 'error';
          } else if (event.type === 'system_alert') {
            toastType = 'info';
          }

          onToast(event.title, event.message, toastType);
        }
        break;

      default:
        console.log(`📡 Unhandled event action: ${event.action}`);
        break;
    }
  }, [onToast, onRefreshGrids]);

  // Auto-connect on mount
  useEffect(() => {
    mountedRef.current = true;
    
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    reconnect: connect
  };
};

export default useEventStream;