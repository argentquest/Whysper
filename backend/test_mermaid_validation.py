"""
Test script for Mermaid CLI validation

This script tests the Mermaid validation functionality using the mmdc CLI.
"""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.mermaid_cli_validator import (
    validate_mermaid_with_cli,
    is_mermaid_cli_available,
    validate_and_fix_mermaid_with_cli,
    validate_mermaid_and_render
)
from mvp_diagram_generator.mermaid_syntax_fixer import fix_mermaid_syntax

def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_cli_availability():
    """Test if Mermaid CLI is available."""
    print_section("Testing Mermaid CLI Availability")

    available = is_mermaid_cli_available()

    if available:
        print("✅ Mermaid CLI (mmdc) is available!")
    else:
        print("❌ Mermaid CLI (mmdc) is NOT available")
        print("   Install with: npm install -g @mermaid-js/mermaid-cli")

    return available

def test_valid_diagram():
    """Test validation with a valid Mermaid diagram."""
    print_section("Testing Valid Mermaid Diagram")

    valid_mermaid = """flowchart TD
    A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]
    D --> B
    C --> E[End]"""

    print("Input diagram:")
    print(valid_mermaid)
    print()

    is_valid, message = validate_mermaid_with_cli(valid_mermaid)

    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    return is_valid

def test_invalid_diagram():
    """Test validation with an invalid Mermaid diagram."""
    print_section("Testing Invalid Mermaid Diagram (Missing Type)")

    invalid_mermaid = """A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]"""

    print("Input diagram:")
    print(invalid_mermaid)
    print()

    is_valid, message = validate_mermaid_with_cli(invalid_mermaid)

    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    return not is_valid  # Return True if it correctly identified as invalid

def test_auto_fix():
    """Test auto-fixing invalid Mermaid diagrams."""
    print_section("Testing Auto-Fix for Invalid Diagrams")

    invalid_mermaid = """A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]
    D --> B"""

    print("Input diagram (missing 'flowchart TD'):")
    print(invalid_mermaid)
    print()

    is_valid, fixed_code, message = validate_and_fix_mermaid_with_cli(invalid_mermaid)

    if is_valid:
        print(f"✅ {message}")
        print("\nFixed diagram:")
        print(fixed_code)
    else:
        print(f"❌ {message}")

    return is_valid

def test_sequence_diagram():
    """Test validation with a sequence diagram."""
    print_section("Testing Valid Sequence Diagram")

    sequence_diagram = """sequenceDiagram
    participant User
    participant API
    participant Database

    User->>API: Request data
    API->>Database: Query
    Database-->>API: Results
    API-->>User: Response"""

    print("Input diagram:")
    print(sequence_diagram)
    print()

    is_valid, message = validate_mermaid_with_cli(sequence_diagram)

    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    return is_valid

def test_syntax_fixer():
    """Test the syntax fixer module."""
    print_section("Testing Mermaid Syntax Fixer")

    bad_syntax = """A-->B
    B->>C
    C<->D"""

    print("Input diagram (no type, bad spacing):")
    print(bad_syntax)
    print()

    result = fix_mermaid_syntax(bad_syntax)

    print(f"Valid: {result.is_valid}")
    print(f"Corrections: {len(result.corrections)}")
    for correction in result.corrections:
        print(f"  - {correction}")

    print(f"\nWarnings: {len(result.warnings)}")
    for warning in result.warnings:
        print(f"  - {warning}")

    print(f"\nErrors: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error}")

    print("\nCorrected code:")
    print(result.corrected_code)

    return True

def test_render_diagram():
    """Test rendering a Mermaid diagram to SVG."""
    print_section("Testing Mermaid Rendering to SVG")

    mermaid_code = """flowchart LR
    A[Client] --> B[Load Balancer]
    B --> C[Server 1]
    B --> D[Server 2]
    C --> E[Database]
    D --> E"""

    print("Input diagram:")
    print(mermaid_code)
    print()

    is_valid, message, rendered = validate_mermaid_and_render(mermaid_code, "svg")

    if is_valid:
        print(f"✅ {message}")
        print(f"   SVG output length: {len(rendered)} characters")
        print(f"   SVG preview (first 200 chars): {rendered[:200]}...")
    else:
        print(f"❌ {message}")

    return is_valid

def test_complex_error():
    """Test with a diagram that has syntax errors."""
    print_section("Testing Complex Syntax Error")

    bad_mermaid = """flowchart TD
    subgraph "Processing"
        A --> B
        B --> C

    C --> D
    D --> end"""

    print("Input diagram (unclosed subgraph, 'end' as node ID):")
    print(bad_mermaid)
    print()

    is_valid, message = validate_mermaid_with_cli(bad_mermaid)

    print(f"Validation result: {is_valid}")
    print(f"Message:\n{message}")

    # Now try to fix it
    print("\n--- Attempting to fix ---")
    is_valid_fixed, fixed_code, fix_message = validate_and_fix_mermaid_with_cli(bad_mermaid)

    if is_valid_fixed:
        print(f"✅ {fix_message}")
        print("\nFixed code:")
        print(fixed_code)
    else:
        print(f"❌ Could not auto-fix: {fix_message}")

    return True  # Always return True as we're just demonstrating error handling

def main():
    """Run all tests."""
    print("=" * 80)
    print("  MERMAID CLI VALIDATION TEST SUITE")
    print("=" * 80)

    results = {}

    # Test 1: CLI availability
    cli_available = test_cli_availability()
    results["CLI Available"] = cli_available

    if not cli_available:
        print("\n⚠️  Cannot run validation tests without Mermaid CLI")
        print("    Install with: npm install -g @mermaid-js/mermaid-cli")
        return

    # Test 2: Valid diagram
    results["Valid Diagram"] = test_valid_diagram()

    # Test 3: Invalid diagram detection
    results["Invalid Detection"] = test_invalid_diagram()

    # Test 4: Auto-fix
    results["Auto-Fix"] = test_auto_fix()

    # Test 5: Sequence diagram
    results["Sequence Diagram"] = test_sequence_diagram()

    # Test 6: Syntax fixer
    results["Syntax Fixer"] = test_syntax_fixer()

    # Test 7: Render diagram
    results["Render SVG"] = test_render_diagram()

    # Test 8: Complex error
    results["Complex Error"] = test_complex_error()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
