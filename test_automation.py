#!/usr/bin/env python3
"""
Test script to verify the inline comments automation works correctly.
Processes a small sample of files to validate the setup before running on all 321 files.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend" / "src"
PYTHON_SCRIPT = ROOT_DIR / "add_inline_comments.py"
NODE_SCRIPT = ROOT_DIR / "add-inline-comments.js"

def test_api_key():
    """Test if API key is set"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY=your-key-here")
        return False
    else:
        # Mask the key for display
        masked = api_key[:7] + "..." + api_key[-4:]
        print(f"✓ API key found: {masked}")
        return True

def test_python_sdk():
    """Test if Python SDK is installed"""
    try:
        import anthropic
        print("✓ Python anthropic SDK installed")
        return True
    except ImportError:
        print("❌ Python anthropic SDK not installed")
        print("\nInstall it with:")
        print("  pip install anthropic")
        return False

def test_node_sdk():
    """Test if Node SDK is installed"""
    try:
        result = subprocess.run(
            ['node', '-e', 'require("@anthropic-ai/sdk")'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Node.js @anthropic-ai/sdk installed")
            return True
        else:
            print("❌ Node.js @anthropic-ai/sdk not installed")
            print("\nInstall it with:")
            print("  npm install @anthropic-ai/sdk")
            return False
    except Exception as e:
        print(f"❌ Node.js test failed: {e}")
        return False

def get_sample_files():
    """Get a small sample of files to test"""
    python_files = []
    ts_files = []

    # Get 2 Python files
    for root, dirs, files in os.walk(BACKEND_DIR):
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.pytest_cache']]
        for file in files:
            if file.endswith('.py') and len(python_files) < 2:
                python_files.append(Path(root) / file)
        if len(python_files) >= 2:
            break

    # Get 2 TypeScript files
    for root, dirs, files in os.walk(FRONTEND_DIR):
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
        for file in files:
            if file.endswith(('.ts', '.tsx')) and len(ts_files) < 2:
                ts_files.append(Path(root) / file)
        if len(ts_files) >= 2:
            break

    return python_files, ts_files

def test_python_processing(sample_file):
    """Test processing a single Python file"""
    print(f"\n  Testing: {sample_file.name}")

    # Read original
    with open(sample_file, 'r', encoding='utf-8') as f:
        original = f.read()

    original_lines = len(original.split('\n'))
    print(f"  Original: {original_lines} lines")

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(PYTHON_SCRIPT), str(sample_file)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"  ❌ Processing failed: {result.stderr}")
            return False

        # Check result
        with open(sample_file, 'r', encoding='utf-8') as f:
            processed = f.read()

        processed_lines = len(processed.split('\n'))
        comments_added = processed.count('#') - original.count('#')

        print(f"  Processed: {processed_lines} lines (+{processed_lines - original_lines})")
        print(f"  Comments added: ~{comments_added}")
        print(f"  ✓ Success!")

        # Restore original
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(original)

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        # Restore original
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(original)
        return False

def test_node_processing(sample_file):
    """Test processing a single TypeScript file"""
    print(f"\n  Testing: {sample_file.name}")

    # Read original
    with open(sample_file, 'r', encoding='utf-8') as f:
        original = f.read()

    original_lines = len(original.split('\n'))
    print(f"  Original: {original_lines} lines")

    try:
        # Run the script
        result = subprocess.run(
            ['node', str(NODE_SCRIPT), str(sample_file)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"  ❌ Processing failed: {result.stderr}")
            return False

        # Check result
        with open(sample_file, 'r', encoding='utf-8') as f:
            processed = f.read()

        processed_lines = len(processed.split('\n'))
        comments_added = processed.count('//') - original.count('//')

        print(f"  Processed: {processed_lines} lines (+{processed_lines - original_lines})")
        print(f"  Comments added: ~{comments_added}")
        print(f"  ✓ Success!")

        # Restore original
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(original)

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        # Restore original
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(original)
        return False

def main():
    print("=" * 80)
    print("INLINE COMMENTS AUTOMATION - SYSTEM TEST")
    print("=" * 80)
    print()

    # Run tests
    print("1. Testing Prerequisites")
    print("-" * 80)
    api_ok = test_api_key()
    python_ok = test_python_sdk()
    node_ok = test_node_sdk()

    if not (api_ok and python_ok and node_ok):
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return 1

    print("\n2. Getting Sample Files")
    print("-" * 80)
    python_files, ts_files = get_sample_files()
    print(f"✓ Found {len(python_files)} Python sample files")
    print(f"✓ Found {len(ts_files)} TypeScript sample files")

    # Test Python processing
    print("\n3. Testing Python File Processing")
    print("-" * 80)
    python_success = all(test_python_processing(f) for f in python_files)

    # Test TypeScript processing
    print("\n4. Testing TypeScript File Processing")
    print("-" * 80)
    ts_success = all(test_node_processing(f) for f in ts_files)

    # Final result
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    if python_success and ts_success:
        print("✓ All tests passed!")
        print("\nYou can now run the full automation:")
        print("  Windows: run_all_inline_comments.bat")
        print("  Linux/Mac: ./run_all_inline_comments.sh")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
