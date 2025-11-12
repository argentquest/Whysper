/**
 * useDiagramSession Hook
 *
 * Manages the lifecycle of a diagram generation session.
 * Handles initialization, updates, and cleanup.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import DiagramApi from '../../../services/diagram/diagramApi';
import type { DiagramStatus, DiagramUpdate } from '../../../services/diagram/diagramApi';

interface UseDiagramSessionOptions {
  onUpdate?: (update: DiagramUpdate) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export function useDiagramSession(options: UseDiagramSessionOptions = {}) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<DiagramStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [cleanupFn, setCleanupFn] = useState<(() => void) | null>(null);
  const lastStatusRef = useRef<string | null>(null);
  const logEvent = useCallback((label: string, payload?: unknown) => {
    // eslint-disable-next-line no-console
    console.log(`[DiagramSession] ${label}`, payload ?? '');
  }, []);

  // Start a new diagram generation session
  const startSession = useCallback(
    async (initialPrompt: string, diagramType: string = 'Mermaid') => {
      try {
        logEvent('Starting session', { initialPrompt, diagramType });
        setLoading(true);
        setError(null);
        lastStatusRef.current = null; // Reset on new session

        // Start the diagram generation
        const result = await DiagramApi.startDiagramGeneration(initialPrompt, diagramType);
        setSessionId(result.session_id);
        setStatus(result.status);
        logEvent('Session started', result.status);
        lastStatusRef.current = result.status.status;

        // Start streaming updates
        const cleanup = DiagramApi.streamDiagramUpdates(
          result.session_id,
          (update) => {
            logEvent('SSE update', update);

            // Ignore keep-alive pings that don't include a session payload.
            if (!update.session_id) {
              return;
            }

            setStatus(prev => ({ ...(prev ?? {}), ...update }));
            options.onUpdate?.(update);
            lastStatusRef.current = update.status ?? lastStatusRef.current;
          },
          (err) => {
            logEvent('SSE error', err);
            setError(err);
            options.onError?.(err);
          },
          () => {
            logEvent('SSE completed');
            options.onComplete?.();
          }
        );

        setCleanupFn(() => cleanup);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to start session');
        setError(error);
        logEvent('Start session failed', error);
        options.onError?.(error);
      } finally {
        setLoading(false);
      }
    },
    [logEvent, options]
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
      // Clean up SSE connection
      logEvent('Ending session', { sessionId });
      cleanupFn?.();

      // Delete session from backend
      await DiagramApi.deleteDiagramSession(sessionId);

      setSessionId(null);
      setStatus(null);
      setError(null);
      setCleanupFn(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to end session');
      setError(error);
    }
  }, [sessionId, cleanupFn]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupFn?.();
    };
  }, [cleanupFn]);

  return {
    sessionId,
    status,
    loading,
    error,
    startSession,
    submitClarification,
    renderDiagram,
    approveRender,
    refreshStatus,
    endSession,
  };
}
