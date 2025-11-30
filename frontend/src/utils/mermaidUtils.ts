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
 *
 * @param {string} language - The language attribute from the code block
 * @param {boolean} inline - Whether the code block is inline
 * @returns {boolean} True if it should be rendered as Mermaid
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
 *
 * @param {string} code - The code content to check
 * @returns {boolean} True if Mermaid syntax is detected
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
 *
 * @param {string} code - The code string with HTML entities
 * @returns {string} The decoded code string
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
 *
 * @param {string} code - The raw Mermaid code
 * @returns {string} The prepared code string
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
 * Get the diagram type from Mermaid code
 * Returns the detected diagram type or 'unknown'
 *
 * @param {string} code - The Mermaid code
 * @returns {string} The diagram type keyword or 'unknown'
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
 *
 * @param {string} language - The language attribute
 * @param {boolean} inline - Whether the code block is inline
 * @returns {boolean} True if it should be rendered as D2
 */
export const isD2Code = (language: string, inline: boolean): boolean => {
  const lang = (language || '').toLowerCase();
  const isD2 = !inline && (lang === 'd2' || lang === 'd2lang');
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
 *
 * @param {string} code - The code content to check
 * @returns {boolean} True if D2 syntax is detected
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
 *
 * @param {string} code - The raw D2 code
 * @returns {string} The prepared code string
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

// ============================================================================
// C4 Diagram Detection and Processing
// ============================================================================

/**
 * Check if a code block should be rendered as a C4 diagram
 * based on the language attribute and inline status
 * Supports: c4, c4diagram, plantuml (if contains C4 elements)
 *
 * @param {string} language - The language attribute
 * @param {boolean} inline - Whether the code block is inline
 * @returns {boolean} True if it should be rendered as C4
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
 *
 * @param {string} code - The code content to check
 * @returns {boolean} True if C4 syntax is detected
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
 *
 * @param {string} code - The C4 code
 * @returns {string} The detected C4 level or 'unknown'
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
 *
 * @param {string} code - The raw C4 code
 * @returns {string} The prepared code string
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
 *
 * @param {string} htmlContent - The HTML string to parse
 * @returns {Array} Array of detected diagram candidates
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

      if (isMermaidSyntax(text)) {
        type = 'mermaid';
      } else if (isD2Syntax(text)) {
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
 * Process HTML content to detect and extract diagram candidates
 * Returns both the original HTML and any detected diagrams
 *
 * @param {string} htmlContent - The HTML string to process
 * @returns {Object} Original HTML and array of detected diagrams
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
