"""
Root conftest.py for pytest configuration.
Sets up Python path and environment for all tests.
"""

import sys
import os

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
