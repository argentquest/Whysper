"""
Test Mermaid Provider with 10 Different Diagram Samples
Including valid and invalid diagrams to test LLM corrections
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.mermaidv1.mermaid_renderer import MermaidV1Provider
from diagrams.llm_correction_service import get_llm_correction_service


# Test Diagrams - Mix of valid and invalid
MERMAID_TEST_DIAGRAMS = {
    "test_001_simple_flowchart_valid": {
        "code": """flowchart TD
    Start[Start] --> Process[Process Data]
    Process --> Decision{Is Valid?}
    Decision -->|Yes| Success[Success]
    Decision -->|No| Error[Error]
    Success --> End[End]
    Error --> End
""",
        "valid": True,
        "description": "Simple valid flowchart"
    },

    "test_002_flowchart_wrong_arrows_invalid": {
        "code": """flowchart TD
    A[Start] -> B[Process]
    B -> C{Decision}
    C -> D[End]
""",
        "valid": False,
        "description": "Flowchart with wrong arrow syntax (should be -->)",
        "expected_fix": "auto_fix should convert -> to -->"
    },

    "test_003_sequence_diagram_valid": {
        "code": """sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Login Request
    Frontend->>Backend: Authenticate
    Backend->>Database: Query User
    Database-->>Backend: User Data
    Backend-->>Frontend: Token
    Frontend-->>User: Success
""",
        "valid": True,
        "description": "Valid sequence diagram"
    },

    "test_004_sequence_missing_diagram_type_invalid": {
        "code": """participant User
    participant System

    User->>System: Request
    System-->>User: Response
""",
        "valid": False,
        "description": "Missing diagram type declaration",
        "expected_fix": "Should add 'sequenceDiagram' at the start"
    },

    "test_005_class_diagram_valid": {
        "code": """classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }

    class Dog {
        +String breed
        +bark()
    }

    class Cat {
        +String color
        +meow()
    }

    Animal <|-- Dog
    Animal <|-- Cat
""",
        "valid": True,
        "description": "Valid class diagram"
    },

    "test_006_state_diagram_valid": {
        "code": """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start
    Processing --> Success: Complete
    Processing --> Failed: Error
    Success --> [*]
    Failed --> Idle: Retry
    Failed --> [*]: Give Up
""",
        "valid": True,
        "description": "Valid state diagram"
    },

    "test_007_flowchart_missing_node_labels_invalid": {
        "code": """flowchart LR
    A --> B
    B --> C
    C --> D
""",
        "valid": False,
        "description": "Nodes without labels (technically valid but poor practice)",
        "expected_fix": "LLM might suggest adding descriptive labels"
    },

    "test_008_er_diagram_valid": {
        "code": """erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses

    CUSTOMER {
        string name
        string email
        string phone
    }

    ORDER {
        int orderID
        date orderDate
        string status
    }

    LINE-ITEM {
        int quantity
        decimal price
    }
""",
        "valid": True,
        "description": "Valid ER diagram"
    },

    "test_009_gantt_chart_valid": {
        "code": """gantt
    title Project Schedule
    dateFormat  YYYY-MM-DD
    section Planning
    Requirements      :a1, 2025-01-01, 7d
    Design           :a2, after a1, 5d
    section Development
    Backend          :b1, after a2, 14d
    Frontend         :b2, after a2, 14d
    section Testing
    Integration      :c1, after b1, 7d
    User Testing     :c2, after c1, 5d
""",
        "valid": True,
        "description": "Valid Gantt chart"
    },

    "test_010_pie_chart_syntax_error_invalid": {
        "code": """pie
    title Distribution
    "Category A" : 45
    "Category B" : 30
    "Category C" 25
