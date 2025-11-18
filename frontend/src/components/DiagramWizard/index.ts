/**
 * DiagramWizard Module Exports
 *
 * Provides easy access to all diagram wizard components and hooks
 */

export { DiagramWizard as default, DiagramWizard } from './DiagramWizard'; // Main diagram wizard component with default and named export

// Hooks for managing diagram session state and interactions
export { useDiagramSession } from './hooks/useDiagramSession';

// API and type definitions for diagram-related services
export { default as DiagramApi } from '../../services/diagram/diagramApi'; // Centralized API for diagram operations
export type { DiagramStatus, DiagramUpdate, DiagramSession } from '../../services/diagram/diagramApi'; // Type definitions for diagram interactions

// Panel components for different stages of diagram creation
export { default as ChatPanel } from './panels/Panel1_Chat'; // Chat interface for generating diagrams
export { default as PreviewPanel } from './panels/Panel2_Preview'; // Visual preview of diagram
export { default as CodeEditorPanel } from './panels/Panel3_CodeEditor'; // Code editing interface for diagram