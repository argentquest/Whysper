/**
 * Validation Service
 *
 * Provides client-side validation for diagram code using the backend provider system.
 * Supports real-time validation as the user types in the code editor.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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

/**
 * Validate diagram code using the backend provider system
 */
export async function validateDiagramCode(
  code: string,
  diagramType: string
): Promise<ValidationResult> {
  try {
    const response = await axios.post(`${API_BASE}/diagram/validate`, {
      code,
      diagram_type: diagramType,
    });

    return {
      isValid: response.data.is_valid,
      errors: response.data.errors || [],
      warnings: response.data.warnings || [],
      suggestions: response.data.suggestions || [],
    };
  } catch (error) {
    console.error('Validation failed:', error);

    // Return basic client-side validation on error
    return performBasicValidation(code, diagramType);
  }
}

/**
 * Basic client-side validation as fallback
 */
function performBasicValidation(code: string, diagramType: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  if (!code || code.trim().length === 0) {
    errors.push({
      message: 'Code cannot be empty',
      severity: 'error',
    });
    return { isValid: false, errors, warnings };
  }

  const trimmedCode = code.trim();

  switch (diagramType) {
    case 'Mermaid':
      return validateMermaid(trimmedCode);
    case 'D2':
      return validateD2(trimmedCode);
    case 'PlantUML':
      return validatePlantUML(trimmedCode);
    default:
      return {
        isValid: true,
        errors: [],
        warnings: [],
      };
  }
}

/**
 * Basic Mermaid validation
 */
function validateMermaid(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

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

  const hasKeyword = mermaidKeywords.some((keyword) => code.includes(keyword));

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

/**
 * Basic D2 validation
 */
function validateD2(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  const hasConnection = /->|<->/.test(code);
  const hasShape = /shape:/.test(code);

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

/**
 * Basic PlantUML validation
 */
function validatePlantUML(code: string): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  if (!code.includes('@startuml')) {
    errors.push({
      line: 1,
      message: 'PlantUML diagram must start with "@startuml"',
      severity: 'error',
    });
  }

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

/**
 * Debounce helper for validation
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}
