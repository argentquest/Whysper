```python
#!/usr/bin/env python3
"""
Debug script to identify why PlantUML and Structurizr providers aren't being loaded
"""
import sys
from pathlib import Path

# Dynamically add the backend directory to the Python path for import resolution
sys.path.insert(0, str(Path(__file__).parent))

# Display a header to clearly indicate the start of the debug script
print("=" * 80)
print("PROVIDER REGISTRY DEBUG")
print("=" * 80)

# Test 1: Verify the existence of provider directories and configuration files
print("\n[1] Checking provider directories...")
# Locate the root directory containing diagram provider folders
diagrams_root = Path(__file__).parent / "diagrams"
print(f"Diagrams root: {diagrams_root}")
print(f"Diagrams root exists: {diagrams_root.exists()}")

# Iterate through each provider folder to check for config and renderer files
for folder in sorted(diagrams_root.iterdir()):
    # Skip hidden or system folders
    if folder.is_dir() and not folder.name.startswith('_'):
        # Check for configuration and renderer files in each provider folder
        config_file = folder / "config.json"
        renderer_file = folder / "kroki_renderer.py" if "kroki" in folder.name else folder / f"{folder.name.replace('v1', '')}_renderer.py"
        print(f"  {folder.name:25} config.json: {config_file.exists()}, renderer: {renderer_file.exists()}")

# Test 2: Attempt direct imports of specific providers to diagnose import issues
print("\n[2] Testing direct imports...")

# Try importing KrokiPlantUML provider and log the result
try:
    from diagrams.krokiplantuml.kroki_renderer import KrokiPlantUMLProvider
    print("  [OK] KrokiPlantUMLProvider imported successfully")
except Exception as e:
    print(f"  [FAIL] KrokiPlantUMLProvider import failed: {e}")

# Try importing KrokiStructurizr provider and log the result
try:
    from diagrams.krokistructurizr.kroki_renderer import KrokiStructurizrProvider
    print("  [OK] KrokiStructurizrProvider imported successfully")
except Exception as e:
    print(f"  [FAIL] KrokiStructurizrProvider import failed: {e}")

# Test 3: Validate the provider registry functionality
print("\n[3] Testing provider registry...")
try:
    # Import the provider registry to check its configuration and availability
    from diagrams.provider_registry import ProviderRegistry
    registry = ProviderRegistry()

    # Retrieve and display statistics about available providers
    stats = registry.get_statistics()
    print(f"  Total providers: {stats['total_providers']}")
    print(f"  Available providers: {stats['available_providers']}")
    print(f"  Provider IDs: {stats['provider_ids']}")

    # Test 4: Check the availability of specific providers
    print("\n[4] Testing specific provider lookups...")
    # Attempt to retrieve and check specific providers
    for provider_id in ['krokiplantuml', 'krokistructurizr', 'krokic4', 'd2v1', 'mermaidv1']:
        provider = registry.get(provider_id)
        if provider:
            print(f"  {provider_id:20} found (available: {provider.is_available()})")
        else:
            print(f"  {provider_id:20} NOT FOUND")

except Exception as e:
    # Catch and display any errors during provider registry testing
    print(f"  [FAIL] Provider registry test failed: {e}")
    import traceback
    traceback.print_exc()

# Display a footer to indicate the end of the debug script
print("\n" + "=" * 80)