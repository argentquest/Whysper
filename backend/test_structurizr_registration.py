"""
Test script to verify Kroki Structurizr provider registration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.provider_registry import get_registry


def test_structurizr_registration():
    """Test that Kroki Structurizr provider is properly registered"""
    print("="*60)
    print("TEST: Kroki Structurizr Provider Registration")
    print("="*60)
    
    # Get the provider registry
    registry = get_registry()
    
    # Get all providers
    all_providers = registry.list_all()
    print(f"Total providers registered: {len(all_providers)}")
    
    # Check for Structurizr provider
    structurizr_providers = [
        p for p in all_providers if p.diagram_type == "structurizr"
    ]
    print(f"Structurizr providers found: {len(structurizr_providers)}")
    
    if structurizr_providers:
        for provider in structurizr_providers:
            print(f"\n✓ Provider ID: {provider.provider_id}")
            print(f"✓ Provider Name: {provider.provider_name}")
            print(f"✓ Diagram Type: {provider.diagram_type}")
            print(f"✓ Available: {provider.available}")
            capabilities = [c.value for c in provider.capabilities]
            print(f"✓ Capabilities: {capabilities}")
            print(f"✓ Supported Formats: {provider.supported_output_formats}")
            
            # Verify it's the krokistructurizr provider
            expected = "krokistructurizr"
            assert provider.provider_id == expected, f"Expected {expected}, got {provider.provider_id}"
            expected = "structurizr"
            assert provider.diagram_type == expected, f"Expected {expected}, got {provider.diagram_type}"
            
            print("\n✅ Structurizr provider properly registered!")
    else:
        print("\n❌ No Structurizr providers found!")
        return False
        
    # Test getting the provider directly
    provider = registry.get("krokistructurizr")
    if provider:
        print(f"\n✓ Direct retrieval successful: {provider.provider_name}")
        print(f"✓ Provider available: {provider.is_available()}")
        print(f"✓ Version: {provider.get_version()}")
    else:
        print("\n❌ Could not retrieve krokistructurizr provider directly!")
        return False
        
    # Test finding by diagram type
    structurizr_providers = registry.find_by_diagram_type("structurizr")
    if structurizr_providers:
        count = len(structurizr_providers)
        print(f"\n✓ Found {count} provider(s) for 'structurizr' type")
        for p in structurizr_providers:
            print(f"  - {p.provider_id}: {p.provider_name}")
    else:
        print("\n❌ No providers found for 'structurizr' diagram type!")
        return False
        
    # Test getting default provider
    default_provider = registry.get_default_provider("structurizr")
    if default_provider:
        print(f"\n✓ Default structurizr provider: {default_provider.provider_id}")
    else:
        print("\n❌ No default provider for 'structurizr' diagram type!")
        return False
        
    # Get registry statistics
    stats = registry.get_statistics()
    print("\nRegistry Statistics:")
    print(f"  Total providers: {stats['total_providers']}")
    print(f"  Available providers: {stats['available_providers']}")
    print(f"  Diagram types: {list(stats['diagram_types'].keys())}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_structurizr_registration()
        if success:
            print("\n" + "="*60)
            print("✅ REGISTRATION TEST PASSED!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ REGISTRATION TEST FAILED!")
            print("="*60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)