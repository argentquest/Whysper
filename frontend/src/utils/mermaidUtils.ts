/**
 * Diagram Utilities
 *
 * Provides detection and decoding utilities for diagram languages:
 * - Mermaid diagrams
 * - D2 diagrams
 */

import { ApiService } from '../services/api';

/**
 * All supported Mermaid diagram types/keywords
 */
const MERMAID_KEYWORDS = [
  'classDiagram',
  'sequenceDiagram',
  'graph',
  'flowchart',
  'stateDiagram',
  'stateDiagram-v2',
  'erDiagram',
  'gantt',
  'pie',
  'journey',
  'gitGraph',
  'mindmap',
  'timeline',
  'quadrantChart',
  'requirementDiagram',
  'sankey-beta',
  'gitgraph',
] as const;

/**
 * C4 diagram keywords - these will be rendered using D2
 * Supports both Mermaid-style and PlantUML-style C4 diagrams
 */
const C4_KEYWORDS = [
  'C4Context',
  'C4Container',
  'C4Component',
  'C4Dynamic',
  'C4Deployment',
] as const;

/**
 * PlantUML C4 markers - these indicate PlantUML-style C4 diagrams
 */
const PLANTUML_C4_MARKERS = [
  '@startuml',
  '@enduml',
  '!include',
] as const;

/**
 * Check if a code block should be rendered as a Mermaid diagram
 * based on the language attribute and inline status
 */
export const isMermaidCode = (language: string, inline: boolean): boolean => {
  const isMermaid = !inline && language === 'mermaid';
  if (isMermaid) {
    console.log('🎨 [DIAGRAM DETECTION] Mermaid diagram detected (language marker)', { language, inline });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'mermaid',
      detection_method: 'language_marker'
    });
  }
  return isMermaid;
};

/**
 * Detect if code content contains Mermaid syntax
 * Uses heuristic pattern matching to identify Mermaid diagram types
 */
export const isMermaidSyntax = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  // Check if any Mermaid keyword exists as a word boundary
  const foundKeyword = MERMAID_KEYWORDS.find(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'i');
    return regex.test(code);
  });

  if (foundKeyword) {
    console.log('🎨 [DIAGRAM DETECTION] Mermaid syntax detected by keyword', {
      keyword: foundKeyword,
      codePreview: code.substring(0, 50) + '...'
    });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'mermaid',
      code_preview: code.substring(0, 100),
      code_length: code.length,
      detection_method: `syntax_pattern:${foundKeyword}`
    });
  }

  return !!foundKeyword;
};

/**
 * Decode HTML entities in Mermaid code
 * Uses browser's native HTML entity decoding for comprehensive support
 */
export const decodeMermaidCode = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return code;
  }

  // Use browser's native HTML entity decoding
  const textarea = document.createElement('textarea');
  textarea.innerHTML = code;
  return textarea.value;
};

/**
 * Prepare Mermaid code for rendering
 * - Removes trailing newlines
 * - Decodes HTML entities
 * - Trims whitespace
 */
export const prepareMermaidCode = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return '';
  }

  // Convert to string and remove trailing newline
  let prepared = String(code).replace(/\n$/, '');

  // Decode HTML entities
  prepared = decodeMermaidCode(prepared);

  return prepared;
};

/**
 * Validate if a string contains valid Mermaid diagram syntax
 * Performs basic validation before attempting to render
 */
export const isValidMermaidDiagram = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const trimmed = code.trim();

  // Must have content
  if (trimmed.length === 0) {
    return false;
  }

  // Should start with a Mermaid keyword or contain one near the beginning
  const firstLines = trimmed.split('\n').slice(0, 3).join('\n');
  return isMermaidSyntax(firstLines);
};

/**
 * Get the diagram type from Mermaid code
 * Returns the detected diagram type or 'unknown'
 */
