/**
 * useDiagramSession Hook
 *
 * Custom React hook that manages the complete lifecycle of a diagram generation session.
 * Handles communication with the backend, real-time updates via Server-Sent Events (SSE),
 * and provides a clean API for starting, monitoring, and terminating diagram generation.
 *
 * ## Session Lifecycle
 * 1. **Initialization**: Hook can start with pre-assigned sessionId from tab
 * 2. **Session Creation**: Backend session created when startSession() is called
 * 3. **SSE Connection**: Automatic SSE connection established using sessionId
 * 4. **Real-time Updates**: SSE messages streamed and processed
 * 5. **Auto-Reconnection**: 5 retry attempts with exponential backoff (2s, 4s, 8s, 16s, 32s)
 * 6. **Session Cleanup**: endSession() deletes backend session and closes connections
 *
 * ## Features
 * - **Pre-assigned Sessions**: Supports session ID provided at initialization
 * - **Automatic SSE**: Establishes SSE connection when sessionId is set
 * - **Error Handling**: Comprehensive error tracking and user callbacks
 * - **Auto-Reconnection**: Automatic reconnection with exponential backoff
 * - **Status Tracking**: Maintains current status and session state
 * - **Keep-Alive**: 30-second keep-alive timeout detection
 *
 * ## API Methods
 * - `startSession()`: Create new session on backend
 * - `submitClarification()`: Submit user response to clarification questions
 * - `confirmReady()`: Mark user as ready to proceed with generation
 * - `renderDiagram()`: Render diagram with optional custom code
 * - `approveRender()`: Approve rendered diagram
 * - `refreshStatus()`: Fetch current session status
 * - `endSession()`: Delete session and cleanup resources
 *
 * ## State Returns
 * - `sessionId`: Current backend session ID
 * - `status`: Latest SSE update containing session state
 * - `loading`: Boolean indicating API request in progress
 * - `error`: Error object if operation failed
 * - `sseConnected`: Boolean indicating SSE connection status
 * - `sseMessages`: Array of recent SSE messages
 *
 * ## Example Usage
 * ```typescript
 * const {
 *   sessionId,
 *   status,
 *   loading,
 *   startSession,
 *   submitClarification,
 * } = useDiagramSession({
 *   initialSessionId: 'diagram-session-123',
 *   onUpdate: (update) => {
 *     console.log('Session updated:', update.status);
 *   },
 *   onError: (err) => {
 *     console.error('Session error:', err.message);
 *   },
 * });
 * ```
 */

import { useState, useCallback, useRef } from 'react';
import DiagramApi from '../../../services/diagram/diagramApi';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';
import { useSSE } from '../../../hooks/useSSE';

/**
 * Configuration options for the useDiagramSession hook
 *
 * @interface UseDiagramSessionOptions
 * @property {Function} [onUpdate] - Callback invoked on every SSE update from backend.
 *                                   Receives the latest DiagramUpdate containing status, scores, and state.
 * @property {Function} [onError] - Callback invoked when an error occurs during any operation.
 *                                 Receives the Error object with descriptive message.
 * @property {Function} [onComplete] - Callback invoked when diagram generation completes or fails.
 * @property {string} [initialSessionId] - Pre-assigned backend session ID from parent tab.
 *                                        Allows session to resume or connect to existing session.
 *
 * ## Callback Details
 * - `onUpdate`: Called for every SSE message. Use to track progress or update UI.
 * - `onError`: Called on API errors, SSE errors, or operation failures.
 * - `onComplete`: Called when status becomes 'completed', 'error', or 'failed'.
 * - `initialSessionId`: If provided, hook skips session creation and connects to existing session.
 */
export interface UseDiagramSessionOptions {
  onUpdate?: (update: DiagramUpdate) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
  initialSessionId?: string;
}

