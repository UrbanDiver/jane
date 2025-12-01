"""
Base Plugin Class

Defines the base class and hook system for plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from src.utils.logger import get_logger


class PluginHook(Enum):
    """
    Plugin hook points where plugins can register callbacks.
    """
    BEFORE_STT = "before_stt"
    AFTER_STT = "after_stt"
    BEFORE_LLM = "before_llm"
    AFTER_LLM = "after_llm"
    BEFORE_TTS = "before_tts"
    AFTER_TTS = "after_tts"
    BEFORE_FUNCTION_CALL = "before_function_call"
    AFTER_FUNCTION_CALL = "after_function_call"
    ON_MESSAGE = "on_message"
    ON_ERROR = "on_error"


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Plugins can:
    - Register functions for LLM function calling
    - Register hooks at various points in the execution flow
    - Access the assistant core and other components
    """
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        """
        Initialize the plugin.
        
        Args:
            name: Plugin name (must be unique)
            version: Plugin version
            description: Plugin description
        """
        self.name = name
        self.version = version
        self.description = description
        self.logger = get_logger(f"plugin.{name}")
        self.enabled = True
        self.hooks: Dict[PluginHook, List[Callable]] = {}
        self.functions: Dict[str, Dict] = {}
        self.logger.info(f"Plugin '{name}' v{version} initialized")
    
    @abstractmethod
    def initialize(self, assistant_core) -> bool:
        """
        Initialize the plugin with access to the assistant core.
        
        This is called when the plugin is loaded. Use this to:
        - Register functions
        - Set up hooks
        - Access assistant components
        
        Args:
            assistant_core: The AssistantCore instance
            
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    def register_function(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        Register a function that the LLM can call.
        
        Args:
            name: Function name (must be unique across all plugins)
            func: Python function to execute
            description: Description of what the function does
            parameters: JSON Schema for function parameters
        """
        self.functions[name] = {
            "function": func,
            "description": description,
            "parameters": parameters,
            "plugin": self.name
        }
        self.logger.info(f"Registered function: {name}")
    
    def register_hook(self, hook: PluginHook, callback: Callable) -> None:
        """
        Register a callback for a plugin hook.
        
        Args:
            hook: The hook point to register for
            callback: Function to call when hook is triggered
        """
        if hook not in self.hooks:
            self.hooks[hook] = []
        self.hooks[hook].append(callback)
        self.logger.debug(f"Registered hook: {hook.value}")
    
    def get_functions(self) -> Dict[str, Dict]:
        """
        Get all functions registered by this plugin.
        
        Returns:
            Dictionary of function definitions
        """
        return self.functions.copy()
    
    def get_hooks(self) -> Dict[PluginHook, List[Callable]]:
        """
        Get all hooks registered by this plugin.
        
        Returns:
            Dictionary of hooks and their callbacks
        """
        return self.hooks.copy()
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
        self.logger.info(f"Plugin '{self.name}' enabled")
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
        self.logger.info(f"Plugin '{self.name}' disabled")
    
    def cleanup(self) -> None:
        """
        Cleanup resources when plugin is unloaded.
        
        Override this method to perform cleanup operations.
        """
        self.logger.info(f"Plugin '{self.name}' cleaned up")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "functions_count": len(self.functions),
            "hooks_count": sum(len(callbacks) for callbacks in self.hooks.values())
        }

