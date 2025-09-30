"""
Security utilities for handling sensitive information safely.
"""
import os
import re
from typing import Any, Dict, List, Union, Optional
from pathlib import Path


class SecurityUtils:
    """Utilities for secure handling of sensitive data."""
    
    # Patterns for identifying sensitive data
    SENSITIVE_PATTERNS = {
        'api_key': re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE),
        'bearer_token': re.compile(r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
        'auth_header': re.compile(r'Authorization:\s*[a-zA-Z0-9_\-\.]+', re.IGNORECASE),
        'password': re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
        'secret': re.compile(r'secret["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
    }
    
    # Fields that should be masked in debug output
    SENSITIVE_FIELDS = {
        'api_key', 'password', 'secret', 'token', 'auth', 'authorization',
        'bearer', 'key', 'credential', 'private'
    }
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        Mask an API key for safe logging/display.
        
        Args:
            api_key: The API key to mask
            
        Returns:
            Masked API key showing only first 3 and last 3 characters
        """
        if not api_key or len(api_key) < 8:
            return "*****"
        
        return f"{api_key[:3]}...{api_key[-3:]}"
    
    @staticmethod
    def mask_sensitive_string(text: str) -> str:
        """
        Mask sensitive information in a string using pattern matching.
        
        Args:
            text: Text that may contain sensitive information
            
        Returns:
            Text with sensitive information masked
        """
        if not text:
            return text
        
        masked_text = text
        
        for pattern_name, pattern in SecurityUtils.SENSITIVE_PATTERNS.items():
            def mask_match(match):
                full_match = match.group(0)
                if len(full_match) > 10:
                    return f"{full_match[:3]}***{full_match[-3:]}"
                else:
                    return "***"
            
            masked_text = pattern.sub(mask_match, masked_text)
        
        return masked_text
    
    @staticmethod
    def mask_dict_values(data: Dict[str, Any], mask_keys: List[str] = None) -> Dict[str, Any]:
        """
        Mask sensitive values in a dictionary.
        
        Args:
            data: Dictionary that may contain sensitive values
            mask_keys: Additional keys to mask (optional)
            
        Returns:
            Dictionary with sensitive values masked
        """
        if not isinstance(data, dict):
            return data
        
        sensitive_keys = SecurityUtils.SENSITIVE_FIELDS.copy()
        if mask_keys:
            sensitive_keys.update(set(mask_keys))
        
        masked_data = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key indicates sensitive data
            is_sensitive = any(sensitive_word in key_lower for sensitive_word in sensitive_keys)
            
            if is_sensitive:
                if isinstance(value, str) and value:
                    masked_data[key] = SecurityUtils.mask_api_key(value)
                elif isinstance(value, bool):
                    masked_data[key] = value  # Keep boolean values as-is
                else:
                    masked_data[key] = "***"
            elif isinstance(value, dict):
                # Recursively mask nested dictionaries
                masked_data[key] = SecurityUtils.mask_dict_values(value, mask_keys)
            elif isinstance(value, str):
                # Check string content for patterns
                masked_data[key] = SecurityUtils.mask_sensitive_string(value)
            else:
                masked_data[key] = value
        
        return masked_data
    
    @staticmethod
    def safe_debug_info(info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a safe version of debug information for logging.
        
        Args:
            info: Debug information dictionary
            
        Returns:
            Safe debug information with sensitive data masked
        """
        return SecurityUtils.mask_dict_values(info)
    
    @staticmethod
    def is_sensitive_key(key: str) -> bool:
        """
        Check if a key name indicates sensitive data.
        
        Args:
            key: Key name to check
            
        Returns:
            True if key appears to contain sensitive data
        """
        key_lower = key.lower()
        return any(sensitive_word in key_lower for sensitive_word in SecurityUtils.SENSITIVE_FIELDS)
    
    @staticmethod
    def validate_api_key_format(api_key: str, provider: str = None) -> bool:
        """
        Validate API key format for security.
        
        Args:
            api_key: API key to validate
            provider: Provider name for specific validation (optional)
            
        Returns:
            True if API key format appears valid
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # General validation - should be reasonable length and not obviously fake
        if len(api_key) < 8 or api_key in ['test', 'fake', 'dummy', '123456']:
            return False
        
        # Provider-specific validation
        if provider == "openrouter" or provider == "openai":
            return api_key.startswith("sk-") and len(api_key) >= 20
        
        # Generic validation for other providers
        return len(api_key) >= 10
    
    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """
        Sanitize a log message by masking sensitive information.
        
        Args:
            message: Log message that may contain sensitive data
            
        Returns:
            Sanitized log message
        """
        return SecurityUtils.mask_sensitive_string(message)

    @staticmethod
    def safe_path_resolve(base_directory: Union[str, Path], file_path: Union[str, Path]) -> Optional[str]:
        """
        Resolves a user-provided file path against a base directory (e.g., codebase root)
        and ensures the resulting path is contained within the base directory to prevent
        path traversal attacks (CWE-22).

        Args:
            base_directory: The trusted root directory path.
            file_path: The user-provided relative or absolute path.

        Returns:
            The safe, resolved absolute path as a string, or None if the path
            attempts to traverse outside the base directory.
        """
        try:
            base_path = Path(base_directory).resolve()
            
            # Combine base directory with the file path, then resolve
            # This handles both relative and absolute paths correctly
            if Path(file_path).is_absolute():
                full_path = Path(file_path).resolve()
            else:
                # For relative paths, combine with base directory first
                full_path = (base_path / file_path).resolve()

            # Check if the fully resolved path is a subpath of the base path
            # Using str().startswith() and os.sep is a robust check for sub-directory containment
            if str(full_path).startswith(str(base_path) + os.sep):
                # Also verify the file actually exists
                if full_path.exists():
                    return str(full_path)
            
            # Allow the base directory itself (e.g., if file_path resolves to base_directory)
            if full_path == base_path and full_path.is_file():
                return str(full_path)

            return None
        except Exception:
            return None