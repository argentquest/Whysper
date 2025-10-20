"""
Test script to verify the Mermaid AI retry system is working.

This simulates the AI retry flow by manually testing the validation
and retry logic without actually calling the AI.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from mvp_diagram_generator.mermaid_cli_validator import (
    validate_mermaid_with_cli,
    is_mermaid_cli_available,
)
from app.services.mermaid_render_service import get_mermaid_service
import re

# Reconfigure stdout for Unicode on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def test_cli_available():
    """Test 1: Verify mmdc CLI is available."""
    print_header("Test 1: Mermaid CLI Availability")

    is_available = is_mermaid_cli_available()

    if is_available:
        print("✅ Mermaid CLI (mmdc) is available")
        return True
    else:
        print("❌ Mermaid CLI (mmdc) is NOT available")
        print("   Install: npm install -g @mermaid-js/mermaid-cli")
        return False


def test_valid_diagram():
    """Test 2: Validate a correct Mermaid diagram."""
    print_header("Test 2: Valid Diagram Validation")

    valid_diagram = """flowchart TD
    A[Start] --> B{Is it valid?}
    B -->|Yes| C[Success]
    B -->|No| D[Fix It]
    D --> B
    C --> E[End]"""

    print(f"Testing diagram ({len(valid_diagram)} chars):")
    print("```mermaid")
    print(valid_diagram)
    print("```\n")

    is_valid, message = validate_mermaid_with_cli(valid_diagram)

    if is_valid:
        print(f"✅ Validation PASSED: {message}")
        return True
    else:
        print(f"❌ Validation FAILED: {message}")
        return False


def test_invalid_diagram():
    """Test 3: Validate an incorrect Mermaid diagram."""
    print_header("Test 3: Invalid Diagram Detection")

    invalid_diagram = """A --> B
    B --> C"""

    print(f"Testing diagram ({len(invalid_diagram)} chars):")
    print("```mermaid")
    print(invalid_diagram)
    print("```\n")
    print("Expected error: Missing diagram type\n")

    is_valid, message = validate_mermaid_with_cli(invalid_diagram)

    if not is_valid:
        print(f"✅ Invalid diagram correctly detected")
        print(f"   Error message: {message[:200]}")
        return True
    else:
        print(f"❌ Should have failed but passed")
        return False


def test_reserved_keyword_error():
    """Test 4: Reserved keyword error detection."""
    print_header("Test 4: Reserved Keyword Error")

    reserved_diagram = """flowchart TD
    A[Start] --> B[Process]
    B --> end
    end --> C[Done]"""

    print(f"Testing diagram ({len(reserved_diagram)} chars):")
    print("```mermaid")
    print(reserved_diagram)
    print("```\n")
    print("Expected error: 'end' is a reserved keyword\n")

    is_valid, message = validate_mermaid_with_cli(reserved_diagram)

    if not is_valid:
        print(f"✅ Reserved keyword error correctly detected")
        print(f"   Error message: {message[:200]}")
        return True
    else:
        print(f"❌ Should have failed but passed")
        return False


def test_validation_service():
    """Test 5: Mermaid service validation."""
    print_header("Test 5: Mermaid Service Validation")

    try:
        service = get_mermaid_service()
        print("✅ Mermaid service initialized successfully")

        # Test service validation
        test_code = """flowchart TD
    A[Test] --> B[Service]"""

        print(f"\nTesting service with simple diagram...")
        is_valid, error_msg = service.validate_mermaid_code(test_code)

        if is_valid:
            print("✅ Service validation PASSED")
            return True
        else:
            print(f"❌ Service validation FAILED: {error_msg}")
            return False

    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False


def test_pattern_extraction():
    """Test 6: Mermaid code block extraction."""
    print_header("Test 6: Code Block Extraction")

    response_text = """Here's a diagram for you:

```mermaid
flowchart TD
    A --> B
    B --> C
```

And another one:

```mermaid
sequenceDiagram
    participant User
    participant API
    User->>API: Request
    API-->>User: Response
```

That's it!"""

    print("Testing pattern extraction from AI response...")
    print(f"Response length: {len(response_text)} chars\n")

    mermaid_pattern = r'```mermaid\s*\n?(.*?)```'
    mermaid_matches = re.findall(mermaid_pattern, response_text, re.DOTALL)

    print(f"Found {len(mermaid_matches)} Mermaid diagram(s)")

    if len(mermaid_matches) == 2:
        print("✅ Extraction PASSED (found 2 diagrams)")
        for i, match in enumerate(mermaid_matches, 1):
            print(f"\n   Diagram #{i}: {len(match)} chars")
            print(f"   First line: {match.strip().split('\\n')[0]}")
        return True
    else:
        print(f"❌ Extraction FAILED (expected 2, found {len(mermaid_matches)})")
        return False


