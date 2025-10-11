/**
 * C4-to-D2 Translator
 *
 * Converts C4 diagram syntax (Mermaid-style) to D2 syntax
 * C4 Model has 4 levels:
 * - Context (C1): System boundaries and external actors
 * - Container (C2): High-level technology choices
 * - Component (C3): Component-level architecture
 * - Code (C4): Class diagrams (not commonly used)
 */

/**
 * C4 entity types and their D2 equivalents
 */
const C4_TO_D2_SHAPES: Record<string, { shape: string; style?: string }> = {
  // People
  'Person': { shape: 'person' },
  'Person_Ext': { shape: 'person', style: 'stroke: #999; fill: #f5f5f5' },

  // Systems
  'System': { shape: 'rectangle', style: 'fill: #1168bd; stroke: #0b4884' },
  'System_Ext': { shape: 'rectangle', style: 'fill: #999; stroke: #666' },
  'SystemDb': { shape: 'cylinder', style: 'fill: #1168bd; stroke: #0b4884' },
  'SystemDb_Ext': { shape: 'cylinder', style: 'fill: #999; stroke: #666' },
  'SystemQueue': { shape: 'queue', style: 'fill: #1168bd; stroke: #0b4884' },
  'SystemQueue_Ext': { shape: 'queue', style: 'fill: #999; stroke: #666' },

  // Containers
  'Container': { shape: 'rectangle', style: 'fill: #438dd5; stroke: #3682c3' },
  'Container_Ext': { shape: 'rectangle', style: 'fill: #999; stroke: #666' },
  'ContainerDb': { shape: 'cylinder', style: 'fill: #438dd5; stroke: #3682c3' },
  'ContainerDb_Ext': { shape: 'cylinder', style: 'fill: #999; stroke: #666' },
  'ContainerQueue': { shape: 'queue', style: 'fill: #438dd5; stroke: #3682c3' },
  'ContainerQueue_Ext': { shape: 'queue', style: 'fill: #999; stroke: #666' },

  // Components
  'Component': { shape: 'rectangle', style: 'fill: #85bbf0; stroke: #78a8d8' },
  'Component_Ext': { shape: 'rectangle', style: 'fill: #999; stroke: #666' },
  'ComponentDb': { shape: 'cylinder', style: 'fill: #85bbf0; stroke: #78a8d8' },
  'ComponentDb_Ext': { shape: 'cylinder', style: 'fill: #999; stroke: #666' },
  'ComponentQueue': { shape: 'queue', style: 'fill: #85bbf0; stroke: #78a8d8' },
  'ComponentQueue_Ext': { shape: 'queue', style: 'fill: #999; stroke: #666' },
};

/**
 * Parse C4 Mermaid syntax and convert to D2
 * Enhanced to support boundaries and nested structures
 */
