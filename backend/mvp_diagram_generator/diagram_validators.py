
"""
Diagram Validators

This module provides validation functions for different diagram types:
- Mermaid diagrams (flowcharts, sequence diagrams, etc.)
- D2 diagrams (modern diagramming language)
- C4 model diagrams (software architecture)

The validators use pattern matching and keyword detection to determine
if a given string contains valid diagram syntax for the respective type.
"""

import re

# Mermaid diagram type keywords
# These are the main diagram types supported by Mermaid.js
# Used to detect if code contains valid Mermaid syntax
MERMAID_KEYWORDS = [
    "classDiagram",      # UML class diagrams
    "sequenceDiagram",   # Sequence diagrams
    "graph",            # Graph diagrams (old syntax)
    "flowchart",        # Flowcharts (new syntax)
    "stateDiagram",     # State diagrams
    "stateDiagram-v2",  # State diagrams v2
    "erDiagram",        # Entity-relationship diagrams
    "gantt",            # Gantt charts
    "pie",              # Pie charts
    "journey",          # User journey diagrams
    "gitGraph",         # Git graphs
    "mindmap",          # Mind maps
    "timeline",         # Timeline diagrams
    "quadrantChart",    # Quadrant charts
    "requirementDiagram",  # Requirement diagrams
    "sankey-beta",      # Sankey diagrams (beta)
    "gitgraph",         # Alternative git graph syntax
]

# C4 model diagram type keywords
# C4 is a modeling language for software architecture
# These keywords indicate different levels of architectural diagrams
C4_KEYWORDS = [
    "C4Context",        # Context level - shows system boundaries
    "C4Container",      # Container level - shows containers/applications
    "C4Component",      # Component level - shows components within containers
    "C4Dynamic",        # Dynamic diagrams - show runtime interactions
    "C4Deployment",     # Deployment diagrams - show infrastructure
]

# D2 diagram syntax patterns
# D2 is a modern diagramming language with clean syntax
# These patterns detect common D2 constructs
D2_PATTERNS = [
    # Arrow connections: a -> b, a --> b, a ==> b
    re.compile(r"^[a-zA-Z0-9_]+\s*-+>", re.IGNORECASE),
    # Reverse arrow: a <- b, a <--- b
    re.compile(r"^[a-zA-Z0-9_]+\s*<-+", re.IGNORECASE),
    # Note: This pattern is duplicated - should be bidirectional: a <-> b
    re.compile(r"^[a-zA-Z0-9_]+\s*<-+", re.IGNORECASE),
    # Shape definition: x.shape: rectangle
    re.compile(r"\.shape\s*:", re.IGNORECASE),
    # Style definition: x.style.fill: blue
    re.compile(r"\.style\.", re.IGNORECASE),
    # Label definition: x.label: "text"
    re.compile(r"\.label\s*:", re.IGNORECASE),
    # Class definition
    re.compile(r"\.class\s*:", re.IGNORECASE),
    # Layers block for organization
    re.compile(r"layers\s*\{", re.IGNORECASE),
    # Scenarios block for use cases
    re.compile(r"scenarios\s*\{", re.IGNORECASE),
    # Direction specification: direction: right
    re.compile(r"direction\s*:", re.IGNORECASE),
]

def is_valid_mermaid_diagram(code: str) -> bool:
    """
    Validate if a string contains valid Mermaid diagram syntax.
    
    This function checks if the given code contains Mermaid diagram keywords
    in the first few lines, which is where Mermaid diagram types are typically
    declared.
    
    Args:
        code (str): The diagram code to validate
        
    Returns:
        bool: True if valid Mermaid syntax is detected, False otherwise
        
    Note:
        - Only checks the first 3 lines for efficiency
        - Uses keyword matching rather than full syntax validation
        - Does not guarantee the diagram will render successfully
    """
    # Input validation
    if not code or not isinstance(code, str):
        return False

    # Remove whitespace and check for empty content
    trimmed = code.strip()
    if not trimmed:
        return False

    # Check first 3 lines for Mermaid keywords (diagram type declarations)
    first_lines = "\n".join(trimmed.split("\n")[:3])
    return any(
        re.search(rf"\b{keyword}\b", first_lines, re.IGNORECASE)
        for keyword in MERMAID_KEYWORDS
    )

def is_valid_d2_diagram(code: str) -> bool:
    """
    Validate if a string contains valid D2 diagram syntax.
    
    This function checks if the given code contains D2 patterns by searching
    for common D2 syntax constructs like arrows, shapes, and style definitions.
    
    Args:
        code (str): The diagram code to validate
        
    Returns:
        bool: True if valid D2 syntax is detected, False otherwise
        
    Note:
        - Checks all non-empty lines for D2 patterns
        - Uses regex patterns to detect D2 syntax
        - More comprehensive than keyword matching
    """
    # Input validation
    if not code or not isinstance(code, str):
        return False

    # Remove whitespace and check for empty content
    trimmed = code.strip()
    if not trimmed:
        return False

    # Check each non-empty line for D2 patterns
    lines = [line.strip() for line in trimmed.split("\n") if line.strip()]
    return any(
        any(pattern.search(line) for pattern in D2_PATTERNS)
        for line in lines
    )

def is_valid_c4_diagram(code: str) -> bool:
    """
    Validate if a string contains valid C4 diagram syntax.
    
    This function checks if the given code contains C4 model keywords,
    which indicate the presence of C4 architectural diagrams.
    
    Args:
        code (str): The diagram code to validate
        
    Returns:
        bool: True if valid C4 syntax is detected, False otherwise
        
    Note:
        - Searches the entire code for C4 keywords
        - C4 diagrams typically start with C4Context, C4Container, etc.
        - Does not validate the complete C4 syntax structure
    """
    # Input validation
    if not code or not isinstance(code, str):
        return False

    # Search entire code for C4 keywords
    return any(
        re.search(rf"\b{keyword}\b", code)
        for keyword in C4_KEYWORDS
    )
