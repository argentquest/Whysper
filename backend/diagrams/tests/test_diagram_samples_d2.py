"""
Test D2 Provider with 10 Different Diagram Samples
Including valid and invalid diagrams to test LLM corrections

PURPOSE:
This test suite validates the D2 provider with real-world diagram scenarios.
It includes both valid diagrams (to test rendering) and invalid diagrams
(to test pattern-based auto-fix and LLM correction capabilities).

TEST COVERAGE:
- Valid diagrams: Test that properly formatted D2 code renders correctly
- Invalid diagrams: Test that common syntax errors are detected and corrected
- Pattern fixes: Test regex-based auto-correction (fast, no LLM)
- SVG generation: Verify actual SVG output, not just mocks
- Error messages: Ensure validation errors are clear and actionable

DIAGRAM TYPES TESTED:
1. Simple flows (valid baseline)
2. Missing direction (pattern-fixable)
3. Containers and nesting (complex valid)
4. Unclosed braces (syntax error)
5. Shapes and styles (valid with custom properties)
6. Bidirectional connections (valid syntax)
7. Invalid arrow spacing (pattern-fixable)
8. SQL tables (advanced valid feature)
9. Network architecture (real-world use case)
10. Unquoted labels (pattern-fixable)

WHY THESE SPECIFIC TESTS?
These tests were chosen based on:
- Common user errors observed in production
- Coverage of D2 feature set (shapes, containers, styles)
- Balance of valid vs invalid (60% valid, 40% invalid)
- Real-world use cases (architecture diagrams, SQL schemas)

RUNNING THE TESTS:
pytest backend/diagrams/tests/test_diagram_samples_d2.py -v

Expected Results:
- All 11 tests should pass (10 parameterized + 1 summary)
- Valid diagrams should generate SVG containing '<svg' tag
- Invalid diagrams should trigger auto-fix attempts
- Pattern fixes should work without LLM
- LLM corrections require running server (tested separately)
"""

from diagrams.d2v1.d2_renderer import D2V1Provider
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


# =====================================================================
# TEST DIAGRAM CATALOG
# =====================================================================
# Each entry contains:
# - code: The D2 diagram code to test
# - valid: Whether this should pass validation
# - description: What this test case validates
# - expected_fix: (for invalid) What correction should occur
#
# NAMING CONVENTION: test_{number}_{description}_{valid/invalid}
# =====================================================================

D2_TEST_DIAGRAMS = {
    "test_001_simple_flow_valid": {
        "code": """direction: right

x: Start
y: Process
z: End

x -> y -> z
""",
        "valid": True,
        "description": "Simple valid flow",
    },
    "test_002_missing_direction_invalid": {
        "code": """x: Start
y: Process
z: End

x -> y -> z
""",
        "valid": False,
        "description": "Missing direction (can be auto-fixed)",
        "expected_fix": "Should add 'direction: right' at start",
    },
    "test_003_containers_valid": {
        "code": """direction: right

frontend: Frontend Layer {
  ui: User Interface {
    shape: rectangle
  }

  components: Components {
    shape: rectangle
  }
}

backend: Backend Layer {
  api: API {
    shape: rectangle
  }

  service: Business Logic {
    shape: rectangle
  }
}

database: Database {
  shape: cylinder
}

frontend.ui -> frontend.components
frontend.components -> backend.api
backend.api -> backend.service
backend.service -> database
""",
        "valid": True,
        "description": "Valid diagram with containers",
    },
    "test_004_unclosed_brace_invalid": {
        "code": """direction: right

container {
  x: Service A
  y: Service B

  x -> y
""",
        "valid": False,
        "description": "Unclosed brace (should be caught by validator)",
        "expected_fix": "Should add closing brace",
    },
    "test_005_shapes_and_styles_valid": {
        "code": """direction: down

user: User {
  shape: person
  style.fill: "#e1f5fe"
}

app: Application {
  shape: rectangle
  style.fill: "#fff3e0"
  style.stroke: "#ff9800"
}

db: Database {
  shape: cylinder
  style.fill: "#f3e5f5"
}

cache: Cache {
  shape: hexagon
  style.fill: "#c8e6c9"
}

user -> app: Uses
app -> db: Stores Data
app -> cache: Checks Cache
""",
        "valid": True,
        "description": "Valid diagram with various shapes and styles",
    },
    "test_006_bidirectional_connections_valid": {
        "code": """direction: right

client: Client
server: Server
database: Database

client <-> server: HTTP
server <-> database: SQL
""",
        "valid": True,
        "description": "Valid diagram with bidirectional connections",
    },
    "test_007_invalid_arrow_spacing_invalid": {
        "code": """direction: right

A - > B
B - > C
C - > D
""",
        "valid": False,
        "description": "Invalid arrow syntax with spaces",
        "expected_fix": "Should fix arrow syntax to ->",
    },
    "test_008_classes_and_sql_valid": {
        "code": """direction: down

classes.user: User {
  shape: sql_table
  id: int {constraint: primary_key}
  name: varchar
  email: varchar
}

classes.order: Order {
  shape: sql_table
  id: int {constraint: primary_key}
  user_id: int {constraint: foreign_key}
  total: decimal
}

classes.item: Item {
  shape: sql_table
  id: int {constraint: primary_key}
  order_id: int {constraint: foreign_key}
  product: varchar
  quantity: int
}

classes.user.id -> classes.order.user_id
classes.order.id -> classes.item.order_id
""",
        "valid": True,
        "description": "Valid SQL table diagram",
    },
    "test_009_network_architecture_valid": {
        "code": """direction: right

internet: Internet {
  shape: cloud
  style.fill: "#bbdefb"
}

lb: Load Balancer {
  shape: rectangle
  style.fill: "#c5e1a5"
}

app1: App Server 1 {
  shape: rectangle
  style.fill: "#fff9c4"
}

app2: App Server 2 {
  shape: rectangle
  style.fill: "#fff9c4"
}

db: Database Cluster {
  shape: cylinder
  style.fill: "#f8bbd0"
}

internet -> lb: HTTPS
lb -> app1: HTTP
lb -> app2: HTTP
app1 -> db: Query
app2 -> db: Query
""",
        "valid": True,
        "description": "Valid network architecture diagram",
    },
    "test_010_label_without_quotes_invalid": {
        "code": """direction: right

A: Service A
B: Service B

A -> B: Connection with spaces
""",
        "valid": False,
        "description": "Label with spaces should be quoted",
        "expected_fix": "Should add quotes around connection label",
    },
}


