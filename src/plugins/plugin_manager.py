"""
Plugin Manager

Manages plugin discovery, loading, and lifecycle.
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.plugins.plugin_base import BasePlugin, PluginHook
from src.utils.logger import get_logger


class PluginManager:
    """
    Manages plugins for the assistant.
    
    Handles:
    - Plugin discovery
    - Plugin loading
    - Hook execution
    - Function registration
    """
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dir: Directory to search for plugins (default: src/plugins/)
        """
        self.logger = get_logger(__name__)
        self.plugin_dir = plugin_dir or Path(__file__).parent
        self.plugins: Dict[str, BasePlugin] = {}
        self.hooks: Dict[PluginHook, List[tuple]] = {}  # List of (plugin_name, callback) tuples
        self.logger.info(f"PluginManager initialized (plugin_dir: {self.plugin_dir})")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory.
        
        Returns:
            List of plugin module names
        """
        plugins = []
        
        # Look for Python files in plugin directory
        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "plugin_base.py" or file_path.name == "plugin_manager.py":
                continue
            
            module_name = file_path.stem
            plugins.append(module_name)
        
        self.logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins
    
    def load_plugin(self, module_name: str, assistant_core) -> Optional[BasePlugin]:
        """
        Load a plugin from a module.
        
        Args:
            module_name: Name of the plugin module
            assistant_core: AssistantCore instance to pass to plugin
            
        Returns:
            Loaded plugin instance, or None if loading failed
        """
        if module_name in self.plugins:
            self.logger.warning(f"Plugin '{module_name}' already loaded")
            return self.plugins[module_name]
        
        try:
            # Import the plugin module
            module = importlib.import_module(f"src.plugins.{module_name}")
            
            # Find plugin class (subclass of BasePlugin)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                self.logger.error(f"No plugin class found in {module_name}")
                return None
            
            # Instantiate plugin
            plugin = plugin_class()
            
            # Initialize plugin
            if not plugin.initialize(assistant_core):
                self.logger.error(f"Plugin '{module_name}' initialization failed")
                return None
            
            # Register plugin
            self.plugins[plugin.name] = plugin
            
            # Register hooks
            for hook, callbacks in plugin.get_hooks().items():
                if hook not in self.hooks:
                    self.hooks[hook] = []
                for callback in callbacks:
                    self.hooks[hook].append((plugin.name, callback))
            
            self.logger.info(f"Plugin '{plugin.name}' loaded successfully")
            return plugin
        
        except Exception as e:
            self.logger.error(f"Error loading plugin '{module_name}': {e}", exc_info=True)
            return None
    
    def load_all_plugins(self, assistant_core) -> List[BasePlugin]:
        """
        Discover and load all available plugins.
        
        Args:
            assistant_core: AssistantCore instance
            
        Returns:
            List of loaded plugins
        """
        plugin_names = self.discover_plugins()
        loaded = []
        
        for plugin_name in plugin_names:
            plugin = self.load_plugin(plugin_name, assistant_core)
            if plugin:
                loaded.append(plugin)
        
        self.logger.info(f"Loaded {len(loaded)}/{len(plugin_names)} plugins")
        return loaded
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a loaded plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance, or None if not found
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """
        Get all loaded plugins.
        
        Returns:
            List of plugin instances
        """
        return list(self.plugins.values())
    
    def get_all_functions(self) -> Dict[str, Dict]:
        """
        Get all functions from all plugins.
        
        Returns:
            Dictionary of function definitions keyed by function name
        """
        all_functions = {}
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            for func_name, func_def in plugin.get_functions().items():
                if func_name in all_functions:
                    self.logger.warning(f"Function '{func_name}' already registered by another plugin")
                all_functions[func_name] = func_def
        return all_functions
    
    def execute_hook(self, hook: PluginHook, *args, **kwargs) -> List[Any]:
        """
        Execute all callbacks registered for a hook.
        
        Args:
            hook: The hook to execute
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
            
        Returns:
            List of return values from callbacks
        """
        if hook not in self.hooks:
            return []
        
        results = []
        for plugin_name, callback in self.hooks[hook]:
            plugin = self.plugins.get(plugin_name)
            if plugin and not plugin.enabled:
                continue
            
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error executing hook {hook.value} in plugin '{plugin_name}': {e}", exc_info=True)
        
        return results
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.plugins:
            self.logger.warning(f"Plugin '{name}' not loaded")
            return False
        
        plugin = self.plugins[name]
        
        # Cleanup plugin
        plugin.cleanup()
        
        # Remove hooks
        for hook in list(self.hooks.keys()):
            self.hooks[hook] = [
                (pname, callback) 
                for pname, callback in self.hooks[hook] 
                if pname != name
            ]
            if not self.hooks[hook]:
                del self.hooks[hook]
        
        # Remove plugin
        del self.plugins[name]
        
        self.logger.info(f"Plugin '{name}' unloaded")
        return True
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.plugins:
            return False
        self.plugins[name].enable()
        return True
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.plugins:
            return False
        self.plugins[name].disable()
        return True

