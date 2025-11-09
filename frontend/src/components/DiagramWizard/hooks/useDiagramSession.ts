/**
 * useDiagramSession Hook
 *
 * Manages the lifecycle of a diagram generation session.
 * Handles initialization, updates, and cleanup.
 */

import { useState, useCallback, useEffect } from 'react';
import DiagramApi, { DiagramStatus, DiagramUpdate } from '../../../services/diagram/diagramApi';

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

  // Start a new diagram generation session
  const startSession = useCallback(
    async (initialPrompt: string, diagramType: string = 'Mermaid') => {
      try {
        setLoading(true);
        setError(null);

        // Start the diagram generation
        const result = await DiagramApi.startDiagramGeneration(initialPrompt, diagramType);
        setSessionId(result.session_id);
        setStatus(result.status);

        // Start streaming updates
        const cleanup = DiagramApi.streamDiagramUpdates(
          result.session_id,
          (update) => {
            setStatus(update);
            options.onUpdate?.(update);
          },
          (err) => {
            setError(err);
            options.onError?.(err);
          },
          () => {
            options.onComplete?.();
          }
        );

        setCleanupFn(() => cleanup);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to start session');
        setError(error);
        options.onError?.(error);
      } finally {
        setLoading(false);
      }
    },
    [options]
  );

  // Submit a clarification response
  const submitClarification = useCallback(
    async (response: string) => {
      if (!sessionId) {
        throw new Error('No active session');
      }

      try {
        setLoading(true);
        setError(null);

        const result = await DiagramApi.submitClarification(sessionId, response);
        setStatus(result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to submit clarification');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  // Render diagram with custom code
  const renderDiagram = useCallback(
    async (code?: string) => {
      if (!sessionId) {
        throw new Error('No active session');
      }

      try {
        setLoading(true);
        setError(null);

        const result = await DiagramApi.renderDiagram(sessionId, code);
        setStatus(result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to render diagram');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  // Refresh the current session status
  const refreshStatus = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    try {
      const result = await DiagramApi.getDiagramStatus(sessionId);
      setStatus(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to refresh status');
      setError(error);
      throw error;
    }
  }, [sessionId]);

  // End the session
  const endSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      // Clean up SSE connection
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
    refreshStatus,
    endSession,
  };
}
