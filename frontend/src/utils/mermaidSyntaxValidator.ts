/**
 * Mermaid Syntax Validator and Auto-Corrector
 * 
 * This utility validates and corrects common Mermaid syntax issues that cause
 * compilation failures. It fixes the most frequent syntax errors generated
 * by AI models or manual input.
 */

export interface MermaidValidationResult {
  isValid: boolean;
  correctedCode: string;
  errors: string[];
  corrections: string[];
  warnings: string[];
}

/**
 * Validates and corrects Mermaid syntax issues
 */
export function validateAndCorrectMermaidSyntax(code: string): MermaidValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const corrections: string[] = [];
  let correctedCode = code;

  console.log('🔧 [MERMAID VALIDATOR] Original code:', code);

  // Fix 1: Ensure diagram type declaration
  if (!hasDiagramTypeDeclaration(correctedCode)) {
    correctedCode = addDiagramTypeDeclaration(correctedCode);
    corrections.push('Added missing diagram type declaration (flowchart TD)');
  }

  // Fix 2: Common arrow syntax issues
  correctedCode = fixArrowSyntax(correctedCode, corrections);

  // Fix 3: Node ID and label issues
  correctedCode = fixNodeSyntax(correctedCode, corrections);

  // Fix 4: Subgraph syntax issues
  correctedCode = fixSubgraphSyntax(correctedCode, corrections);

  // Fix 5: Class diagram syntax issues
  correctedCode = fixClassDiagramSyntax(correctedCode, corrections);

  // Fix 6: Sequence diagram syntax issues
  correctedCode = fixSequenceDiagramSyntax(correctedCode, corrections);

  // Fix 7: Clean up extra whitespace and formatting
  correctedCode = cleanupFormatting(correctedCode, corrections);

  // Final validation
  const validationErrors = validateMermaidStructure(correctedCode);
  errors.push(...validationErrors);

  // Check for potential issues that might cause rendering problems
  const potentialIssues = checkPotentialIssues(correctedCode);
  warnings.push(...potentialIssues);

  const isValid = errors.length === 0;

  console.log('🔧 [MERMAID VALIDATOR] Corrections made:', corrections);
  console.log('🔧 [MERMAID VALIDATOR] Warnings:', warnings);
  console.log('🔧 [MERMAID VALIDATOR] Errors found:', errors);
  console.log('🔧 [MERMAID VALIDATOR] Corrected code:', correctedCode);

  return {
    isValid,
    correctedCode,
    errors,
    corrections,
    warnings
  };
}

/**
 * Check if code has a diagram type declaration
 */
function hasDiagramTypeDeclaration(code: string): boolean {
  const diagramTypes = [
    'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
    'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt',
    'pie', 'journey', 'gitGraph', 'mindmap', 'timeline',
    'quadrantChart', 'requirementDiagram', 'sankey-beta'
  ];
  
  const firstLine = code.trim().split('\n')[0].toLowerCase();
  return diagramTypes.some(type => firstLine.startsWith(type.toLowerCase()));
}

/**
 * Add appropriate diagram type declaration
 */
function addDiagramTypeDeclaration(code: string): string {
  const trimmedCode = code.trim();
  
  // Try to infer the best diagram type from the content
  if (trimmedCode.includes('participant') || trimmedCode.includes('->>')) {
    return `sequenceDiagram\n${trimmedCode}`;
  } else if (trimmedCode.includes('class ') || trimmedCode.includes(' inheritance')) {
    return `classDiagram\n${trimmedCode}`;
  } else if (trimmedCode.includes('state ') || trimmedCode.includes('[*]')) {
    return `stateDiagram-v2\n${trimmedCode}`;
  } else if (trimmedCode.includes('gantt') || trimmedCode.includes('title ') || trimmedCode.includes('section ')) {
    return `gantt\n${trimmedCode}`;
  } else {
    // Default to flowchart
    return `flowchart TD\n${trimmedCode}`;
  }
}

/**
 * Fix common arrow syntax issues
 */
