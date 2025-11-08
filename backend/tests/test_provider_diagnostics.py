"""
Test provider diagnostics during server startup
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_provider_diagnostics():
    """Test provider diagnostics"""
    # Import and run diagnostics
    from debug_provider_availability import test_provider_diagnostics
    
    # Capture output
    import io
    from contextlib import redirect_stdout
    
    captured_output = io.StringIO()
    with redirect_stdout(captured_output):
        test_provider_diagnostics()
    
    output = captured_output.getvalue()
    
    # Basic assertions
    assert "PROVIDER REGISTRY DIAGNOSTICS" in output
    assert "CONFIGURATION LOADING DIAGNOSTICS" in output
    assert "CLI TOOL AVAILABILITY DIAGNOSTICS" in output
    
    # Check for common issues
    if "❌" in output:
        # Log the issues found
        print("Found issues in provider diagnostics:")
        print(output)
        pytest.fail("Provider diagnostics found issues - see output above")
    
    print("✅ Provider diagnostics completed successfully")