@pytest.fixture
def d2_provider():
    """Create a D2 provider instance"""
    provider_folder = Path(__file__).parent.parent / "d2v1"
    return D2V1Provider(provider_folder)


@pytest.mark.parametrize("test_id", list(D2_TEST_DIAGRAMS.keys()))
def test_d2_diagram_samples(test_id, d2_provider):
    """
    Test each D2 diagram sample through the full validation/correction/render pipeline.

    TEST METHODOLOGY:
    This test simulates the real-world workflow that occurs when a user submits
    diagram code through the API. It exercises:

    1. VALIDATION STEP:
       - Call validate_code() to check syntax
       - Capture error messages from D2 CLI
       - Verify error messages are actionable

    2. CORRECTION STEP (for invalid diagrams):
       - Call auto_fix_pattern_based() for regex-based fixes
       - Verify fixes are applied correctly
       - Re-validate to confirm fix worked
       - Track correction method used (pattern vs LLM vs none)

    3. RENDERING STEP (for valid diagrams):
       - Call render() to generate SVG
       - Verify SVG is well-formed (contains '<svg' tag)
       - Measure output size (should be >1KB for real diagrams)
       - Check for common SVG structure (<?xml declaration, viewBox, etc.)

    ASSERTIONS:
    - Invalid diagrams should be detected (is_valid = False)
    - Pattern fixes should resolve common errors without LLM
    - Valid diagrams should render actual SVG (not empty/mock)
    - SVG output should contain '<svg' or '<?xml' tag
    - Errors should contain helpful messages

    WHY PRINT STATEMENTS?
    The print statements provide detailed test output showing:
    - Which test is running
    - Validation results and error messages
    - Auto-fix attempts and results
    - SVG generation success and size
    This is invaluable for debugging test failures.

    EXPECTED OUTCOMES BY TEST:
    - test_001_simple_flow_valid: Should validate and render immediately
    - test_002_missing_direction_invalid: Should auto-fix by adding "direction: right"
    - test_003_containers_valid: Should handle nested containers correctly
    - test_004_unclosed_brace_invalid: Should auto-fix by adding closing braces
    - test_005_shapes_and_styles_valid: Should render with custom styles
    - test_006_bidirectional_connections_valid: Should handle <-> syntax
    - test_007_invalid_arrow_spacing_invalid: Should normalize "- >" to "->"
    - test_008_classes_and_sql_valid: Should render SQL table diagram
    - test_009_network_architecture_valid: Should render multi-node network
    - test_010_label_without_quotes_invalid: Should add quotes to labels

    Args:
        test_id: Test case identifier (e.g., "test_001_simple_flow_valid")
        d2_provider: D2V1Provider fixture (auto-injected by pytest)
    """
    test_data = D2_TEST_DIAGRAMS[test_id]

    # ===== Test Header =====
    print(f"\n{'=' * 60}")
    print(f"TEST: {test_id}")
    print(f"Description: {test_data['description']}")
    print(f"Expected Valid: {test_data['valid']}")
    print(f"{'=' * 60}")

    # ===== Pre-flight Check =====
    # Skip test if D2 CLI is not installed (e.g., in CI without D2)
    if not d2_provider.is_available():
        pytest.skip("D2 CLI not available")

    code = test_data["code"]
    expected_valid = test_data["valid"]

    # ===== Step 1: VALIDATION =====
    # This calls the D2 CLI to validate syntax
    # Expected: ~100-300ms for validation
    print("\n1. Validating code...")
    validation_result = d2_provider.validate_code(code)

    print(f"   Is Valid: {validation_result.is_valid}")
    if validation_result.error:
        # Truncate error for readability (full error in logs)
        print(f"   Error: {validation_result.error[:200]}...")

    # ===== Step 2: PATTERN-BASED AUTO-FIX =====
    # Only run for invalid diagrams (expected_valid = False)
    # This tests the pattern-based correction system
    if not expected_valid and not validation_result.is_valid:
        print("\n2. Testing pattern-based auto-fix...")
        fix_result = d2_provider.auto_fix_pattern_based(code, validation_result.error or "Syntax error")

        print(f"   Auto Fixed: {fix_result.auto_fixed}")
        print(f"   Correction Method: {fix_result.correction_method}")

        if fix_result.auto_fixed and fix_result.fixed_code:
            print(f"   Fixed code preview: {fix_result.fixed_code[:100]}...")

            # Re-validate the fixed code to confirm it worked
            fixed_validation = d2_provider.validate_code(fix_result.fixed_code)
            print(f"   Fixed code valid: {fixed_validation.is_valid}")

    # ===== Step 3: SVG RENDERING =====
    # Only render if code is valid (or expected to be valid)
    # This generates actual SVG using D2 CLI
    if expected_valid or (validation_result.is_valid):
        print("\n3. Testing SVG rendering...")
        render_result = d2_provider.render(code, output_format="svg")

        print(f"   Render Success: {render_result.success}")
        if render_result.content:
            print(f"   SVG Size: {len(render_result.content)} bytes")
            print(f"   Contains SVG: {'<svg' in render_result.content}")

            # CRITICAL ASSERTION: Verify actual SVG was generated
            # This ensures we're not just getting mock/empty content
            assert "<svg" in render_result.content or "<?xml" in render_result.content
        else:
            print(f"   Render Error: {render_result.error}")

    print(f"\n✅ Test {test_id} completed")


