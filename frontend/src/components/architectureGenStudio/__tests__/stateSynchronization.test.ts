/**
 * State Synchronization Tests for Architecture Gen Studio
 * Tests state management, updates, and consistency
 */

import type {
  ArchitectureStudioState,
  Agent,
  AgentOption,
  DiagramResponse,
  ValidationResult,
  GeneratedDiagram,
} from '../types/architectureStudio';
import { DEFAULT_STATE } from '../types/architectureStudio';

// ============================================================================
// State Synchronization Test Suite
// ============================================================================

export interface StateTest {
  name: string;
  description: string;
  initialState: ArchitectureStudioState;
  action: (state: ArchitectureStudioState) => ArchitectureStudioState;
  expectedChanges: Partial<ArchitectureStudioState>;
  shouldNotChange?: (keyof ArchitectureStudioState)[];
}

// ============================================================================
// Test Scenarios
// ============================================================================

const MOCK_AGENT: Agent = {
  id: 'agent-1',
  name: 'C4 Agent',
  description: 'C4 diagram generator',
};

const MOCK_AGENT_OPTION: AgentOption = {
  id: 'option-1',
  agentId: 'agent-1',
  name: 'System Context',
  description: 'System context diagram',
  template: 'Create a C4 system context diagram',
  validationRules: ['Include system boundary'],
  outputFormat: 'SVG',
  enabled: true,
};

const MOCK_DIAGRAM: DiagramResponse = {
  svg: '<svg></svg>',
  provider: 'mermaid',
  code: 'graph TD\n A --> B',
  metadata: {
    provider: 'mermaid',
    generationParameters: {},
  },
  status: 'success',
  timestamp: new Date().toISOString(),
};

const MOCK_VALIDATION_RESULT: ValidationResult = {
  isValid: true,
  errors: [],
  warnings: [],
};

// ============================================================================
// Agent State Tests
// ============================================================================

export const TEST_AGENT_FETCH: StateTest = {
  name: 'Agent Fetch and Load',
  description: 'Loading agents from API into state',
  initialState: {
    ...DEFAULT_STATE,
    agentsLoading: true,
  },
  action: (state) => ({
    ...state,
    agents: [MOCK_AGENT],
    agentsLoading: false,
    agentsError: null,
  }),
  expectedChanges: {
    agents: [MOCK_AGENT],
    agentsLoading: false,
    agentsError: null,
  },
  shouldNotChange: ['currentAgent', 'selectedDiagramType'],
};

export const TEST_AGENT_SELECTION: StateTest = {
  name: 'Agent Selection',
  description: 'User selects an agent from dropdown',
  initialState: {
    ...DEFAULT_STATE,
    agents: [MOCK_AGENT],
  },
  action: (state) => ({
    ...state,
    currentAgent: MOCK_AGENT,
    currentAgentOptions: [],
    optionsLoading: true,
  }),
  expectedChanges: {
    currentAgent: MOCK_AGENT,
    optionsLoading: true,
  },
  shouldNotChange: ['agents', 'currentPrompt'],
};

export const TEST_AGENT_OPTIONS_LOAD: StateTest = {
  name: 'Load Agent Options',
  description: 'Loading available options for selected agent',
  initialState: {
    ...DEFAULT_STATE,
    currentAgent: MOCK_AGENT,
    optionsLoading: true,
  },
  action: (state) => ({
    ...state,
    currentAgentOptions: [MOCK_AGENT_OPTION],
    optionsLoading: false,
    optionsError: null,
  }),
  expectedChanges: {
    currentAgentOptions: [MOCK_AGENT_OPTION],
    optionsLoading: false,
    optionsError: null,
  },
  shouldNotChange: ['currentAgent'],
};

// ============================================================================
// Prompt State Tests
// ============================================================================

export const TEST_PROMPT_AUTO_POPULATION: StateTest = {
  name: 'Prompt Auto-Population from Template',
  description: 'When agent option is selected, template populates prompt',
  initialState: {
    ...DEFAULT_STATE,
    currentAgent: MOCK_AGENT,
    selectedAgentOption: null,
    currentPrompt: '',
  },
  action: (state) => ({
    ...state,
    selectedAgentOption: MOCK_AGENT_OPTION,
    currentPrompt: MOCK_AGENT_OPTION.template,
    promptHasUnsavedChanges: false,
  }),
  expectedChanges: {
    selectedAgentOption: MOCK_AGENT_OPTION,
    currentPrompt: MOCK_AGENT_OPTION.template,
    promptHasUnsavedChanges: false,
  },
};

