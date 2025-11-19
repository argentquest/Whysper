"""
Root conftest.py for pytest configuration.
Sets up Python path and environment for all tests.
"""

import sys
import os
from pathlib import Path

# Determine the backend directory path by going up two levels from the current file's directory
# This ensures we can reference the backend root directory regardless of test location
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add backend directory to Python path to enable importing modules from backend
# Inserting at index 0 ensures this path takes precedence over system paths
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Add key subdirectories to Python path to enable importing from specific backend modules
# This allows tests to import from providers, common, and app directories
sys.path.insert(0, os.path.join(backend_dir, 'providers'))
sys.path.insert(0, os.path.join(backend_dir, 'common'))
sys.path.insert(0, os.path.join(backend_dir, 'app'))

# Set PYTHONPATH environment variable to include backend directory
# This ensures consistent module import behavior across different environments
os.environ['PYTHONPATH'] = f"{backend_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"


def save_svg_artifact(test_name: str, diagram_type: str, content: str, provider_id: str):
    """Save SVG content to file for inspection."""
    # Create a dedicated directory for storing test artifacts
    # This helps organize and track generated SVG files from tests
    artifacts_dir = Path(__file__).parent / "providers_test_artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Skip saving if content is empty or doesn't contain an SVG
    # This prevents creating empty or invalid artifact files
    if not content or "<svg" not in content:
        return None

    # Generate a unique filename based on test details to avoid overwriting
    filename = f"{test_name}_{diagram_type}_{provider_id}.svg"
    filepath = artifacts_dir / filename

    # Attempt to write SVG content to file, handling potential write errors
    try:
        filepath.write_text(content)
        return str(filepath)
    except Exception as e:
        # Log warning if file saving fails, but don't interrupt test execution
        print(f"Warning: Could not save SVG artifact: {e}")
        return None
