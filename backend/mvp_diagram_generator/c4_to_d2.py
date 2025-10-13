"""
C4 to D2 Diagram Converter

This module provides functionality to convert C4 model diagrams to D2 format.
C4 is a modeling language for software architecture, while D2 is a modern
diagramming language with clean syntax and powerful layout capabilities.

The conversion handles:
- Entity definition parsing (Person, System, Container, Component)
- Relationship parsing (Rel, Rel_U, Rel_Back, etc.)
- Proper D2 syntax generation with shapes and connections
- Layout and styling preservation
- Boundary/Container support
"""

import re
from typing import Dict
from common.logger import get_logger

# Initialize module logger for debugging and monitoring
logger = get_logger(__name__)

# C4 entity types and their D2 equivalents
C4_TO_D2_SHAPES: Dict[str, Dict[str, str]] = {
    # People
    'Person': {'shape': 'person'},
    'Person_Ext': {'shape': 'person', 'style': 'stroke: #999; fill: #f5f5f5'},

    # Systems
    'System': {'shape': 'rectangle', 'style': 'fill: #1168bd; stroke: #0b4884'},
    'System_Ext': {'shape': 'rectangle', 'style': 'fill: #999; stroke: #666'},
    'SystemDb': {'shape': 'cylinder', 'style': 'fill: #1168bd; stroke: #0b4884'},
    'SystemDb_Ext': {'shape': 'cylinder', 'style': 'fill: #999; stroke: #666'},
    'SystemQueue': {'shape': 'queue', 'style': 'fill: #1168bd; stroke: #0b4884'},
    'SystemQueue_Ext': {'shape': 'queue', 'style': 'fill: #999; stroke: #666'},

    # Containers
    'Container': {
        'shape': 'rectangle',
        'style': 'fill: #438dd5; stroke: #3682c3'
    },
    'Container_Ext': {'shape': 'rectangle', 'style': 'fill: #999; stroke: #666'},
    'ContainerDb': {
        'shape': 'cylinder',
        'style': 'fill: #438dd5; stroke: #3682c3'
    },
    'ContainerDb_Ext': {'shape': 'cylinder', 'style': 'fill: #999; stroke: #666'},
    'ContainerQueue': {
        'shape': 'queue',
        'style': 'fill: #438dd5; stroke: #3682c3'
    },
    'ContainerQueue_Ext': {'shape': 'queue', 'style': 'fill: #999; stroke: #666'},

    # Components
    'Component': {
        'shape': 'rectangle',
        'style': 'fill: #85bbf0; stroke: #78a8d8'
    },
    'Component_Ext': {'shape': 'rectangle', 'style': 'fill: #999; stroke: #666'},
    'ComponentDb': {
        'shape': 'cylinder',
        'style': 'fill: #85bbf0; stroke: #78a8d8'
    },
    'ComponentDb_Ext': {'shape': 'cylinder', 'style': 'fill: #999; stroke: #666'},
    'ComponentQueue': {
        'shape': 'queue',
        'style': 'fill: #85bbf0; stroke: #78a8d8'
    },
    'ComponentQueue_Ext': {'shape': 'queue', 'style': 'fill: #999; stroke: #666'},
}


