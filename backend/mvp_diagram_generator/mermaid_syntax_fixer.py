"""
Mermaid Syntax Fixer

This module provides automatic fixing for common Mermaid diagram syntax errors.
It attempts to correct issues that frequently occur in AI-generated or manually written diagrams.
"""

import re
import logging
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class MermaidFixResult:
    """Result of Mermaid syntax fixing operation"""
    is_valid: bool
    corrected_code: str
    corrections: List[str]
    warnings: List[str]
    errors: List[str]

def fix_mermaid_syntax(code: str) -> MermaidFixResult:
    """
    Attempts to fix common Mermaid syntax errors.

    Args:
        code (str): The Mermaid code to fix

    Returns:
        MermaidFixResult: Result containing corrected code and diagnostics
    """
    corrections = []
    warnings = []
    errors = []
    corrected_code = code.strip()

    if not corrected_code:
        errors.append("Empty Mermaid code")
        return MermaidFixResult(False, corrected_code, corrections, warnings, errors)

    # Fix 1: Ensure diagram type declaration
    if not has_diagram_type_declaration(corrected_code):
        corrected_code = add_diagram_type_declaration(corrected_code)
        corrections.append("Added missing diagram type declaration")

    # Fix 2: Fix arrow syntax issues
    corrected_code, arrow_fixes = fix_arrow_syntax(corrected_code)
    corrections.extend(arrow_fixes)

    # Fix 3: Fix node syntax issues
    corrected_code, node_fixes = fix_node_syntax(corrected_code)
    corrections.extend(node_fixes)

    # Fix 4: Fix subgraph syntax issues
    corrected_code, subgraph_fixes = fix_subgraph_syntax(corrected_code)
    corrections.extend(subgraph_fixes)

    # Fix 5: Fix sequence diagram syntax
    corrected_code, seq_fixes = fix_sequence_diagram_syntax(corrected_code)
    corrections.extend(seq_fixes)

    # Fix 6: Clean up formatting
    corrected_code, format_fixes = cleanup_formatting(corrected_code)
    corrections.extend(format_fixes)

    # Basic validation
    validation_errors = validate_basic_structure(corrected_code)
    errors.extend(validation_errors)

    # Check for potential issues
    potential_warnings = check_potential_issues(corrected_code)
    warnings.extend(potential_warnings)

    is_valid = len(errors) == 0

    logger.debug(f"Mermaid syntax fixer: {len(corrections)} corrections, {len(warnings)} warnings, {len(errors)} errors")

    return MermaidFixResult(is_valid, corrected_code, corrections, warnings, errors)

def has_diagram_type_declaration(code: str) -> bool:
    """Check if code has a diagram type declaration."""
    diagram_types = [
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt',
        'pie', 'journey', 'gitGraph', 'mindmap', 'timeline',
        'quadrantChart', 'requirementDiagram', 'sankey-beta'
    ]

    first_line = code.strip().split('\n')[0].strip()
    return any(first_line.startswith(dtype) for dtype in diagram_types)

def add_diagram_type_declaration(code: str) -> str:
    """Add appropriate diagram type declaration based on content."""
    trimmed = code.strip()

    # Try to infer the diagram type
    if 'participant' in trimmed or '->>' in trimmed:
        return f"sequenceDiagram\n{trimmed}"
    elif 'class ' in trimmed or '<|--' in trimmed:
        return f"classDiagram\n{trimmed}"
    elif 'state ' in trimmed or '[*]' in trimmed:
        return f"stateDiagram-v2\n{trimmed}"
    elif re.search(r'\bgantt\b', trimmed, re.IGNORECASE):
        return f"gantt\n{trimmed}"
    else:
        # Default to flowchart
        return f"flowchart TD\n{trimmed}"

def fix_arrow_syntax(code: str) -> tuple[str, List[str]]:
    """Fix common arrow syntax issues."""
    corrections = []
    fixed = code

    original = fixed

    # Fix flowchart arrows - ensure proper spacing
    fixed = re.sub(r'(\w+)-->', r'\1 -->', fixed)
    fixed = re.sub(r'-->(\w+)', r'--> \1', fixed)

    # Fix sequence diagram arrows
    fixed = re.sub(r'(\w+)-->>', r'\1 -->>', fixed)
    fixed = re.sub(r'-->>(\w+)', r'-->> \1', fixed)

    # Fix bidirectional arrows
    fixed = re.sub(r'(\w+)<-->', r'\1 <-->', fixed)
    fixed = re.sub(r'<-->(\w+)', r'<--> \1', fixed)

    if fixed != original:
        corrections.append("Fixed arrow spacing")

    return fixed, corrections

