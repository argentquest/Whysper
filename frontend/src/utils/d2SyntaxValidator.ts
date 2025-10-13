/**
 * D2 Syntax Validator and Auto-Corrector
 * 
 * This utility validates and corrects common D2 syntax issues that cause
 * compilation failures. It fixes the most frequent syntax errors generated
 * by AI models or manual input.
 */

export interface D2ValidationResult {
  isValid: boolean;
  correctedCode: string;
  errors: string[];
  corrections: string[];
}

/**
 * Validates and corrects D2 syntax issues
 */
export function validateAndCorrectD2Syntax(code: string): D2ValidationResult {
  const errors: string[] = [];
  const corrections: string[] = [];
  let correctedCode = code;

  console.log('🔧 [D2 VALIDATOR] Original code:', code);

  // Fix 1: Convert JSON-style object syntax to proper D2 syntax
  // Pattern: name: { shape: circle, label: "text" } -> name: "text" { shape: circle }
  const objectPattern = /(\w+):\s*\{\s*shape:\s*(\w+)[^}]*label:\s*"([^"]+)"[^}]*\}/g;
  correctedCode = correctedCode.replace(objectPattern, (match, name, shape, label) => {
    corrections.push(`Fixed object syntax for ${name}: converted JSON-style to D2 syntax`);
    return `${name}: "${label}" {\n  shape: ${shape}`;
  });

  // Fix 2: Convert nested style objects to dot notation
  // Pattern: style: { fill: "#color" } -> style.fill: "#color"
  const stylePattern = /style:\s*\{([^}]+)\}/g;
  correctedCode = correctedCode.replace(stylePattern, (match, styleContent) => {
    const styleLines = styleContent.split(',').map(line => line.trim());
    const fixedStyles = styleLines.map(line => {
      const [property, value] = line.split(':').map(s => s.trim());
      if (property && value) {
        return `  style.${property}: ${value}`;
      }
      return '';
    }).filter(Boolean).join('\n');
    
    corrections.push('Fixed nested style object to dot notation');
    return fixedStyles;
  });

  // Fix 3: Ensure proper brace matching
  const openBraces = (correctedCode.match(/{/g) || []).length;
  const closeBraces = (correctedCode.match(/}/g) || []).length;
  
  if (openBraces > closeBraces) {
    const missingBraces = openBraces - closeBraces;
    correctedCode += '\n}'.repeat(missingBraces);
    corrections.push(`Added ${missingBraces} missing closing brace(s)`);
  } else if (closeBraces > openBraces) {
    errors.push(`Too many closing braces: ${closeBraces - openBraces} extra brace(s)`);
  }

  // Fix 4: Convert invalid arrow syntax
  // Pattern: A - > B -> A -> B
  const arrowPattern = /\s*-\s*>\s*/g;
  correctedCode = correctedCode.replace(arrowPattern, ' -> ');
  if (arrowPattern.test(code)) {
    corrections.push('Fixed arrow syntax (removed spaces around arrow)');
  }

  // Fix 5: Ensure proper label syntax for connections
  // Pattern: A -> B: "label" -> A -> B: "label" (already correct, but validate quotes)
  const connectionPattern = /(\w+)\s*->\s*(\w+):\s*"?([^"]+)"?/g;
  correctedCode = correctedCode.replace(connectionPattern, (match, from, to, label) => {
    if (!label.includes('"')) {
      corrections.push(`Added quotes to connection label: ${label}`);
      return `${from} -> ${to}: "${label}"`;
    }
    return match;
  });

  // Fix 6: Remove invalid property syntax
  // Pattern: property: value without proper context
  const invalidPropertyPattern = /^\s*(\w+):\s*([^{}\n]+)\s*$/gm;
  correctedCode = correctedCode.replace(invalidPropertyPattern, (match, prop, value) => {
    // Skip if this looks like a valid connection or object definition
    if (value.includes('->') || value.includes('"') || prop === 'direction') {
      return match;
    }
    
    corrections.push(`Removed invalid property: ${prop}: ${value}`);
    return `# Invalid property removed: ${prop}: ${value}`;
  });

  // Fix 7: Ensure proper direction syntax
  if (!correctedCode.includes('direction:') && correctedCode.includes('->')) {
    correctedCode = 'direction: right\n\n' + correctedCode;
    corrections.push('Added default direction: right');
  }

  // Final validation
  const validationErrors = validateD2Structure(correctedCode);
  errors.push(...validationErrors);

  const isValid = errors.length === 0;

  console.log('🔧 [D2 VALIDATOR] Corrections made:', corrections);
  console.log('🔧 [D2 VALIDATOR] Errors found:', errors);
  console.log('🔧 [D2 VALIDATOR] Corrected code:', correctedCode);

  return {
    isValid,
    correctedCode,
    errors,
    corrections
  };
}

/**
 * Basic structural validation for D2 code
 */
function validateD2Structure(code: string): string[] {
  const errors: string[] = [];
  const lines = code.split('\n');

  // Check for unmatched braces again (final verification)
  let braceStack = 0;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const openCount = (line.match(/{/g) || []).length;
    const closeCount = (line.match(/}/g) || []).length;
    
    braceStack += openCount - closeCount;
    
    if (braceStack < 0) {
      errors.push(`Line ${i + 1}: Too many closing braces`);
      braceStack = 0;
    }
  }
  
  if (braceStack > 0) {
    errors.push(`Unmatched opening braces: ${braceStack} braces not closed`);
  }

  // Check for invalid object definitions
  const objectDefPattern = /^(\w+):\s*"([^"]*)"\s*\{/;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes(':') && !objectDefPattern.test(line) && 
        !line.includes('->') && !line.startsWith('#') && 
        !line.startsWith('direction:') && !line.includes('.')) {
      // This might be an invalid object definition
      if (!line.includes('{') && !line.includes('style.')) {
        errors.push(`Line ${i + 1}: Invalid object definition: ${line}`);
      }
    }
  }

  return errors;
}

/**
 * Quick validation to check if D2 code looks reasonable
 */
export function looksLikeValidD2(code: string): boolean {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const trimmed = code.trim();
  if (!trimmed) {
    return false;
  }

  // Look for D2-specific patterns
  const d2Patterns = [
    /\w+\s*->\s*\w+/, // Connections
    /direction:\s*\w+/, // Direction
    /\w+:\s*"[^"]+"\s*\{/, // Object definitions
    /style\.\w+:/ // Style properties
  ];

  return d2Patterns.some(pattern => pattern.test(trimmed));
}