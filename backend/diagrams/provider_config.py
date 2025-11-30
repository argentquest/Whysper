"""
Provider Configuration Management

Handles hierarchical configuration with:
- Root config.json (defaults for all providers)
- Provider-specific config.json (overrides only)
- Deep merge for partial overrides
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum
import json
import logging
from copy import deepcopy

from common.logging_decorator import log_method_call

logger = logging.getLogger(__name__)


class CorrectionStrategy(str, Enum):
    """Strategy for error correction"""
    NONE = "none"
    PATTERN_ONLY = "pattern_only"
    LLM_ONLY = "llm_only"
    PATTERN_THEN_LLM = "pattern_then_llm"
    USER_ONLY = "user_only"


class LLMCorrectionConfig(BaseModel):
    """LLM correction configuration"""
    enabled: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    model_override: Optional[str] = None
    max_tokens: Optional[int] = Field(default=4000, ge=100, le=100000)


class PatternCorrectionConfig(BaseModel):
    """Pattern-based correction configuration"""
    enabled: bool = True


class UserCorrectionConfig(BaseModel):
    """User correction configuration"""
    enabled: bool = True
    session_timeout_seconds: int = Field(default=300, ge=60, le=3600)


class ValidationConfig(BaseModel):
    """Validation configuration"""
    timeout_seconds: int = Field(default=120, ge=10, le=600)
    max_code_length_bytes: int = Field(default=512000, ge=1024, le=524288)


class RenderingConfig(BaseModel):
    """Rendering configuration"""
    timeout_seconds: int = Field(default=120, ge=10, le=600)
    default_output_format: str = "svg"


class BatchConfig(BaseModel):
    """Batch rendering configuration"""
    enabled: bool = False
    max_items: int = Field(default=50, ge=1, le=100)


class DefaultConfig(BaseModel):
    """Default configuration that applies to all providers"""
    llm_correction: LLMCorrectionConfig = Field(default_factory=LLMCorrectionConfig)
    pattern_correction: PatternCorrectionConfig = Field(default_factory=PatternCorrectionConfig)
    correction_strategy: CorrectionStrategy = Field(default=CorrectionStrategy.PATTERN_THEN_LLM)
    user_correction: UserCorrectionConfig = Field(default_factory=UserCorrectionConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)
    batch: BatchConfig = Field(default_factory=BatchConfig)


class GlobalSettings(BaseModel):
    """Global settings that affect entire diagram system"""
    session_cleanup_interval_seconds: int = Field(default=300, ge=60, le=3600)
    max_concurrent_renders: int = Field(default=10, ge=1, le=100)
    enable_metrics: bool = True
    enable_debug_logging: bool = False


class RootConfig(BaseModel):
    """Root configuration file (backend/diagrams/config.json)"""
    version: str = "1.0"
    description: str = "Default configuration for all diagram providers"
    defaults: DefaultConfig = Field(default_factory=DefaultConfig)
    global_settings: GlobalSettings = Field(default_factory=GlobalSettings)


class ProviderConfig(BaseModel):
    """
    Provider-specific configuration.
    Merges defaults from root config with provider overrides.
    """

    # Provider identity (required in provider config)
    provider_id: str = Field(..., description="Unique provider identifier")
    provider_name: str = Field(..., description="Human-readable provider name")
    description: Optional[str] = Field(None, description="Provider description")

    # Diagram type support (required in provider config)
    diagram_type: str = Field(..., description="Primary diagram type")
    supported_output_formats: List[str] = Field(..., description="Supported output formats")

    # These come from defaults, but can be overridden
    llm_correction: LLMCorrectionConfig = Field(default_factory=LLMCorrectionConfig)
    pattern_correction: PatternCorrectionConfig = Field(default_factory=PatternCorrectionConfig)
    correction_strategy: CorrectionStrategy = Field(default=CorrectionStrategy.PATTERN_THEN_LLM)
    user_correction: UserCorrectionConfig = Field(default_factory=UserCorrectionConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)
    batch: BatchConfig = Field(default_factory=BatchConfig)

    # Provider-specific custom settings (not in defaults)
    custom: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "use_enum_values": True
    }


class ConfigMerger:
    """Handles merging of default config with provider overrides"""

    @staticmethod
    @log_method_call
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        Override values take precedence over base values.

        Args:
            base: Base dictionary (defaults)
            override: Override dictionary (provider-specific)

        Returns:
            Merged dictionary
        """
        result = deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = ConfigMerger.deep_merge(result[key], value)
            else:
                # Override value
                result[key] = deepcopy(value)

        return result

    @staticmethod
    @log_method_call
    def merge_configs(
        root_config: RootConfig,
        provider_config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge root defaults with provider overrides.

        Args:
            root_config: Root configuration with defaults
            provider_config_data: Provider-specific configuration data

        Returns:
            Merged configuration dictionary
        """
        # Start with defaults from root config
        merged = root_config.defaults.model_dump()

        # Get provider overrides
        provider_overrides = provider_config_data.get('overrides', {})

        # Deep merge overrides into defaults
        merged = ConfigMerger.deep_merge(merged, provider_overrides)

        # Add provider-specific required fields
        merged['provider_id'] = provider_config_data['provider_id']
        merged['provider_name'] = provider_config_data['provider_name']
        merged['description'] = provider_config_data.get('description', '')
        merged['diagram_type'] = provider_config_data['diagram_type']
        merged['supported_output_formats'] = provider_config_data['supported_output_formats']

        # Add custom settings (not merged, just added)
        merged['custom'] = provider_config_data.get('custom', {})

        return merged


class ProviderConfigLoader:
    """Loads and merges configurations"""

    @log_method_call
    def __init__(self, diagrams_root: Path):
        """
        Initialize the config loader.

        Args:
            diagrams_root: Path to diagrams folder
        """
        self.diagrams_root = diagrams_root
        self.root_config = self._load_root_config()

    @log_method_call
    def _load_root_config(self) -> RootConfig:
        """Load root config.json from diagrams folder"""
        root_config_file = self.diagrams_root / "config.json"

        if not root_config_file.exists():
            logger.warning("No root config.json found, creating default")
            default_config = RootConfig()
            self._save_root_config(default_config)
            return default_config

        try:
            with open(root_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            config = RootConfig(**config_data)
            logger.info("✅ Loaded root configuration with defaults")
            return config

        except Exception as e:
            logger.error(f"Error loading root config: {e}")
            logger.info("Using default root configuration")
            return RootConfig()

    @log_method_call
    def _save_root_config(self, config: RootConfig):
        """Save the root config.json"""
        root_config_file = self.diagrams_root / "config.json"

        try:
            with open(root_config_file, 'w', encoding='utf-8') as f:
                json.dump(
                    config.model_dump(mode='json'),
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            logger.info("Saved root configuration")
        except Exception as e:
            logger.error(f"Error saving root config: {e}")

    @log_method_call
    def load_provider_config(self, provider_folder: Path) -> Optional[ProviderConfig]:
        """
        Load provider configuration by merging root defaults with provider overrides.

        Args:
            provider_folder: Path to provider folder

        Returns:
            Merged ProviderConfig or None if error
        """
        provider_config_file = provider_folder / "config.json"
        provider_id = provider_folder.name

        # If no provider config exists, create minimal default
        if not provider_config_file.exists():
            logger.warning(f"No config.json in {provider_id}, using defaults only")
            return self._create_minimal_provider_config(provider_id)

        try:
            with open(provider_config_file, 'r', encoding='utf-8') as f:
                provider_data = json.load(f)

            # Validate required fields
            required_fields = ['provider_id', 'provider_name', 'diagram_type', 'supported_output_formats']
            for field in required_fields:
                if field not in provider_data:
                    logger.error(f"Provider config missing required field: {field}")
                    return None

            # Merge with root defaults
            merged_data = ConfigMerger.merge_configs(self.root_config, provider_data)

            # Create ProviderConfig from merged data
            config = ProviderConfig(**merged_data)

            logger.info(
                f"✅ Loaded config for {provider_id}: "
                f"LLM retries={config.llm_correction.max_retries}, "
                f"strategy={config.correction_strategy}"
            )

            return config

        except Exception as e:
            logger.error(f"Error loading provider config from {provider_config_file}: {e}")
            return None

    @log_method_call
    def _create_minimal_provider_config(self, provider_id: str) -> ProviderConfig:
        """Create minimal provider config using all defaults"""
        # Detect diagram type from provider_id
        if 'mermaid' in provider_id.lower():
            diagram_type = 'mermaid'
            formats = ['mermaid', 'svg']
        elif 'd2' in provider_id.lower():
            diagram_type = 'd2'
            formats = ['d2', 'svg']
        else:
            diagram_type = provider_id.replace('v1', '').replace('v2', '')
            formats = ['svg']

        # Use all defaults from root config
        merged_data = self.root_config.defaults.model_dump()
        merged_data.update({
            'provider_id': provider_id,
            'provider_name': f"{diagram_type.capitalize()} Renderer",
            'description': f"Auto-generated config for {provider_id}",
            'diagram_type': diagram_type,
            'supported_output_formats': formats,
            'custom': {}
        })

        return ProviderConfig(**merged_data)

    @log_method_call
    def save_provider_config(
        self,
        config: ProviderConfig,
        provider_folder: Path,
        include_defaults: bool = False
    ) -> None:
        """
        Save provider configuration.

        Args:
            config: Provider configuration to save
            provider_folder: Path to provider folder
            include_defaults: If True, save full config. If False, save only overrides.

        """
        provider_config_file = provider_folder / "config.json"

        try:
            if include_defaults:
                # Save full config
                config_data = config.model_dump(mode='json')
            else:
                # Save only overrides by comparing with defaults
                config_data = self._extract_overrides(config)

            provider_folder.mkdir(parents=True, exist_ok=True)

            with open(provider_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved config for {config.provider_id}")
        except Exception as e:
            logger.error(f"Error saving provider config: {e}")

    @log_method_call
    def _extract_overrides(self, config: ProviderConfig) -> Dict[str, Any]:
        """
        Extract only values that differ from defaults.

        Returns:
            Dictionary with provider identity + overrides + custom
        """
        defaults = self.root_config.defaults.model_dump()
        current = config.model_dump()

        overrides = {}

        # Compare each section with defaults
        for section in ['llm_correction', 'pattern_correction', 'correction_strategy',
                        'user_correction', 'validation', 'rendering', 'batch']:

            if section in current and section in defaults:
                if isinstance(current[section], dict):
                    section_overrides = {}
                    for key, value in current[section].items():
                        if key not in defaults[section] or defaults[section][key] != value:
                            section_overrides[key] = value
                    if section_overrides:
                        overrides[section] = section_overrides
                else:
                    # For non-dict values (like correction_strategy)
                    if current[section] != defaults[section]:
                        overrides[section] = current[section]

        # Build minimal config with overrides
        result = {
            'provider_id': config.provider_id,
            'provider_name': config.provider_name,
            'description': config.description,
            'diagram_type': config.diagram_type,
            'supported_output_formats': config.supported_output_formats,
        }

        if overrides:
            result['overrides'] = overrides

        if config.custom:
            result['custom'] = config.custom

        return result

    @log_method_call
    def get_root_config(self) -> RootConfig:
        """Get the root configuration"""
        return self.root_config


# Global instance
_config_loader = None


@log_method_call
def get_config_loader() -> ProviderConfigLoader:
    """Get the global config loader instance"""
    global _config_loader
    if _config_loader is None:
        diagrams_root = Path(__file__).parent
        _config_loader = ProviderConfigLoader(diagrams_root)
    return _config_loader


@log_method_call
def load_provider_config(provider_folder: Path) -> Optional[ProviderConfig]:
    """Convenience function to load provider config with defaults merged"""
    loader = get_config_loader()
    return loader.load_provider_config(provider_folder)
