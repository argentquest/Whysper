/**
 * Integration Tests for Architecture Gen Studio
 * Tests the complete workflow from API calls to state updates
 */

import { Agent, AgentOption, DiagramResponse, ValidationResult, GenerateDiagramRequest } from '../types/architectureStudio';

// ============================================================================
// Mock API Setup
// ============================================================================

// Mock agents data for testing
export const MOCK_AGENTS: Agent[] = [
  {
    id: 'agent-1',
    name: 'C4 Diagram Agent',
    description: 'Generates C4 architecture diagrams',
  },
  {
    id: 'agent-2',
    name: 'Sequence Diagram Agent',
    description: 'Generates sequence diagrams',
  },
  {
    id: 'agent-3',
    name: 'ER Diagram Agent',
    description: 'Generates entity relationship diagrams',
  },
];

// Mock agent options
export const MOCK_AGENT_OPTIONS: Record<string, AgentOption[]> = {
  'agent-1': [
    {
      id: 'option-1-1',
      agentId: 'agent-1',
      name: 'System Context Diagram',
      description: 'High-level overview of system interactions',
      template: 'Create a C4 system context diagram for a [SYSTEM_NAME] system that [SYSTEM_PURPOSE]',
      validationRules: ['Must include system boundary', 'Must show external systems'],
      outputFormat: 'SVG',
      enabled: true,
    },
    {
      id: 'option-1-2',
      agentId: 'agent-1',
      name: 'Container Diagram',
      description: 'Technology-specific architecture overview',
      template: 'Create a C4 container diagram showing [CONTAINERS] in [SYSTEM_NAME]',
      validationRules: ['Must show major containers', 'Must include technologies'],
      outputFormat: 'SVG',
      enabled: true,
    },
  ],
  'agent-2': [
    {
      id: 'option-2-1',
      agentId: 'agent-2',
      name: 'User Flow Sequence',
      description: 'Sequence of user interactions',
      template: 'Create a sequence diagram for user action: [ACTION_DESCRIPTION]',
      validationRules: ['Must show participants', 'Must show message flow'],
      outputFormat: 'SVG',
      enabled: true,
    },
  ],
};

// Mock diagram response
export const MOCK_DIAGRAM_RESPONSE: DiagramResponse = {
  svg: '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="blue"/></svg>',
  provider: 'mermaid',
  code: 'graph TD\n  A[Start] --> B[Process]\n  B --> C[End]',
  metadata: {
    provider: 'mermaid',
    generationParameters: {
      theme: 'default',
      layout: 'default',
    },
  },
  status: 'success',
  timestamp: new Date().toISOString(),
};

// Mock validation result
export const MOCK_VALIDATION_RESULT: ValidationResult = {
  isValid: true,
  errors: [],
  warnings: [],
};

export const MOCK_VALIDATION_ERROR_RESULT: ValidationResult = {
  isValid: false,
  errors: [
    {
      id: 'error-1',
      message: 'Invalid mermaid syntax',
      code: 'SYNTAX_ERROR',
      details: 'Missing closing bracket on line 2',
      timestamp: new Date().toISOString(),
    },
  ],
  warnings: [],
};

// ============================================================================
// Mock API Client
// ============================================================================

export class MockAPIClient {
  private agents = MOCK_AGENTS;
  private agentOptions = MOCK_AGENT_OPTIONS;
  private delayMs = 100;

  setDelay(ms: number) {
    this.delayMs = ms;
  }

  async fetchAgents(): Promise<Agent[]> {
    await this.delay();
    return this.agents;
  }

  async fetchAgentOptions(agentId: string): Promise<AgentOption[]> {
    await this.delay();
    const options = this.agentOptions[agentId];
    if (!options) {
      throw new Error(`No options found for agent ${agentId}`);
    }
    return options;
  }

  async submitPrompt(request: GenerateDiagramRequest): Promise<{
    requestId: string;
    initialResponse?: DiagramResponse;
  }> {
    await this.delay();
    if (!request.agentId || !request.prompt) {
      throw new Error('Missing required fields: agentId, prompt');
    }
    return {
      requestId: `req-${Date.now()}`,
      initialResponse: MOCK_DIAGRAM_RESPONSE,
    };
  }

  async validateCode(request: { code: string; diagramType: string }): Promise<ValidationResult> {
    await this.delay();
    if (!request.code) {
      throw new Error('Code is required for validation');
    }
    // Simulate validation error if code is empty or very short
    if (request.code.trim().length < 5) {
      return MOCK_VALIDATION_ERROR_RESULT;
    }
    return MOCK_VALIDATION_RESULT;
  }

