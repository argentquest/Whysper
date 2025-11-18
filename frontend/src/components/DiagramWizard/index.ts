```typescript
// Export the main diagram wizard component, providing both default and named export for flexible usage
export { DiagramWizard as default, DiagramWizard } from './DiagramWizard';

// Expose diagram session management hook to enable state tracking and interaction control for diagram workflow
export { useDiagramSession } from './hooks/useDiagramSession';

// Import centralized diagram API to standardize service interactions and provide type-safe data management
export { default as DiagramApi } from '../../services/diagram/diagramApi';

// Define type exports to ensure type consistency and safety across diagram-related operations and components
export type { DiagramStatus, DiagramUpdate, DiagramSession } from '../../services/diagram/diagramApi';

// Export panel components representing different sequential stages of the diagram creation workflow
export { default as ChatPanel } from './panels/Panel1_Chat';      // Chat interface for initial diagram generation
export { default as PreviewPanel } from './panels/Panel2_Preview'; // Visual preview and refinement stage
export { default as CodeEditorPanel } from './panels/Panel3_CodeEditor'; // Final code editing and customization interface