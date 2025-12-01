"""
API Layer for Jane AI Voice Assistant

Provides REST API and WebSocket endpoints for interacting with the assistant.
"""

from src.api.main import create_app, get_app

__all__ = [
    "create_app",
    "get_app"
]

