Here's the code with added inline comments explaining the logic:

// Base configuration for API endpoint, using environment variable or localhost fallback
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1';

export class DiagramApi {
  /**
   * Start a new diagram generation session with optional model selection
   */
  static async startDiagramGeneration(
    initialPrompt: string,
    diagramType: string = 'Mermaid',
    modelId?: string
  ): Promise<DiagramSession> {
    // Prepare request body with required diagram generation parameters
    const body: Record<string, unknown> = {
      initial_prompt: initialPrompt,
      diagram_type: diagramType,
    };

    // Include model_id if provided (for model selection feature)
    if (modelId) {
      body.model_id = modelId;
    }

    // Send POST request to start diagram generation
    const response = await fetch(`${API_BASE}/diagram/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    // Throw error if request fails
    if (!response.ok) {
      throw new Error(`Failed to start diagram generation: ${response.statusText}`);
    }

    // Return parsed JSON response
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
    // Create EventSource to listen for server-side events
    const eventSource = new EventSource(`${API_BASE}/diagram/stream/${sessionId}`);

    // Handle incoming messages from server
    eventSource.onmessage = (event) => {
      try {
        // Parse incoming event data
        const update = JSON.parse(event.data);
        onUpdate(update);

        // Close connection if final update is received
        if (update.status === 'completed' || update.status === 'error') {
          eventSource.close();
          onComplete();
        }
      } catch (error) {
        // Handle parsing errors
        console.error('Failed to parse diagram update:', error);
        onError(error instanceof Error ? error : new Error('Failed to parse update'));
      }
    };

    // Handle connection errors
    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      eventSource.close();
      onError(new Error('SSE connection failed'));
    };

    // Return cleanup function to close event source
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
    // Send POST request with clarification response
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

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to submit clarification: ${resp.statusText}`);
    }

    // Return parsed JSON response
    return resp.json();
  }

  /**
   * Confirm that the user is ready to proceed with diagram generation
   */
  static async confirmReady(sessionId: string): Promise<DiagramStatus> {
    // Send POST request to confirm readiness
    const resp = await fetch(`${API_BASE}/diagram/confirm_ready`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to confirm ready: ${resp.statusText}`);
    }

    // Return parsed JSON response
    return resp.json();
  }

  /**
   * Approve diagram rendering
   */
  static async approveRender(sessionId: string): Promise<DiagramStatus> {
    // Send POST request to approve rendering
    const resp = await fetch(`${API_BASE}/diagram/approve_render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to approve render: ${resp.statusText}`);
    }

    // Return parsed JSON response
    return resp.json();
  }

  /**
   * Render diagram with custom code
   */
  static async renderDiagram(
    sessionId: string,
    code?: string
  ): Promise<DiagramStatus> {
    // Send POST request to render diagram
    const resp = await fetch(`${API_BASE}/diagram/render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        code: code || null, // Allow optional custom code
      }),
    });

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to render diagram: ${resp.statusText}`);
    }

    // Return parsed JSON response
    return resp.json();
  }

  /**
   * Get current session status
   */
  static async getDiagramStatus(sessionId: string): Promise<DiagramStatus> {
    // Fetch current status for given session
    const resp = await fetch(`${API_BASE}/diagram/${sessionId}`);

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to get diagram status: ${resp.statusText}`);
    }

    // Return parsed JSON response
    return resp.json();
  }

  /**
   * Delete a diagram session
   */
  static async deleteDiagramSession(sessionId: string): Promise<void> {
    // Send DELETE request to remove session
    const resp = await fetch(`${API_BASE}/diagram/${sessionId}`, {
      method: 'DELETE',
    });

    // Throw error if request fails
    if (!resp.ok) {
      throw new Error(`Failed to delete session: ${resp.statusText}`);
    }
  }
}