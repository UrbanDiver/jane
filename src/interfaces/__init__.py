"""
Interfaces for Jane AI Voice Assistant

This module defines abstract base classes (interfaces) for all major components,
making the system more extensible and testable.
"""

from src.interfaces.engines import (
    STTEngineInterface,
    TTSEngineInterface,
    LLMEngineInterface
)
from src.interfaces.controllers import (
    FileControllerInterface,
    AppControllerInterface,
    InputControllerInterface
)
from src.interfaces.function_handler import FunctionHandlerInterface

__all__ = [
    "STTEngineInterface",
    "TTSEngineInterface",
    "LLMEngineInterface",
    "FileControllerInterface",
    "AppControllerInterface",
    "InputControllerInterface",
    "FunctionHandlerInterface"
]

