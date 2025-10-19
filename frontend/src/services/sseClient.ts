/**
 * Server-Sent Events (SSE) Client for Real-Time Progress Updates
 *
 * This service handles streaming chat responses with progress updates
 * from the backend. It provides real-time feedback during D2 diagram
 * validation, rendering, and AI processing.
 */

export interface ProgressEvent {
  stage: string;
  message: string;
}

export interface ErrorEvent {
  error: string;
}

export interface CompleteEvent {
  message: any;
  conversationId: string;
}

export interface SSECallbacks {
  onProgress?: (event: ProgressEvent) => void;
  onError?: (event: ErrorEvent) => void;
  onComplete?: (event: CompleteEvent) => void;
  onConnectionError?: (error: Error) => void;
}

/**
 * Send chat message via SSE and receive streaming progress updates
 *
 * @param message - The user's message
 * @param conversationId - The conversation ID
 * @param settings - Chat settings (model, systemPrompt, etc.)
 * @param contextFiles - Optional context files
 * @param callbacks - Event callbacks for progress, error, and completion
 * @returns A function to abort the connection
 */
export function streamChatMessage(
  message: string,
  conversationId: string,
  settings: any,
  contextFiles: string[] = [],
  callbacks: SSECallbacks = {}
): () => void {
  const BACKEND_PORT = import.meta.env.VITE_BACKEND_PORT || '8003';
  const API_BASE_URL = import.meta.env.DEV
    ? `http://localhost:${BACKEND_PORT}/api/v1`
    : '/api/v1';

  const url = `${API_BASE_URL}/stream`;

  console.log('🌊 [SSE] Initiating streaming connection:', url);

  // Create AbortController for cancellation
  const controller = new AbortController();
  const signal = controller.signal;

  // Send POST request to SSE endpoint
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({
      message,
      conversationId,
      settings,
      contextFiles,
    }),
    signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      console.log('✅ [SSE] Connected to stream');

      // Read stream chunks
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log('✅ [SSE] Stream complete');
          break;
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete events (separated by \n\n)
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const eventText of events) {
          if (!eventText.trim()) continue;

          try {
            // Parse SSE event format
            const lines = eventText.split('\n');
            let eventType = 'message';
            let eventData = '';

            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.substring(6).trim();
              } else if (line.startsWith('data:')) {
                eventData = line.substring(5).trim();
              }
            }

            // Parse JSON data
            const data = JSON.parse(eventData);

            console.log(`📨 [SSE] Event: ${eventType}`, data);

            // Dispatch to appropriate callback
            switch (eventType) {
              case 'progress':
                if (callbacks.onProgress) {
                  callbacks.onProgress(data as ProgressEvent);
                }
                break;

              case 'error':
                if (callbacks.onError) {
                  callbacks.onError(data as ErrorEvent);
                }
                break;

              case 'complete':
                if (callbacks.onComplete) {
                  callbacks.onComplete(data as CompleteEvent);
                }
                break;

              default:
                console.warn(`⚠️ [SSE] Unknown event type: ${eventType}`);
            }
          } catch (error) {
            console.error('❌ [SSE] Failed to parse event:', eventText, error);
          }
        }
      }
    })
    .catch((error) => {
      if (error.name === 'AbortError') {
        console.log('🛑 [SSE] Connection aborted by user');
      } else {
        console.error('❌ [SSE] Connection error:', error);
        if (callbacks.onConnectionError) {
          callbacks.onConnectionError(error);
        }
      }
    });

  // Return abort function
  return () => {
    console.log('🛑 [SSE] Aborting connection');
    controller.abort();
  };
}