export const convertC4ToD2 = (c4Code: string): string => {
  if (!c4Code || typeof c4Code !== 'string') {
    return '';
  }

  const lines = c4Code.trim().split('\n');
  const d2Lines: string[] = [];
  let c4Level = 'Context'; // Default level
  const indentStack: string[] = []; // Track nesting
  let currentContainer: string | null = null;

  // Add title if present
  const titleMatch = c4Code.match(/title\s+(.+)/);
  if (titleMatch) {
    d2Lines.push(`# ${titleMatch[1]}`);
    d2Lines.push('');
  }

  // Add direction for better layout
  d2Lines.push('direction: down');
  d2Lines.push('');

  // Process line by line
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();

    // Skip empty lines and comments
    if (!trimmedLine || trimmedLine.startsWith('#')) {
      continue;
    }

    // Detect C4 level
    if (/^C4(Context|Container|Component|Dynamic|Deployment)/i.test(trimmedLine)) {
      c4Level = trimmedLine.match(/^C4(\w+)/i)?.[1] || 'Context';
      continue;
    }

    // Skip title (already handled)
    if (trimmedLine.startsWith('title ')) {
      continue;
    }

    // Handle closing braces
    if (trimmedLine === '}') {
      if (currentContainer) {
        d2Lines.push('}');
        d2Lines.push('');
        currentContainer = null;
      }
      continue;
    }

    // Parse boundaries/containers: System_Boundary(id, "label") {
    const boundaryMatch = trimmedLine.match(/^(Boundary|Enterprise_Boundary|System_Boundary|Container_Boundary)\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)\s*\{/);
    if (boundaryMatch) {
      const [, , id, label] = boundaryMatch;
      currentContainer = id;

      d2Lines.push(`${id}: {`);
      d2Lines.push(`  label: "${label}"`);
      d2Lines.push(`  style: {`);
      d2Lines.push(`    stroke: #666`);
      d2Lines.push(`    stroke-width: 2`);
      d2Lines.push(`    stroke-dash: 5`);
      d2Lines.push(`    fill: transparent`);
      d2Lines.push(`  }`);
      d2Lines.push('');
      continue;
    }

    // Parse entity definitions: Type(id, "label", "description", "technology")
    const entityMatch = trimmedLine.match(/^(\w+)\s*\(\s*(\w+)\s*,\s*"([^"]+)"(?:\s*,\s*"([^"]*)")?(?:\s*,\s*"([^"]*)")?\s*\)/);
    if (entityMatch) {
      const [, type, id, label, description, technology] = entityMatch;
      const shapeInfo = C4_TO_D2_SHAPES[type] || { shape: 'rectangle' };

      // Build entity definition
      const entityLines: string[] = [];
      const prefix = currentContainer ? '  ' : '';
      const fullId = currentContainer ? `${currentContainer}.${id}` : id;

      entityLines.push(`${prefix}${id}: {`);
      entityLines.push(`${prefix}  label: "${label}"`);
      entityLines.push(`${prefix}  shape: ${shapeInfo.shape}`);

      if (description || technology) {
        const desc = technology ? `${description || ''}\n[${technology}]` : description;
        entityLines.push(`${prefix}  tooltip: "${desc}"`);
      }

      if (shapeInfo.style) {
        entityLines.push(`${prefix}  style: {${shapeInfo.style}}`);
      }

      entityLines.push(`${prefix}}`);
      entityLines.push('');

      d2Lines.push(...entityLines);
      continue;
    }

    // Parse relationships: Rel(from, to, "label", "technology")
    const relMatch = trimmedLine.match(/^Rel(?:_[A-Z]+)?\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]+)"(?:\s*,\s*"([^"]*)")?\s*\)/);
    if (relMatch) {
      const [, from, to, label, technology] = relMatch;

      // Handle relationships with containers
      const fromId = currentContainer && !from.includes('.') ? `${currentContainer}.${from}` : from;
      const toId = currentContainer && !to.includes('.') ? `${currentContainer}.${to}` : to;

      const fullLabel = technology ? `${label}\\n[${technology}]` : label;
      d2Lines.push(`${fromId} -> ${toId}: "${fullLabel}"`);
      continue;
    }
  }

  // Close any open containers
  if (currentContainer) {
    d2Lines.push('}');
    d2Lines.push('');
  }

  return d2Lines.join('\n');
};

/**
 * Simplified C4-to-D2 conversion for basic structures
 * This is a fallback if full parsing fails
 */
export const simpleC4ToD2 = (c4Code: string): string => {
  if (!c4Code || typeof c4Code !== 'string') {
    return '';
  }

  let d2Code = c4Code;

  // Replace C4 keywords with D2 equivalents
  d2Code = d2Code.replace(/^C4(Context|Container|Component|Dynamic|Deployment)/gm, '# C4 $1 Diagram');

  // Convert Person() to D2 shape
  d2Code = d2Code.replace(/Person\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)/g, '$1: {label: "$2"; shape: person}');

  // Convert System() to D2 shape
  d2Code = d2Code.replace(/System\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)/g, '$1: {label: "$2"; shape: rectangle}');

  // Convert Rel() to D2 connection
  d2Code = d2Code.replace(/Rel\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]+)"\s*\)/g, '$1 -> $2: "$3"');

  return d2Code;
};

/**
 * Detect if code is C4 syntax (even without language marker)
 */
export const looksLikeC4 = (code: string): boolean => {
  if (!code || typeof code !== 'string') {
    return false;
  }

  const c4Patterns = [
    /\b(Person|System|Container|Component)\s*\(/,
    /\bRel\s*\(/,
    /\bC4(Context|Container|Component|Dynamic|Deployment)\b/,
    /\bBoundary\s*\(/,
  ];

  return c4Patterns.some(pattern => pattern.test(code));
};

/**
 * Get C4 level from code
 */
export const extractC4Level = (code: string): string => {
  const match = code.match(/C4(Context|Container|Component|Dynamic|Deployment)/i);
  return match ? match[1] : 'Unknown';
};
