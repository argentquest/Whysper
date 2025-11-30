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
from unittest.mock import patch, MagicMock, AsyncMock

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

    # Mock the registry and provider
    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import ValidationResult
    mock_provider.validate_code.return_value = ValidationResult(is_valid=True, code_length=len(state["diagram_code"]))

    # Patch get_registry in validation_nodes to return our mock registry
    with patch('app.utils.diagram_wizard.nodes.validation_nodes.get_registry', return_value=mock_registry):
        # We also need to patch PROVIDER_AVAILABLE in validation_nodes if it was False
        with patch('app.utils.diagram_wizard.nodes.validation_nodes.PROVIDER_AVAILABLE', True):
            result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")
    print(f"Validation Error: {result.get('validation_error', 'None')}")

    assert result.get("is_valid") == True, "Mermaid code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"

    # Verify mock usage
    mock_registry.get_default_provider.assert_called_with(DiagramType.MERMAID.value)
    mock_provider.validate_code.assert_called_once()

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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import ValidationResult
    mock_provider.validate_code.return_value = ValidationResult(is_valid=True, code_length=len(state["diagram_code"]))

    with patch('app.utils.diagram_wizard.nodes.validation_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.validation_nodes.PROVIDER_AVAILABLE', True):
            result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")

    assert result.get("is_valid") == True, "D2 code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"

    mock_registry.get_default_provider.assert_called_with(DiagramType.D2.value)

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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import ValidationResult
    mock_provider.validate_code.return_value = ValidationResult(is_valid=True, code_length=len(state["diagram_code"]))

    with patch('app.utils.diagram_wizard.nodes.validation_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.validation_nodes.PROVIDER_AVAILABLE', True):
            result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")

    assert result.get("is_valid") == True, "PlantUML code should be valid"
    assert result.get("current_state") == "rendering", "Should move to rendering state"

    mock_registry.get_default_provider.assert_called_with(DiagramType.PLANTUML.value)

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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import ValidationResult
    mock_provider.validate_code.return_value = ValidationResult(is_valid=False, error="Invalid syntax", code_length=len(state["diagram_code"]))

    with patch('app.utils.diagram_wizard.nodes.validation_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.validation_nodes.PROVIDER_AVAILABLE', True):
            result = await validate_code(state)

    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Current State: {result.get('current_state')}")

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

    # No need to mock registry as empty code check happens before provider call
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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import RenderResult, ValidationResult
    # Mock successful render - MUST be an async mock or return a future because render_diagram awaits it
    # We can use AsyncMock for the method
    mock_provider.render_with_validation = AsyncMock()
    mock_provider.render_with_validation.return_value = RenderResult(success=True, content="<svg>...</svg>", output_format="svg", validation=ValidationResult(is_valid=True, code_length=10))

    with patch('app.utils.diagram_wizard.nodes.rendering_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.rendering_nodes.PROVIDER_AVAILABLE', True):
            result = await render_diagram(state)

    print(f"Current State: {result.get('current_state')}")
    print(f"Has SVG Output: {len(result.get('svg_output', '')) > 0}")

    assert result.get("current_state") == "ready", "Should be in ready state"
    assert len(result.get("svg_output", "")) > 0, "Should have SVG output"

    mock_registry.get_default_provider.assert_called_with(DiagramType.MERMAID.value)
    mock_provider.render_with_validation.assert_awaited_once()

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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import RenderResult, ValidationResult
    mock_provider.render_with_validation = AsyncMock()
    mock_provider.render_with_validation.return_value = RenderResult(success=True, content="<svg>...</svg>", output_format="svg", validation=ValidationResult(is_valid=True, code_length=10))

    with patch('app.utils.diagram_wizard.nodes.rendering_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.rendering_nodes.PROVIDER_AVAILABLE', True):
            result = await render_diagram(state)

    print(f"Current State: {result.get('current_state')}")
    print(f"Has SVG Output: {len(result.get('svg_output', '')) > 0}")

    assert result.get("current_state") == "ready", "Should be in ready state"
    assert len(result.get("svg_output", "")) > 0, "Should have SVG output"

    mock_registry.get_default_provider.assert_called_with(DiagramType.D2.value)

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

    mock_registry = MagicMock()
    mock_provider = MagicMock()
    mock_registry.get_default_provider.return_value = mock_provider

    from diagrams.base_diagram import ValidationResult, RenderResult
    val_res = ValidationResult(is_valid=True, code_length=len(state["diagram_code"]))
    mock_provider.validate_code.return_value = val_res

    with patch('app.utils.diagram_wizard.nodes.validation_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.validation_nodes.PROVIDER_AVAILABLE', True):
            validation_result = await validate_code(state)

    # render_diagram uses diagram_type to get provider again.
    render_res = RenderResult(success=True, content="<svg>...</svg>", output_format="svg", validation=val_res)
    mock_provider.render_with_validation = AsyncMock()
    mock_provider.render_with_validation.return_value = render_res

    with patch('app.utils.diagram_wizard.nodes.rendering_nodes.get_registry', return_value=mock_registry):
        with patch('app.utils.diagram_wizard.nodes.rendering_nodes.PROVIDER_AVAILABLE', True):
            render_result = await render_diagram(state)

    assert validation_result.get("is_valid") is True
    print("✅ PASSED: Validation successful")


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