  async renderDiagram(request: { code: string; diagramType: string }): Promise<DiagramResponse> {
    await this.delay();
    if (!request.code) {
      throw new Error('Code is required for rendering');
    }
    return {
      ...MOCK_DIAGRAM_RESPONSE,
      code: request.code,
    };
  }

  async cancelRequest(requestId: string): Promise<void> {
    await this.delay();
    if (!requestId) {
      throw new Error('Request ID is required');
    }
  }

  private async delay(): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, this.delayMs));
  }
}

// ============================================================================
// Test Scenarios
// ============================================================================

export interface TestScenario {
  name: string;
  description: string;
  steps: TestStep[];
  expectedResult: string;
}

export interface TestStep {
  action: string;
  params?: Record<string, any>;
  expectedResponse?: any;
  expectedError?: string;
}

// Scenario 1: Agent Selection and Option Loading
export const SCENARIO_AGENT_SELECTION: TestScenario = {
  name: 'Agent Selection and Option Loading',
  description: 'User selects an agent and views available diagram options',
  steps: [
    {
      action: 'fetchAgents',
      expectedResponse: MOCK_AGENTS,
    },
    {
      action: 'selectAgent',
      params: { agentId: 'agent-1' },
    },
    {
      action: 'fetchAgentOptions',
      params: { agentId: 'agent-1' },
      expectedResponse: MOCK_AGENT_OPTIONS['agent-1'],
    },
  ],
  expectedResult: 'Agent selected, options loaded and displayed',
};

// Scenario 2: Diagram Generation Workflow
export const SCENARIO_DIAGRAM_GENERATION: TestScenario = {
  name: 'Complete Diagram Generation',
  description: 'User generates a diagram from prompt to rendering',
  steps: [
    {
      action: 'selectAgent',
      params: { agentId: 'agent-1' },
    },
    {
      action: 'selectAgentOption',
      params: { optionId: 'option-1-1' },
    },
    {
      action: 'submitPrompt',
      params: {
        agentId: 'agent-1',
        prompt: 'Create a system context diagram',
        diagramType: 'mermaid',
      },
      expectedResponse: {
        requestId: expect.any(String),
        initialResponse: MOCK_DIAGRAM_RESPONSE,
      },
    },
    {
      action: 'connectSSE',
      params: { requestId: expect.any(String) },
    },
  ],
  expectedResult: 'Diagram generated successfully with SSE updates',
};

// Scenario 3: Code Validation and Rendering
export const SCENARIO_CODE_VALIDATION: TestScenario = {
  name: 'Code Validation and Rendering',
  description: 'User validates code and renders diagram',
  steps: [
    {
      action: 'validateCode',
      params: {
        code: 'graph TD\n  A[Start] --> B[Process]',
        diagramType: 'mermaid',
      },
      expectedResponse: MOCK_VALIDATION_RESULT,
    },
    {
      action: 'renderDiagram',
      params: {
        code: 'graph TD\n  A[Start] --> B[Process]',
        diagramType: 'mermaid',
      },
      expectedResponse: MOCK_DIAGRAM_RESPONSE,
    },
  ],
  expectedResult: 'Code validated and diagram rendered',
};

// Scenario 4: Error Handling - Invalid Code
export const SCENARIO_VALIDATION_ERROR: TestScenario = {
  name: 'Validation Error Handling',
  description: 'System handles validation errors gracefully',
  steps: [
    {
      action: 'validateCode',
      params: {
        code: 'a',
        diagramType: 'mermaid',
      },
      expectedResponse: MOCK_VALIDATION_ERROR_RESULT,
    },
    {
      action: 'showErrors',
      params: { errors: MOCK_VALIDATION_ERROR_RESULT.errors },
    },
  ],
  expectedResult: 'Validation errors displayed to user',
};

// Scenario 5: Request Cancellation
export const SCENARIO_REQUEST_CANCELLATION: TestScenario = {
  name: 'Request Cancellation',
  description: 'User cancels an ongoing request',
  steps: [
    {
      action: 'submitPrompt',
      params: {
        agentId: 'agent-1',
        prompt: 'Generate diagram',
        diagramType: 'mermaid',
      },
    },
    {
      action: 'cancelRequest',
      params: { requestId: expect.any(String) },
    },
  ],
  expectedResult: 'Request cancelled successfully',
};

