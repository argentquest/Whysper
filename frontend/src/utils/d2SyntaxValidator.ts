/**
 * Simple D2 Syntax Detector
 * Basic detection for D2 diagram content - validation handled by backend
 */

/**
 * Quick check if content looks like D2 diagram code
 */
export function isD2Syntax(content: string): boolean {
  if (!content || typeof content !== 'string') {
    return false;
  }

  const trimmed = content.trim();
  if (!trimmed) {
    return false;
  }

  // Look for basic D2 patterns
  const d2Patterns = [
    /\w+\s*->\s*\w+/, // Connections
    /direction:\s*\w+/, // Direction
    /\w+:\s*"[^"]+"\s*\{/, // Object definitions
    /style\.\w+:/ // Style properties
  ];

  return d2Patterns.some(pattern => pattern.test(trimmed));
}

/**
 * Prepare D2 code for backend processing
 */
export function prepareD2Code(content: string): string {
  return content.trim();
}

/**
 * Quick validation check - backend handles actual validation
 */
export function quickD2Check(content: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (!content || content.trim().length === 0) {
    errors.push('D2 code is empty');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}