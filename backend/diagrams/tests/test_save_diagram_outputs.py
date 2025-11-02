"""
Test Diagram Output Saving
Shows where test diagram results are stored
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.d2v1.d2_renderer import D2V1Provider
from diagrams.mermaidv1.mermaid_renderer import MermaidV1Provider


# Output directories
TEST_OUTPUT_DIR = Path("backend") / "diagrams" / "tests" / "test_outputs"
STATIC_DIAGRAMS_DIR = Path("backend") / "static" / "diagrams"


def setup_output_directories():
    """Create output directories if they don't exist"""
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_OUTPUT_DIR, STATIC_DIAGRAMS_DIR


@pytest.fixture
def d2_provider():
    """D2 provider instance"""
    provider_folder = Path(__file__).parent.parent / "d2v1"
    return D2V1Provider(provider_folder)


@pytest.fixture
def mermaid_provider():
    """Mermaid provider instance"""
    provider_folder = Path(__file__).parent.parent / "mermaidv1"
    return MermaidV1Provider(provider_folder)


def test_save_d2_diagram_output(d2_provider):
    """Test saving D2 diagram output to test directory"""
    print("\n" + "="*60)
    print("TEST: Saving D2 Diagram Output")
    print("="*60)

    if not d2_provider.is_available():
        pytest.skip("D2 CLI not available")

    # Setup directories
    test_dir, static_dir = setup_output_directories()

    # Simple D2 diagram
    code = """direction: right

Frontend: Frontend App {
  shape: rectangle
  style.fill: "#e1f5fe"
}

Backend: Backend API {
  shape: rectangle
  style.fill: "#fff3e0"
}

Database: PostgreSQL {
  shape: cylinder
  style.fill: "#f3e5f5"
}

Frontend -> Backend: HTTPS
Backend -> Database: SQL
"""

    print(f"\n1. Rendering D2 diagram...")
    result = d2_provider.render(code, output_format="svg")

    assert result.success, f"Rendering failed: {result.error}"
    assert result.content is not None

    # Save to test output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"d2_test_output_{timestamp}.svg"
    test_filepath = test_dir / test_filename

    print(f"\n2. Saving to test directory...")
    with open(test_filepath, "w", encoding="utf-8") as f:
        f.write(result.content)

    print(f"   ✓ Saved to: {test_filepath}")
    print(f"   ✓ File size: {len(result.content)} bytes ({len(result.content)/1024:.1f} KB)")

    # Also save to static directory (for API downloads)
    static_filename = f"d2_diagram_{timestamp}.svg"
    static_filepath = static_dir / static_filename

    print(f"\n3. Saving to static directory (for API)...")
    with open(static_filepath, "w", encoding="utf-8") as f:
        f.write(result.content)

    print(f"   ✓ Saved to: {static_filepath}")
    print(f"   ✓ API download URL: /api/v1/diagrams/download/{static_filename}")

    # Verify files exist
    assert test_filepath.exists()
    assert static_filepath.exists()
    assert test_filepath.stat().st_size > 0
    assert static_filepath.stat().st_size > 0

    print(f"\n✅ Test completed successfully!")
    print(f"\nOutput Locations:")
    print(f"  Test Output: {test_filepath.absolute()}")
    print(f"  Static Output: {static_filepath.absolute()}")

    return test_filepath, static_filepath


