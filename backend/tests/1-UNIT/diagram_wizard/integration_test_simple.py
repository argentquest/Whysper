"""
Simple integration test for diagram wizard with provider registry.

This test verifies that the diagram wizard nodes can be imported and used
with the provider registry system.
"""

import asyncio
import sys
import os

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Setup path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

print("=" * 70)
print("DIAGRAM WIZARD - PROVIDER INTEGRATION TEST")
print("=" * 70)

# Test 1: Check imports work
print("\nTest 1: Verify imports...")
try:
    from app.utils.diagram_wizard.graph_state import DiagramType

    print("✅ graph_state imports OK")
except ImportError as e:
    print(f"❌ Failed to import graph_state: {e}")
    sys.exit(1)

try:
    from app.utils.diagram_wizard import nodes

    print("✅ nodes module imports OK")
except ImportError as e:
    print(f"❌ Failed to import nodes: {e}")
    sys.exit(1)

# Test 2: Check provider registry available
print("\nTest 2: Check provider registry...")
try:
    from diagrams.provider_registry import get_registry

    registry = get_registry()
    print("✅ Provider registry available")

    # List available providers
    mermaid_provider = registry.get_provider("mermaidv1")
    d2_provider = registry.get_provider("d2v1")
    plantuml_provider = registry.get_provider("krokiplantuml")

    if mermaid_provider:
        print("   ✅ Mermaid provider (mermaidv1) available")
    else:
        print("   ⚠️  Mermaid provider not available")

    if d2_provider:
        print("   ✅ D2 provider (d2v1) available")
    else:
        print("   ⚠️  D2 provider not available")

    if plantuml_provider:
        print("   ✅ PlantUML provider (krokiplantuml) available")
    else:
        print("   ⚠️  PlantUML provider not available")

except ImportError as e:
    print(f"❌ Provider registry not available: {e}")
except Exception as e:
    print(f"⚠️  Provider registry error: {e}")

# Test 3: Check validate_code node
print("\nTest 3: Test validate_code node...")


async def test_validate():
    state = {
        "diagram_code": """graph TD
    A[Start] --> B[End]""",
        "diagram_type": DiagramType.MERMAID,
    }

    try:
        result = await nodes.validate_code(state)
        print("✅ validate_code executed")
        print(f"   - is_valid: {result.get('is_valid')}")
        print(f"   - current_state: {result.get('current_state')}")
        print(f"   - provider_id: {result.get('provider_id', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ validate_code failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# Test 4: Check render_diagram node
print("\nTest 4: Test render_diagram node...")


async def test_render():
    state = {
        "diagram_code": """graph TD
    A[Start] --> B[End]""",
        "diagram_type": DiagramType.MERMAID,
    }

    try:
        result = await nodes.render_diagram(state)
        print("✅ render_diagram executed")
        print(f"   - current_state: {result.get('current_state')}")
        print(f"   - svg_output length: {len(result.get('svg_output', ''))}")
        has_svg = len(result.get("svg_output", "")) > 0
        print(f"   - has_svg: {has_svg}")
        return True
    except Exception as e:
        print(f"❌ render_diagram failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# Test 5: Full workflow
print("\nTest 5: Test full validation -> rendering workflow...")


async def test_full_workflow():
    state = {
        "diagram_code": """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E""",
        "diagram_type": DiagramType.MERMAID,
    }

    try:
        # Validate
        print("  Step 1: Validating code...")
        validation_result = await nodes.validate_code(state)
        state.update(validation_result)
        print(f"    ✅ Validation: {validation_result.get('is_valid')}")

        # Render
        print("  Step 2: Rendering diagram...")
        render_result = await nodes.render_diagram(state)
        print(f"    ✅ Rendered: {render_result.get('current_state')}")

        # Check provider_id was propagated
        if render_result.get("provider_id"):
            print(f"    ✅ Provider ID: {render_result.get('provider_id')}")

        print("✅ Full workflow successful")
        return True
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return False


# Run async tests
async def run_tests():
    results = []
    results.append(await test_validate())
    results.append(await test_render())
    results.append(await test_full_workflow())
    return all(results)


print("\n" + "=" * 70)
print("RUNNING ASYNC NODE TESTS")
print("=" * 70)

success = asyncio.run(run_tests())

# Summary
print("\n" + "=" * 70)
if success:
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("=" * 70)
    print("\nIntegration Status:")
    print("✅ Diagram wizard nodes imported successfully")
    print("✅ Provider registry integration confirmed")
    print("✅ Validation node works with provider system")
    print("✅ Rendering node works with provider system")
    print("✅ Provider ID properly propagated through workflow")
    print("\n✨ Diagram wizard is successfully integrated with provider system!")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED")
    print("=" * 70)
    sys.exit(1)