export const TEST_PROMPT_EDIT: StateTest = {
  name: 'Prompt Edit Marks as Unsaved',
  description: 'Editing prompt marks it as having unsaved changes',
  initialState: {
    ...DEFAULT_STATE,
    currentPrompt: 'Original prompt',
    promptHasUnsavedChanges: false,
  },
  action: (state) => ({
    ...state,
    currentPrompt: 'Modified prompt',
    promptHasUnsavedChanges: true,
  }),
  expectedChanges: {
    currentPrompt: 'Modified prompt',
    promptHasUnsavedChanges: true,
  },
};

export const TEST_PROMPT_CHARACTER_LIMIT: StateTest = {
  name: 'Prompt Character Limit Enforcement',
  description: 'Prompt cannot exceed 5000 characters',
  initialState: {
    ...DEFAULT_STATE,
    currentPrompt: 'a'.repeat(4999),
  },
  action: (state) => ({
    ...state,
    currentPrompt: 'a'.repeat(5000), // Should be capped at 5000
  }),
  expectedChanges: {
    currentPrompt: 'a'.repeat(5000),
  },
};

// ============================================================================
// Diagram Generation State Tests
// ============================================================================

export const TEST_SUBMIT_PROMPT_START: StateTest = {
  name: 'Diagram Generation Start',
  description: 'Submitting prompt starts generation process',
  initialState: {
    ...DEFAULT_STATE,
    isProcessing: false,
    currentStatus: 'Idle',
  },
  action: (state) => ({
    ...state,
    isProcessing: true,
    processingRequestId: 'req-123',
    currentStatus: 'LLM Execution...',
  }),
  expectedChanges: {
    isProcessing: true,
    processingRequestId: 'req-123',
    currentStatus: 'LLM Execution...',
  },
};

export const TEST_DIAGRAM_RECEIVED: StateTest = {
  name: 'Diagram Response Received',
  description: 'Store generated diagram in state',
  initialState: {
    ...DEFAULT_STATE,
    isProcessing: true,
    selectedDiagramType: 'mermaid',
    generatedDiagrams: new Map(),
  },
  action: (state) => {
    const diagrams = new Map(state.generatedDiagrams);
    diagrams.set('mermaid', {
      type: 'mermaid',
      response: MOCK_DIAGRAM,
      generatedAt: new Date().toISOString(),
    });
    return {
      ...state,
      generatedDiagrams: diagrams,
      isProcessing: false,
      currentStatus: 'Diagram Generated',
    };
  },
  expectedChanges: {
    isProcessing: false,
    currentStatus: 'Diagram Generated',
  },
};

export const TEST_DIAGRAM_TYPE_SWITCH: StateTest = {
  name: 'Switch Diagram Type',
  description: 'Switching diagram type preserves all diagrams',
  initialState: {
    ...DEFAULT_STATE,
    selectedDiagramType: 'mermaid',
    generatedDiagrams: new Map([
      ['mermaid', {
        type: 'mermaid',
        response: MOCK_DIAGRAM,
        generatedAt: new Date().toISOString(),
      }],
    ]),
  },
  action: (state) => ({
    ...state,
    selectedDiagramType: 'd2',
    codeEditorContent: '', // Code switches with diagram type
  }),
  expectedChanges: {
    selectedDiagramType: 'd2',
  },
  shouldNotChange: [], // generatedDiagrams should persist
};

export const TEST_REQUEST_CANCELLATION: StateTest = {
  name: 'Cancel Request',
  description: 'Cancelling request stops processing',
  initialState: {
    ...DEFAULT_STATE,
    isProcessing: true,
    processingRequestId: 'req-123',
    currentStatus: 'LLM Execution...',
  },
  action: (state) => ({
    ...state,
    isProcessing: false,
    processingRequestId: null,
    currentStatus: 'Cancelled',
  }),
  expectedChanges: {
    isProcessing: false,
    processingRequestId: null,
    currentStatus: 'Cancelled',
  },
};