export const getMermaidDiagramType = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return 'unknown';
  }

  for (const keyword of MERMAID_KEYWORDS) {
    const regex = new RegExp(`\\b${keyword}\\b`, 'i');
    if (regex.test(code)) {
      return keyword;
    }
  }

  return 'unknown';
};

// ============================================================================
// D2 Diagram Detection and Processing
// ============================================================================

/**
 * Common D2 diagram keywords and patterns
 * D2 uses a simpler syntax than Mermaid - connections with arrows, shapes, etc.
 */


/**
 * Check if a code block should be rendered as a D2 diagram
 * based on the language attribute and inline status
 */
export const isD2Code = (language: string, inline: boolean): boolean => {
  const isD2 = !inline && (language === 'd2' || language === 'd2lang');
  if (isD2) {
    console.log('🎯 [DIAGRAM DETECTION] D2 diagram detected (language marker)', { language, inline });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'd2',
      detection_method: 'language_marker'
    });
  }
  return isD2;
};

/**
 * Detect if code content contains D2 syntax
 * Uses simplified pattern matching - backend handles actual validation
 */
export const isD2Syntax = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const trimmed = code.trim();
  if (trimmed.length === 0) {
    return false;
  }

  // Look for basic D2 patterns
  const d2Patterns = [
    /\w+\s*->\s*\w+/, // Connections
    /direction:\s*\w+/, // Direction
    /\w+:\s*"[^"]+"\s*\{/, // Object definitions
    /style\.\w+:/ // Style properties
  ];

  const hasMatch = d2Patterns.some(pattern => pattern.test(trimmed));

  if (hasMatch) {
    console.log('🎯 [DIAGRAM DETECTION] D2 syntax detected by pattern matching', {
      codePreview: code.substring(0, 50) + '...'
    });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'd2',
      code_preview: code.substring(0, 100),
      code_length: code.length,
      detection_method: 'syntax_pattern'
    });
  }

  return hasMatch;
};

/**
 * Prepare D2 code for rendering
 * - Removes trailing newlines
 * - Decodes HTML entities
 * - Trims whitespace
 */
export const prepareD2Code = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return '';
  }

  // Convert to string and remove trailing newline
  let prepared = String(code).replace(/\n$/, '');

  // Decode HTML entities (reuse the same function)
  const textarea = document.createElement('textarea');
  textarea.innerHTML = prepared;
  prepared = textarea.value;

  return prepared;
};

/**
 * Validate if a string contains valid D2 diagram syntax
 * Performs basic validation before attempting to render
 */
export const isValidD2Diagram = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const trimmed = code.trim();

  // Must have content
  if (trimmed.length === 0) {
    return false;
  }

  // Should contain D2 syntax patterns
  return isD2Syntax(trimmed);
};

// ============================================================================
// C4 Diagram Detection and Processing
// ============================================================================

/**
 * Check if a code block should be rendered as a C4 diagram
 * based on the language attribute and inline status
 * Supports: c4, c4diagram, plantuml (if contains C4 elements)
 */
export const isC4Code = (language: string, inline: boolean): boolean => {
  // Direct C4 language markers
  const isDirectC4 = !inline && (language === 'c4' || language === 'c4diagram');

  // PlantUML marker - need additional check for C4 content
  const isPlantUML = !inline && (language === 'plantuml' || language === 'puml');

  if (isDirectC4) {
    console.log('🏗️ [DIAGRAM DETECTION] C4 diagram detected (language marker)', { language, inline });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'c4' as any,
      detection_method: 'c4_language_marker'
    });
    return true;
  }

  if (isPlantUML) {
    console.log('🏗️ [DIAGRAM DETECTION] PlantUML detected (language marker), checking for C4 content', { language, inline });
    // Note: Additional C4 content check will be done by isC4Syntax in the calling code
    return false; // Let isC4Syntax handle the actual C4 detection
  }

  return false;
};

/**
 * Detect if code content contains C4 syntax
 * C4 diagrams use specific keywords for different levels
 * Supports both Mermaid-style and PlantUML-style C4 diagrams
 */
