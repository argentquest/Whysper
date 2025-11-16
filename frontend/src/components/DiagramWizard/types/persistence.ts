/**
 * DiagramWizard Persistence Types
 * Defines the structure for persisted state in localStorage
 */

export interface DiagramWizardPreferences {
  defaultDiagramType: 'Mermaid' | 'D2' | 'PlantUML' | 'auto';
  autoSave: boolean;
  keepSessionHistory: boolean;
  maxHistoryItems: number;
  theme: 'light' | 'dark' | 'auto';
  showScoreInfo: boolean;
}

export interface SavedSession {
  sessionId: string;
  timestamp: number;
  initialPrompt: string;
  diagramType: string;
  diagramCode: string;
  svgOutput: string;
  conversationHistory: Array<[string, string]>;
  score: number;
  scoreInfo?: {
    entities: boolean;
    actions: boolean;
    structure: boolean;
    info_score: number;
    word_count: number;
    has_minimum_info: boolean;
    has_good_info: boolean;
  };
}

export interface DiagramWizardPersistedState {
  preferences: DiagramWizardPreferences;
  sessionHistory: SavedSession[];
  lastSession?: SavedSession;
  stats: {
    totalSessions: number;
    successfulGenerations: number;
    lastUsed: number;
  };
}

export const DEFAULT_PREFERENCES: DiagramWizardPreferences = {
  defaultDiagramType: 'auto',
  autoSave: true,
  keepSessionHistory: true,
  maxHistoryItems: 10,
  theme: 'auto',
  showScoreInfo: true,
};

export const getInitialPersistedState = (): DiagramWizardPersistedState => ({
  preferences: DEFAULT_PREFERENCES,
  sessionHistory: [],
  stats: {
    totalSessions: 0,
    successfulGenerations: 0,
    lastUsed: Date.now(),
  },
});
