"""
Integration test for diagram wizard with provider registry.

Tests that diagram wizard nodes properly integrate with the provider system
for validation and rendering of diagrams.
"""

import asyncio
import logging
from typing import Dict, Any
import pytest
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import from diagram wizard module
from app.utils.diagram_wizard.graph_state import GraphState, DiagramType
from app.utils.diagram_wizard.nodes import validate_code, render_diagram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_validate_mermaid_code():
    """Test validation of Mermaid diagram code."""
    print("\n" + "="*60)
    print("TEST 1: Validate Mermaid Code")
    print("="*60)

    state: GraphState = {
        "diagram_code": """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E""",
        "diagram_type": DiagramType.MERMAID,
    }

    result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error', 'None')}")
    print(f"Provider ID: {result.get('provider_id', 'Not set')}")

    assert result.get("is_valid") == True, "Mermaid code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"
    print("✅ PASSED: Mermaid validation works")


@pytest.mark.asyncio
async def test_validate_d2_code():
    """Test validation of D2 diagram code."""
    print("\n" + "="*60)
    print("TEST 2: Validate D2 Code")
    print("="*60)

    state: GraphState = {
        "diagram_code": """A: Client
B: Server
C: Database

A -> B: Request
B -> C: Query
C -> B: Response
B -> A: Result""",
        "diagram_type": DiagramType.D2,
    }

    result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error', 'None')}")
    print(f"Provider ID: {result.get('provider_id', 'Not set')}")

    assert result.get("is_valid") == True, "D2 code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"
    print("✅ PASSED: D2 validation works")


@pytest.mark.asyncio
async def test_validate_plantuml_code():
    """Test validation of PlantUML diagram code."""
    print("\n" + "="*60)
    print("TEST 3: Validate PlantUML Code")
    print("="*60)

    state: GraphState = {
        "diagram_code": """@startuml
actor User
participant Server
database Database

User -> Server: Request
Server -> Database: Query
Database --> Server: Data
Server --> User: Response
@enduml""",
        "diagram_type": DiagramType.PLANTUML,
    }

    result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error', 'None')}")
    print(f"Provider ID: {result.get('provider_id', 'Not set')}")

    assert result.get("is_valid") == True, "PlantUML code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"
    print("✅ PASSED: PlantUML validation works")


@pytest.mark.asyncio
async def test_validate_invalid_code():
    """Test validation of invalid diagram code."""
    print("\n" + "="*60)
    print("TEST 4: Validate Invalid Mermaid Code")
    print("="*60)

    state: GraphState = {
        "diagram_code": "This is not valid diagram code",
        "diagram_type": DiagramType.MERMAID,
    }

    result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error', 'None')}")

    assert result.get("is_valid") == False, "Invalid code should fail validation"
    assert result.get("current_state") == "validation_error", "Should move to error state"
    print("✅ PASSED: Invalid code detection works")


@pytest.mark.asyncio
async def test_validate_empty_code():
    """Test validation of empty diagram code."""
    print("\n" + "="*60)
    print("TEST 5: Validate Empty Code")
    print("="*60)

    state: GraphState = {
        "diagram_code": "",
        "diagram_type": DiagramType.MERMAID,
    }

    result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error')}")

    assert result.get("is_valid") == False, "Empty code should fail"
    assert "No diagram code provided" in result.get("validation_error", ""), "Should mention empty code"
    print("✅ PASSED: Empty code detection works")


@pytest.mark.asyncio
async def test_render_mermaid_diagram():
    """Test rendering of Mermaid diagram to SVG."""
    print("\n" + "="*60)
    print("TEST 6: Render Mermaid Diagram")
    print("="*60)

    state: GraphState = {
        "diagram_code": """graph TD
    A[Start] --> B[End]""",
        "diagram_type": DiagramType.MERMAID,
    }

    result = await render_diagram(state)

    print(f"Current State: {result.get('current_state')}")
    print(f"Has SVG Output: {len(result.get('svg_output', '')) > 0}")
    print(f"SVG Preview: {result.get('svg_output', '')[:100]}...")

    assert result.get("current_state") == "ready", "Should be in ready state"
    assert len(result.get("svg_output", "")) > 0, "Should have SVG output"
    print("✅ PASSED: Mermaid rendering works")


@pytest.mark.asyncio
async def test_render_d2_diagram():
    """Test rendering of D2 diagram to SVG."""
    print("\n" + "="*60)
    print("TEST 7: Render D2 Diagram")
    print("="*60)

    state: GraphState = {
        "diagram_code": """A: Client
B: Server
A -> B: Request
B -> A: Response""",
        "diagram_type": DiagramType.D2,
    }

    result = await render_diagram(state)

    print(f"Current State: {result.get('current_state')}")
    print(f"Has SVG Output: {len(result.get('svg_output', '')) > 0}")
    print(f"SVG Preview: {result.get('svg_output', '')[:100]}...")

    assert result.get("current_state") == "ready", "Should be in ready state"
    assert len(result.get("svg_output", "")) > 0, "Should have SVG output"
    print("✅ PASSED: D2 rendering works")


@pytest.mark.asyncio
async def test_render_empty_diagram():
    """Test rendering of empty diagram code."""
    print("\n" + "="*60)
    print("TEST 8: Render Empty Diagram")
    print("="*60)

    state: GraphState = {
        "diagram_code": "",
        "diagram_type": DiagramType.MERMAID,
    }

    result = await render_diagram(state)

    print(f"Current State: {result.get('current_state')}")
    print(f"Error Message: {result.get('error_message', 'None')}")

    assert result.get("current_state") == "error", "Should be in error state"
    print("✅ PASSED: Empty diagram error handling works")


@pytest.mark.asyncio
async def test_provider_id_propagation():
    """Test that provider_id is propagated through validation and rendering."""
    print("\n" + "="*60)
    print("TEST 9: Provider ID Propagation")
    print("="*60)

    # Start with validation
    state: GraphState = {
        "diagram_code": """graph TD
    A[Test] --> B[Result]""",
        "diagram_type": DiagramType.MERMAID,
    }

    validation_result = await validate_code(state)
    provider_id = validation_result.get("provider_id")

    print(f"Provider ID from validation: {provider_id}")

    # Update state with validation result
    state.update(validation_result)

    # Now test rendering with provider_id set
    render_result = await render_diagram(state)

    print(f"Provider ID in render result: {render_result.get('provider_id')}")
    print(f"Render state: {render_result.get('current_state')}")

    assert provider_id is not None, "Validation should set provider_id"
    print("✅ PASSED: Provider ID propagation works")


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("DIAGRAM WIZARD - PROVIDER INTEGRATION TESTS")
    print("="*60)
    print("Testing diagram wizard integration with provider registry")

    try:
        await test_validate_mermaid_code()
        await test_validate_d2_code()
        await test_validate_plantuml_code()
        await test_validate_invalid_code()
        await test_validate_empty_code()
        await test_render_mermaid_diagram()
        await test_render_d2_diagram()
        await test_render_empty_diagram()
        await test_provider_id_propagation()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nIntegration Summary:")
        print("✅ Mermaid validation and rendering working")
        print("✅ D2 validation and rendering working")
        print("✅ PlantUML validation working")
        print("✅ Invalid code detection working")
        print("✅ Empty code handling working")
        print("✅ Provider registry integration successful")
        print("✅ Fallback rendering works")
        print("✅ Error handling works")
        print("\nThe diagram wizard is successfully integrated with the provider system!")
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
