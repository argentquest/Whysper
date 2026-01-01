/**
 * Screens Index
 *
 * Exports all screen components for the DiagramWizard
 */

// Export SystemDescriptionScreen to enable dynamic importing of system description stage
// Allows flexible wizard navigation and component rendering
export { SystemDescriptionScreen } from './SystemDescriptionScreen'

// Export GenerationScreen to complete the wizard's component export set
// Provides final screen for displaying generation results and outputs
export { GenerationScreen } from './GenerationScreen'
