/**
 * Architecture Gen Studio - Type Definitions
 * All TypeScript interfaces and types for the application
 */

// ============================================================================
// Agent & SubAgent Types
// ============================================================================

export interface Agent {
  id: string;
  name: string;
  description?: string;
  type?: string; // Agent type/category (e.g., 'Architecture', 'Code Generation', etc.)
}

export interface AgentOption {
  id: string;
  agentId: string;
  name: string;
  description: string;
  template: string; // Auto-populated into prompt editor
  validationRules: string[];
  outputFormat: string;
  enabled: boolean;
}

// ============================================================================
// Diagram Types
// ============================================================================

export type DiagramType = 'mermaid' | 'd2' | 'structurizr' | 'plantuml';

export interface DiagramResponse {
  svg: string; // SVG markup for rendering
  provider: string; // mermaid, d2, kroki-*, etc.
  code: string; // Diagram source code
  metadata: {
    provider: string;
    generationParameters: object;
  };
  status: string; // success, error, etc.
  timestamp: string; // ISO 8601 format
}

export interface GeneratedDiagram {
  type: DiagramType;
  response: DiagramResponse;
  generatedAt: string;
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  id: string;
  message: string;
  code?: string;
  details?: string;
  timestamp: string;
}

export interface ValidationWarning {
  id: string;
  message: string;
}

// ============================================================================
// SSE Message Types
// ============================================================================

export type SSEMessageType = 'info' | 'error' | 'progress' | 'retry' | 'success' | 'diagram';

export interface SSEMessage {
  id: string;
  timestamp: Date;
  type: SSEMessageType;
  message: string;
  isRead?: boolean;
  details?: {
    svg?: string;
    provider?: string;
    metadata?: object;
  };
}

// ============================================================================
// State Management Types
// ============================================================================

export interface ArchitectureStudioState {
  // Agent & Options
  currentAgent: Agent | null;
  agents: Agent[];
  agentsLoading: boolean;
  agentsError: string | null;

  // Agent Options
  currentAgentOptions: AgentOption[];
  selectedAgentOption: AgentOption | null;
  optionsLoading: boolean;
  optionsError: string | null;

  // Prompt Editor
  currentPrompt: string;
  promptHasUnsavedChanges: boolean;

  // Diagram Generation
  selectedDiagramType: DiagramType;
  generatedDiagrams: Map<DiagramType, GeneratedDiagram>;
  isProcessing: boolean;
  processingError: string | null;
  processingRequestId: string | null;

  // Code Editor
  codeEditorContent: string;
  codeEditorHasUnsavedChanges: boolean;
  validationResult: ValidationResult | null;
  isValidating: boolean;
  isRendering: boolean;

  // UI State
  columnWidths: {
    left: number; // percentage
    center: number; // percentage
    right: number; // percentage
  };
  collapsedColumns: {
    left: boolean;
    center: boolean;
    right: boolean;
  };
  sseMessages: SSEMessage[];
  currentStatus: string;
  statusHistory: StatusMessage[];

  // Zoom
  zoomLevel: number;
}

export interface StatusMessage {
  message: string;
  timestamp: string;
  type: 'idle' | 'processing' | 'success' | 'error';
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface GenerateDiagramRequest {
  agentId: string;
  prompt: string;
  diagramType?: DiagramType;
}

export interface ValidateCodeRequest {
  code: string;
  diagramType: DiagramType;
}

export interface RenderDiagramRequest {
  code: string;
  diagramType: DiagramType;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface HeaderProps {
  onAgentChange: (agent: Agent) => void;
  currentAgent: Agent | null;
  agents: Agent[];
  agentsLoading: boolean;
  notificationCount: number;
  onLogout: () => void;
}

export interface LeftColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
  currentAgent: Agent | null;
  agentOptions: AgentOption[];
  selectedOption: AgentOption | null;
  onOptionSelect: (option: AgentOption) => void;
  currentPrompt: string;
  onPromptChange: (prompt: string) => void;
  onSubmit: (prompt: string) => Promise<void>;
  onCancel: () => Promise<void>;
  isProcessing: boolean;
  hasUnsavedPrompt: boolean;
  optionsLoading: boolean;
  optionsError: string | null;
}

export interface CenterColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
  selectedDiagramType: DiagramType;
  onDiagramTypeChange: (type: DiagramType) => void;
  generatedDiagrams: Map<DiagramType, GeneratedDiagram>;
  isLoading: boolean;
  error: string | null;
  zoomLevel: number;
  onZoomChange: (level: number) => void;
  onExport: (format: 'svg' | 'pdf' | 'code') => void;
  onMinimize: () => void;
}

export interface RightColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
  code: string;
  onCodeChange: (code: string) => void;
  diagramType: DiagramType;
  onValidate: (code: string) => Promise<void>;
  onRender: (code: string) => Promise<void>;
  validationResult: ValidationResult | null;
  isValidating: boolean;
  isRendering: boolean;
  hasUnsavedChanges: boolean;
  errors: ValidationError[];
  onErrorDismiss: () => void;
}

export interface FooterProps {
  currentStatus: string;
  sseMessages: SSEMessage[];
  unreadMessageCount: number;
  isSSEConnected?: boolean;
}

// ============================================================================
// LocalStorage Keys
// ============================================================================

export const STORAGE_KEYS = {
  CURRENT_AGENT: 'studio_currentAgent',
  LAST_PROMPT: 'studio_lastPrompt',
  SELECTED_AGENT_OPTION: 'studio_selectedAgentOption',
  COLUMN_WIDTHS: 'studio_columnWidths',
  COLLAPSED_COLUMNS: 'studio_collapsedColumns',
  ZOOM_LEVEL: 'studio_zoomLevel',
} as const;

// ============================================================================
// Constants
// ============================================================================

export const DIAGRAM_TYPES: DiagramType[] = ['mermaid', 'd2', 'structurizr', 'plantuml'];

export const DEFAULT_ZOOM = 100; // percentage
export const MIN_ZOOM = 20; // percentage
export const MAX_ZOOM = 300; // percentage
export const ZOOM_STEP = 20; // percentage

export const PROMPT_MAX_CHARACTERS = 5000;
export const COLUMN_MIN_WIDTH = 33.33; // percentage (1/3 of screen)

export const DEFAULT_STATE: ArchitectureStudioState = {
  currentAgent: null,
  agents: [],
  agentsLoading: false,
  agentsError: null,

  currentAgentOptions: [],
  selectedAgentOption: null,
  optionsLoading: false,
  optionsError: null,

  currentPrompt: '',
  promptHasUnsavedChanges: false,

  selectedDiagramType: 'mermaid',
  generatedDiagrams: new Map(),
  isProcessing: false,
  processingError: null,
  processingRequestId: null,

  codeEditorContent: '',
  codeEditorHasUnsavedChanges: false,
  validationResult: null,
  isValidating: false,
  isRendering: false,

  columnWidths: {
    left: 33.33,
    center: 33.33,
    right: 33.34,
  },
  collapsedColumns: {
    left: false,
    center: false,
    right: false,
  },
  sseMessages: [],
  currentStatus: 'Idle',
  statusHistory: [],

  zoomLevel: DEFAULT_ZOOM,
};
