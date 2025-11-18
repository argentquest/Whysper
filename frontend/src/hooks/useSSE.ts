```typescript
import { useState, useEffect, useRef, useCallback } from 'react';

// Define the structure for Server-Sent Event messages with generic type support
export interface SSEMessage<T = any> {
  id: string;
  type: string;
  data: T;
  timestamp: number;
  isRead: boolean;
}

// Configure options for the SSE hook with flexible connection management
export interface UseSSEOptions<T = any> {
  url: string;
  enabled?: boolean;
  onMessage?: (message: SSEMessage<T>) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  keepAliveTimeout?: number;
  autoClose?: boolean; // Automatically close connection on terminal states
}

// Define return type with methods for managing SSE connection
export interface UseSSEReturn<T = any> {
  messages: SSEMessage<T>[];
  isConnected: boolean;
  error: Error | null;
  connect: () => void;
  disconnect: () => void;
  clearMessages: () => void;
  markAsRead: (messageId: string) => void;
  markAllAsRead: () => void;
}

export function useSSE<T = any>({
  url,
  enabled = true,
  onMessage,
  onError,
  onConnect,
  onDisconnect,
  maxReconnectAttempts = 5,
  reconnectInterval = 2000,
  keepAliveTimeout = 30000,
  autoClose = true,
}: UseSSEOptions<T>): UseSSEReturn<T> {
  // Create state variables to track connection status, messages, and errors
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<SSEMessage<T>[]>([]);
  const [error, setError] = useState<Error | null>(null);

  // Use refs to manage connection lifecycle and prevent memory leaks
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const keepAliveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Disconnect method to cleanly close the server connection
  const disconnect = useCallback(() => {
    // Close existing EventSource and clear all timers
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Clear reconnection and keep-alive timers to prevent memory leaks
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Reset connection status and trigger disconnect callback
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current);
      keepAliveTimerRef.current = null;
    }

    // Update connection status and trigger disconnect callback
    setIsConnected(false);
    onDisconnect?.();
  }, [onDisconnect]);

  // Clear keep-alive timer to prevent stale connections
  const clearKeepAliveTimer = useCallback(() => {
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current);
      keepAliveTimerRef.current = null;
    }
  }, []);

  // Reset keep-alive timer to detect connection staleness
  const resetKeepAliveTimer = useCallback(() => {
    clearKeepAliveTimer();
    keepAliveTimerRef.current = setTimeout(() => {
      console.warn('[useSSE] Keep-alive timeout - no messages received in', keepAliveTimeout, 'ms');
      disconnect();
    }, keepAliveTimeout);
  }, [keepAliveTimeout, clearKeepAliveTimer, disconnect]);

  // Establish Server-Sent Events connection with robust error handling
  const connect = useCallback(() => {
    // Prevent connection if not enabled or missing URL
    if (!enabled || !url) {
      console.log('[useSSE] Connection skipped - enabled:', enabled, 'url:', url);
      return;
    }

    // Close any existing connection before creating new one
    disconnect();

    try {
      console.log('[useSSE] Establishing SSE connection to:', url);
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle successful connection establishment
      eventSource.addEventListener('open', () => {
        console.log('[useSSE] SSE connection opened');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        resetKeepAliveTimer();
        onConnect?.();
      });

      // Process incoming messages from server
      eventSource.addEventListener('message', (event) => {
        resetKeepAliveTimer();

        try {
          const data = JSON.parse(event.data);

          // Skip keep-alive messages to reduce noise
          if (data.type === 'keep-alive' || data.type === 'ping') {
            console.log('[useSSE] Keep-alive received');
            return;
          }

          // Create standardized message object for consistent handling
          const message: SSEMessage<T> = {
            id: data.id || `msg-${Date.now()}-${Math.random()}`,
            type: data.type || data.status || 'message',
            data: data,
            timestamp: Date.now(),
            isRead: false,
          };

          // Update messages state and trigger onMessage callback
          setMessages((prev) => [...prev, message]);
          onMessage?.(message);

          // Log server waiting status for debugging
          if (data.status === 'waiting') {
            console.log('[useSSE] Server is waiting for LLM response:', data.message);
          }

          // Automatically close connection on terminal states if enabled
          if (autoClose && (data.status === 'completed' || data.status === 'error')) {
            console.log('[useSSE] Terminal status received, closing connection');
            setTimeout(() => {
              disconnect();
            }, 1000);
          }
        } catch (err) {
          console.error('[useSSE] Error parsing SSE message:', err);
        }
      });

      // Handle connection errors with intelligent reconnection strategy
      eventSource.addEventListener('error', (event) => {
        const es = event.target as EventSource;
        console.error('[useSSE] SSE error occurred, readyState:', es.readyState);

        if (es.readyState === EventSource.CLOSED) {
          setIsConnected(false);
          clearKeepAliveTimer();

          const err = new Error('SSE connection closed');
          setError(err);
          onError?.(err);

          // Implement exponential backoff for reconnection attempts
          if (reconnectAttempts.current < maxReconnectAttempts) {
            reconnectAttempts.current++;
            const delay = reconnectInterval * Math.pow(2, reconnectAttempts.current - 1);
            console.log(
              `[useSSE] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`
            );

            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, delay);
          } else {
            console.error('[useSSE] Max reconnection attempts reached');
            const maxAttemptsError = new Error(
              'Failed to connect after ' + maxReconnectAttempts + ' attempts'
            );
            setError(maxAttemptsError);
            onError?.(maxAttemptsError);
          }
        }
      });
    } catch (err) {
      console.error('[useSSE] Error creating SSE connection:', err);
      const connectionError = err instanceof Error ? err : new Error('Failed to establish SSE connection');
      setError(connectionError);
      onError?.(connectionError);
    }
  }, [
    url,
    enabled,
    onMessage,
    onError,
    onConnect,
    maxReconnectAttempts,
    reconnectInterval,
    resetKeepAliveTimer,
    disconnect,
    autoClose,
  ]);

  // Manage connection lifecycle with automatic connection and cleanup
  useEffect(() => {
    if (enabled && url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, enabled, connect, disconnect]);

  // Utility methods for managing messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const markAsRead = useCallback((messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, isRead: true } : msg))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setMessages((prev) => prev.map((msg) => ({ ...msg, isRead: true })));
  }, []);

  // Expose hook API with messages, connection status, and utility methods
  return {
    messages,
    isConnected,
    error,
    connect,
    disconnect,
    clearMessages,
    markAsRead,
    markAllAsRead,
  };
}