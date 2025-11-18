Here's the code with inline comments explaining the logic:

import { useState, useEffect, useRef, useCallback } from 'react';

// Define the structure of a Server-Sent Event message with generic type support
export interface SSEMessage<T = any> {
  id: string;
  type: string;
  data: T;
  timestamp: number;
  isRead: boolean;
}

// Define configuration options for the SSE hook
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
  autoClose?: boolean; // Auto-close on completed/error status
}

// Define the return type for the SSE hook
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
  // Initialize state variables for connection status, messages, and errors
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<SSEMessage<T>[]>([]);
  const [error, setError] = useState<Error | null>(null);

  // Create refs to manage EventSource, reconnection, and keep-alive timers
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const keepAliveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Disconnect method to close the connection and clean up timers
  const disconnect = useCallback(() => {
    // Close existing EventSource if it exists
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Clear keep-alive timer
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current);
      keepAliveTimerRef.current = null;
    }

    // Update connection status and trigger disconnect callback
    setIsConnected(false);
    onDisconnect?.();
  }, [onDisconnect]);

  // Clear the keep-alive timer
  const clearKeepAliveTimer = useCallback(() => {
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current);
      keepAliveTimerRef.current = null;
    }
  }, []);

  // Reset keep-alive timer with a timeout to detect connection staleness
  const resetKeepAliveTimer = useCallback(() => {
    clearKeepAliveTimer();
    keepAliveTimerRef.current = setTimeout(() => {
      console.warn('[useSSE] Keep-alive timeout - no messages received in', keepAliveTimeout, 'ms');
      disconnect();
    }, keepAliveTimeout);
  }, [keepAliveTimeout, clearKeepAliveTimer, disconnect]);

  // Connect method to establish Server-Sent Events connection
  const connect = useCallback(() => {
    // Skip connection if not enabled or no URL provided
    if (!enabled || !url) {
      console.log('[useSSE] Connection skipped - enabled:', enabled, 'url:', url);
      return;
    }

    // Close any existing connection
    disconnect();

    try {
      console.log('[useSSE] Establishing SSE connection to:', url);
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle successful connection
      eventSource.addEventListener('open', () => {
        console.log('[useSSE] SSE connection opened');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        resetKeepAliveTimer();
        onConnect?.();
      });

      // Handle incoming messages
      eventSource.addEventListener('message', (event) => {
        resetKeepAliveTimer();

        try {
          const data = JSON.parse(event.data);

          // Ignore keep-alive messages
          if (data.type === 'keep-alive' || data.type === 'ping') {
            console.log('[useSSE] Keep-alive received');
            return;
          }

          // Create standardized message object
          const message: SSEMessage<T> = {
            id: data.id || `msg-${Date.now()}-${Math.random()}`,
            type: data.type || data.status || 'message',
            data: data,
            timestamp: Date.now(),
            isRead: false,
          };

          // Add message to state and call onMessage callback
          setMessages((prev) => [...prev, message]);
          onMessage?.(message);

          // Log waiting status for debugging
          if (data.status === 'waiting') {
            console.log('[useSSE] Server is waiting for LLM response:', data.message);
          }

          // Auto-close connection on terminal states if enabled
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

      // Handle connection errors with reconnection strategy
      eventSource.addEventListener('error', (event) => {
        const es = event.target as EventSource;
        console.error('[useSSE] SSE error occurred, readyState:', es.readyState);

        if (es.readyState === EventSource.CLOSED) {
          setIsConnected(false);
          clearKeepAliveTimer();

          const err = new Error('SSE connection closed');
          setError(err);
          onError?.(err);

          // Attempt reconnection with exponential backoff
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

  // Automatically connect on mount and when dependencies change
  useEffect(() => {
    if (enabled && url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, enabled, connect, disconnect]);

  // Methods to manage messages
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

  // Return hook API with messages, connection status, and utility methods
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