"""
D2 Syntax Fixer for Backend

This module provides comprehensive D2 syntax validation and auto-correction
for the backend diagram generation system. It fixes common syntax errors
that cause D2 compilation failures.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class D2SyntaxFixResult:
    """Result of D2 syntax fixing operation"""
    def __init__(self, is_valid: bool, corrected_code: str, errors: List[str], corrections: List[str]):
        self.is_valid = is_valid
        self.corrected_code = corrected_code
        self.errors = errors
        self.corrections = corrections

def fix_d2_syntax(code: str) -> D2SyntaxFixResult:
    """
    Validates and corrects D2 syntax issues
    
    Args:
        code (str): The D2 diagram code to validate and fix
        
    Returns:
        D2SyntaxFixResult: Result containing validation status, corrected code, and messages
    """
    errors: List[str] = []
    corrections: List[str] = []
    corrected_code = code

    logger.debug(f"[D2 FIXER] Original code: {code}")

    # Fix 1: Convert JSON-style object syntax to proper D2 syntax
    # Pattern: name: { shape: circle, label: "text" } -> name: "text" { shape: circle }
    object_pattern = re.compile(r'(\w+):\s*\{\s*shape:\s*(\w+)[^}]*label:\s*"([^"]+)"[^}]*\}', re.MULTILINE)
    matches = object_pattern.findall(corrected_code)
    if matches:
        for name, shape, label in matches:
            corrections.append(f"Fixed object syntax for {name}: converted JSON-style to D2 syntax")
        
        def replace_object(match):
            name, shape, label = match.groups()
            return f'{name}: "{label}" {{\n  shape: {shape}'
        
        corrected_code = object_pattern.sub(replace_object, corrected_code)

    # Fix 2: Convert nested style objects to dot notation
    # Pattern: style: { fill: "#color" } -> style.fill: "#color"
    style_pattern = re.compile(r'style:\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)
    matches = style_pattern.findall(corrected_code)
    if matches:
        for style_content in matches:
            style_lines = style_content.split(',').map(lambda line: line.strip())
            fixed_styles = []
            for line in style_lines:
                if ':' in line:
                    prop, value = line.split(':', 1)
                    prop = prop.strip()
                    value = value.strip()
                    if prop and value:
                        fixed_styles.append(f'  style.{prop}: {value}')
            
            corrections.append('Fixed nested style object to dot notation')
            
            def replace_style(match):
                return '\n'.join(fixed_styles)
            
            corrected_code = style_pattern.sub(replace_style, corrected_code)

    # Fix 3: Ensure proper brace matching
    open_braces = corrected_code.count('{')
    close_braces = corrected_code.count('}')
    
    if open_braces > close_braces:
        missing_braces = open_braces - close_braces
        corrected_code += '\n}' * missing_braces
        corrections.append(f'Added {missing_braces} missing closing brace(s)')
    elif close_braces > open_braces:
        errors.append(f'Too many closing braces: {close_braces - open_braces} extra brace(s)')

    # Fix 4: Convert invalid arrow syntax
    # Pattern: A - > B -> A -> B
    if re.search(r'\s*-\s*>\s*', corrected_code):
        corrected_code = re.sub(r'\s*-\s*>\s*', ' -> ', corrected_code)
        corrections.append('Fixed arrow syntax (removed spaces around arrow)')

    # Fix 5: Ensure proper label syntax for connections
    # Pattern: A -> B: "label" -> A -> B: "label" (already correct, but validate quotes)
    connection_pattern = re.compile(r'(\w+)\s*->\s*(\w+):\s*"?([^"]+)"?', re.MULTILINE)
    
    def fix_connection(match):
        from_node, to_node, label = match.groups()
        if '"' not in label:
            corrections.append(f'Added quotes to connection label: {label}')
            return f'{from_node} -> {to_node}: "{label}"'
        return match.group(0)
    
    corrected_code = connection_pattern.sub(fix_connection, corrected_code)

    # Fix 6: Handle unterminated connection labels (main issue from the error)
    # Pattern: A -> B: "text without closing quote
    lines = corrected_code.split('\n')
    fixed_lines = []
    in_connection_label = False
    current_connection = ''
    
    for i, line in enumerate(lines):
        line = line.rstrip()
        
        # Check if this line starts a connection label
        connection_match = re.match(r'^(\w+)\s*->\s*(\w+):\s*"([^"]*)$', line)
        if connection_match:
            in_connection_label = True
            current_connection = line
            continue
        
        # Check if this line continues an unterminated label
        if in_connection_label:
            # Check if this line ends a connection
            end_connection_match = re.match(r'^([^"]+)"\s*$', line)
            if end_connection_match:
                # Complete the connection with this line
                parts = current_connection.split('->')
                if len(parts) >= 2:
                    from_part = parts[0].strip()
                    to_parts = ' -> '.join(parts[1:]).split(':')
                    if len(to_parts) >= 2:
                        to_part = to_parts[0].strip()
                        label_part = ':'.join(to_parts[1:]).strip().strip('"')
                        label = (label_part + ' ' + end_connection_match.group(1)).strip()
                        fixed_lines.append(f'{from_part} -> {to_part}: "{label}"')
                        corrections.append('Fixed multi-line connection label')
                        in_connection_label = False
                        current_connection = ''
                        continue
            
            # Check if this line is a new connection (missing closing quote on previous)
            new_connection_match = re.match(r'^(\w+)\s*->\s*(\w+):\s*(.+)$', line)
            if new_connection_match:
                # Close the previous connection and start a new one
                parts = current_connection.split('->')
                if len(parts) >= 2:
                    from_part = parts[0].strip()
                    to_parts = ' -> '.join(parts[1:]).split(':')
                    if len(to_parts) >= 2:
                        to_part = to_parts[0].strip()
                        label_part = ':'.join(to_parts[1:]).strip().strip('"')
                        label = label_part.strip()
                        fixed_lines.append(f'{from_part} -> {to_part}: "{label}"')
                        corrections.append('Fixed unterminated connection label before new connection')
                
                # Handle the new connection
                if '"' in new_connection_match.group(3):
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(f'{new_connection_match.group(1)} -> {new_connection_match.group(2)}: "{new_connection_match.group(3)}"')
                    corrections.append('Added quotes to connection label')
                in_connection_label = False
                current_connection = ''
                continue
            
            # This is part of the label, add it to current connection
            current_connection += ' ' + line
            continue
        
        # Regular line, just add it
        fixed_lines.append(line)
    
    # Handle any remaining unterminated connection
    if in_connection_label and current_connection:
        parts = current_connection.split('->')
        if len(parts) >= 2:
            from_part = parts[0].strip()
            to_parts = ' -> '.join(parts[1:]).split(':')
            if len(to_parts) >= 2:
                to_part = to_parts[0].strip()
                label_part = ':'.join(to_parts[1:]).strip().strip('"')
                label = label_part.strip()
                fixed_lines.append(f'{from_part} -> {to_part}: "{label}"')
                corrections.append('Fixed unterminated connection label at end of file')
    
    corrected_code = '\n'.join(fixed_lines)

    # Fix 7: Remove invalid property syntax
    # Pattern: property: value without proper context
    invalid_property_pattern = re.compile(r'^\s*(\w+):\s*([^{}\n]+)\s*$', re.MULTILINE)
    
    def remove_invalid_property(match):
        prop, value = match.groups()
        # Skip if this looks like a valid connection or object definition
        if '->' in value or '"' in value or prop == 'direction':
            return match.group(0)
        
        corrections.append(f'Removed invalid property: {prop}: {value}')
        return f'# Invalid property removed: {prop}: {value}'
    
    corrected_code = invalid_property_pattern.sub(remove_invalid_property, corrected_code)

    # Fix 8: Ensure proper direction syntax
    if 'direction:' not in corrected_code and '->' in corrected_code:
        corrected_code = 'direction: right\n\n' + corrected_code
        corrections.append('Added default direction: right')

    # Final validation
    validation_errors = validate_d2_structure(corrected_code)
    errors.extend(validation_errors)

    is_valid = len(errors) == 0

    logger.debug(f"[D2 FIXER] Corrections made: {corrections}")
    logger.debug(f"[D2 FIXER] Errors found: {errors}")
    logger.debug(f"[D2 FIXER] Corrected code: {corrected_code}")

    return D2SyntaxFixResult(is_valid, corrected_code, errors, corrections)

def validate_d2_structure(code: str) -> List[str]:
    """
    Basic structural validation for D2 code
    
    Args:
        code (str): The D2 code to validate
        
    Returns:
        List[str]: List of validation errors
    """
    errors: List[str] = []
    lines = code.split('\n')

    # Check for unmatched braces again (final verification)
    brace_stack = 0
    for i, line in enumerate(lines):
        open_count = line.count('{')
        close_count = line.count('}')
        
        brace_stack += open_count - close_count
        
        if brace_stack < 0:
            errors.append(f'Line {i + 1}: Too many closing braces')
            brace_stack = 0
    
    if brace_stack > 0:
        errors.append(f'Unmatched opening braces: {brace_stack} braces not closed')

    # Check for invalid object definitions
    object_def_pattern = re.compile(r'^(\w+):\s*"([^"]*)"\s*\{')
    for i, line in enumerate(lines):
        line = line.strip()
        if ':' in line and not object_def_pattern.match(line) and \
           '->' not in line and not line.startswith('#') and \
           not line.startswith('direction:') and '.' not in line:
            # This might be an invalid object definition
            if '{' not in line and not line.startswith('style.'):
                errors.append(f'Line {i + 1}: Invalid object definition: {line}')

    return errors

def looks_like_valid_d2(code: str) -> bool:
    """
    Quick validation to check if D2 code looks reasonable
    
    Args:
        code (str): The D2 code to check
        
    Returns:
        bool: True if the code looks like valid D2
    """
    if not code or not isinstance(code, str):
        return False

    trimmed = code.strip()
    if not trimmed:
        return False

    # Look for D2-specific patterns
    d2_patterns = [
        re.compile(r'\w+\s*->\s*\w+'),  # Connections
        re.compile(r'direction:\s*\w+'),  # Direction
        re.compile(r'\w+:\s*"[^"]+"\s*\{'),  # Object definitions
        re.compile(r'style\.\w+:'),  # Style properties
    ]

    return any(pattern.search(trimmed) for pattern in d2_patterns)