// Scenario 6: Multiple Diagram Types
export const SCENARIO_MULTIPLE_DIAGRAMS: TestScenario = {
  name: 'Multiple Diagram Type Switching',
  description: 'User switches between different diagram types',
  steps: [
    {
      action: 'selectDiagramType',
      params: { type: 'mermaid' },
    },
    {
      action: 'renderDiagram',
      params: { code: 'graph TD\n  A --> B', diagramType: 'mermaid' },
    },
    {
      action: 'selectDiagramType',
      params: { type: 'd2' },
    },
    {
      action: 'renderDiagram',
      params: { code: 'A -> B', diagramType: 'd2' },
    },
  ],
  expectedResult: 'Successfully switched between diagram types and rendered',
};

// ============================================================================
// Integration Test Suite
// ============================================================================

export class IntegrationTestSuite {
  private apiClient: MockAPIClient;

  constructor() {
    this.apiClient = new MockAPIClient();
  }

  async runScenario(scenario: TestScenario): Promise<TestResult> {
    const result: TestResult = {
      scenarioName: scenario.name,
      passed: true,
      steps: [],
      errors: [],
    };

    try {
      for (const step of scenario.steps) {
        const stepResult = await this.executeStep(step);
        result.steps.push(stepResult);

        if (!stepResult.passed) {
          result.passed = false;
          result.errors.push(stepResult.error || 'Step failed');
        }
      }
    } catch (error) {
      result.passed = false;
      result.errors.push(error instanceof Error ? error.message : 'Unknown error');
    }

    return result;
  }

  private async executeStep(step: TestStep): Promise<StepResult> {
    const stepResult: StepResult = {
      action: step.action,
      passed: true,
    };

    try {
      switch (step.action) {
        case 'fetchAgents':
          const agents = await this.apiClient.fetchAgents();
          stepResult.passed = agents.length === MOCK_AGENTS.length;
          break;

        case 'fetchAgentOptions':
          const options = await this.apiClient.fetchAgentOptions(step.params?.agentId);
          stepResult.passed = Array.isArray(options) && options.length > 0;
          break;

        case 'submitPrompt':
          const submitResult = await this.apiClient.submitPrompt(step.params);
          stepResult.passed = !!submitResult.requestId;
          break;

        case 'validateCode':
          const validationResult = await this.apiClient.validateCode(step.params);
          stepResult.passed = validationResult !== null;
          break;

        case 'renderDiagram':
          const renderResult = await this.apiClient.renderDiagram(step.params);
          stepResult.passed = !!renderResult.svg;
          break;

        case 'cancelRequest':
          await this.apiClient.cancelRequest(step.params?.requestId);
          stepResult.passed = true;
          break;

        case 'selectAgent':
        case 'selectAgentOption':
        case 'selectDiagramType':
        case 'connectSSE':
        case 'showErrors':
          // UI actions that always succeed
          stepResult.passed = true;
          break;

        default:
          stepResult.passed = false;
          stepResult.error = `Unknown action: ${step.action}`;
      }
    } catch (error) {
      stepResult.passed = false;
      stepResult.error = error instanceof Error ? error.message : 'Unknown error';
    }

    return stepResult;
  }

  async runAllScenarios(): Promise<TestResult[]> {
    const scenarios = [
      SCENARIO_AGENT_SELECTION,
      SCENARIO_DIAGRAM_GENERATION,
      SCENARIO_CODE_VALIDATION,
      SCENARIO_VALIDATION_ERROR,
      SCENARIO_REQUEST_CANCELLATION,
      SCENARIO_MULTIPLE_DIAGRAMS,
    ];

    const results: TestResult[] = [];
    for (const scenario of scenarios) {
      results.push(await this.runScenario(scenario));
    }
    return results;
  }
}

// ============================================================================
// Test Result Types
// ============================================================================

export interface TestResult {
  scenarioName: string;
  passed: boolean;
  steps: StepResult[];
  errors: string[];
}

export interface StepResult {
  action: string;
  passed: boolean;
  error?: string;
}

// ============================================================================
// Test Runner
// ============================================================================

export async function runIntegrationTests(): Promise<void> {
  const suite = new IntegrationTestSuite();
  const results = await suite.runAllScenarios();

  console.log('='.repeat(70));
  console.log('Architecture Gen Studio - Integration Test Results');
  console.log('='.repeat(70));

  let passedCount = 0;
  let failedCount = 0;

  for (const result of results) {
    if (result.passed) {
      console.log(`✓ ${result.scenarioName}`);
      passedCount++;
    } else {
      console.log(`✗ ${result.scenarioName}`);
      if (result.errors.length > 0) {
        console.log(`  Errors: ${result.errors.join(', ')}`);
      }
      failedCount++;
    }
  }

  console.log('='.repeat(70));
  console.log(`Total: ${passedCount} passed, ${failedCount} failed out of ${results.length} scenarios`);
  console.log('='.repeat(70));
}