function fixArrowSyntax(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Fix mixed arrow syntax (some people use -->, some use -->)
  fixedCode = fixedCode.replace(/-->\s*/g, '--> ');
  fixedCode = fixedCode.replace(/\s*-->/g, ' -->');
  
  // Fix sequence diagram arrows
  fixedCode = fixedCode.replace(/->>\s*/g, '-->> ');
  fixedCode = fixedCode.replace(/\s*->>/g, ' -->>');
  
  // Fix bidirectional arrows
  fixedCode = fixedCode.replace(/<-->\s*/g, '<--> ');
  fixedCode = fixedCode.replace(/\s*<-->/g, ' <-->');
  
  // Fix x marks (for sequence diagrams)
  fixedCode = fixedCode.replace(/-x\s*/g, '-x ');
  fixedCode = fixedCode.replace(/\s*-x/g, ' -x');
  
  // Fix x marks with double lines
  fixedCode = fixedCode.replace(/--x\s*/g, '--x ');
  fixedCode = fixedCode.replace(/\s*--x/g, ' --x');
  
  if (fixedCode !== code) {
    corrections.push('Fixed arrow syntax formatting');
  }
  
  return fixedCode;
}

/**
 * Fix node ID and label issues
 */
function fixNodeSyntax(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Fix nodes with special characters that need quotes
  fixedCode = fixedCode.replace(/(\w+)\s*\[\s*([^\]]+?)\s*\]/g, (match, id, label) => {
    // If label contains special characters, ensure it's properly quoted
    if (label.includes(' ') || label.includes('-') || label.includes('(') || label.includes(')')) {
      if (!label.startsWith('"') && !label.endsWith('"')) {
        corrections.push(`Added quotes to node label: ${label}`);
        return `${id}["${label}"]`;
      }
    }
    return match;
  });
  
  // Fix node definitions with colons (common mistake)
  fixedCode = fixedCode.replace(/(\w+):\s*(\[|\()/g, '$1$2');
  
  // Fix parentheses for round nodes (should be [])
  fixedCode = fixedCode.replace(/(\w+)\s*\(\s*([^)]+?)\s*\)/g, (match, id, label) => {
    corrections.push(`Changed parentheses to brackets for node: ${id}`);
    return `${id}[${label}]`;
  });
  
  return fixedCode;
}

/**
 * Fix subgraph syntax issues
 */
