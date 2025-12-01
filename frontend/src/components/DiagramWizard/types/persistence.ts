// Type definitions for DiagramWizard's persistence and state management
// Provides structured interfaces for storing application preferences and session data

// Defines user preferences for diagram generation and app behavior
export interface DiagramWizardPreferences {
  defaultDiagramType: 'Mermaid' | 'D2' | 'PlantUML' | 'auto' // Specifies default diagram rendering engine
  autoSave: boolean // Automatically save session state
  keepSessionHistory: boolean // Retain history of previous sessions
  maxHistoryItems: number // Limit number of stored historical sessions
  theme: 'light' | 'dark' | 'auto' // UI theme selection
  showScoreInfo: boolean // Toggle display of diagram generation quality metrics
}

// Represents a single saved diagram generation session
export interface SavedSession {
  sessionId: string // Unique identifier for the session
  timestamp: number // Unix timestamp of session creation
  initialPrompt: string // Original user input that generated the diagram
  diagramType: string // Type of diagram generated
  diagramCode: string // Source code/markup for the diagram
  svgOutput: string // Rendered diagram as SVG
  conversationHistory: Array<[string, string]> // Interaction log between user and system
  score: number // Overall quality/relevance score
  scoreInfo?: {
    // Optional detailed scoring breakdown
    entities: boolean
    actions: boolean
    structure: boolean
    info_score: number
    word_count: number
    has_minimum_info: boolean
    has_good_info: boolean
  }
}

// Complete persisted state structure for the entire application
export interface DiagramWizardPersistedState {
  preferences: DiagramWizardPreferences // User's app-wide preferences
  sessionHistory: SavedSession[] // Array of past diagram generation sessions
  lastSession?: SavedSession // Most recently created session
  stats: {
    // Usage and generation statistics
    totalSessions: number
    successfulGenerations: number
    lastUsed: number
  }
}

// Default configuration for initial app state
export const DEFAULT_PREFERENCES: DiagramWizardPreferences = {
  defaultDiagramType: 'auto', // Default to automatic diagram type selection
  autoSave: true, // Enable automatic saving by default
  keepSessionHistory: true, // Preserve session history
  maxHistoryItems: 10, // Keep up to 10 historical sessions
  theme: 'auto', // Match system theme by default
  showScoreInfo: true, // Show detailed generation scoring
}

// Factory function to create initial persisted state
export const getInitialPersistedState = (): DiagramWizardPersistedState => ({
  preferences: DEFAULT_PREFERENCES, // Start with default preferences
  sessionHistory: [], // Empty session history
  stats: {
    totalSessions: 0, // Initialize session counters to zero
    successfulGenerations: 0,
    lastUsed: Date.now(), // Record current timestamp as last used
  },
})
