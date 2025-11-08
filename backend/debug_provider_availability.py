#!/usr/bin/env python3
"""
Diagnostic script to check diagram provider availability and configuration issues.

This script helps diagnose why providers might not be working correctly
by checking:
1. Provider registration and discovery
2. Configuration loading and merging
3. CLI tool availability
4. Provider is_available() method results
"""

import sys
import os
from pathlib import Path
import logging
import json

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_provider_registry():
    """Check provider registry discovery and registration"""
    print("\n" + "="*60)
    print("PROVIDER REGISTRY DIAGNOSTICS")
    print("="*60)
    
    try:
        from diagrams.provider_registry import get_registry
        
        registry = get_registry()
        stats = registry.get_statistics()
        
        print(f"✅ Registry initialized successfully")
        print(f"   Total providers: {stats['total_providers']}")
        print(f"   Available providers: {stats['available_providers']}")
        print(f"   Unavailable providers: {stats['unavailable_providers']}")
        print(f"   Diagram types: {stats['diagram_types']}")
        print(f"   Provider IDs: {stats['provider_ids']}")
        
        # List all providers with their status
        all_providers = registry.list_all()
        print("\n--- Provider Details ---")
        for metadata in all_providers:
            status = "✅ AVAILABLE" if metadata.available else "❌ UNAVAILABLE"
            print(f"   {metadata.provider_id:20} {status}")
            print(f"      Name: {metadata.provider_name}")
            print(f"      Type: {metadata.diagram_type}")
            print(f"      Version: {metadata.version}")
            print(f"      Capabilities: {[c.value for c in metadata.capabilities]}")
            print()
        
        return registry
        
    except Exception as e:
        print(f"❌ Registry initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_config_loading():
    """Check configuration loading and merging"""
    print("\n" + "="*60)
    print("CONFIGURATION LOADING DIAGNOSTICS")
    print("="*60)
    
    try:
        from diagrams.provider_config import get_config_loader
        
        loader = get_config_loader()
        root_config = loader.get_root_config()
        
        print(f"✅ Root config loaded successfully")
        print(f"   Version: {root_config.version}")
        print(f"   Description: {root_config.description}")
        print(f"   LLM correction enabled: {root_config.defaults.llm_correction.enabled}")
        print(f"   Pattern correction enabled: {root_config.defaults.pattern_correction.enabled}")
        print(f"   Correction strategy: {root_config.defaults.correction_strategy}")
        print(f"   Debug logging: {root_config.global_settings.enable_debug_logging}")
        
        # Check provider preferences
        if hasattr(root_config, 'provider_preferences'):
            print(f"   Provider preferences: {root_config.provider_preferences}")
        else:
            print("   ⚠️  No provider_preferences found in root config")
        
        # Check individual provider configs
        diagrams_root = Path(__file__).parent / "diagrams"
        print(f"\n--- Provider Configs ---")
        
        for provider_folder in diagrams_root.iterdir():
            if not provider_folder.is_dir() or provider_folder.name.startswith('_'):
                continue
                
            config_file = provider_folder / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    print(f"   {provider_folder.name}:")
                    print(f"      ✅ Config exists")
                    print(f"      Provider ID: {config_data.get('provider_id', 'MISSING')}")
                    print(f"      Diagram type: {config_data.get('diagram_type', 'MISSING')}")
                    print(f"      Has overrides: {'overrides' in config_data}")
                    print(f"      Has custom: {'custom' in config_data}")
                    
                    # Check for specific issues
                    if 'custom' in config_data:
                        custom = config_data['custom']
                        if 'executable_path' in custom:
                            path = custom['executable_path']
                            if path is None:
                                print(f"      ⚠️  executable_path is null - may cause issues")
                            elif isinstance(path, str) and not path.strip():
                                print(f"      ⚠️  executable_path is empty string")
                            else:
                                print(f"      ✅ executable_path: {path}")
                        else:
                            print(f"      ⚠️  No executable_path in custom settings")
                    
                except Exception as e:
                    print(f"   {provider_folder.name}: ❌ Failed to load config: {e}")
            else:
                print(f"   {provider_folder.name}: ❌ No config.json found")
        
        return loader
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_cli_tools():
    """Check availability of CLI tools used by providers"""
    print("\n" + "="*60)
    print("CLI TOOL AVAILABILITY DIAGNOSTICS")
    print("="*60)
    
    import subprocess
    
    tools_to_check = [
        ("d2", "D2 Diagram Tool"),
        ("mermaid", "Mermaid CLI (mmdc)"),
        ("plantuml", "PlantUML"),
        ("node", "Node.js (for Mermaid)")
    ]
    
    for tool, description in tools_to_check:
        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   {tool:15} ✅ AVAILABLE - {result.stdout.strip()}")
            else:
                print(f"   {tool:15} ❌ UNAVAILABLE - Exit code: {result.returncode}")
        except FileNotFoundError:
            print(f"   {tool:15} ❌ NOT FOUND - Install {description}")
        except subprocess.TimeoutExpired:
            print(f"   {tool:15} ❌ TIMEOUT - Tool hung on version check")
        except Exception as e:
            print(f"   {tool:15} ❌ ERROR - {e}")

def check_individual_providers():
    """Check individual provider availability methods"""
    print("\n" + "="*60)
    print("INDIVIDUAL PROVIDER AVAILABILITY")
    print("="*60)
    
    try:
        from diagrams.provider_registry import get_registry
        registry = get_registry()
        
        # Get all registered providers
        all_providers = registry.list_all()
        
        for metadata in all_providers:
            provider_id = metadata.provider_id
            provider = registry.get(provider_id)
            
            if provider:
                print(f"\n--- {provider_id} ---")
                print(f"   Provider class: {type(provider).__name__}")
                print(f"   Provider folder: {provider.provider_folder}")
                print(f"   Config loaded: {provider.config is not None}")
                
                if provider.config:
                    print(f"   Config provider_id: {provider.config.provider_id}")
                    print(f"   Config diagram_type: {provider.config.diagram_type}")
                    print(f"   LLM retries: {provider.config.llm_correction.max_retries}")
                    print(f"   Custom settings: {provider.config.custom}")
                
                # Test is_available() method
                try:
                    available = provider.is_available()
                    print(f"   is_available(): {available}")
                    
                    if not available:
                        # Try to get more details
                        if hasattr(provider, '_cli_available'):
                            print(f"   CLI cache: {provider._cli_available}")
                        if hasattr(provider, 'd2_executable'):
                            print(f"   D2 executable: {provider.d2_executable}")
                        
                        # Try version check
                        version = provider.get_version()
                        print(f"   Version: {version}")
                        
                except Exception as e:
                    print(f"   ❌ is_available() failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"\n--- {provider_id} ---")
                print(f"   ❌ Provider not found in registry")
    
    except Exception as e:
        print(f"❌ Provider check failed: {e}")
        import traceback
        traceback.print_exc()

def check_environment():
    """Check environment variables and paths"""
    print("\n" + "="*60)
    print("ENVIRONMENT DIAGNOSTICS")
    print("="*60)
    
    # Check PATH
    path_env = os.environ.get('PATH', '')
    print(f"PATH includes {len(path_env.split(os.pathsep))} directories")
    
    # Check current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Check if we're in backend directory
    backend_dir = Path(__file__).parent
    print(f"Backend directory: {backend_dir}")
    print(f"Diagrams directory: {backend_dir / 'diagrams'}")
    
    # Check for specific environment variables
    env_vars = [
        'PROVIDERS',
        'DEBUG',
        'PYTHONPATH'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")

def main():
    """Run all diagnostics"""
    print("DIAGRAM PROVIDER DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This tool helps diagnose issues with diagram provider configuration")
    print("and availability. Run this when providers are not working correctly.")
    print()
    
    # Run all diagnostic checks
    check_environment()
    check_config_loading()
    check_cli_tools()
    check_provider_registry()
    check_individual_providers()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)
    print("\nIf you see issues above:")
    print("1. Install missing CLI tools (D2, Mermaid, etc.)")
    print("2. Check config.json files for null executable_path")
    print("3. Ensure providers are properly implemented")
    print("4. Verify PATH includes required tools")

if __name__ == "__main__":
    main()