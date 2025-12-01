"""
Example Plugin

This is a demonstration plugin showing how to create plugins for the assistant.
"""

from src.plugins.plugin_base import BasePlugin, PluginHook
from typing import Dict, Any


class ExamplePlugin(BasePlugin):
    """
    Example plugin that demonstrates plugin capabilities.
    
    This plugin:
    - Registers a custom function
    - Registers hooks to intercept messages
    - Shows how to access assistant components
    """
    
    def __init__(self):
        """Initialize the example plugin."""
        super().__init__(
            name="example",
            version="1.0.0",
            description="Example plugin demonstrating plugin capabilities"
        )
        self.message_count = 0
    
    def initialize(self, assistant_core) -> bool:
        """
        Initialize the plugin.
        
        Args:
            assistant_core: AssistantCore instance
            
        Returns:
            True if initialization successful
        """
        self.assistant_core = assistant_core
        
        # Register a custom function
        self.register_function(
            "get_plugin_info",
            self.get_plugin_info,
            "Get information about loaded plugins",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        # Register hooks
        self.register_hook(PluginHook.ON_MESSAGE, self.on_message)
        self.register_hook(PluginHook.BEFORE_LLM, self.before_llm)
        
        self.logger.info("Example plugin initialized")
        return True
    
    def get_plugin_info(self) -> str:
        """
        Example function that can be called by the LLM.
        
        Returns:
            Information about the plugin
        """
        info = self.get_info()
        return f"Plugin: {info['name']} v{info['version']} - {info['description']}"
    
    def on_message(self, message: Dict[str, str]) -> None:
        """
        Hook callback for ON_MESSAGE.
        
        Args:
            message: Message dictionary with 'role' and 'content'
        """
        self.message_count += 1
        self.logger.debug(f"Message #{self.message_count}: {message.get('role', 'unknown')}")
    
    def before_llm(self, messages: list) -> list:
        """
        Hook callback for BEFORE_LLM.
        
        Can modify messages before they're sent to LLM.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Modified (or original) messages list
        """
        # Example: Add a system message if not present
        has_system = any(msg.get('role') == 'system' for msg in messages)
        if not has_system:
            messages.insert(0, {
                "role": "system",
                "content": "You are a helpful assistant. This message was added by the example plugin."
            })
            self.logger.debug("Added system message via plugin hook")
        
        return messages
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded."""
        self.logger.info(f"Example plugin processed {self.message_count} messages")
        super().cleanup()