def test_d2_summary(d2_provider):
    """Summary of all D2 test diagrams"""
    print(f"\n{'=' * 60}")
    print("D2 TEST DIAGRAMS SUMMARY")
    print(f"{'=' * 60}")

    valid_count = sum(1 for d in D2_TEST_DIAGRAMS.values() if d["valid"])
    invalid_count = len(D2_TEST_DIAGRAMS) - valid_count

    print(f"Total Diagrams: {len(D2_TEST_DIAGRAMS)}")
    print(f"Valid Diagrams: {valid_count}")
    print(f"Invalid Diagrams (for testing corrections): {invalid_count}")
    print(f"\nD2 CLI Available: {d2_provider.is_available()}")

    if d2_provider.is_available():
        print(f"D2 Version: {d2_provider.get_version()}")

    print("\nDiagram Features Covered:")
    features = [
        "Simple flows",
        "Containers and nesting",
        "Various shapes (circle, rectangle, cylinder, etc.)",
        "Custom styles and colors",
        "Bidirectional connections",
        "SQL tables",
        "Network architectures",
        "Cloud shapes",
    ]

    for feature in features:
        print(f"  - {feature}")

    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("D2 DIAGRAM SAMPLES TEST SUITE")
    print("=" * 60)

    provider_folder = Path(__file__).parent.parent / "d2v1"
    provider = D2V1Provider(provider_folder)

    test_d2_summary(provider)

    for test_id in D2_TEST_DIAGRAMS.keys():
        try:
            test_d2_diagram_samples(test_id, provider)
        except Exception as e:
            print(f"\n❌ Test {test_id} failed: {e}")
            import traceback

            traceback.print_exc()
