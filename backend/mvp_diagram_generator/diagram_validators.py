```python
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
from .d2_syntax_fixer import fix_d2_syntax
from .d2_cli_validator import validate_d2_with_cli, is_d2_cli_available
from .mermaid_cli_validator import validate_mermaid_with_cli, is_mermaid_cli_available
from .mermaid_syntax_fixer import fix_mermaid_syntax

# Define keywords for detecting different diagram types
# These keywords help quickly identify the type of diagram syntax
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

# Define keywords for C4 model diagrams
# Used to detect different levels of architectural diagrams
C4_KEYWORDS = [
    "C4Context",        # Context level - shows system boundaries
    "C4Container",      # Container level - shows containers/applications
    "C4Component",      # Component level - shows components within containers
    "C4Dynamic",        # Dynamic diagrams - show runtime interactions
    "C4Deployment",     # Deployment diagrams - show infrastructure
]

# Define regex patterns to detect D2 diagram syntax
# These patterns help identify common D2 language constructs
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
    # Validate input: ensure it's a non-empty string
    if not code or not isinstance(code, str):
        return False

    # Remove whitespace to check for empty content
    trimmed = code.strip()
    if not trimmed:
        return False

    # Attempt validation using Mermaid CLI if available
    # CLI provides the most reliable validation method
    if is_mermaid_cli_available():
        # First try direct CLI validation
        is_valid, _ = validate_mermaid_with_cli(trimmed)
        if is_valid:
            return True

        # If CLI validation fails, try to fix and validate again
        from .mermaid_cli_validator import validate_and_fix_mermaid_with_cli
        is_valid, fixed_code, _ = validate_and_fix_mermaid_with_cli(trimmed)
        return is_valid

    # Fallback to pattern-based validation if CLI is not available
    # Use syntax fixer to attempt repairing the diagram
    result = fix_mermaid_syntax(trimmed)
    return result.is_valid

def is_valid_d2_diagram(code: str) -> bool:
    # Validate input: ensure it's a non-empty string
    if not code or not isinstance(code, str):
        return False

    # Remove whitespace to check for empty content
    trimmed = code.strip()
    if not trimmed:
        return False

    # Attempt validation using D2 CLI if available
    # CLI provides the most reliable validation method
    if is_d2_cli_available():
        # First try direct CLI validation
        is_valid, _ = validate_d2_with_cli(trimmed)
        if is_valid:
            return True
        
        # If CLI validation fails, try to fix and validate again
        from .d2_cli_validator import validate_and_fix_d2_with_cli
        is_valid, fixed_code, _ = validate_and_fix_d2_with_cli(trimmed)
        return is_valid
    
    # Fallback to pattern-based validation if CLI is not available
    # Use syntax fixer to attempt repairing the diagram
    result = fix_d2_syntax(trimmed)
    return result.is_valid

def is_valid_c4_diagram(code: str) -> bool:
    # Validate input: ensure it's a non-empty string
    if not code or not isinstance(code, str):
        return False

    # Check for C4 keywords that indicate valid C4 diagram syntax
    # This is a simple pattern-based detection method
    if any(
        re.search(rf"\b{keyword}\b", code)
        for keyword in C4_KEYWORDS
    ):
        return True

    # Define additional PlantUML C4 functions to validate
    # These functions are commonly used in C4 model diagrams
    c4_functions = [
        "Person", "System", "Container", "Component",
        "Rel", "RelU", "RelBack", "RelLeft", "RelRight", "RelUp", "RelDown",
        "System_Boundary", "Container_Boundary", "Component_Boundary"
    ]

    # Check if any C4 functions are present in the code
    return any(
        re.search(rf"\b{func}\s*\(", code)
        for func in c4_functions
    )
```

I've added inline comments that explain:
- The purpose of different code sections
- The logic behind validation methods
- What different checks are doing
- Why certain approaches are used

The comments focus on explaining the WHAT and WHY of the code's logic, keeping the original code exactly the same.