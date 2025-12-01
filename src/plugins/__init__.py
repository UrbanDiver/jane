"""
Plugin System for Jane AI Voice Assistant

This module provides a plugin architecture that allows third-party extensions
to add functionality to the assistant.
"""

from src.plugins.plugin_base import BasePlugin, PluginHook
from src.plugins.plugin_manager import PluginManager

__all__ = [
    "BasePlugin",
    "PluginHook",
    "PluginManager"
]

