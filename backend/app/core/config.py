"""
Configuration management for WhisperCode Web2 Backend.

This module provides centralized configuration management using Pydantic BaseSettings.
It handles environment variables, .env file loading, and provides type-safe access
to all application settings.

Key Features:
- Type-safe configuration with validation
- Environment variable override support
- Default values with documentation
- AI provider and model configuration
- Security and rate limiting settings
- Development and production profiles
"""
from typing import List, Optional
from pydantic import Field
try:
    # Try to import from pydantic-settings (Pydantic v2)
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions (Pydantic v1)
    from pydantic import BaseSettings
from common.env_manager import env_manager


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env files.
    
    This class defines all configuration options for the WhisperCode Web2 Backend.
    Settings are loaded with the following precedence:
    1. Environment variables (highest priority)
    2. .env file values (medium priority)  
    3. Default values defined in this class (lowest priority)
    
    Example environment variables:
        API_TITLE="Custom API Title"
        DEBUG=true
        PORT=8080
        API_KEY="your-api-key-here"
    """
    
    # ==================== API Configuration ====================
    api_title: str = "WhisperCode Web2 Backend"
    api_description: str = "FastAPI backend for WhisperCode Web2 with AI chat, code extraction, and Mermaid rendering"
    api_version: str = "2.0.0"
    debug: bool = False  # Enable debug mode for development (auto-reload, detailed errors)
    
    # ==================== Server Configuration ====================
    host: str = "0.0.0.0"  # Server host (0.0.0.0 allows external connections)
    port: int = 8001       # Server port (8001 to avoid conflicts with other services)
    reload: bool = True    # Auto-reload on code changes (development only)
    
    # ==================== CORS Configuration ====================
    # Cross-Origin Resource Sharing (CORS) allowed origins
    # These URLs are permitted to make requests to the API from browsers
    cors_origins: List[str] = [
        # React development servers (default ports)
        "http://localhost:3000",   # Create React App default
        "http://localhost:5173",   # Vite default
        "http://localhost:5174",   # Vite alternate ports
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        # 127.0.0.1 equivalents (some browsers/tools prefer this)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
    ]
    
    # ==================== AI Provider Configuration ====================
    # Configuration for AI chat providers (OpenRouter, Anthropic, OpenAI)
    api_key: str = Field(
        default="", 
        description="Default API key for AI providers (can be overridden per request)"
    )
    provider: str = Field(
        default="openrouter", 
        description="Default AI provider (openrouter, anthropic, openai)"
    )
    default_model: str = Field(
        default="", 
        description="Default AI model to use when none specified"
    )
    
    @property
    def models(self) -> List[str]:
        """
        Get the list of available AI models from environment or defaults.
        
        This property dynamically loads the available models from the
        environment configuration, allowing for runtime model updates
        without code changes.
        
        Returns:
            List[str]: List of available AI model identifiers
        """
        _, _, models, _ = load_env_defaults()
        return models
    
    # ==================== Code Extraction Configuration ====================
    # Limits and settings for code block extraction from AI responses
    max_code_blocks: int = Field(
        default=50, 
        description="Maximum number of code blocks to extract per request"
    )
    max_code_length: int = Field(
        default=10000, 
        description="Maximum length of a single code block in characters"
    )
    
    # ==================== Mermaid Configuration ====================
    # Settings for Mermaid diagram rendering
    mermaid_timeout: int = Field(
        default=30, 
        description="Timeout for Mermaid rendering operations in seconds"
    )
    mermaid_max_nodes: int = Field(
        default=100, 
        description="Maximum number of nodes allowed in a Mermaid diagram"
    )
    
    # ==================== File Operations Configuration ====================
    # Limits for file upload and management operations
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB in bytes
        description="Maximum file size allowed for uploads in bytes (10MB)"
    )
    max_files_per_request: int = Field(
        default=100, 
        description="Maximum number of files that can be processed per request"
    )
    
    # ==================== Pydantic Model Configuration ====================
    model_config = {
        "env_file": ".env",           # Load settings from .env file
        "case_sensitive": False,      # Environment variables are case-insensitive
        "extra": "ignore"            # Ignore extra environment variables
    }


def load_env_defaults() -> tuple[str, str, List[str], str]:
    """
    Load environment defaults from configuration files.
    
    This function interfaces with the common env_manager to load AI provider
    configuration from environment files. It provides fallback defaults if
    no configuration is found.
    
    Returns:
        tuple: A 4-tuple containing:
            - api_key (str): The API key for AI providers
            - provider (str): The default AI provider name
            - models (List[str]): List of available AI models
            - default_model (str): The default model to use
    
    Example:
        api_key, provider, models, default_model = load_env_defaults()
        print(f"Using {provider} with {len(models)} available models")
    """
    # Load environment data using the common env_manager
    env_data = env_manager.load_env_file()
    
    # Extract API key (empty string if not found)
    api_key = env_data.get("API_KEY", "")
    
    # Extract provider with fallback to OpenRouter
    provider = env_data.get("PROVIDER", "openrouter")
    
    # Parse models from comma-separated string in environment
    models_str = env_data.get("MODELS", "")
    if models_str:
        # Split comma-separated models and strip whitespace
        models = [model.strip() for model in models_str.split(",")]
    else:
        # Fallback to default model list if none configured
        models = [
            # OpenAI models via OpenRouter
            "openai/gpt-3.5-turbo",
            "openai/gpt-4", 
            # Anthropic models via OpenRouter
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            # Open source models via OpenRouter
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/wizardlm-2-8x22b",
            # Google models via OpenRouter
            "google/gemini-pro-1.5",
            # xAI models via OpenRouter
            "x-ai/grok-code-fast-1"
        ]
    
    # Extract default model or use first available model
    default_model = env_data.get("DEFAULT_MODEL", "")
    if not default_model and models:
        # If no default specified, use the first model in the list
        default_model = models[0]
    
    return api_key, provider, models, default_model


# ==================== Global Settings Instance ====================
# Create a global settings instance that can be imported throughout the application
# This ensures consistent configuration access across all modules
settings = Settings()