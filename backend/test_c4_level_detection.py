#!/usr/bin/env python3
"""
Test script for C4 level detection in rendering_api.py

Tests the detect_c4_level function with various prompts to ensure
it correctly identifies C1, C2, C3, and C4 levels.
"""

import re
from typing import Optional

# Import the detection function (copy of it for testing)
def detect_c4_level(prompt: str) -> Optional[str]:
    """
    Detect C4 level (C1, C2, C3, C4) from user prompt.

    Returns:
        str: "C1", "C2", "C3", "C4", or None if not detected
    """
    # Normalize prompt to uppercase for matching
    prompt_upper = prompt.upper()

    # Look for explicit C4 level indicators
    patterns = [
        (r'\bC1\b|SYSTEM\s+CONTEXT', 'C1'),
        (r'\bC2\b|CONTAINER(?:\s+DIAGRAM)?', 'C2'),
        (r'\bC3\b|COMPONENT(?:\s+DIAGRAM)?', 'C3'),
        (r'\bC4\b|CODE\s+LEVEL', 'C4'),
    ]

    for pattern, level in patterns:
        if re.search(pattern, prompt_upper):
            return level

    return None


# Test cases
test_cases = [
    # C1 tests
    ("Create a C1 diagram for an e-commerce system", "C1"),
    ("I need a system context diagram showing users and external services", "C1"),
    ("Show the C1 level architecture with actors and the main system", "C1"),

    # C2 tests
    ("Create a C2 diagram showing all internal containers", "C2"),
    ("I need a container diagram for the microservices system", "C2"),
    ("Show the C2 architecture with APIs, databases, and services", "C2"),
    ("Create a container level architecture", "C2"),

    # C3 tests
    ("Create a C3 diagram for the order service", "C3"),
    ("I need a component diagram showing the internals of the API gateway", "C3"),
    ("Show the C3 level with all components inside the payment service", "C3"),
    ("Create a component level diagram", "C3"),

    # C4 tests
    ("Create a C4 code level diagram showing class relationships", "C4"),
    ("I need a code level architecture with detailed class structures", "C4"),

    # None tests (no level detected)
    ("Create a flowchart showing the user registration process", None),
    ("I need a simple diagram with boxes and arrows", None),
    ("Show the system flow", None),
]


def run_tests():
    """Run all test cases and report results."""
    print("=" * 70)
    print("C4 Level Detection Tests")
    print("=" * 70)

    passed = 0
    failed = 0

    for prompt, expected_level in test_cases:
        detected_level = detect_c4_level(prompt)
        status = "✓ PASS" if detected_level == expected_level else "✗ FAIL"

        if detected_level == expected_level:
            passed += 1
        else:
            failed += 1

        print(f"\n{status}")
        print(f"  Prompt: {prompt}")
        print(f"  Expected: {expected_level}")
        print(f"  Detected: {detected_level}")

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} total")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