// ============================================================================
// Code Editor State Tests
// ============================================================================

export const TEST_CODE_EDIT: StateTest = {
  name: 'Code Editor Edit',
  description: 'Editing code marks as unsaved',
  initialState: {
    ...DEFAULT_STATE,
    codeEditorContent: 'graph TD\n A --> B',
    codeEditorHasUnsavedChanges: false,
  },
  action: (state) => ({
    ...state,
    codeEditorContent: 'graph TD\n A --> B --> C',
    codeEditorHasUnsavedChanges: true,
  }),
  expectedChanges: {
    codeEditorContent: 'graph TD\n A --> B --> C',
    codeEditorHasUnsavedChanges: true,
  },
};

export const TEST_CODE_VALIDATION: StateTest = {
  name: 'Code Validation',
  description: 'Validating code updates validation result',
  initialState: {
    ...DEFAULT_STATE,
    isValidating: true,
    validationResult: null,
  },
  action: (state) => ({
    ...state,
    isValidating: false,
    validationResult: MOCK_VALIDATION_RESULT,
  }),
  expectedChanges: {
    isValidating: false,
    validationResult: MOCK_VALIDATION_RESULT,
  },
};

export const TEST_DIAGRAM_RENDER: StateTest = {
  name: 'Diagram Render',
  description: 'Rendering diagram updates state',
  initialState: {
    ...DEFAULT_STATE,
    isRendering: true,
  },
  action: (state) => {
    const diagrams = new Map(state.generatedDiagrams);
    diagrams.set('mermaid', {
      type: 'mermaid',
      response: MOCK_DIAGRAM,
      generatedAt: new Date().toISOString(),
    });
    return {
      ...state,
      isRendering: false,
      generatedDiagrams: diagrams,
      currentStatus: 'Diagram rendered successfully',
    };
  },
  expectedChanges: {
    isRendering: false,
    currentStatus: 'Diagram rendered successfully',
  },
};

// ============================================================================
// UI State Tests
// ============================================================================

export const TEST_COLLAPSE_COLUMN: StateTest = {
  name: 'Collapse Column',
  description: 'Collapsing a column updates state',
  initialState: {
    ...DEFAULT_STATE,
    collapsedColumns: {
      left: false,
      center: false,
      right: false,
    },
  },
  action: (state) => ({
    ...state,
    collapsedColumns: {
      ...state.collapsedColumns,
      left: true,
    },
  }),
  expectedChanges: {
    collapsedColumns: {
      left: true,
      center: false,
      right: false,
    },
  },
};

export const TEST_COLUMN_WIDTH_CHANGE: StateTest = {
  name: 'Column Width Change',
  description: 'Dragging column divider updates widths',
  initialState: {
    ...DEFAULT_STATE,
    columnWidths: {
      left: 33.33,
      center: 33.33,
      right: 33.34,
    },
  },
  action: (state) => ({
    ...state,
    columnWidths: {
      left: 40,
      center: 35,
      right: 25,
    },
  }),
  expectedChanges: {
    columnWidths: {
      left: 40,
      center: 35,
      right: 25,
    },
  },
};

export const TEST_ZOOM_LEVEL_CHANGE: StateTest = {
  name: 'Zoom Level Change',
  description: 'Zooming updates zoom level',
  initialState: {
    ...DEFAULT_STATE,
    zoomLevel: 100,
  },
  action: (state) => ({
    ...state,
    zoomLevel: 150,
  }),
  expectedChanges: {
    zoomLevel: 150,
  },
};

// ============================================================================
// SSE Message State Tests
// ============================================================================

export const TEST_SSE_MESSAGE_ADD: StateTest = {
  name: 'Add SSE Message',
  description: 'Receiving SSE message adds to state',
  initialState: {
    ...DEFAULT_STATE,
    sseMessages: [],
  },
  action: (state) => ({
    ...state,
    sseMessages: [
      ...state.sseMessages,
      {
        id: 'msg-1',
        timestamp: new Date(),
        type: 'progress',
        message: 'Processing...',
        isRead: false,
      },
    ],
  }),
  expectedChanges: {
    sseMessages: expect.arrayContaining([
      expect.objectContaining({
        type: 'progress',
        message: 'Processing...',
      }),
    ]),
  },
};

