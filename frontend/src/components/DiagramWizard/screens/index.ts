/**
 * Screens Index
 *
 * Exports all three screen components for the DiagramWizard
 */

// Exports the ModelSelectionScreen component and ModelId type
// Allows other parts of the application to import and use these specific screen and type
export { ModelSelectionScreen, type ModelId } from './ModelSelectionScreen';

// Exports the SystemDescriptionScreen component
// Enables importing this screen component in other modules
export { SystemDescriptionScreen } from './SystemDescriptionScreen';

// Exports the GenerationScreen component
// Provides access to this screen for other parts of the application
export { GenerationScreen } from './GenerationScreen';