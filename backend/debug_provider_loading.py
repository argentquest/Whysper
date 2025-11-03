#!/usr/bin/env python3
"""
Debug script to identify why PlantUML and Structurizr providers aren't being loaded
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("PROVIDER REGISTRY DEBUG")
print("=" * 80)

# Test 1: Check if directories exist
print("\n[1] Checking provider directories...")
diagrams_root = Path(__file__).parent / "diagrams"
print(f"Diagrams root: {diagrams_root}")
print(f"Diagrams root exists: {diagrams_root.exists()}")

for folder in sorted(diagrams_root.iterdir()):
    if folder.is_dir() and not folder.name.startswith('_'):
        config_file = folder / "config.json"
        renderer_file = folder / "kroki_renderer.py" if "kroki" in folder.name else folder / f"{folder.name.replace('v1', '')}_renderer.py"
        print(f"  {folder.name:25} config.json: {config_file.exists()}, renderer: {renderer_file.exists()}")

# Test 2: Try importing the kroki providers directly
print("\n[2] Testing direct imports...")

try:
    from diagrams.krokiplantuml.kroki_renderer import KrokiPlantUMLProvider
    print("  [OK] KrokiPlantUMLProvider imported successfully")
except Exception as e:
    print(f"  [FAIL] KrokiPlantUMLProvider import failed: {e}")

try:
    from diagrams.krokistructurizr.kroki_renderer import KrokiStructurizrProvider
    print("  [OK] KrokiStructurizrProvider imported successfully")
except Exception as e:
    print(f"  [FAIL] KrokiStructurizrProvider import failed: {e}")

# Test 3: Test the provider registry
print("\n[3] Testing provider registry...")
try:
    from diagrams.provider_registry import ProviderRegistry
    registry = ProviderRegistry()

    stats = registry.get_statistics()
    print(f"  Total providers: {stats['total_providers']}")
    print(f"  Available providers: {stats['available_providers']}")
    print(f"  Provider IDs: {stats['provider_ids']}")

    print("\n[4] Testing specific provider lookups...")
    for provider_id in ['krokiplantuml', 'krokistructurizr', 'krokic4', 'd2v1', 'mermaidv1']:
        provider = registry.get(provider_id)
        if provider:
            print(f"  {provider_id:20} found (available: {provider.is_available()})")
        else:
            print(f"  {provider_id:20} NOT FOUND")

except Exception as e:
    print(f"  [FAIL] Provider registry test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
