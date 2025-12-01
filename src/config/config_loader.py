"""
Configuration loader with YAML file support and environment variable overrides.

Loads configuration from:
1. Default values (from schema)
2. config.yaml file (if exists)
3. Environment variables (override YAML)
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from src.config.config_schema import AssistantConfig


# Global config instance
_config: Optional[AssistantConfig] = None


def _load_yaml_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        raise ValueError(f"Error loading config file {config_path}: {e}")


def _get_env_overrides() -> dict:
    """
    Get configuration overrides from environment variables.
    
    Environment variables should be prefixed with JANE_ and use nested keys
    separated by underscores. Field names with underscores are preserved.
    For example:
    - JANE_STT_MODEL_SIZE=large-v3 (maps to stt.model_size)
    - JANE_STT_DEVICE=cpu (maps to stt.device)
    - JANE_LLM_TEMPERATURE=0.8 (maps to llm.temperature)
    - JANE_FILE_CONTROLLER_SAFE_MODE=false (maps to file_controller.safe_mode)
    
    The mapping uses known config structure to correctly parse field names.
    """
    overrides = {}
    prefix = "JANE_"
    
    # Known config sections (including those with underscores)
    known_sections = ['stt', 'tts', 'llm', 'file_controller', 'app_controller', 'input_controller']
    
    # Known field names for each section
    config_structure = {
        'stt': ['model_size', 'device', 'compute_type', 'num_workers', 'sample_rate'],
        'tts': ['model_name', 'device'],
        'llm': ['model_path', 'n_gpu_layers', 'n_ctx', 'n_batch', 'verbose', 'temperature', 'max_tokens'],
        'file_controller': ['safe_mode', 'allowed_directories'],
        'app_controller': ['common_apps'],
        'input_controller': ['safe_mode', 'pause'],
    }
    
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        
        # Remove prefix and convert to lowercase
        config_key = key[len(prefix):].lower()
        
        # Try to match section name (could be multiple parts)
        section = None
        remaining_parts = None
        
        # Try progressively longer section names
        parts = config_key.split('_')
        for i in range(len(parts), 0, -1):
            candidate_section = '_'.join(parts[:i])
            if candidate_section in known_sections:
                section = candidate_section
                remaining_parts = parts[i:]
                break
        
        if section is None or len(remaining_parts) == 0:
            continue
        
        # Find matching field name from remaining parts
        field_name = None
        for i in range(len(remaining_parts), 0, -1):
            candidate = '_'.join(remaining_parts[:i])
            if candidate in config_structure[section]:
                field_name = candidate
                break
        
        if field_name is None:
            # Fallback: use all remaining parts as field name
            field_name = '_'.join(remaining_parts)
        
        # Build nested structure
        if section not in overrides:
            overrides[section] = {}
        
        # Set value (convert string booleans and numbers)
        if value.lower() in ('true', 'false'):
            overrides[section][field_name] = value.lower() == 'true'
        elif value.isdigit():
            overrides[section][field_name] = int(value)
        elif value.replace('.', '', 1).isdigit():
            overrides[section][field_name] = float(value)
        else:
            overrides[section][field_name] = value
    
    return overrides


def _merge_configs(default: dict, yaml_config: dict, env_overrides: dict) -> dict:
    """Merge configuration dictionaries with precedence: env > yaml > default."""
    import copy
    
    # Start with default
    merged = copy.deepcopy(default)
    
    # Apply YAML config
    def deep_update(base, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_update(base[key], value)
            else:
                base[key] = value
    
    deep_update(merged, yaml_config)
    deep_update(merged, env_overrides)
    
    return merged


def load_config(config_path: Optional[Path] = None) -> AssistantConfig:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_path: Path to config.yaml file. If None, looks for config.yaml
                    in the project root.
    
    Returns:
        AssistantConfig instance with loaded configuration
    """
    global _config
    
    if config_path is None:
        # Look for config.yaml in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.yaml"
    
    # Load YAML config
    yaml_config = _load_yaml_config(config_path)
    
    # Get environment variable overrides
    env_overrides = _get_env_overrides()
    
    # Create default config
    default_config = AssistantConfig().model_dump()
    
    # Merge configurations
    merged_config = _merge_configs(default_config, yaml_config, env_overrides)
    
    # Validate and create config object
    try:
        _config = AssistantConfig(**merged_config)
        return _config
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")


def get_config() -> AssistantConfig:
    """
    Get the loaded configuration.
    
    If config hasn't been loaded yet, loads it automatically.
    
    Returns:
        AssistantConfig instance
    """
    global _config
    
    if _config is None:
        _config = load_config()
    
    return _config


def reload_config(config_path: Optional[Path] = None) -> AssistantConfig:
    """
    Reload configuration from file.
    
    Args:
        config_path: Path to config.yaml file
    
    Returns:
        AssistantConfig instance
    """
    global _config
    _config = None
    return load_config(config_path)