def convert_c4_to_d2(c4_code: str) -> str:
    """
    Convert C4 diagram syntax to D2 syntax.
    
    This implementation parses C4 entities and relationships and generates
    equivalent D2 syntax with proper shapes, connections, and styling.
    
    Args:
        c4_code (str): C4 diagram source code to convert
        
    Returns:
        str: Converted D2 code
        
    Features:
        1. Parse C4 entity definitions (Person, System, Container, Component)
        2. Parse C4 relationships (Rel, Rel_U, Rel_Back, etc.)
        3. Generate appropriate D2 shapes and connections
        4. Handle C4-specific syntax like boundaries and nested structures
        5. Preserve layout and styling
    """
    logger.info("Converting C4 to D2")
    
    # Input validation - handle None and invalid inputs
    if not c4_code or not isinstance(c4_code, str):
        logger.warning("Empty or invalid C4 code provided")
        return ""
    
    logger.debug(f"C4 code length: {len(c4_code)} characters")
    
    # DEBUG: Log sample of input to understand structure
    lines = c4_code.split('\n')[:10]  # First 10 lines
    logger.debug("DEBUG: First 10 lines of C4 input:")
    for i, line in enumerate(lines, 1):
        logger.debug(f"  {i}: {line}")
    
    # Check for C4 entities that should be converted
    entity_pattern = r'\b(Person|System|Container|Component)\s*\('
    rel_pattern = r'\bRel(?:_[A-Z]+)?\s*\('
    has_entities = bool(re.search(entity_pattern, c4_code))
    has_relationships = bool(re.search(rel_pattern, c4_code))
    debug_msg = (
        f"DEBUG: Found entities: {has_entities}, "
        f"relationships: {has_relationships}"
    )
    logger.debug(debug_msg)

    lines = c4_code.strip().split('\n')
    d2_lines = []
    current_container = None
    
    # Track entities and their containers for relationship qualification
    entity_containers = {}  # Maps entity_id -> container_id

    # Add title if present
    title_match = re.search(r'title\s+(.+)', c4_code)
    if title_match:
        d2_lines.append(f"# {title_match.group(1)}")
        d2_lines.append('')

    # Add direction for better layout
    d2_lines.append('direction: down')
    d2_lines.append('')

    # Process line by line
    for i, line in enumerate(lines):
        trimmed_line = line.strip()

        # Skip empty lines and comments
        if not trimmed_line or trimmed_line.startswith('#'):
            continue

        # Detect C4 level
        c4_level_pattern = r'^C4(Context|Container|Component|Dynamic|Deployment)'
        if re.match(c4_level_pattern, trimmed_line, re.IGNORECASE):
            continue

        # Skip title (already handled)
        if trimmed_line.startswith('title '):
            continue

        # Handle closing braces
        if trimmed_line == '}':
            if current_container:
                d2_lines.append('}')
                d2_lines.append('')
                current_container = None
            continue

        # Parse boundaries/containers: System_Boundary(id, "label") {
        boundary_pattern = (
            r'^(Boundary|Enterprise_Boundary|System_Boundary|Container_Boundary)'
            r'\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)\s*\{'
        )
        boundary_match = re.match(boundary_pattern, trimmed_line)
        if boundary_match:
            _, boundary_id, label = boundary_match.groups()
            current_container = boundary_id

            d2_lines.append(f'{boundary_id}: {{')
            d2_lines.append(f'  label: "{label}"')
            d2_lines.append('  style: {')
            d2_lines.append('    stroke: #666')
            d2_lines.append('    stroke-width: 2')
            d2_lines.append('    stroke-dash: 5')
            d2_lines.append('    fill: transparent')
            d2_lines.append('  }')
            d2_lines.append('')
            continue

        # Parse entity definitions
        entity_pattern = (
            r'^(\w+)\s*\(\s*(\w+)\s*,\s*"([^"]+)"'
            r'(?:\s*,\s*"([^"]*)")?(?:\s*,\s*"([^"]*)")?\s*\)'
        )
        entity_match = re.match(entity_pattern, trimmed_line)
        if entity_match:
            entity_type, entity_id, label, description, technology = entity_match.groups()
            shape_info = C4_TO_D2_SHAPES.get(entity_type, {'shape': 'rectangle'})

            # Track entity container for relationship qualification
            if current_container:
                entity_containers[entity_id] = current_container
                logger.debug(f"Tracked entity {entity_id} in container {current_container}")

            # Build entity definition
            prefix = '  ' if current_container else ''
            d2_lines.append(f'{prefix}{entity_id}: {{')
            d2_lines.append(f'{prefix}  label: "{label}"')
            d2_lines.append(f'{prefix}  shape: {shape_info["shape"]}')

            if description or technology:
                if technology:
                    desc = f"{description or ''}\\n[{technology}]"
                else:
                    desc = description
                d2_lines.append(f'{prefix}  tooltip: "{desc}"')

            if 'style' in shape_info:
                d2_lines.append(f'{prefix}  style: {{{shape_info["style"]}}}')

            d2_lines.append(f'{prefix}}}')
            d2_lines.append('')
            continue

        # Parse relationships: Rel(from, to, "label", "technology")
        rel_pattern = (
            r'^Rel(?:_[A-Z]+)?\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]+)"'
            r'(?:\s*,\s*"([^"]*)")?\s*\)'
        )
        rel_match = re.match(rel_pattern, trimmed_line)
        if rel_match:
            from_id, to_id, label, technology = rel_match.groups()

            # Handle relationships with containers
            # First, check if we're currently inside a container
            if current_container and '.' not in from_id:
                from_full = f"{current_container}.{from_id}"
            elif '.' not in from_id and from_id in entity_containers:
                # If not inside container but entity is tracked, use its container
                from_full = f"{entity_containers[from_id]}.{from_id}"
            else:
                from_full = from_id
                
            if current_container and '.' not in to_id:
                to_full = f"{current_container}.{to_id}"
            elif '.' not in to_id and to_id in entity_containers:
                # If not inside container but entity is tracked, use its container
                to_full = f"{entity_containers[to_id]}.{to_id}"
            else:
                to_full = to_id

            if technology:
                full_label = f"{label}\\n[{technology}]"
            else:
                full_label = label
                
            d2_lines.append(f'{from_full} -> {to_full}: "{full_label}"')
            logger.debug(f"Added relationship: {from_full} -> {to_full}")
            continue

    # Close any open containers
    if current_container:
        d2_lines.append('}')
        d2_lines.append('')

    d2_code = '\n'.join(d2_lines)
    
    logger.debug(f"Converted D2 code length: {len(d2_code)} characters")
    
    # DEBUG: Check if entities were preserved (shouldn't be with current impl)
    entity_pattern = r'\b(Person|System|Container|Component)\s*\('
    entities_preserved = bool(re.search(entity_pattern, d2_code))
    debug_msg = (
        f"DEBUG: Entities preserved in output (should be False): "
        f"{entities_preserved}"
    )
    logger.debug(debug_msg)
    
    return d2_code


