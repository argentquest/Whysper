```python
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

# Add parent directory to path for imports to support module resolution
sys.path.insert(0, str(Path(__file__).parent.parent))

from provider_test_helper import DiagramTestRunner


def load_test_cases(test_file: str = "test25.json") -> list:
    # Determine the full path to the test file
    script_dir = Path(__file__).parent
    test_path = script_dir / test_file

    # Check if test file exists before attempting to load
    if not test_path.exists():
        print(f"Error: Test file not found: {test_path}")
        return []

    try:
        # Open and parse JSON test file with UTF-8 encoding
        with open(test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures (dict or list)
        if isinstance(data, dict):
            # Use specific key for D2 tests if data is a dictionary
            tests = data.get('d2_capability_tests', [])
        else:
            tests = data

        # Normalize test cases with consistent structure
        test_cases = []
        for i, test in enumerate(tests[:25], 1):
            test_cases.append({
                'id': test.get('id', i),  # Use index as fallback ID
                'description': test.get('description', f'Test {i}'),  # Default description
                'code': test.get('code', ''),  # Ensure code exists
                'name': test.get('name', f'Test {i}')  # Default name
            })

        return test_cases

    except json.JSONDecodeError as e:
        # Catch and report JSON parsing errors
        print(f"Error parsing test file: {e}")
        return []


def main():
    # Print header to indicate start of test suite
    print("\n" + "=" * 80)
    print("D2 Provider Tests - Using d2v1 provider from provider system")
    print("=" * 80)

    # Load test cases from JSON file
    test_cases = load_test_cases()
    if not test_cases:
        print("No test cases found. Exiting.")
        return 0

    print(f"Loaded {len(test_cases)} test cases\n")

    # Initialize test runner with specific provider configuration
    runner = DiagramTestRunner(
        provider_id="d2v1",  # Specify D2 v1 provider
        diagram_type="d2",   # Set diagram type
        test_output_dir="test_results_25"  # Directory for test results
    )

    # Execute all test cases and collect summary
    summary = runner.run_tests(
        test_cases=test_cases,
        test_name="LLM D2 Tests (d2v1 Provider)"
    )

    # Print detailed test execution summary
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
    # Run main test suite and exit with appropriate status code
    success_rate = main()
    sys.exit(0 if success_rate >= 80 else 1)
```

The comments explain the logic for key sections, including file loading, test case normalization, test runner configuration, and result reporting.