function fixSubgraphSyntax(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Fix subgraph declarations without proper end
  const subgraphMatches = fixedCode.match(/subgraph\s+[^{]+{/gi);
  const endMatches = fixedCode.match(/end/gi);
  
  if (subgraphMatches && subgraphMatches.length > (endMatches ? endMatches.length : 0)) {
    const missingEnds = subgraphMatches.length - (endMatches ? endMatches.length : 0);
    fixedCode += '\n' + 'end'.repeat(missingEnds);
    corrections.push(`Added ${missingEnds} missing 'end' statement(s) for subgraph(s)`);
  }
  
  // Fix subgraph title formatting
  fixedCode = fixedCode.replace(/subgraph\s+["']([^"']+)["']/gi, (match, title) => {
    return `subgraph "${title}"`;
  });
  
  return fixedCode;
}

/**
 * Fix class diagram syntax issues
 */
function fixClassDiagramSyntax(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Fix class inheritance syntax (should use --> or <--)
  fixedCode = fixedCode.replace(/(\w+)\s*<\|\s*\-\s*(\w+)/g, '$1 <|-- $2');
  fixedCode = fixedCode.replace(/(\w+)\s*\|\s*>\s*\-\s*(\w+)/g, '$1 --|> $2');
  
  // Fix class relationship syntax
  fixedCode = fixedCode.replace(/(\w+)\s*-\s*([^>\-]+)\s*-\s*(\w+)/g, '$1 --> $2 : $3');
  
  // Fix class member syntax (should be +, -, #)
  fixedCode = fixedCode.replace(/(\w+)\s*:\s*(\w+)/g, (match, member, type) => {
    // This is a simplified fix - in real cases we'd need to detect visibility
    return `+${member}: ${type}`;
  });
  
  return fixedCode;
}

/**
 * Fix sequence diagram syntax issues
 */
function fixSequenceDiagramSyntax(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Fix participant declarations
  fixedCode = fixedCode.replace(/participant\s+(\w+)\s+as\s+(\w+)/gi, (match, actor, alias) => {
    return `participant ${actor} as ${alias}`;
  });
  
  // Fix message syntax without proper labels
  fixedCode = fixedCode.replace(/(\w+)\s*->>\s*(\w+)\s*$/gm, '$1 ->> $2');
  
  // Fix message syntax with labels that aren't properly quoted
  fixedCode = fixedCode.replace(/(\w+)\s*->>\s*(\w+)\s*:\s*([^"\n]+)$/gm, (match, from, to, label) => {
    if (label.includes(' ')) {
      corrections.push(`Added quotes to message label: ${label}`);
      return `${from} ->> ${to}: "${label}"`;
    }
    return match;
  });
  
  return fixedCode;
}

/**
 * Clean up extra whitespace and formatting
 */
function cleanupFormatting(code: string, corrections: string[]): string {
  let fixedCode = code;
  
  // Remove extra blank lines
  fixedCode = fixedCode.replace(/\n\s*\n\s*\n/g, '\n\n');
  
  // Fix indentation (basic cleanup)
  fixedCode = fixedCode.split('\n').map(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('subgraph') && !trimmed.startsWith('end')) {
      return trimmed;
    }
    return trimmed;
  }).join('\n');
  
  // Ensure proper spacing around arrows
  fixedCode = fixedCode.replace(/(\w+)(-->|<-->|->>|--x|-\x)(\w+)/g, '$1 $2 $3');
  
  if (fixedCode !== code) {
    corrections.push('Cleaned up formatting and whitespace');
  }
  
  return fixedCode;
}

/**
 * Basic structural validation for Mermaid code
 */
function validateMermaidStructure(code: string): string[] {
  const errors: string[] = [];
  const lines = code.split('\n');
  
  // Check for unmatched subgraphs
  let subgraphCount = 0;
  for (const line of lines) {
    const trimmed = line.trim().toLowerCase();
    if (trimmed.startsWith('subgraph')) {
      subgraphCount++;
    } else if (trimmed === 'end') {
      subgraphCount--;
    }
  }
  
  if (subgraphCount > 0) {
    errors.push(`Unmatched subgraph declarations: ${subgraphCount} subgraph(s) not closed`);
  } else if (subgraphCount < 0) {
    errors.push(`Too many 'end' statements: ${Math.abs(subgraphCount)} extra end(s)`);
  }
  
  // Check for invalid characters in node IDs
  const nodeIds = code.match(/\b([a-zA-Z_][a-zA-Z0-9_]*)\b/g) || [];
  for (const id of nodeIds) {
    if (id.includes(' ') || id.includes('-')) {
      errors.push(`Invalid node ID: "${id}". Node IDs should not contain spaces or hyphens. Use quotes or underscores instead.`);
    }
  }
  
  return errors;
}

/**
 * Check for potential issues that might cause rendering problems
 */
function checkPotentialIssues(code: string): string[] {
  const warnings: string[] = [];
  
  // Check for very long lines that might cause rendering issues
  const lines = code.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].length > 200) {
      warnings.push(`Line ${i + 1} is very long (${lines[i].length} characters). This might cause rendering issues.`);
    }
  }
  
  // Check for potentially problematic node names
  const problematicNames = ['end', 'start', 'subgraph', 'graph', 'flowchart'];
  const nodeIds = code.match(/\b([a-zA-Z_][a-zA-Z0-9_]*)\b/g) || [];
  for (const id of nodeIds) {
    if (problematicNames.includes(id.toLowerCase())) {
      warnings.push(`Node ID "${id}" might conflict with Mermaid keywords. Consider using a different name.`);
    }
  }
  
  // Check for missing quotes in labels
  const labelMatches = code.match(/\[[^\]]+\]/g) || [];
  for (const label of labelMatches) {
    const content = label.slice(1, -1); // Remove brackets
    if (content.includes(' ') && !content.startsWith('"')) {
      warnings.push(`Label "${content}" contains spaces but is not quoted. This might cause rendering issues.`);
    }
  }
  
  return warnings;
}

/**
 * Quick validation to check if Mermaid code looks reasonable
 */
export function looksLikeValidMermaid(code: string): boolean {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const trimmed = code.trim();
  if (!trimmed) {
    return false;
  }

  // Look for Mermaid-specific patterns
  const mermaidPatterns = [
    /\b(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram)\b/i,
    /\w+\s*(-->|<-->|->>|--x|\s*-->\s*)\s*\w+/,
    /\w+\s*\[[^\]]+\]/, // Node with label
    /subgraph\s+/i,
    /participant\s+/i,
  ];

  return mermaidPatterns.some(pattern => pattern.test(trimmed));
}