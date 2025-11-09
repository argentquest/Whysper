"""
Validate all 25 D2 tests using the Provider System (d2v1 provider)

This script:
1. Loads each test case from test.json
2. Gets the D2 code (pre-generated from test.json)
3. Renders with d2v1 provider via /api/v1/diagrams/v2/render
4. Saves validation results and SVG files

The key difference from MVP approach:
- Uses /api/v1/diagrams/v2/render endpoint (provider system)
- Specifies provider_id: "d2v1"
- Focuses on rendering quality from provider, not LLM generation
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from provider_test_helper import DiagramTestRunner


def load_test_cases(test_file: str = "test25.json") -> list:
    """
    Load test cases from test25.json file.

    Args:
        test_file: Path to test file

    Returns:
        List of test case dictionaries
    """
    script_dir = Path(__file__).parent
    test_path = script_dir / test_file

    if not test_path.exists():
        print(f"Error: Test file not found: {test_path}")
        return []

    try:
        with open(test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both dict and list formats
        if isinstance(data, dict):
            # D2 tests use d2_capability_tests key
            tests = data.get('d2_capability_tests', [])
        else:
            tests = data

        # Convert test data to expected format
        test_cases = []
        for i, test in enumerate(tests[:25], 1):
            test_cases.append({
                'id': test.get('id', i),
                'description': test.get('description', f'Test {i}'),
                'code': test.get('code', ''),
                'name': test.get('name', f'Test {i}')
            })

        return test_cases

    except json.JSONDecodeError as e:
        print(f"Error parsing test file: {e}")
        return []


def main():
    """Main test runner"""
    print("\n" + "=" * 80)
    print("D2 Provider Tests - Using d2v1 provider from provider system")
    print("=" * 80)

    # Load test cases
    test_cases = load_test_cases()
    if not test_cases:
        print("No test cases found. Exiting.")
        return 0

    print(f"Loaded {len(test_cases)} test cases\n")

    # Create test runner for d2v1 provider
    runner = DiagramTestRunner(
        provider_id="d2v1",
        diagram_type="d2",
        test_output_dir="test_results_25"
    )

    # Run all tests
    summary = runner.run_tests(
        test_cases=test_cases,
        test_name="LLM D2 Tests (d2v1 Provider)"
    )

    # Print detailed summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Provider:     {summary['provider_id']}")
    print(f"Diagram Type: {summary['diagram_type']}")
    print(f"Total Tests:  {summary['total_tests']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print("=" * 80 + "\n")

    return summary['success_rate']


if __name__ == "__main__":
    success_rate = main()
    sys.exit(0 if success_rate >= 80 else 1)
