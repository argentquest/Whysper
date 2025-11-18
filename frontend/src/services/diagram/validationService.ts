Here's the TypeScript code with inline comments explaining the logic:

```typescript
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1'; // Define base API endpoint, with fallback to localhost

export interface ValidationError {
  line?: number;
  column?: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions?: string[];
}

export async function validateDiagramCode(
  code: string,
  diagramType: string
): Promise<ValidationResult> {
  try {
    // Send validation request to backend API with code and diagram type
    const response = await axios.post(`${API_BASE}/diagram/validate`, {
      code,
      diagram_type: diagramType,
    });

    // Transform API response into standardized validation result
    return {
      isValid: response.data.is_valid,
      errors: response.data.errors || [],
      warnings: response.data.warnings || [],
      suggestions: response.data.suggestions || [],
    };
  } catch (error) {
    // Log error and fall back to client-side validation if API call fails
    console.error('Validation failed:', error);
    return performBasicValidation(code, diagramType);
  }
}

function performBasicValidation(code: string, diagramType: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Immediately return error if code is empty
  if (!code || code.trim().length === 0) {
    errors.push({
      message: 'Code cannot be empty',
      severity: 'error',
    });
    return { isValid: false, errors, warnings };
  }

  const trimmedCode = code.trim();

  // Route to specific diagram type validation based on input
  switch (diagramType) {
    case 'Mermaid':
      return validateMermaid(trimmedCode);
    case 'D2':
      return validateD2(trimmedCode);
    case 'PlantUML':
      return validatePlantUML(trimmedCode);
    default:
      // Return valid result for unknown diagram types
      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
  }
}

function validateMermaid(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // List of valid Mermaid diagram type keywords
  const mermaidKeywords = [
    'flowchart',
    'sequenceDiagram',
    'gantt',
    'classDiagram',
    'stateDiagram',
    'pie',
    'erDiagram',
    'journey',
    'graph',
  ];

  // Check if any Mermaid keyword is present in the code
  const hasKeyword = mermaidKeywords.some((keyword) => code.includes(keyword));

  // Add error if no diagram type keyword is found
  if (!hasKeyword) {
    errors.push({
      line: 1,
      message: 'Missing Mermaid diagram type declaration (e.g., "flowchart TD", "sequenceDiagram")',
      severity: 'error',
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

function validateD2(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Check for connections and shape definitions
  const hasConnection = /->|<->/.test(code);
  const hasShape = /shape:/.test(code);

  // Add error if no connections or shapes are found
  if (!hasConnection && !hasShape) {
    errors.push({
      line: 1,
      message: 'D2 diagram should contain connections (e.g., "a -> b") or shapes (e.g., "shape: rectangle")',
      severity: 'error',
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

function validatePlantUML(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Check for @startuml marker at the beginning
  if (!code.includes('@startuml')) {
    errors.push({
      line: 1,
      message: 'PlantUML diagram must start with "@startuml"',
      severity: 'error',
    });
  }

  // Check for @enduml marker at the end
  if (!code.includes('@enduml')) {
    errors.push({
      message: 'PlantUML diagram must end with "@enduml"',
      severity: 'error',
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    // Clear previous timeout to prevent multiple calls
    if (timeout) {
      clearTimeout(timeout);
    }
    // Set new timeout to delay function execution
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}