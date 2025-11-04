/**
 * Custom hook for Server-Sent Events (SSE) integration
 * Handles real-time message streaming from backend
 */

import { useEffect, useCallback, useRef, useState } from 'react';
import { SSEMessage } from '../types/architectureStudio';

export interface UseSSEReturn {
  messages: SSEMessage[];
  isConnected: boolean;
  connect: (requestId: string) => void;
  disconnect: () => void;
  clearMessages: () => void;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5;

export function useSSE(): UseSSEReturn {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ============================================================================
  // Connection Management
  // ============================================================================

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback((requestId: string) => {
    // Clear previous connection
    disconnect();

    try {
      const url = `${API_BASE_URL}/diagrams/v2/stream?requestId=${encodeURIComponent(requestId)}`;
      const eventSource = new EventSource(url);

      eventSourceRef.current = eventSource;
      reconnectCountRef.current = 0;

      // ========================================================================
      // Event Handlers
      // ========================================================================

      eventSource.addEventListener('open', () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
      });

      eventSource.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          const message: SSEMessage = {
            id: `${Date.now()}-${Math.random()}`,
            type: data.type || 'info',
            message: data.message,
            timestamp: new Date(),
            details: data.details,
          };
          setMessages((prev) => [...prev, message]);
        } catch (error) {
          console.error('Error parsing SSE message:', error);
        }
      });

      eventSource.addEventListener('diagram', (event) => {
        try {
          const data = JSON.parse(event.data);
          const message: SSEMessage = {
            id: `${Date.now()}-${Math.random()}`,
            type: 'diagram',
            message: 'Diagram generated successfully',
            timestamp: new Date(),
            details: {
              svg: data.svg,
              provider: data.provider,
              metadata: data.metadata,
            },
          };
          setMessages((prev) => [...prev, message]);
        } catch (error) {
          console.error('Error parsing diagram message:', error);
        }
      });

      eventSource.addEventListener('error', (event) => {
        const eventSource = event.target as EventSource;
        if (eventSource.readyState === EventSource.CLOSED) {
          setIsConnected(false);
          disconnect();

          // Reconnect logic
          if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS) {
            reconnectCountRef.current += 1;
            const delay = RECONNECT_DELAY * Math.pow(2, reconnectCountRef.current - 1);
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectCountRef.current})`);

            reconnectTimeoutRef.current = setTimeout(() => {
              connect(requestId);
            }, delay);
          } else {
            const message: SSEMessage = {
              id: `${Date.now()}-${Math.random()}`,
              type: 'error',
              message: 'Failed to connect after multiple attempts',
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, message]);
          }
        }
      });
    } catch (error) {
      console.error('Error setting up SSE connection:', error);
      const message: SSEMessage = {
        id: `${Date.now()}-${Math.random()}`,
        type: 'error',
        message: 'Failed to establish SSE connection',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, message]);
    }
  }, [disconnect]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // ============================================================================
  // Cleanup
  // ============================================================================

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    messages,
    isConnected,
    connect,
    disconnect,
    clearMessages,
  };
}