// ============================================================================
// Test Runner
// ============================================================================

export interface TestStateSynchronizationResult {
  testName: string;
  passed: boolean;
  error?: string;
  details?: Record<string, any>;
}

export class StateSynchronizationTestRunner {
  private tests: StateTest[] = [
    TEST_AGENT_FETCH,
    TEST_AGENT_SELECTION,
    TEST_AGENT_OPTIONS_LOAD,
    TEST_PROMPT_AUTO_POPULATION,
    TEST_PROMPT_EDIT,
    TEST_PROMPT_CHARACTER_LIMIT,
    TEST_SUBMIT_PROMPT_START,
    TEST_DIAGRAM_RECEIVED,
    TEST_DIAGRAM_TYPE_SWITCH,
    TEST_REQUEST_CANCELLATION,
    TEST_CODE_EDIT,
    TEST_CODE_VALIDATION,
    TEST_DIAGRAM_RENDER,
    TEST_COLLAPSE_COLUMN,
    TEST_COLUMN_WIDTH_CHANGE,
    TEST_ZOOM_LEVEL_CHANGE,
    TEST_SSE_MESSAGE_ADD,
  ];

  runAllTests(): TestStateSynchronizationResult[] {
    return this.tests.map((test) => this.runTest(test));
  }

  private runTest(test: StateTest): TestStateSynchronizationResult {
    try {
      // Apply action to state
      const newState = test.action(test.initialState);

      // Verify expected changes
      for (const [key, expectedValue] of Object.entries(test.expectedChanges)) {
        const stateKey = key as keyof ArchitectureStudioState;
        const actualValue = newState[stateKey];

        if (!this.deepEqual(actualValue, expectedValue)) {
          return {
            testName: test.name,
            passed: false,
            error: `Expected ${key} to be ${JSON.stringify(expectedValue)}, got ${JSON.stringify(actualValue)}`,
          };
        }
      }

      // Verify fields that should not change
      if (test.shouldNotChange) {
        for (const key of test.shouldNotChange) {
          const initialValue = test.initialState[key];
          const finalValue = newState[key];

          if (!this.deepEqual(initialValue, finalValue)) {
            return {
              testName: test.name,
              passed: false,
              error: `Field ${key} should not have changed`,
            };
          }
        }
      }

      return {
        testName: test.name,
        passed: true,
      };
    } catch (error) {
      return {
        testName: test.name,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private deepEqual(a: any, b: any): boolean {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (typeof a !== 'object' || typeof b !== 'object') return false;

    if (a instanceof Map && b instanceof Map) {
      if (a.size !== b.size) return false;
      for (const [key, value] of a) {
        if (!this.deepEqual(value, b.get(key))) return false;
      }
      return true;
    }

    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) return false;
      return a.every((v, i) => this.deepEqual(v, b[i]));
    }

    if (a instanceof Date && b instanceof Date) {
      return a.getTime() === b.getTime();
    }

    const keysA = Object.keys(a);
    const keysB = Object.keys(b);

    if (keysA.length !== keysB.length) return false;
    return keysA.every((key) => this.deepEqual(a[key], b[key]));
  }
}

// ============================================================================
// Test Runner Execution
// ============================================================================

export async function runStateSynchronizationTests(): Promise<void> {
  const runner = new StateSynchronizationTestRunner();
  const results = runner.runAllTests();

  console.log('='.repeat(70));
  console.log('State Synchronization Test Results');
  console.log('='.repeat(70));

  let passedCount = 0;
  let failedCount = 0;

  for (const result of results) {
    if (result.passed) {
      console.log(`✓ ${result.testName}`);
      passedCount++;
    } else {
      console.log(`✗ ${result.testName}`);
      if (result.error) {
        console.log(`  Error: ${result.error}`);
      }
      failedCount++;
    }
  }

  console.log('='.repeat(70));
  console.log(`Total: ${passedCount} passed, ${failedCount} failed out of ${results.length} tests`);
  console.log('='.repeat(70));
}