def test_save_mermaid_diagram_output(mermaid_provider):
    """Test saving Mermaid diagram output to test directory"""
    print("\n" + "="*60)
    print("TEST: Saving Mermaid Diagram Output")
    print("="*60)

    if not mermaid_provider.is_available():
        pytest.skip("Mermaid CLI not available")

    # Setup directories
    test_dir, static_dir = setup_output_directories()

    # Simple Mermaid diagram
    code = """flowchart TD
    Start[Start Process] --> Check{Check Status}
    Check -->|Valid| Process[Process Data]
    Check -->|Invalid| Error[Show Error]
    Process --> Success[Success]
    Error --> End[End]
    Success --> End
"""

    print(f"\n1. Rendering Mermaid diagram...")
    result = mermaid_provider.render(code, output_format="svg")

    assert result.success, f"Rendering failed: {result.error}"
    assert result.content is not None

    # Save to test output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"mermaid_test_output_{timestamp}.svg"
    test_filepath = test_dir / test_filename

    print(f"\n2. Saving to test directory...")
    with open(test_filepath, "w", encoding="utf-8") as f:
        f.write(result.content)

    print(f"   ✓ Saved to: {test_filepath}")
    print(f"   ✓ File size: {len(result.content)} bytes ({len(result.content)/1024:.1f} KB)")

    # Also save to static directory
    static_filename = f"mermaid_diagram_{timestamp}.svg"
    static_filepath = static_dir / static_filename

    print(f"\n3. Saving to static directory (for API)...")
    with open(static_filepath, "w", encoding="utf-8") as f:
        f.write(result.content)

    print(f"   ✓ Saved to: {static_filepath}")
    print(f"   ✓ API download URL: /api/v1/diagrams/download/{static_filename}")

    # Verify files exist
    assert test_filepath.exists()
    assert static_filepath.exists()

    print(f"\n✅ Test completed successfully!")
    print(f"\nOutput Locations:")
    print(f"  Test Output: {test_filepath.absolute()}")
    print(f"  Static Output: {static_filepath.absolute()}")

    return test_filepath, static_filepath


def test_output_directory_summary():
    """Print summary of all output directories"""
    print("\n" + "="*60)
    print("DIAGRAM OUTPUT DIRECTORY SUMMARY")
    print("="*60)

    # Setup directories
    test_dir, static_dir = setup_output_directories()

    print(f"\n[TEST OUTPUT] Test Output Directory:")
    print(f"   Location: {test_dir.absolute()}")
    print(f"   Purpose: Store test-generated diagrams for verification")

    if test_dir.exists():
        files = list(test_dir.glob("*"))
        print(f"   Files: {len(files)}")
        for f in files[-5:]:  # Show last 5 files
            print(f"     - {f.name} ({f.stat().st_size} bytes)")
    else:
        print(f"   Status: Directory will be created on first test run")

    print(f"\n[STATIC] Static Diagrams Directory:")
    print(f"   Location: {static_dir.absolute()}")
    print(f"   Purpose: Store diagrams for API download endpoints")
    print(f"   API Endpoint: /api/v1/diagrams/download/{{filename}}")

    if static_dir.exists():
        files = list(static_dir.glob("*"))
        print(f"   Files: {len(files)}")
        for f in files[-5:]:  # Show last 5 files
            print(f"     - {f.name} ({f.stat().st_size} bytes)")
    else:
        print(f"   Status: Directory will be created on first use")

    print(f"\n[OTHER] Other Diagram Directories:")

    # Check for other existing directories
    backend_path = Path("backend")
    diagram_dirs = [
        backend_path / "static" / "d2_diagrams",
        backend_path / "static" / "mermaid_diagrams",
        backend_path / "Testing",
        backend_path / "Testing" / "test_results_25" / "svg",
    ]

    for dir_path in diagram_dirs:
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            print(f"   - {dir_path}: {len(files)} files")

    print(f"\n{'='*60}")

    return test_dir, static_dir


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DIAGRAM OUTPUT SAVING TEST")
    print("="*60)

    # Show directory summary first
    test_output_directory_summary()

    # Test D2
    print("\n\nTesting D2 output saving...")
    d2_folder = Path(__file__).parent.parent / "d2v1"
    d2_prov = D2V1Provider(d2_folder)
    if d2_prov.is_available():
        test_save_d2_diagram_output(d2_prov)
    else:
        print("⚠️  D2 CLI not available, skipping D2 test")

    # Test Mermaid
    print("\n\nTesting Mermaid output saving...")
    mermaid_folder = Path(__file__).parent.parent / "mermaidv1"
    mermaid_prov = MermaidV1Provider(mermaid_folder)
    if mermaid_prov.is_available():
        test_save_mermaid_diagram_output(mermaid_prov)
    else:
        print("⚠️  Mermaid CLI not available, skipping Mermaid test")

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
