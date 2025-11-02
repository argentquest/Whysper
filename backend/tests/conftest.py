"""
Root conftest.py for pytest configuration.
Sets up Python path and environment for all tests.
"""

import sys
import os
from pathlib import Path

# Get the backend directory (parent of tests directory)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add backend directory to Python path so all imports work
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Add subdirectories to path
sys.path.insert(0, os.path.join(backend_dir, 'providers'))
sys.path.insert(0, os.path.join(backend_dir, 'common'))
sys.path.insert(0, os.path.join(backend_dir, 'app'))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{backend_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"


def save_svg_artifact(test_name: str, diagram_type: str, content: str, provider_id: str):
    """Save SVG content to file for inspection."""
    # Create artifacts directory in providers test folder
    artifacts_dir = Path(__file__).parent / "providers_test_artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not content or "<svg" not in content:
        return None

    filename = f"{test_name}_{diagram_type}_{provider_id}.svg"
    filepath = artifacts_dir / filename

    try:
        filepath.write_text(content)
        return str(filepath)
    except Exception as e:
        print(f"Warning: Could not save SVG artifact: {e}")
        return None
