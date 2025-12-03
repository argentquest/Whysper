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

import { useCallback, useRef,useState } from 'react'

import { useSSE } from '../../../hooks/useSSE'
import type { DiagramUpdate } from '../../../services/diagram/diagramApi'
import DiagramApi from '../../../services/diagram/diagramApi'

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
  onUpdate?: (update: DiagramUpdate) => void
  onError?: (error: Error) => void
  onComplete?: () => void
  initialSessionId?: string
}

export function useDiagramSession(options: UseDiagramSessionOptions = {}) {
  // Store the pre-assigned session ID from the tab (for linking when we call /start)
  // This should NOT be used to immediately connect to SSE - only passed to /start API call
  const initialSessionId = options.initialSessionId

  // Backend session UUID - null until startSession() creates a session
  // Will be set to the result.session_id returned from /start endpoint
  // This triggers SSE connection only AFTER session is created on backend
  const [sessionId, setSessionId] = useState<string | null>(null)

  // Latest session status update received via SSE
  // Contains: status, history, clarifications, diagramCode, svgOutput, scores, etc.
  const [status, setStatus] = useState<DiagramUpdate | null>(null)

  // Loading state during API requests (startSession, submitClarification, etc.)
  const [loading, setLoading] = useState(false)

  // Error state if any operation fails (API calls, SSE connection, etc.)
  const [error, setError] = useState<Error | null>(null)

  // Track previous status value to detect transitions
  // Used ref instead of state to avoid triggering re-renders
  const lastStatusRef = useRef<string | null>(null)

  // Utility function to log session events with consistent formatting
  const logEvent = useCallback((label: string, payload?: unknown) => {

    console.log(`[DiagramSession] ${label}`, payload ?? '')
  }, [])

  // Configure SSE connection for real-time backend updates
  // Automatically connects when sessionId is set, disconnects when cleared
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

  const {
    isConnected: sseConnected, // Boolean: true when connection is active
    error: sseError, // Error object if SSE connection fails
    messages: sseMessages, // Array of received SSE messages (for debugging)
    clearMessages: clearSSEMessages, // Function to clear message history
    disconnect: disconnectSSE, // Function to manually disconnect SSE
  } = useSSE<DiagramUpdate>({
    // Construct SSE endpoint URL using session ID
    url: sessionId ? `${API_BASE}/diagram/stream/${sessionId}` : '',

    // Only connect when sessionId exists (prevents premature connections)
    enabled: !!sessionId,

    // Handle incoming SSE messages
    onMessage: (message) => {
      // Extract update payload from SSE message
      const update = message.data

      logEvent('SSE update', update)

      // Ignore keep-alive pings that don't contain session data
      // Backend sends periodic pings to keep connection alive
      if (!update.session_id) {
        return
      }

      // Transform snake_case fields to camelCase for consistency
      // Backend sends json_representation, frontend expects jsonRepresentation
      const transformedUpdate = { ...update }

      if (update.json_representation) {
        transformedUpdate.jsonRepresentation = update.json_representation
      }
      if ((update as any).svg_output && !update.svgOutput) {
        transformedUpdate.svgOutput = (update as any).svg_output
      }
      if ((update as any).diagram_code && !update.diagramCode) {
        transformedUpdate.diagramCode = (update as any).diagram_code
      }
      if ((update as any).diagram_type && !update.diagramType) {
        transformedUpdate.diagramType = (update as any).diagram_type
      }

      // Merge new update with existing status (preserves fields not in current update)
      setStatus((prev) => ({ ...(prev ?? {}), ...transformedUpdate }))

      // Notify parent component of the update
      options.onUpdate?.(update)

      // Store status value for transition detection
      lastStatusRef.current = update.status ?? lastStatusRef.current

      // Check if processing has reached terminal state
      if (
        update.status === 'completed' ||
        update.status === 'error' ||
        update.status === 'failed'
      ) {
        logEvent('SSE completed/failed', update.status)

        // Notify parent that processing is complete
        options.onComplete?.()

        // Convert 'failed' status into an error for proper error handling
        if (update.status === 'failed') {
          const errorMessage = update.error || update.message || 'Diagram generation failed'
          const failedError = new Error(errorMessage)
          setError(failedError)
          options.onError?.(failedError)
        }
      }
    },

    // Handle SSE connection errors
    onError: (err) => {
      logEvent('SSE error', err)

      // Note: EventSource API doesn't provide HTTP status codes in error events,
      // so we can't directly detect "session not found" (404) errors here.
      // Stale session prevention is handled by session validation on DiagramWizard mount.

      setError(err)
      options.onError?.(err)
    },

    // Log when SSE connection is established
    onConnect: () => {
      logEvent('SSE connected')
    },

    // Log when SSE connection is lost
    onDisconnect: () => {
      logEvent('SSE disconnected')
    },

    // Reconnection configuration
    maxReconnectAttempts: Number.POSITIVE_INFINITY, // Keep trying indefinitely
    reconnectInterval: 2000, // Wait 2 seconds before first retry (exponential backoff applied)
    keepAliveTimeout: 300000, // Consider connection dead if no message for 5 minutes
    autoClose: true, // Automatically close connection when component unmounts
  })

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
        logEvent('Starting session', { initialPrompt, diagramType, modelId, sessionId })

        // Set loading state to show UI spinner
        setLoading(true)

        // Clear any previous error state from last session
        setError(null)

        // Reset status tracking for new session
        lastStatusRef.current = null

        // Clear old SSE messages from previous session
        clearSSEMessages()

        // Call backend API to create new session and begin AI analysis
        // Pass the pre-assigned initialSessionId (from tab) to link them together
        // Backend returns session_id (should match what was passed) and initial status
        const result = await DiagramApi.startDiagramGeneration(
          initialPrompt,
          diagramType,
          modelId,
          initialSessionId || undefined // Pass pre-assigned session ID from tab if available
        )

        // Store session ID - this triggers SSE connection via useSSE hook
        // Use the returned session_id (which should match what we passed)
        setSessionId(result.session_id)

        // Store initial status from session creation response
        setStatus(result.status as DiagramUpdate)

        logEvent('Session started', result.status)

        // SSE connection will automatically establish when sessionId changes
      } catch (err) {
        // Handle session creation failure
        const error = err instanceof Error ? err : new Error('Failed to start session')
        setError(error)
        logEvent('Start session failed', error)

        // Notify parent component of the error
        options.onError?.(error)
      } finally {
        // Clear loading state regardless of success/failure
        setLoading(false)
      }
    },
    [logEvent, options, clearSSEMessages, initialSessionId]
  )

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
      // Ensure session exists before submitting clarification
      if (!sessionId) {
        throw new Error('No active session')
      }

      try {
        logEvent('Submitting clarification', { sessionId, response })

        // Set loading state to show UI spinner
        setLoading(true)

        // Clear previous error state
        setError(null)

        // Send clarification response to backend
        // Backend triggers AI to assess response and update clarity score
        const result = await DiagramApi.submitClarification(sessionId, response)

        // Update status with AI's assessment
        // May include new clarity_score and json_representation
        setStatus(result)

        logEvent('Clarification response', result)
      } catch (err) {
        // Handle clarification submission failure
        const error = err instanceof Error ? err : new Error('Failed to submit clarification')
        setError(error)
        logEvent('Clarification failed', error)

        // Re-throw to allow caller to handle error
        throw error
      } finally {
        // Clear loading state regardless of outcome
        setLoading(false)
      }
    },
    [logEvent, sessionId]
  )

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
      // Ensure session exists before rendering
      if (!sessionId) {
        throw new Error('No active session')
      }

      try {
        logEvent('Rendering diagram', { sessionId, hasCustomCode: Boolean(code) })

        // Set loading state for UI feedback
        setLoading(true)

        // Clear previous errors
        setError(null)

        // Send render request to backend with optional custom code
        // If code provided, use it; otherwise backend uses generated code
        const result = await DiagramApi.renderDiagram(sessionId, code)

        // Update status with rendered SVG output
        setStatus(result)

        logEvent('Render response', result)
      } catch (err) {
        // Handle rendering failure
        const error = err instanceof Error ? err : new Error('Failed to render diagram')
        setError(error)
        logEvent('Render failed', error)

        // Re-throw to allow caller to handle
        throw error
      } finally {
        // Clear loading state
        setLoading(false)
      }
    },
    [logEvent, sessionId]
  )

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
    // Ensure session exists before approving
    if (!sessionId) {
      throw new Error('No active session')
    }

    try {
      logEvent('Approving render', { sessionId })

      // Set loading state
      setLoading(true)

      // Clear previous errors
      setError(null)

      // Send approval to backend to mark diagram as finalized
      const result = await DiagramApi.approveRender(sessionId)

      // Update status with approval confirmation
      setStatus(result)

      logEvent('Approve render response', result)
    } catch (err) {
      // Handle approval failure
      const error = err instanceof Error ? err : new Error('Failed to approve render')
      setError(error)
      logEvent('Approve render failed', error)

      // Re-throw to allow caller to handle
      throw error
    } finally {
      // Clear loading state
      setLoading(false)
    }
  }, [logEvent, sessionId])

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
    // Ensure session exists before confirming
    if (!sessionId) {
      throw new Error('No active session')
    }

    try {
      logEvent('Confirming ready', { sessionId })

      // Set loading state for UI feedback
      setLoading(true)

      // Clear previous errors
      setError(null)

      // Signal backend that user is satisfied with clarification phase
      // This triggers AI to begin generating diagram code
      const result = await DiagramApi.confirmReady(sessionId)

      // Update status - should transition to 'generating' status
      setStatus(result)

      logEvent('Confirm ready response', result)
    } catch (err) {
      // Handle confirmation failure
      const error = err instanceof Error ? err : new Error('Failed to confirm ready')
      setError(error)
      logEvent('Confirm ready failed', error)

      // Re-throw to allow caller to handle
      throw error
    } finally {
      // Clear loading state
      setLoading(false)
    }
  }, [logEvent, sessionId])

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
    // Ensure session exists before fetching status
    if (!sessionId) {
      throw new Error('No active session')
    }

    try {
      logEvent('Refreshing status', { sessionId })

      // Fetch latest status from backend without SSE
      // Useful for manual refresh or when SSE connection is lost
      const result = await DiagramApi.getDiagramStatus(sessionId)

      // Update local status with fetched data
      setStatus(result)

      logEvent('Status refreshed', result)
    } catch (err) {
      // Handle fetch failure
      const error = err instanceof Error ? err : new Error('Failed to refresh status')
      setError(error)
      logEvent('Refresh failed', error)

      // Re-throw to allow caller to handle
      throw error
    }
  }, [logEvent, sessionId])

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
    // Ignore if no active session
    if (!sessionId) return

    try {
      logEvent('Ending session', { sessionId })

      // Call backend API to delete session and free resources
      // Backend will cleanup: session data, temp files, LLM connections
      await DiagramApi.deleteDiagramSession(sessionId)

      // Reset all local state to initial values
      setSessionId(null) // Setting null triggers SSE disconnection via useSSE hook
      setStatus(null) // Clear session status data
      setError(null) // Clear any error state
      clearSSEMessages() // Clear SSE message history
    } catch (err) {
      // Handle cleanup failure
      const error = err instanceof Error ? err : new Error('Failed to end session')
      setError(error)
      // Don't throw - cleanup should be best-effort
    }
  }, [sessionId, clearSSEMessages, logEvent])

  // Return hook API with all session management functions and state
  return {
    sessionId, // Current backend session UUID (null if no active session)
    status, // Latest session status from SSE (contains history, code, SVG, etc.)
    loading, // True during API requests (start, clarify, render, etc.)
    error, // Error object if any operation failed
    sseConnected, // True when SSE connection is active
    sseMessages, // Array of received SSE messages (for debugging)
    sseError, // Error object if SSE connection failed
    startSession, // Function to create new session
    submitClarification, // Function to answer AI's clarification questions
    confirmReady, // Function to skip clarification and proceed to generation
    renderDiagram, // Function to generate SVG from diagram code
    approveRender, // Function to approve rendered diagram
    refreshStatus, // Function to manually fetch latest status
    endSession, // Function to cleanup and delete session
    clearSSEMessages, // Function to clear SSE message history
  }
}