def fix_node_syntax(code: str) -> tuple[str, List[str]]:
    """Fix node ID and label issues."""
    corrections = []
    fixed = code

    # Fix nodes with special characters that need quotes
    def fix_node_label(match):
        node_id = match.group(1)
        label = match.group(2)

        # If label contains special characters, ensure it's quoted
        if any(char in label for char in [' ', '-', '(', ')', ':', ';']):
            if not (label.startswith('"') and label.endswith('"')):
                corrections.append(f"Added quotes to node label: {label}")
                return f'{node_id}["{label}"]'

        return match.group(0)

    fixed = re.sub(r'(\w+)\[([^\]]+)\]', fix_node_label, fixed)

    return fixed, corrections

def fix_subgraph_syntax(code: str) -> tuple[str, List[str]]:
    """Fix subgraph syntax issues."""
    corrections = []
    fixed = code

    # Count subgraph declarations and end statements
    subgraph_count = len(re.findall(r'\bsubgraph\b', fixed, re.IGNORECASE))
    end_count = len(re.findall(r'^\s*end\s*$', fixed, re.MULTILINE))

    # Add missing 'end' statements
    if subgraph_count > end_count:
        missing = subgraph_count - end_count
        fixed += '\n' + '\n'.join(['end'] * missing)
        corrections.append(f"Added {missing} missing 'end' statement(s)")

    return fixed, corrections

def fix_sequence_diagram_syntax(code: str) -> tuple[str, List[str]]:
    """Fix sequence diagram syntax issues."""
    corrections = []
    fixed = code

    # Only apply if this looks like a sequence diagram
    if 'sequenceDiagram' not in fixed and '->>' not in fixed:
        return fixed, corrections

    # Fix participant declarations
    original = fixed
    fixed = re.sub(
        r'participant\s+(\w+)\s+as\s+(["\']?)([^"\'\n]+)\2',
        r'participant \1 as \3',
        fixed,
        flags=re.IGNORECASE
    )

    if fixed != original:
        corrections.append("Fixed participant declarations")

    return fixed, corrections

def cleanup_formatting(code: str) -> tuple[str, List[str]]:
    """Clean up extra whitespace and formatting."""
    corrections = []
    original = code

    # Remove excessive blank lines (more than 2 consecutive)
    fixed = re.sub(r'\n\s*\n\s*\n+', '\n\n', code)

    # Trim whitespace from each line (but preserve indentation for subgraphs)
    lines = fixed.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped:
            # Preserve some indentation for readability
            if stripped.startswith('end'):
                cleaned_lines.append(stripped)
            elif any(stripped.startswith(kw) for kw in ['subgraph', 'participant', 'sequenceDiagram', 'flowchart', 'graph']):
                cleaned_lines.append(stripped)
            else:
                # Regular lines get minimal indent
                cleaned_lines.append('    ' + stripped if cleaned_lines and not cleaned_lines[-1].startswith(('flowchart', 'graph', 'sequenceDiagram')) else stripped)
        else:
            cleaned_lines.append('')

    fixed = '\n'.join(cleaned_lines)

    # Remove trailing/leading whitespace
    fixed = fixed.strip()

    if fixed != original:
        corrections.append("Cleaned up formatting and whitespace")

    return fixed, corrections

def validate_basic_structure(code: str) -> List[str]:
    """Basic structural validation."""
    errors = []

    # Check for unmatched subgraphs
    subgraph_count = len(re.findall(r'\bsubgraph\b', code, re.IGNORECASE))
    end_count = len(re.findall(r'^\s*end\s*$', code, re.MULTILINE))

    if subgraph_count > end_count:
        errors.append(f"Unmatched subgraph declarations: {subgraph_count - end_count} missing 'end' statement(s)")
    elif subgraph_count < end_count:
        errors.append(f"Too many 'end' statements: {end_count - subgraph_count} extra")

    return errors

def check_potential_issues(code: str) -> List[str]:
    """Check for potential rendering issues."""
    warnings = []

    # Check for very long lines
    for i, line in enumerate(code.split('\n'), 1):
        if len(line) > 200:
            warnings.append(f"Line {i} is very long ({len(line)} chars) - may cause rendering issues")

    # Check for potentially problematic node IDs
    problematic = ['end', 'start', 'subgraph', 'graph', 'flowchart']
    for word in problematic:
        if re.search(rf'\b{word}\b(?!\s+(TD|LR|TB|RL))', code, re.IGNORECASE):
            # Only warn if it's not a diagram type declaration
            first_line = code.strip().split('\n')[0]
            if word.lower() not in first_line.lower():
                warnings.append(f"'{word}' might conflict with Mermaid keywords")

    return warnings
