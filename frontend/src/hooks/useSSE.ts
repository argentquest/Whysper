/**
 * Enhanced SSE Hook for DiagramWizard
 * Provides robust Server-Sent Events with automatic reconnection
 *
 * Adapted from ArchitectureGenStudio with improvements for DiagramWizard use case
 */

import { useCallback,useEffect, useRef, useState } from 'react'

/**
 * SSEMessage type definition
 *
 * Describes the structure and properties of SSEMessage
 */
export interface SSEMessage<T = unknown> {
  id: string
  type: string
  data: T
  timestamp: number
  isRead: boolean
}

/**
 * UseSSEOptions type definition
 *
 * Describes the structure and properties of UseSSEOptions
 */
export interface UseSSEOptions<T = unknown> {
  url: string
  enabled?: boolean
  onMessage?: (message: SSEMessage<T>) => void
  onError?: (error: Error) => void
  onConnect?: () => void
  onDisconnect?: () => void
  maxReconnectAttempts?: number
  reconnectInterval?: number
  keepAliveTimeout?: number
  autoClose?: boolean // Auto-close on completed/error status
}

/**
 * UseSSEReturn type definition
 *
 * Describes the structure and properties of UseSSEReturn
 */
export interface UseSSEReturn<T = unknown> {
  messages: SSEMessage<T>[]
  isConnected: boolean
  error: Error | null
  connect: () => void
  disconnect: () => void
  clearMessages: () => void
  markAsRead: (messageId: string) => void
  markAllAsRead: () => void
}

export function useSSE<T = unknown>({
  url,
  enabled = true,
  onMessage,
  onError,
  onConnect,
  onDisconnect,
  maxReconnectAttempts = Number.POSITIVE_INFINITY,
  reconnectInterval = 2000,
  keepAliveTimeout = 300000,
  autoClose = true,
}: UseSSEOptions<T>): UseSSEReturn<T> {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<SSEMessage<T>[]>([])
  const [error, setError] = useState<Error | null>(null)

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const keepAliveTimerRef = useRef<NodeJS.Timeout | null>(null)
  const connectRef = useRef<() => void>(() => {})

  const scheduleReconnect = useCallback(() => {
    const hasAttemptsLeft =
      !Number.isFinite(maxReconnectAttempts) || reconnectAttempts.current < maxReconnectAttempts

    if (!hasAttemptsLeft) {
      console.error('[useSSE] Max reconnection attempts reached')
      const maxAttemptsError = new Error(
        'Failed to connect after ' + reconnectAttempts.current + ' attempts'
      )
      setError(maxAttemptsError)
      onError?.(maxAttemptsError)
      return
    }

    reconnectAttempts.current++
    const delay = reconnectInterval * Math.pow(2, reconnectAttempts.current - 1)
    console.log(
      `[useSSE] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`
    )
    reconnectTimeoutRef.current = setTimeout(() => {
      connectRef.current()
    }, delay)
  }, [maxReconnectAttempts, onError, reconnectInterval])

  // ============================================================================
  // Connection Management
  // ============================================================================

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Clear keep-alive timer
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current)
      keepAliveTimerRef.current = null
    }

    setIsConnected(false)
    onDisconnect?.()
  }, [onDisconnect])

  // ============================================================================
  // Keep-alive Timer Management
  // ============================================================================

  const clearKeepAliveTimer = useCallback(() => {
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current)
      keepAliveTimerRef.current = null
    }
  }, [])

  const resetKeepAliveTimer = useCallback(() => {
    clearKeepAliveTimer()
    keepAliveTimerRef.current = setTimeout(() => {
      console.warn('[useSSE] Keep-alive timeout - no messages received in', keepAliveTimeout, 'ms')
      disconnect()
      scheduleReconnect()
    }, keepAliveTimeout)
  }, [keepAliveTimeout, clearKeepAliveTimer, disconnect, scheduleReconnect])

  const connect = useCallback(() => {
    connectRef.current = connect

    if (!enabled || !url) {
      console.log('[useSSE] Connection skipped - enabled:', enabled, 'url:', url)
      return
    }

    // Close existing connection
    disconnect()

    try {
      console.log('[useSSE] Establishing SSE connection to:', url)
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      // ========================================================================
      // Open Handler
      // ========================================================================
      eventSource.addEventListener('open', () => {
        console.log('[useSSE] SSE connection opened')
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
        resetKeepAliveTimer()
        onConnect?.()
      })

      // ========================================================================
      // Message Handler
      // ========================================================================
      eventSource.addEventListener('message', (event) => {
        resetKeepAliveTimer()

        try {
          const data = JSON.parse(event.data)

          // Handle keep-alive messages (old style)
          if (data.type === 'keep-alive' || data.type === 'ping') {
            console.log('[useSSE] Keep-alive received')
            return
          }

          // Always process messages (including "waiting" status updates)
          const message: SSEMessage<T> = {
            id: data.id || `msg-${Date.now()}-${Math.random()}`,
            type: data.type || data.status || 'message',
            data: data,
            timestamp: Date.now(),
            isRead: false,
          }

          setMessages((prev) => [...prev, message])
          onMessage?.(message)

          // Log waiting status for debugging
          if (data.status === 'waiting') {
            console.log('[useSSE] Server is waiting for LLM response:', data.message)
          }

          // Auto-close on terminal states if enabled
          if (autoClose && (data.status === 'completed' || data.status === 'error')) {
            console.log('[useSSE] Terminal status received, closing connection')
            setTimeout(() => {
              disconnect()
            }, 1000) // Small delay to ensure all messages are processed
          }
        } catch (err) {
          console.error('[useSSE] Error parsing SSE message:', err)
        }
      })

      // ========================================================================
      // Error Handler with Exponential Backoff
      // ========================================================================
      eventSource.addEventListener('error', (event) => {
        const es = event.target as EventSource
        console.error('[useSSE] SSE error occurred, readyState:', es.readyState)

        if (es.readyState === EventSource.CLOSED) {
          setIsConnected(false)
          clearKeepAliveTimer()

          const err = new Error('SSE connection closed')
          setError(err)
          onError?.(err)

          // Attempt reconnection with exponential backoff
          scheduleReconnect()
        }
      })
    } catch (err) {
      console.error('[useSSE] Error creating SSE connection:', err)
      const connectionError =
        err instanceof Error ? err : new Error('Failed to establish SSE connection')
      setError(connectionError)
      onError?.(connectionError)
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
    scheduleReconnect,
    autoClose,
  ])

  // ============================================================================
  // Auto-connect on mount and when dependencies change
  // ============================================================================
  useEffect(() => {
    if (enabled && url) {
      connect()
    }

    return () => {
      disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, enabled]) // Only depend on url and enabled to avoid reconnection loops

  // ============================================================================
  // Message Management
  // ============================================================================

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const markAsRead = useCallback((messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, isRead: true } : msg))
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setMessages((prev) => prev.map((msg) => ({ ...msg, isRead: true })))
  }, [])

  // ============================================================================
  // Return Hook API
  // ============================================================================

  return {
    messages,
    isConnected,
    error,
    connect,
    disconnect,
    clearMessages,
    markAsRead,
    markAllAsRead,
  }
}
