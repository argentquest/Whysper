#!/usr/bin/env python3
"""
Reorganize test results from backend/tests/ to backend/testresult25/ with timestamps
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Create timestamp for folder names
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Source and destination paths
backend_path = Path("backend")
source_tests_path = backend_path / "tests"
dest_base_path = backend_path / "testresult25"

# Ensure destination exists
dest_base_path.mkdir(exist_ok=True)

# List of test providers to reorganize
providers = [
    "llmd2test",
    "llmmermaidtest",
    "llmkrokid2test",
    "llmkrokimermaidtest",
    "llmkrokic4test",
    "llmkrokiplantumtest",
    "llmkrokistructurizrtest",
]

print(f"\nReorganizing test results with timestamp: {timestamp}\n")
print("=" * 70)

# Organize each provider's results
for provider in providers:
    source_dir = source_tests_path / provider / "test_results_25"

    if not source_dir.exists():
        print(f"❌ {provider}: Source directory not found ({source_dir})")
        continue

    # Create destination folder with timestamp
    dest_dir = dest_base_path / f"{provider}_{timestamp}"

    try:
        # Copy the entire test_results_25 folder
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        shutil.copytree(source_dir, dest_dir)

        # Count files
        svg_count = len(list(dest_dir.glob("svg/*.svg")))
        error_count = len(list(dest_dir.glob("errors/*.txt")))

        print(f"✅ {provider}")
        print(f"   Location: testresult25/{provider}_{timestamp}/")
        print(f"   SVGs: {svg_count}")
        print(f"   Error files: {error_count}")

    except Exception as e:
        print(f"❌ {provider}: Error copying - {str(e)}")

print("\n" + "=" * 70)
print(f"\nAll test results have been reorganized into:")
print(f"  backend/testresult25/[provider]_{timestamp}/")
print(f"\nTimestamp: {timestamp}")
print("\nNew structure:")
print(f"  backend/testresult25/")
print(f"  ├── llmd2test_{timestamp}/")
print(f"  ├── llmmermaidtest_{timestamp}/")
print(f"  ├── llmkrokid2test_{timestamp}/")
print(f"  ├── llmkrokimermaidtest_{timestamp}/")
print(f"  ├── llmkrokic4test_{timestamp}/")
print(f"  ├── llmkrokiplantumtest_{timestamp}/")
print(f"  └── llmkrokistructurizrtest_{timestamp}/")
print(f"\nEach folder contains:")
print(f"  ├── svg/              (25 SVG files)")
print(f"  ├── errors/           (Error logs)")
print(f"  └── validation_results.json")

