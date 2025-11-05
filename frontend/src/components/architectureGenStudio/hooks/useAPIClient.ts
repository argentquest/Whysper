/**
 * Custom hook for API client operations
 * Provides all API calls for Architecture Gen Studio
 */

import { useCallback } from 'react';
import type {
  Agent,
  AgentOption,
  DiagramResponse,
  GenerateDiagramRequest,
  ValidateCodeRequest,
  RenderDiagramRequest,
  ValidationResult,
} from '../types/architectureStudio';

// Placeholder for actual API base URL - replace with your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface UseAPIClientReturn {
  // Agents
  fetchAgents: () => Promise<Agent[]>;
  fetchAgentOptions: (agentId: string) => Promise<AgentOption[]>;
  // Diagrams
  submitPrompt: (request: GenerateDiagramRequest) => Promise<{
    requestId: string;
    initialResponse?: DiagramResponse;
  }>;
  validateCode: (request: ValidateCodeRequest) => Promise<ValidationResult>;
  renderDiagram: (request: RenderDiagramRequest) => Promise<DiagramResponse>;
  cancelRequest: (requestId: string) => Promise<void>;
}

export function useAPIClient(): UseAPIClientReturn {
  // ============================================================================
  // Agent API Calls
  // ============================================================================

  const fetchAgents = useCallback(async (): Promise<Agent[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }

      const agentPrompts = await response.json();

      // Transform agent prompts to Agent interface format
      const agents: Agent[] = agentPrompts.map((prompt: any) => ({
        id: prompt.name, // Use name as ID (unique identifier)
        name: prompt.title || prompt.name, // Use title for display, fallback to name
        description: prompt.description || '',
        type: prompt.category && prompt.category.length > 0 ? prompt.category[0] : undefined,
      }));

      return agents;
    } catch (error) {
      console.error('Error fetching agents:', error);
      throw error;
    }
  }, []);

  const fetchAgentOptions = useCallback(async (agentId: string): Promise<AgentOption[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${agentId}/options`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch agent options: ${response.statusText}`);
      }

      const options: AgentOption[] = await response.json();
      return options;
    } catch (error) {
      console.error(`Error fetching options for agent ${agentId}:`, error);
      throw error;
    }
  }, []);

  // ============================================================================
  // Diagram API Calls
  // ============================================================================

  const submitPrompt = useCallback(
    async (request: GenerateDiagramRequest): Promise<{ requestId: string; initialResponse?: DiagramResponse }> => {
      try {
        const response = await fetch(`${API_BASE_URL}/diagrams/v2/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          throw new Error(`Failed to submit prompt: ${response.statusText}`);
        }

        const result = await response.json();
        // Result should contain requestId for SSE tracking and possibly initial response
        return {
          requestId: result.requestId,
          initialResponse: result.diagram,
        };
      } catch (error) {
        console.error('Error submitting prompt:', error);
        throw error;
      }
    },
    []
  );

  const validateCode = useCallback(async (request: ValidateCodeRequest): Promise<ValidationResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/diagrams/v2/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(30000), // 30 second timeout
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result: ValidationResult = await response.json();
      return result;
    } catch (error) {
      console.error('Error validating code:', error);
      throw error;
    }
  }, []);

  const renderDiagram = useCallback(async (request: RenderDiagramRequest): Promise<DiagramResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/diagrams/v2/render`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Render failed: ${response.statusText}`);
      }

      const diagram: DiagramResponse = await response.json();
      return diagram;
    } catch (error) {
      console.error('Error rendering diagram:', error);
      throw error;
    }
  }, []);

  const cancelRequest = useCallback(async (requestId: string): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/diagrams/v2/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requestId }),
      });

      if (!response.ok) {
        throw new Error(`Cancel request failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error canceling request:', error);
      throw error;
    }
  }, []);

  return {
    fetchAgents,
    fetchAgentOptions,
    submitPrompt,
    validateCode,
    renderDiagram,
    cancelRequest,
  };
}