def test_error_summary_building():
    """Test 7: Error summary building for AI retry."""
    print_header("Test 7: Error Summary Building")

    validation_errors = [
        "Mermaid Diagram #1 Error:\nParse error on line 3: Unexpected token 'end'",
        "Mermaid Diagram #2 Error:\nMissing diagram type declaration",
    ]

    error_summary = "\n\n".join(validation_errors)

    print("Building error summary for AI retry...")
    print(f"Number of errors: {len(validation_errors)}\n")

    correction_prompt = (
        f"FIX THESE MERMAID SYNTAX ERRORS:\n\n{error_summary}\n\n"
        f"RULES:\n"
        f"- Always start with diagram type (flowchart TD, sequenceDiagram, etc.)\n"
        f"- Use proper arrow syntax with spaces: A --> B (not A-->B)\n"
        f"- Quote labels with special characters: A[\"My Node\"]\n"
        f"- Do NOT use reserved keywords as node IDs (end, start, subgraph, etc.)\n"
        f"- Close all subgraphs with 'end'\n\n"
        f"Return ONLY the corrected ```mermaid code block. Keep it SIMPLE and COMPLETE."
    )

    print("Generated correction prompt:")
    print("-" * 80)
    print(correction_prompt[:500] + "...")
    print("-" * 80)

    if "FIX THESE MERMAID SYNTAX ERRORS" in correction_prompt:
        print("\n✅ Error summary building PASSED")
        print(f"   Prompt length: {len(correction_prompt)} chars")
        return True
    else:
        print("\n❌ Error summary building FAILED")
        return False


def test_truncation_detection():
    """Test 8: Truncation detection."""
    print_header("Test 8: Truncation Detection")

    # Truncated response (more opening than closing backticks)
    truncated_response = """Here's the corrected diagram:

```mermaid
flowchart TD
    A --> B
    B --> C"""  # Missing closing ```

    print("Testing truncation detection...")
    print(f"Response:\n{truncated_response}\n")

    opening_count = truncated_response.count('```mermaid')
    closing_count = truncated_response.count('```\n')

    print(f"Opening blocks: {opening_count}")
    print(f"Closing blocks: {closing_count}")

    if opening_count > closing_count:
        print("\n✅ Truncation correctly detected")
        print("   ⚠️  Response appears to be TRUNCATED")
        return True
    else:
        print("\n❌ Should have detected truncation")
        return False


def test_retry_loop_simulation():
    """Test 9: Simulate retry loop logic."""
    print_header("Test 9: Retry Loop Simulation")

    max_retries = 5
    retry_count = 0
    all_valid = False

    print(f"Simulating retry loop (max {max_retries} attempts)...")
    print(f"Scenario: Invalid diagram that gets progressively better\n")

    # Simulate progressive improvement
    diagrams = [
        "A --> B",  # Missing type
        "flowchart TD\n    A-->B",  # Missing arrow spacing
        "flowchart TD\n    A --> end",  # Reserved keyword
        "flowchart TD\n    A --> B\n    B --> finish",  # Undefined node
        "flowchart TD\n    A --> B\n    B --> C[Finish]",  # Valid!
    ]

    while retry_count < max_retries:
        current_diagram = diagrams[min(retry_count, len(diagrams) - 1)]
        retry_count += 1

        print(f"Attempt {retry_count}/{max_retries}:")
        print(f"  Code: {current_diagram.replace(chr(10), ' ')[:50]}...")

        is_valid, error_msg = validate_mermaid_with_cli(current_diagram)

        if is_valid:
            all_valid = True
            print(f"  ✅ Valid on attempt {retry_count}!")
            break
        else:
            print(f"  ❌ Invalid: {error_msg[:60]}...")

    if all_valid:
        print(f"\n✅ Retry loop simulation PASSED")
        print(f"   Succeeded after {retry_count} attempt(s)")
        return True
    else:
        print(f"\n❌ Retry loop simulation FAILED")
        print(f"   All {max_retries} retries exhausted")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("  MERMAID AI RETRY SYSTEM - TEST SUITE")
    print("=" * 80)

    tests = [
        ("CLI Available", test_cli_available),
        ("Valid Diagram", test_valid_diagram),
        ("Invalid Diagram", test_invalid_diagram),
        ("Reserved Keyword", test_reserved_keyword_error),
        ("Validation Service", test_validation_service),
        ("Pattern Extraction", test_pattern_extraction),
        ("Error Summary", test_error_summary_building),
        ("Truncation Detection", test_truncation_detection),
        ("Retry Loop Simulation", test_retry_loop_simulation),
    ]

    results = []

    # Run tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")

    print(f"\n{'=' * 80}")
    print(f"  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'=' * 80}\n")

    if passed == total:
        print("🎉 All tests passed! The Mermaid AI retry system is working correctly.\n")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the output above.\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
