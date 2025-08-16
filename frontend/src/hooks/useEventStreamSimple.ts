/**
 * Super Simple EventStream Hook
 * Just connect and log - nothing fancy
 */

import { useEffect, useRef, useState } from 'react';
import { auth } from '../config/firebase';

interface EventStreamOptions {
  clientId?: string;
  onEvent?: (eventData: any) => void;
}

export const useEventStreamSimple = (options: EventStreamOptions = {}) => {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const hasReconnectedRef = useRef(false);
  const mountedRef = useRef(true);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');

  useEffect(() => {
    mountedRef.current = true;
    
    const connect = async () => {
      console.log('🔌 [SimpleEventStream] Starting connection...');
      
      try {
        // Get token
        const user = auth.currentUser;
        if (!user) {
          console.log('❌ [SimpleEventStream] No user logged in');
          return;
        }

        const token = await user.getIdToken();
        console.log('✅ [SimpleEventStream] Got token');

        // Build URL with dynamic client ID
        const clientIdParam = options.clientId || 'xyz-corp'; // Fallback to xyz-corp if not provided
        const url = `http://localhost:8000/api/v1/events/stream?token=${token}&client_id=${clientIdParam}&event_types=gmail_processed`;
        console.log('🔍 [SimpleEventStream] Using client_id:', clientIdParam);
        console.log('🌐 [SimpleEventStream] Connecting to:', url);

        // Create EventSource
        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
          console.log('✅ [SimpleEventStream] Connected!');
          setStatus('connected');
          hasReconnectedRef.current = false; // Reset reconnection flag on successful connection
        };

        eventSource.onmessage = (event) => {
          console.log('📨 [SimpleEventStream] Message received:', event.data);
          
          try {
            const data = JSON.parse(event.data);
            
            // Handle different message types
            if (data.type === 'event') {
              console.log('🎯 [SimpleEventStream] Event received:', data.data.type, data.data.title);
              
              // Call custom event handler if provided
              if (options.onEvent) {
                options.onEvent(data.data);
              }
            } else if (data.type === 'connection') {
              console.log('🔗 [SimpleEventStream] Connection confirmed');
            } else if (data.type === 'heartbeat') {
              console.log('💓 [SimpleEventStream] Heartbeat');
            }
          } catch (error) {
            console.log('❌ [SimpleEventStream] Error parsing message:', error);
          }
        };

        eventSource.onerror = (error) => {
          console.log('❌ [SimpleEventStream] Error:', error);
          setStatus('error');
          eventSource.close();
          
          // Try to reconnect once after 5 seconds
          if (!hasReconnectedRef.current && mountedRef.current) {
            hasReconnectedRef.current = true;
            console.log('🔄 [SimpleEventStream] Will attempt reconnection in 5 seconds...');
            reconnectTimeoutRef.current = setTimeout(() => {
              if (mountedRef.current) {
                console.log('🔄 [SimpleEventStream] Attempting reconnection...');
                setStatus('connecting');
                connect();
              }
            }, 5000);
          } else {
            console.log('❌ [SimpleEventStream] Not reconnecting (already tried or component unmounted)');
          }
        };

      } catch (error) {
        console.log('💥 [SimpleEventStream] Connection failed:', error);
        setStatus('error');
      }
    };

    connect();

    return () => {
      console.log('🧹 [SimpleEventStream] Cleanup');
      mountedRef.current = false;
      
      // Clear reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      
      // Close EventSource
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []); // Only run once

  return { status };
};

export default useEventStreamSimple;