export function useDiagramSession(options: UseDiagramSessionOptions = {}) {
  const [sessionId, setSessionId] = useState<string | null>(options.initialSessionId ?? null);
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

  /**
   * Initiates a new diagram generation session on the backend
   *
   * Creates a new session with the provided system description and AI model.
   * Automatically establishes SSE connection for real-time updates.
   *
   * @async
   * @function startSession
   * @param {string} initialPrompt - User's system description (e.g., "A Data Processing Pipeline")
   * @param {string} [diagramType='Mermaid'] - Target diagram type: 'Mermaid', 'D2', or 'PlantUML'
   * @param {string} [modelId] - AI model to use: 'gpt5', 'grok', 'claude', 'gemini'
   * @returns {Promise<void>} Resolves when session is created and SSE connection established
   * @throws {Error} If session creation fails (API error, network issue, etc.)
   *
   * @example
   * await startSession(
   *   'A microservices architecture with API gateway',
   *   'Mermaid',
   *   'claude'
   * );
   *
   * Side Effects:
   * - Sets sessionId state, triggering SSE connection
   * - Updates status with initial response
   * - Clears previous messages and error state
   */
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

  /**
   * Submits user response to AI clarification question
   *
   * Called during the clarification phase when AI asks questions to refine
   * system understanding. Response is sent to AI for processing.
   *
   * @async
   * @function submitClarification
   * @param {string} response - User's answer to the clarification question
   * @returns {Promise<void>} Resolves when response is submitted and processed
   * @throws {Error} If no active session or submission fails
   *
   * @example
   * await submitClarification('It uses REST APIs and communicates with PostgreSQL');
   *
   * Side Effects:
   * - Updates status with AI's assessment (clarity_score, json_representation)
   * - Triggers next clarification question if clarity_score < 8
   */
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

  /**
   * Renders diagram with generated or custom code
   *
   * Generates SVG visualization of the diagram code. Can use AI-generated code
   * or replace with custom code provided by user.
   *
   * @async
   * @function renderDiagram
   * @param {string} [code] - Optional custom diagram code to render instead of generated code
   * @returns {Promise<void>} Resolves when diagram is rendered
   * @throws {Error} If no active session or rendering fails
   *
   * @example
   * await renderDiagram(); // Render generated code
   * await renderDiagram('graph LR\n  A-->B'); // Render custom code
   */
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

  /**
   * Approves the rendered diagram
   *
   * Confirms that the user approves the current diagram rendering.
   * Called after diagram preview to proceed to export/final step.
   *
   * @async
   * @function approveRender
   * @returns {Promise<void>} Resolves when approval is registered
   * @throws {Error} If no active session or approval fails
   */
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

  /**
   * Confirms user readiness to proceed with diagram generation
   *
   * Called at end of clarification phase when user has answered all questions
   * and AI has sufficient information. Triggers transition to generation phase.
   *
   * @async
   * @function confirmReady
   * @returns {Promise<void>} Resolves when confirmation is processed
   * @throws {Error} If no active session or confirmation fails
   *
   * Side Effects:
   * - AI begins generating diagram code
   * - Status transitions from 'clarifying' to 'generating'
   */
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

  /**
   * Fetches current session status from backend
   *
   * Useful for syncing state when returning to session or checking progress.
   *
   * @async
   * @function refreshStatus
   * @returns {Promise<void>} Resolves when status is fetched and updated
   * @throws {Error} If no active session or fetch fails
   */
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
  /**
   * Terminates the diagram generation session and cleans up resources
   *
   * Called when user closes the wizard or tab is closed. Deletes the backend session,
   * closes SSE connection, and resets all state. This is critical for proper
   * resource cleanup and preventing memory leaks.
   *
   * @async
   * @function endSession
   * @returns {Promise<void>} Resolves when session is terminated and cleaned up
   *
   * Side Effects:
   * - Backend session deleted
   * - SSE connection closed
   * - All state reset to initial values
   * - Called automatically on component unmount
   *
   * Note: This is called in cleanup effect when DiagramWizard component unmounts
   * (when tab is closed).
   */
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
