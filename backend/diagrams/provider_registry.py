"""
Provider Registry

Auto-discovers and manages diagram providers.
Scans diagrams folder for provider subfolders and registers them.
"""

from pathlib import Path
from typing import Dict, List, Optional, Type
import importlib
import logging

from .base_diagram import BaseDiagramProvider
from .models import ProviderMetadata
from .provider_config import ProviderConfigLoader
from .llm_correction_service import get_llm_correction_service

from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry for all diagram providers.
    Auto-discovers providers from diagrams folder.
    """

    @log_method_call
    def __init__(self, diagrams_root: Optional[Path] = None, auto_discover: bool = True):
        """
        Initialize provider registry.

        Args:
            diagrams_root: Path to diagrams folder. If None, uses default.
            auto_discover: Whether to auto-discover providers on initialization. Default True.
        """
        if diagrams_root is None:
            diagrams_root = Path(__file__).parent

        self.diagrams_root = diagrams_root
        self._providers: Dict[str, BaseDiagramProvider] = {}

        if auto_discover:
            self._discover_providers()

    @log_method_call
    def _discover_providers(self):
        """Auto-discover providers from diagrams subfolders"""
        logger.info(f"Discovering providers in: {self.diagrams_root}")

        for folder in self.diagrams_root.iterdir():
            # Skip non-directories and special folders
            if not folder.is_dir():
                continue
            if folder.name.startswith('_'):
                continue
            if folder.name in ['tests', '__pycache__']:
                continue

            provider_id = folder.name

            # Check if config.json exists
            config_file = folder / "config.json"
            if not config_file.exists():
                logger.debug(f"Skipping {provider_id} - no config.json found")
                continue

            # Try to import provider module
            try:
                module_path = f"diagrams.{provider_id}.{self._get_renderer_module_name(provider_id)}"
                logger.debug(f"Attempting to import: {module_path}")

                module = importlib.import_module(module_path)

                # Find provider class
                provider_class = self._find_provider_class(module)

                if provider_class:
                    # Instantiate with folder path
                    provider = provider_class(folder)

                    # Set LLM correction service
                    llm_service = get_llm_correction_service()
                    provider.set_llm_correction_service(llm_service)

                    # Register
                    self.register(provider)
                    logger.info(f"✅ Registered provider: {provider_id}")
                else:
                    logger.warning(f"⚠️  No provider class found in {provider_id}")

            except ImportError as e:
                logger.debug(f"⚠️  Could not import provider {provider_id}: {e}")
                # This is expected for providers not yet implemented
            except Exception as e:
                logger.error(f"❌ Error loading provider {provider_id}: {e}", exc_info=True)

    @log_method_call
    def _get_renderer_module_name(self, provider_id: str) -> str:
        """
        Determine expected module name from provider_id.

        Examples:
        - mermaidv1 -> mermaid_renderer
        - d2v1 -> d2_renderer
        - mermaid-playwright -> mermaid_renderer
        - plantumlv1 -> plantuml_renderer
        - krokid2 -> kroki_renderer
        - krokistructurizr -> kroki_renderer
        """
        base_name = provider_id.lower()

        # Remove version suffix
        base_name = base_name.replace('v1', '').replace('v2', '')

        # Remove hyphens
        base_name = base_name.replace('-', '_')

        # Map to renderer module name
        # Check for kroki-based providers first (they have precedence)
        if 'kroki' in base_name:
            return 'kroki_renderer'
        elif 'mermaid' in base_name:
            return 'mermaid_renderer'
        elif 'd2' in base_name:
            return 'd2_renderer'
        elif 'plantuml' in base_name:
            return 'plantuml_renderer'
        elif 'c4' in base_name:
            return 'c4_renderer'
        elif 'structurizr' in base_name:
            return 'kroki_renderer'
        else:
            return 'renderer'

    @log_method_call
    def _find_provider_class(self, module) -> Optional[Type[BaseDiagramProvider]]:
        """Find provider class in module

        Prioritizes concrete subclasses over base classes.
        This ensures KrokiD2Provider is used instead of KrokiBaseProvider, etc.
        """
        from .kroki_base import KrokiBaseProvider

        candidate = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, BaseDiagramProvider) and
                attr != BaseDiagramProvider):
                # Skip abstract/base Kroki classes
                if attr == KrokiBaseProvider:
                    continue
                # Prefer concrete classes
                if candidate is None or issubclass(attr, candidate):
                    candidate = attr

        return candidate

    @log_method_call
    def register(self, provider: BaseDiagramProvider):
        """
        Register a provider.

        Args:
            provider: Provider instance to register
        """
        self._providers[provider.provider_id] = provider
        logger.debug(f"Provider {provider.provider_id} registered successfully")

    @log_method_call
    def unregister(self, provider_id: str):
        """
        Unregister a provider.

        Args:
            provider_id: ID of provider to unregister
        """
        if provider_id in self._providers:
            del self._providers[provider_id]
            logger.info(f"Provider {provider_id} unregistered")

    @log_method_call
    def get(self, provider_id: str) -> Optional[BaseDiagramProvider]:
        """
        Get a provider by ID.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(provider_id)

    @log_method_call
    def list_all(self) -> List[ProviderMetadata]:
        """
        List all registered providers.

        Returns:
            List of provider metadata
        """
        return [p.get_metadata() for p in self._providers.values()]

    @log_method_call
    def list_available(self) -> List[ProviderMetadata]:
        """
        List only available providers.

        Returns:
            List of available provider metadata
        """
        return [p.get_metadata() for p in self._providers.values() if p.is_available()]

    @log_method_call
    def find_by_diagram_type(self, diagram_type: str) -> List[BaseDiagramProvider]:
        """
        Find all providers for a specific diagram type.

        Args:
            diagram_type: Diagram type (e.g., "mermaid", "d2")

        Returns:
            List of providers that support this diagram type
        """
        return [
            p for p in self._providers.values()
            if p.diagram_type.lower() == diagram_type.lower() and p.is_available()
        ]

    @log_method_call
    def find_by_output_format(self, output_format: str) -> List[BaseDiagramProvider]:
        """
        Find all providers that support a specific output format.

        Args:
            output_format: Output format (e.g., "svg", "png")

        Returns:
            List of providers that support this format
        """
        return [
            p for p in self._providers.values()
            if output_format.lower() in [fmt.lower() for fmt in p.supported_output_formats]
            and p.is_available()
        ]

    @log_method_call
    def get_default_provider(self, diagram_type: str) -> Optional[BaseDiagramProvider]:
        """
        Get default provider for a diagram type.
        Uses preferences from root config.json, falls back to v1 providers, then first available.

        Args:
            diagram_type: Diagram type

        Returns:
            Default provider or None
        """
        providers = self.find_by_diagram_type(diagram_type)
        if not providers:
            return None

        # STEP 1: Check root config for provider preferences
        try:
            config_file = self.diagrams_root / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    root_config = json.load(f)
                    preferences = root_config.get('provider_preferences', {})
                    preferred_provider_id = preferences.get(diagram_type.lower())

                    if preferred_provider_id:
                        for p in providers:
                            if p.provider_id == preferred_provider_id:
                                logger.debug(f"Using configured preference for {diagram_type}: {preferred_provider_id}")
                                return p
                        logger.warning(f"Configured provider '{preferred_provider_id}' for '{diagram_type}' not found or unavailable")
        except Exception as e:
            logger.debug(f"Could not load provider preferences from config: {e}")

        # STEP 2: Prefer v1 providers (fallback)
        for p in providers:
            if 'v1' in p.provider_id.lower():
                logger.debug(f"Using v1 provider for {diagram_type}: {p.provider_id}")
                return p

        # STEP 3: Use first available (final fallback)
        logger.debug(f"Using first available provider for {diagram_type}: {providers[0].provider_id}")
        return providers[0]

    @log_method_call
    def reload_provider(self, provider_id: str) -> bool:
        """
        Reload a provider's configuration.

        Args:
            provider_id: Provider to reload

        Returns:
            True if successful, False otherwise
        """
        provider = self.get(provider_id)
        if provider:
            return provider.reload_config()
        return False

    @log_method_call
    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        total = len(self._providers)
        available = len([p for p in self._providers.values() if p.is_available()])
        unavailable = total - available

        diagram_types = {}
        for provider in self._providers.values():
            dtype = provider.diagram_type
            if dtype not in diagram_types:
                diagram_types[dtype] = 0
            diagram_types[dtype] += 1

        return {
            "total_providers": total,
            "available_providers": available,
            "unavailable_providers": unavailable,
            "diagram_types": diagram_types,
            "provider_ids": list(self._providers.keys())
        }


# Global singleton
_registry = None


@log_method_call
def get_registry(diagrams_root: Optional[Path] = None) -> ProviderRegistry:
    """
    Get the global provider registry instance.

    Args:
        diagrams_root: Optional path to diagrams folder

    Returns:
        ProviderRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ProviderRegistry(diagrams_root)
    return _registry


@log_method_call
def reset_registry():
    """Reset the global registry (for testing)"""
    global _registry
    _registry = None


@log_method_call
def get_provider_registry(diagrams_root: Optional[Path] = None) -> ProviderRegistry:
    """
    Alias for get_registry() - for convenience.

    Args:
        diagrams_root: Optional path to diagrams folder

    Returns:
        ProviderRegistry instance
    """
    return get_registry(diagrams_root)


@log_method_call
def set_provider_registry(registry: Optional[ProviderRegistry]):
    """
    Set the global registry instance (for testing).

    Args:
        registry: Registry instance or None to clear
    """
    global _registry
    _registry = registry
