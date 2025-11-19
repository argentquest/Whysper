/**
 * Diagram API Client
 *
 * Provides a TypeScript-safe API client for diagram generation endpoints.
 * Handles session management, SSE streaming, and all diagram operations.
 */

export interface ScoreInfo {
  entities: boolean;
  actions: boolean;
  structure: boolean;
  info_score: number;
  word_count: number;
  is_detailed_enough: boolean;
  has_enough_info: boolean;
  has_minimum_info: boolean;
  has_good_info: boolean;
  needed_score: string;
}

export interface DiagramSession {
  session_id: string;
  status: DiagramStatus;
  message?: string;
}

export interface DiagramStatus {
  session_id: string;
  history: Array<[string, string]>;
  currentState: Record<string, unknown>;
  clarifications: string[];
  diagramCode: string;
  svgOutput: string;
  errors: string[];
  diagramType: string;
  isRunning: boolean;
  jsonRepresentation?: Record<string, unknown>;
  score?: number;
  score_info?: ScoreInfo;
  clarity_score?: number;
  assessment_score?: number;
}

export interface DiagramUpdate extends DiagramStatus {
  status?: string;
  message?: string;
  type?: string;
  question?: string;
  message_role?: 'assistant' | 'user';
  error?: string;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1';

export class DiagramApi {
  /**
   * Start a new diagram generation session with optional model selection
   */
  static async startDiagramGeneration(
    initialPrompt: string,
    diagramType: string = 'Mermaid',
    modelId?: string,
    sessionId?: string
  ): Promise<DiagramSession> {
    const body: Record<string, unknown> = {
      initial_prompt: initialPrompt,
      diagram_type: diagramType,
    };

    // Include session_id if provided (links to tab ID for session persistence)
    if (sessionId) {
      body.session_id = sessionId;
    }

    // Include model_id if provided (for model selection feature)
    if (modelId) {
      body.model_id = modelId;
    }

    const response = await fetch(`${API_BASE}/diagram/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Failed to start diagram generation: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Stream diagram updates via Server-Sent Events
   */
  static streamDiagramUpdates(
    sessionId: string,
    onUpdate: (update: DiagramUpdate) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): () => void {
    const eventSource = new EventSource(`${API_BASE}/diagram/stream/${sessionId}`);

    eventSource.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        onUpdate(update);

        // Check if this was the final update
        if (update.status === 'completed' || update.status === 'error') {
          eventSource.close();
          onComplete();
        }
      } catch (error) {
        console.error('Failed to parse diagram update:', error);
        onError(error instanceof Error ? error : new Error('Failed to parse update'));
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      eventSource.close();
      onError(new Error('SSE connection failed'));
    };

    // Return cleanup function
    return () => {
      eventSource.close();
    };
  }

  /**
   * Submit a clarification response
   */
  static async submitClarification(
    sessionId: string,
    response: string
  ): Promise<DiagramStatus> {
    const resp = await fetch(`${API_BASE}/diagram/clarify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        response: response,
      }),
    });

    if (!resp.ok) {
      throw new Error(`Failed to submit clarification: ${resp.statusText}`);
    }

    return resp.json();
  }
  /**
   * Confirm that the user is ready to proceed with diagram generation
   */
  static async confirmReady(sessionId: string): Promise<DiagramStatus> {
    const resp = await fetch(`${API_BASE}/diagram/confirm_ready`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    if (!resp.ok) {
      throw new Error(`Failed to confirm ready: ${resp.statusText}`);
    }

    return resp.json();
  }

  static async approveRender(sessionId: string): Promise<DiagramStatus> {
    const resp = await fetch(`${API_BASE}/diagram/approve_render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    if (!resp.ok) {
      throw new Error(`Failed to approve render: ${resp.statusText}`);
    }

    return resp.json();
  }

  /**
   * Render diagram with custom code
   */
  static async renderDiagram(
    sessionId: string,
    code?: string
  ): Promise<DiagramStatus> {
    const resp = await fetch(`${API_BASE}/diagram/render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        code: code || null,
      }),
    });

    if (!resp.ok) {
      throw new Error(`Failed to render diagram: ${resp.statusText}`);
    }

    return resp.json();
  }

  /**
   * Get current session status
   */
  static async getDiagramStatus(sessionId: string): Promise<DiagramStatus> {
    const resp = await fetch(`${API_BASE}/diagram/${sessionId}`);

    if (!resp.ok) {
      throw new Error(`Failed to get diagram status: ${resp.statusText}`);
    }

    return resp.json();
  }

  /**
   * Delete a diagram session
   */
  static async deleteDiagramSession(sessionId: string): Promise<void> {
    const resp = await fetch(`${API_BASE}/diagram/${sessionId}`, {
      method: 'DELETE',
    });

    if (!resp.ok) {
      throw new Error(`Failed to delete session: ${resp.statusText}`);
    }
  }
}

export default DiagramApi;
