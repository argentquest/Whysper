/**
 * useDiagramSession Hook
 *
 * Manages the lifecycle of a diagram generation session.
 * Handles initialization, updates, and cleanup.
 *
 * UPDATED: Now uses enhanced SSE hook with automatic reconnection
 */

import { useState, useCallback, useRef } from 'react';
import DiagramApi from '../../../services/diagram/diagramApi';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';
import { useSSE } from '../../../hooks/useSSE';

export interface UseDiagramSessionOptions {
  onUpdate?: (update: DiagramUpdate) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export function useDiagramSession(options: UseDiagramSessionOptions = {}) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<DiagramUpdate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const lastStatusRef = useRef<string | null>(null);

  const logEvent = useCallback((label: string, payload?: unknown) => {
    // eslint-disable-next-line no-console
    console.log(`[DiagramSession] ${label}`, payload ?? '');
  }, []);

  // Enhanced SSE hook with automatic reconnection
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1';
  const {
    isConnected: sseConnected,
    error: sseError,
    messages: sseMessages,
    clearMessages: clearSSEMessages,
  } = useSSE<DiagramUpdate>({
    url: sessionId ? `${API_BASE}/diagram/stream/${sessionId}` : '',
    enabled: !!sessionId,
    onMessage: (message) => {
      const update = message.data;

      logEvent('SSE update', update);

      // Ignore keep-alive pings that don't include a session payload
      if (!update.session_id) {
        return;
      }

      // Update status
      setStatus((prev) => ({ ...(prev ?? {}), ...update }));

      // Call user's onUpdate callback
      options.onUpdate?.(update);

      // Track last status
      lastStatusRef.current = update.status ?? lastStatusRef.current;

      // Check for completion or failure
      if (update.status === 'completed' || update.status === 'error' || update.status === 'failed') {
        logEvent('SSE completed/failed', update.status);
        options.onComplete?.();

        // If failed, treat it as an error
        if (update.status === 'failed') {
          const errorMessage = update.error || update.message || 'Diagram generation failed';
          const failedError = new Error(errorMessage);
          setError(failedError);
          options.onError?.(failedError);
        }
      }
    },
    onError: (err) => {
      logEvent('SSE error', err);
      setError(err);
      options.onError?.(err);
    },
    onConnect: () => {
      logEvent('SSE connected');
    },
    onDisconnect: () => {
      logEvent('SSE disconnected');
    },
    maxReconnectAttempts: 5,
    reconnectInterval: 2000,
    keepAliveTimeout: 30000,
    autoClose: true,
  });

  // Start a new diagram generation session with optional model selection
  const startSession = useCallback(
    async (initialPrompt: string, diagramType: string = 'Mermaid', modelId?: string) => {
      try {
        logEvent('Starting session', { initialPrompt, diagramType, modelId });
        setLoading(true);
        setError(null);
        lastStatusRef.current = null; // Reset on new session
        clearSSEMessages(); // Clear previous messages

        // Start the diagram generation with model_id if provided
        const result = await DiagramApi.startDiagramGeneration(initialPrompt, diagramType, modelId);
        setSessionId(result.session_id);
        setStatus(result.status as DiagramUpdate);
        logEvent('Session started', result.status);

        // SSE connection will auto-start via useSSE hook when sessionId is set
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to start session');
        setError(error);
        logEvent('Start session failed', error);
        options.onError?.(error);
      } finally {
        setLoading(false);
      }
    },
    [logEvent, options, clearSSEMessages]
  );

  // Submit a clarification response
  const submitClarification = useCallback(
    async (response: string) => {
      if (!sessionId) {
        throw new Error('No active session');
      }

      try {
        logEvent('Submitting clarification', { sessionId, response });
        setLoading(true);
        setError(null);

        const result = await DiagramApi.submitClarification(sessionId, response);
        setStatus(result);
        logEvent('Clarification response', result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to submit clarification');
        setError(error);
        logEvent('Clarification failed', error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [logEvent, sessionId]
  );

  // Render diagram with custom code
  const renderDiagram = useCallback(
    async (code?: string) => {
      if (!sessionId) {
        throw new Error('No active session');
      }

      try {
        logEvent('Rendering diagram', { sessionId, hasCustomCode: Boolean(code) });
        setLoading(true);
        setError(null);

        const result = await DiagramApi.renderDiagram(sessionId, code);
        setStatus(result);
        logEvent('Render response', result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to render diagram');
        setError(error);
        logEvent('Render failed', error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [logEvent, sessionId]
  );

  // Approve render
  const approveRender = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    try {
      logEvent('Approving render', { sessionId });
      setLoading(true);
      setError(null);

      const result = await DiagramApi.approveRender(sessionId);
      setStatus(result);
      logEvent('Approve render response', result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to approve render');
      setError(error);
      logEvent('Approve render failed', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [logEvent, sessionId]);

  // Confirm ready to proceed with diagram generation
  const confirmReady = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    try {
      logEvent('Confirming ready', { sessionId });
      setLoading(true);
      setError(null);

      const result = await DiagramApi.confirmReady(sessionId);
      setStatus(result);
      logEvent('Confirm ready response', result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to confirm ready');
      setError(error);
      logEvent('Confirm ready failed', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [logEvent, sessionId]);

  // Refresh the current session status
  const refreshStatus = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    try {
      logEvent('Refreshing status', { sessionId });
      const result = await DiagramApi.getDiagramStatus(sessionId);
      setStatus(result);
      logEvent('Status refreshed', result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to refresh status');
      setError(error);
      logEvent('Refresh failed', error);
      throw error;
    }
  }, [logEvent, sessionId]);

  // End the session
  const endSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      logEvent('Ending session', { sessionId });

      // Delete session from backend
      await DiagramApi.deleteDiagramSession(sessionId);

      // Reset state (SSE will auto-disconnect when sessionId becomes null)
      setSessionId(null);
      setStatus(null);
      setError(null);
      clearSSEMessages();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to end session');
      setError(error);
    }
  }, [sessionId, clearSSEMessages, logEvent]);

  return {
    sessionId,
    status,
    loading,
    error,
    sseConnected,
    sseMessages,
    sseError,
    startSession,
    submitClarification,
    confirmReady,
    renderDiagram,
    approveRender,
    refreshStatus,
    endSession,
    clearSSEMessages,
  };
}