""",
        "valid": False,
        "description": "Pie chart with missing colon",
        "expected_fix": "Should add colon before last number"
    }
}


@pytest.fixture
def mermaid_provider():
    """Create a Mermaid provider instance"""
    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    return MermaidV1Provider(provider_folder)


@pytest.mark.parametrize("test_id", list(MERMAID_TEST_DIAGRAMS.keys()))
def test_mermaid_diagram_samples(test_id, mermaid_provider):
    """Test each Mermaid diagram sample"""
    test_data = MERMAID_TEST_DIAGRAMS[test_id]

    print(f"\n{'='*60}")
    print(f"TEST: {test_id}")
    print(f"Description: {test_data['description']}")
    print(f"Expected Valid: {test_data['valid']}")
    print(f"{'='*60}")

    if not mermaid_provider.is_available():
        pytest.skip("Mermaid CLI not available")

    code = test_data["code"]
    expected_valid = test_data["valid"]

    # Step 1: Validate the code
    print(f"\n1. Validating code...")
    validation_result = mermaid_provider.validate_code(code)

    print(f"   Is Valid: {validation_result.is_valid}")
    if validation_result.error:
        print(f"   Error: {validation_result.error[:200]}...")

    # Step 2: For invalid diagrams, test auto-fix
    if not expected_valid and not validation_result.is_valid:
        print(f"\n2. Testing pattern-based auto-fix...")
        fix_result = mermaid_provider.auto_fix_pattern_based(
            code,
            validation_result.error or "Syntax error"
        )

        print(f"   Auto Fixed: {fix_result.auto_fixed}")
        print(f"   Correction Method: {fix_result.correction_method}")

        if fix_result.auto_fixed and fix_result.fixed_code:
            print(f"   Fixed code preview: {fix_result.fixed_code[:100]}...")

            # Validate the fixed code
            fixed_validation = mermaid_provider.validate_code(fix_result.fixed_code)
            print(f"   Fixed code valid: {fixed_validation.is_valid}")

    # Step 3: For valid diagrams, test rendering
    if expected_valid or (validation_result.is_valid):
        print(f"\n3. Testing SVG rendering...")
        render_result = mermaid_provider.render(code, output_format="svg")

        print(f"   Render Success: {render_result.success}")
        if render_result.content:
            print(f"   SVG Size: {len(render_result.content)} bytes")
            print(f"   Contains SVG: {'<svg' in render_result.content}")
            assert "<svg" in render_result.content
        else:
            print(f"   Render Error: {render_result.error}")

    print(f"\n✅ Test {test_id} completed")


def test_mermaid_summary(mermaid_provider):
    """Summary of all Mermaid test diagrams"""
    print(f"\n{'='*60}")
    print("MERMAID TEST DIAGRAMS SUMMARY")
    print(f"{'='*60}")

    valid_count = sum(1 for d in MERMAID_TEST_DIAGRAMS.values() if d["valid"])
    invalid_count = len(MERMAID_TEST_DIAGRAMS) - valid_count

    print(f"Total Diagrams: {len(MERMAID_TEST_DIAGRAMS)}")
    print(f"Valid Diagrams: {valid_count}")
    print(f"Invalid Diagrams (for testing corrections): {invalid_count}")
    print(f"\nMermaid CLI Available: {mermaid_provider.is_available()}")

    if mermaid_provider.is_available():
        print(f"Mermaid Version: {mermaid_provider.get_version()}")

    print(f"\nDiagram Types Covered:")
    types = set()
    for test_data in MERMAID_TEST_DIAGRAMS.values():
        # Extract diagram type from code
        first_line = test_data["code"].strip().split('\n')[0]
        types.add(first_line.split()[0])

    for t in sorted(types):
        print(f"  - {t}")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MERMAID DIAGRAM SAMPLES TEST SUITE")
    print("="*60)

    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    provider = MermaidV1Provider(provider_folder)

    test_mermaid_summary(provider)

    for test_id in MERMAID_TEST_DIAGRAMS.keys():
        try:
            test_mermaid_diagram_samples(test_id, provider)
        except Exception as e:
            print(f"\n❌ Test {test_id} failed: {e}")
            import traceback
            traceback.print_exc()