def simple_c4_to_d2(c4_code: str) -> str:
    """
    Simplified C4-to-D2 conversion for basic structures.
    This is a fallback if full parsing fails.
    
    Args:
        c4_code (str): C4 diagram source code
        
    Returns:
        str: Partially converted D2 code
    """
    if not c4_code or not isinstance(c4_code, str):
        return ""

    d2_code = c4_code

    # Replace C4 keywords with D2 equivalents
    c4_pattern = r'^C4(Context|Container|Component|Dynamic|Deployment)'
    d2_code = re.sub(c4_pattern, r'# C4 \1 Diagram', d2_code, flags=re.MULTILINE)

    # Convert Person() to D2 shape
    d2_code = re.sub(
        r'Person\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)',
        r'\1: {label: "\2"; shape: person}',
        d2_code
    )

    # Convert System() to D2 shape
    d2_code = re.sub(
        r'System\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*\)',
        r'\1: {label: "\2"; shape: rectangle}',
        d2_code
    )

    # Convert Rel() to D2 connection
    d2_code = re.sub(
        r'Rel\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]+)"\s*\)',
        r'\1 -> \2: "\3"',
        d2_code
    )

    return d2_code


def looks_like_c4(code: str) -> bool:
    """
    Detect if code is C4 syntax (even without language marker).
    
    Args:
        code (str): Code to analyze
        
    Returns:
        bool: True if code appears to be C4 syntax
    """
    if not code or not isinstance(code, str):
        return False

    c4_patterns = [
        re.compile(r'\b(Person|System|Container|Component)\s*\('),
        re.compile(r'\bRel\s*\('),
        re.compile(r'\bC4(Context|Container|Component|Dynamic|Deployment)\b'),
        re.compile(r'\bBoundary\s*\('),
    ]

    return any(pattern.search(code) for pattern in c4_patterns)


def extract_c4_level(code: str) -> str:
    """
    Get C4 level from code.
    
    Args:
        code (str): C4 diagram code
        
    Returns:
        str: The C4 level (Context, Container, Component, etc.)
    """
    c4_pattern = r'C4(Context|Container|Component|Dynamic|Deployment)'
    match = re.search(c4_pattern, code, re.IGNORECASE)
    return match.group(1) if match else 'Unknown'