export const isC4Syntax = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  // Check for Mermaid-style C4 keywords
  const foundMermaidKeyword = C4_KEYWORDS.find(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`);
    return regex.test(code);
  });

  if (foundMermaidKeyword) {
    console.log('🏗️ [DIAGRAM DETECTION] C4 Mermaid syntax detected by keyword', {
      keyword: foundMermaidKeyword,
      codePreview: code.substring(0, 50) + '...'
    });
    // Log to backend
    ApiService.logDiagramEvent({
      event_type: 'detection',
      diagram_type: 'c4' as any,
      code_preview: code.substring(0, 100),
      code_length: code.length,
      detection_method: `c4_mermaid_keyword:${foundMermaidKeyword}`
    });
    return true;
  }

  // Check for PlantUML-style C4 markers
  const foundPlantUMLMarker = PLANTUML_C4_MARKERS.find(marker => {
    const regex = new RegExp(marker, 'i');
    return regex.test(code);
  });

  if (foundPlantUMLMarker) {
    // Additional check: make sure it's actually C4, not just any PlantUML
    const hasC4Elements = /\b(Person|System|Container|Component|Rel)\s*\(/.test(code);

    if (hasC4Elements) {
      console.log('🏗️ [DIAGRAM DETECTION] C4 PlantUML syntax detected', {
        marker: foundPlantUMLMarker,
        codePreview: code.substring(0, 50) + '...'
      });
      // Log to backend
      ApiService.logDiagramEvent({
        event_type: 'detection',
        diagram_type: 'c4' as any,
        code_preview: code.substring(0, 100),
        code_length: code.length,
        detection_method: `c4_plantuml_marker:${foundPlantUMLMarker}`
      });
      return true;
    }
  }

  return false;
};

/**
 * Get the C4 level from code (Context, Container, Component, etc.)
 */
export const getC4Level = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return 'unknown';
  }

  for (const keyword of C4_KEYWORDS) {
    const regex = new RegExp(`\\b${keyword}\\b`);
    if (regex.test(code)) {
      // Extract level name (e.g., "C4Context" -> "Context")
      return keyword.replace('C4', '');
    }
  }

  return 'unknown';
};

/**
 * Prepare C4 code for rendering
 * C4 will be rendered using D2, so we may need to preprocess
 */
export const prepareC4Code = (code: string): string => {
  if (!code || typeof code !== 'string') {
    return '';
  }

  // Convert to string and remove trailing newline
  let prepared = String(code).replace(/\n$/, '');

  // Decode HTML entities (reuse the same function)
  const textarea = document.createElement('textarea');
  textarea.innerHTML = prepared;
  prepared = textarea.value;

  return prepared;
};

// ============================================================================
// Enhanced Detection for Mixed HTML Content
// ============================================================================

/**
 * Extract potential diagram code from HTML elements
 * Handles <pre><code>, inline <code>, and <p> tags
 */
export const extractDiagramCandidates = (htmlContent: string): Array<{
  code: string;
  type: 'mermaid' | 'd2' | 'unknown';
  element: 'pre' | 'code' | 'p';
  language?: string;
}> => {
  const candidates: Array<{
    code: string;
    type: 'mermaid' | 'd2' | 'unknown';
    element: 'pre' | 'code' | 'p';
    language?: string;
  }> = [];

  // Create a temporary DOM to parse HTML
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlContent;

  // Extract from <pre><code> blocks (highest priority)
  const preCodeBlocks = tempDiv.querySelectorAll('pre code');
  preCodeBlocks.forEach(codeEl => {
    const code = codeEl.textContent || '';
    const language = codeEl.className.match(/language-(\w+)/)?.[1] || '';
    
    if (code.trim().length > 0) {
      let type: 'mermaid' | 'd2' | 'unknown' = 'unknown';
      
      // Check explicit language markers first
      if (language === 'mermaid' || isMermaidSyntax(code)) {
        type = 'mermaid';
      } else if (language === 'd2' || language === 'd2lang' || isD2Syntax(code)) {
        type = 'd2';
      }
      
      candidates.push({
        code: decodeMermaidCode(code),
        type,
        element: 'pre',
        language
      });
    }
  });

  // Extract from standalone <code> blocks (inline code)
  const codeBlocks = tempDiv.querySelectorAll('code:not(pre code)');
  codeBlocks.forEach(codeEl => {
    const code = codeEl.textContent || '';
    const language = codeEl.className.match(/language-(\w+)/)?.[1] || '';
    
    if (code.trim().length > 10) { // Only consider longer inline code blocks
      let type: 'mermaid' | 'd2' | 'unknown' = 'unknown';
      
      if (language === 'mermaid' || isMermaidSyntax(code)) {
        type = 'mermaid';
      } else if (language === 'd2' || language === 'd2lang' || isD2Syntax(code)) {
        type = 'd2';
      }
      
      if (type !== 'unknown') {
        candidates.push({
          code: decodeMermaidCode(code),
          type,
          element: 'code',
          language
        });
      }
    }
  });

  // Extract from <p> tags (very lenient detection)
  const paragraphs = tempDiv.querySelectorAll('p');
  paragraphs.forEach(pEl => {
    const text = pEl.textContent || '';
    
    // Look for paragraph content that might be diagram code
    if (text.trim().length > 20) { // Reasonable minimum length
      let type: 'mermaid' | 'd2' | 'unknown' = 'unknown';
      
      if (isMermaidSyntaxLenient(text)) {
        type = 'mermaid';
      } else if (isD2SyntaxLenient(text)) {
        type = 'd2';
      }
      
      if (type !== 'unknown') {
        candidates.push({
          code: decodeMermaidCode(text),
          type,
          element: 'p'
        });
      }
    }
  });

  return candidates;
};

/**
 * Very lenient Mermaid syntax detection for plain text content
 * Catches more potential diagrams with lower confidence threshold
 *
 * IMPORTANT: This uses stricter patterns than before to avoid false positives
 * Only triggers when there's strong evidence of diagram syntax
 */
export const isMermaidSyntaxLenient = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const text = code.trim();
  const textLower = text.toLowerCase();

  // FIRST: Check for explicit Mermaid keywords (highest confidence)
  // These are very specific and unlikely to appear in regular text
  const hasExplicitKeyword = MERMAID_KEYWORDS.some(keyword => {
    const regex = new RegExp(`\\b${keyword.toLowerCase()}\\b`, 'i');
    return regex.test(textLower);
  });

  if (hasExplicitKeyword) {
    return true; // If we find an explicit keyword, it's very likely a diagram
  }

  // SECOND: Check for strict Mermaid-specific patterns
  // These patterns are unique to Mermaid and unlikely to appear in prose
  const strictPatterns = [
    // Mermaid arrow syntax (specific formats)
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*-->\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$/m,  // a --> b (on its own line)
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*->>?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:/m, // sequence diagram: a ->> b:

    // State diagram markers
    /\[\*\]\s*-->/,   // [*] --> (state start)
    /-->\s*\[\*\]/,   // --> [*] (state end)

    // Subgraph syntax
    /subgraph\s+["']?[\w\s]+["']?\s*$/m,

    // Participant declarations (sequence diagrams)
    /^\s*participant\s+[a-zA-Z_]/m,

    // Class diagram syntax
    /^\s*class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{/m,

    // Graph direction declarations
    /^\s*graph\s+(TD|TB|BT|RL|LR)\s*$/m,
    /^\s*flowchart\s+(TD|TB|BT|RL|LR)\s*$/m,

    // Multiple Mermaid arrows on separate lines (strong indicator)
    /-->\s*$.*\n.*-->\s*$/ms,
  ];

  // Count strict pattern matches
  const strictMatches = strictPatterns.filter(pattern => pattern.test(text));

  // Need at least 2 strict pattern matches, OR
  // 1 strict match + multiple lines that look like diagram syntax
  if (strictMatches.length >= 2) {
    return true;
  }

  if (strictMatches.length === 1) {
    // Check if we have multiple lines with arrow-like patterns
    const lines = text.split('\n').filter(line => line.trim().length > 0);
    const arrowLines = lines.filter(line =>
      /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(-->|->|---|==|\.\.)/m.test(line)
    );

    // If we have 1 strict match and multiple arrow lines, likely a diagram
    if (arrowLines.length >= 2) {
      return true;
    }
  }

  // Default: not confident this is a Mermaid diagram
  return false;
};

/**
 * Very lenient D2 syntax detection for plain text content
 * Catches more potential diagrams with lower confidence threshold
 *
 * IMPORTANT: This uses stricter patterns than before to avoid false positives
 * Only triggers when there's strong evidence of D2 diagram syntax
 */
export const isD2SyntaxLenient = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const text = code.trim();

  // FIRST: Check for strict D2-specific patterns
  // These patterns are unique to D2 and unlikely to appear in prose
  const strictPatterns = [
    // D2 arrow connections (on their own lines)
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*-+>\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$/m,
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*<-+>\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$/m,
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*<-+\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$/m,

    // D2 property assignments (must be on own line)
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\.shape\s*:\s*/m,
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\.style\./m,
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\.label\s*:\s*/m,

    // D2 blocks
    /^\s*layers\s*\{/m,
    /^\s*scenarios\s*\{/m,
    /^\s*direction\s*:\s*(up|down|right|left)/m,

    // D2 labeled elements (specific format)
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*["'][^"']+["']\s*$/m,
  ];

  // Count strict pattern matches
  const strictMatches = strictPatterns.filter(pattern => pattern.test(text));

  // Need at least 2 strict pattern matches for confidence
  if (strictMatches.length >= 2) {
    return true;
  }

  // Alternative: Check for multiple D2 arrows on separate lines (strong indicator)
  const lines = text.split('\n').filter(line => line.trim().length > 0);
  const arrowLines = lines.filter(line =>
    /^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(-+>|<-+>|<-+)\s*[a-zA-Z_][a-zA-Z0-9_]*/.test(line)
  );

  // If we have multiple arrow lines, likely a D2 diagram
  if (arrowLines.length >= 3) {
    return true;
  }

  // Default: not confident this is a D2 diagram
  return false;
};

/**
 * Process HTML content to detect and extract diagram candidates
 * Returns both the original HTML and any detected diagrams
 */
export const processMixedHtmlContent = (htmlContent: string): {
  originalHtml: string;
  diagrams: Array<{
    code: string;
    type: 'mermaid' | 'd2';
    element: 'pre' | 'code' | 'p';
    language?: string;
    confidence: 'high' | 'medium' | 'low';
  }>;
} => {
  const candidates = extractDiagramCandidates(htmlContent);
  
  // Filter and score candidates
  const diagrams = candidates
    .filter(candidate => candidate.type !== 'unknown')
    .map(candidate => {
      let confidence: 'high' | 'medium' | 'low' = 'low';
      
      // High confidence: explicit language marker or <pre><code>
      if (candidate.language || candidate.element === 'pre') {
        confidence = 'high';
      }
      // Medium confidence: inline <code> with detected syntax
      else if (candidate.element === 'code') {
        confidence = 'medium';
      }
      // Low confidence: <p> tags with detected patterns
      else if (candidate.element === 'p') {
        confidence = 'low';
      }
      
      return {
        code: candidate.code,
        type: candidate.type as 'mermaid' | 'd2',
        element: candidate.element,
        language: candidate.language,
        confidence
      };
    });
  
  return {
    originalHtml: htmlContent,
    diagrams
  };
};
