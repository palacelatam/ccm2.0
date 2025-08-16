/**
 * Minimal EventStream Hook
 * A simplified, stable implementation for SSE connections
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { auth } from '../config/firebase';

export interface UseEventStreamOptions {
  enabled?: boolean;
  clientId?: string;
  eventTypes?: string[];
  onMessage?: (data: any) => void;
  debug?: boolean;
}

export interface UseEventStreamState {
  connected: boolean;
  error: string | null;
  lastEventTime: Date | null;
}

export const useEventStreamMinimal = (options: UseEventStreamOptions = {}) => {
  const { 
    enabled = true, 
    clientId,
    eventTypes = ['gmail_processed', 'trade_matched', 'match_created', 'duplicate_detected'],
    onMessage, 
    debug = false 
  } = options;
  
  // Generate a unique ID for this hook instance
  const hookId = useRef(Math.random().toString(36).substr(2, 9));
  
  const log = useCallback((message: string, data?: any) => {
    if (debug) {
      console.log(`[EventStream-${hookId.current}] ${message}`, data || '');
    }
  }, [debug]);
  
  const [state, setState] = useState<UseEventStreamState>({
    connected: false,
    error: null,
    lastEventTime: null
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isMountedRef = useRef(true);

  // Remove the old log definition since we have the new one above

  const cleanup = useCallback(() => {
    log('Cleaning up connection');
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (isMountedRef.current) {
      setState({
        connected: false,
        error: null,
        lastEventTime: null
      });
    }
  }, [log]);

  const connect = useCallback(async () => {
    if (!enabled || !isMountedRef.current) {
      log('Connection disabled or component unmounted');
      return;
    }

    // Clean up any existing connection
    cleanup();

    try {
      // Get auth token
      const user = auth.currentUser;
      if (!user) {
        log('No authenticated user');
        setState(prev => ({ ...prev, error: 'Not authenticated' }));
        return;
      }

      const token = await user.getIdToken();
      log('Got auth token');

      // Build SSE URL
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams({
        token: token
      });
      
      // Add optional parameters
      if (clientId) {
        params.append('client_id', clientId);
      }
      if (eventTypes && eventTypes.length > 0) {
        params.append('event_types', eventTypes.join(','));
      }
      
      const url = `${baseUrl}/api/v1/events/stream?${params.toString()}`;

      log('Connecting to SSE', url);

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        if (!isMountedRef.current) return;
        log('Connected successfully');
        reconnectAttemptsRef.current = 0; // Reset reconnect counter on successful connection
        setState({
          connected: true,
          error: null,
          lastEventTime: new Date()
        });
      };

      eventSource.onmessage = (event) => {
        if (!isMountedRef.current) return;
        
        try {
          const data = JSON.parse(event.data);
          log('Received message', data);
          
          setState(prev => ({
            ...prev,
            lastEventTime: new Date()
          }));

          // Handle different message types
          if (data.type === 'connection') {
            log('Connection confirmed', data.data);
          } else if (data.type === 'heartbeat') {
            log('Heartbeat received');
          } else if (data.type === 'event' && onMessage) {
            onMessage(data.data);
          }
        } catch (error) {
          log('Error parsing message', error);
        }
      };

      eventSource.onerror = (error) => {
        if (!isMountedRef.current) return;
        
        log('Connection error', error);
        
        // Don't reconnect if component is unmounting
        if (!isMountedRef.current) {
          cleanup();
          return;
        }

        // Update state
        setState(prev => ({
          ...prev,
          connected: false,
          error: 'Connection lost'
        }));

        // Close the connection
        eventSource.close();
        eventSourceRef.current = null;

        // Stop reconnecting after too many failures
        if (reconnectAttemptsRef.current >= 10) {
          log('Max reconnection attempts reached, stopping reconnection');
          setState(prev => ({
            ...prev,
            error: 'Max reconnection attempts reached'
          }));
          return;
        }

        // Calculate exponential backoff delay (max 30 seconds)
        reconnectAttemptsRef.current += 1;
        const baseDelay = 1000; // 1 second
        const maxDelay = 30000; // 30 seconds
        const delay = Math.min(baseDelay * Math.pow(2, reconnectAttemptsRef.current - 1), maxDelay);
        
        log(`Scheduling reconnection attempt ${reconnectAttemptsRef.current} in ${delay}ms (${delay/1000}s)`);
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current && enabled) {
            log(`Attempting to reconnect (attempt ${reconnectAttemptsRef.current})`);
            connect();
          }
        }, delay);
      };

    } catch (error) {
      log('Failed to connect', error);
      if (isMountedRef.current) {
        setState(prev => ({
          ...prev,
          connected: false,
          error: error instanceof Error ? error.message : 'Connection failed'
        }));
      }
    }
  }, [enabled, clientId, eventTypes, onMessage, log, cleanup]);

  // Effect to manage connection lifecycle
  useEffect(() => {
    isMountedRef.current = true;

    if (enabled) {
      connect();
    }

    return () => {
      isMountedRef.current = false;
      cleanup();
    };
  }, [enabled, clientId, eventTypes]); // Re-run if these change

  // Manual reconnect function
  const reconnect = useCallback(() => {
    log('Manual reconnect requested');
    reconnectAttemptsRef.current = 0; // Reset attempts for manual reconnect
    cleanup();
    if (enabled) {
      connect();
    }
  }, [enabled, connect, cleanup, log]);

  return {
    ...state,
    reconnect
  };
};

export default useEventStreamMinimal;