#!/usr/bin/env python3
"""
Simple test script for keyword scorer module.
Tests the keyword scoring and diagram type determination logic.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.diagram_wizard.keyword_scorer import KeywordScorer, determine_diagram_type
from app.utils.diagram_wizard.graph_state import DiagramType


def test_keyword_scorer():
    """Test the KeywordScorer class."""
    scorer = KeywordScorer()

    # Test 1: Flowchart/Mermaid detection
    flowchart_text = """
    I need a flowchart showing the user registration process.
    The flow starts with login, then checks if user exists.
    If not, creates account. Then authenticates and validates.
    Final step is redirecting to dashboard.
    """

    print("=" * 60)
    print("TEST 1: Flowchart (Mermaid) Detection")
    print("=" * 60)
    scores = scorer.score_text(flowchart_text)
    print(f"Text: {flowchart_text[:100]}...")
    print(f"Scores: {scores}")
    assert scores["Mermaid"] > scores["D2"], "Mermaid should score higher for flowchart"
    print("[OK] PASSED: Mermaid scored highest for flowchart text\n")

    # Test 2: Architecture/D2 detection
    architecture_text = """
    We have a microservices architecture with:
    - Frontend client connecting to API Gateway
    - API Gateway routing to User Service and Product Service
    - Each service has its own database
    - Services communicate via RabbitMQ message queue
    - Redis cache for performance
    - Load balancer for distribution
    """

    print("=" * 60)
    print("TEST 2: Architecture (D2) Detection")
    print("=" * 60)
    scores = scorer.score_text(architecture_text)
    print(f"Text: {architecture_text[:100]}...")
    print(f"Scores: {scores}")
    assert scores["D2"] > scores["Mermaid"], "D2 should score higher for architecture"
    print("[OK] PASSED: D2 scored highest for architecture text\n")

    # Test 3: UML/PlantUML detection
    uml_text = """
    Design a class diagram with:
    - User class with attributes (id, name, email)
    - Order class with methods (createOrder, updateOrder)
    - Inheritance between RegularUser and PremiumUser
    - Associations and dependencies between classes
    """

    print("=" * 60)
    print("TEST 3: UML (PlantUML) Detection")
    print("=" * 60)
    scores = scorer.score_text(uml_text)
    print(f"Text: {uml_text[:100]}...")
    print(f"Scores: {scores}")
    assert scores["PlantUML"] > scores["Mermaid"], "PlantUML should score higher for UML"
    print("[OK] PASSED: PlantUML scored highest for UML text\n")


def test_determine_diagram_type():
    """Test the determine_diagram_type function."""

    print("=" * 60)
    print("TEST 4: Determine Diagram Type Function")
    print("=" * 60)

    test_cases = [
        (
            "flowchart with decision points and conditional branches",
            DiagramType.MERMAID,
            "Flowchart"
        ),
        (
            "system architecture with microservices backend frontend database",
            DiagramType.D2,
            "Architecture"
        ),
        (
            "class diagram with inheritance polymorphism interfaces",
            DiagramType.PLANTUML,
            "UML"
        ),
    ]

    for text, expected_type, description in test_cases:
        diagram_type, scores = determine_diagram_type(text)
        print(f"\nCase: {description}")
        print(f"Input: {text}")
        print(f"Determined: {diagram_type.value}")
        print(f"Expected: {expected_type.value}")
        print(f"Scores: {scores}")
        assert diagram_type == expected_type, f"Expected {expected_type.value}, got {diagram_type.value}"
        print(f"[OK] PASSED")


def test_empty_input():
    """Test handling of empty input."""
    print("\n" + "=" * 60)
    print("TEST 5: Empty Input Handling")
    print("=" * 60)

    scorer = KeywordScorer()
    scores = scorer.score_text("")

    print(f"Empty text scores: {scores}")
    # Should distribute evenly
    assert abs(scores["Mermaid"] - scores["D2"]) < 5, "Empty input should distribute evenly"
    print("[OK] PASSED: Empty input handled correctly\n")


def test_mixed_keywords():
    """Test text with mixed keywords."""
    print("=" * 60)
    print("TEST 6: Mixed Keywords")
    print("=" * 60)

    mixed_text = """
    We need a sequence diagram showing interactions between:
    - User submitting a request
    - API Gateway routing the request
    - Backend service processing
    - Database query and response
    - Final response back to user
    """

    scorer = KeywordScorer()
    scores = scorer.score_text(mixed_text)
    diagram_type, scores = determine_diagram_type(mixed_text)

    print(f"Text: {mixed_text[:100]}...")
    print(f"Determined Type: {diagram_type.value}")
    print(f"Scores: {scores}")
    # Sequence diagrams can be in both Mermaid and PlantUML
    assert diagram_type in [DiagramType.MERMAID, DiagramType.PLANTUML]
    print("[OK] PASSED: Mixed keywords handled correctly\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("KEYWORD SCORER TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_keyword_scorer()
        test_determine_diagram_type()
        test_empty_input()
        test_mixed_keywords()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
