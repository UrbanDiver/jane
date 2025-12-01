"""
API Server Entry Point

Starts the FastAPI server with uvicorn.
"""

import uvicorn
import argparse
from src.api.main import create_app
from typing import Optional
from src.backend.assistant_core import AssistantCore
from src.config import get_config
from src.utils.logger import get_logger


def create_api_server(
    assistant: Optional[AssistantCore] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    api_key: Optional[str] = None,
    reload: bool = False
):
    """
    Create and configure API server.
    
    Args:
        assistant: AssistantCore instance (creates one if not provided)
        host: Server host
        port: Server port
        api_key: Optional API key for authentication
        reload: Enable auto-reload for development
        
    Returns:
        Configured FastAPI application
    """
    logger = get_logger(__name__)
    
    # Create assistant if not provided
    if assistant is None:
        logger.info("Creating AssistantCore instance...")
        config = get_config()
        assistant = AssistantCore(config=config)
        logger.info("AssistantCore created")
    
    # Create FastAPI app
    app = create_app(api_key=api_key)
    
    # Set assistant instance for routes and WebSocket
    from src.api.routes import set_assistant
    from src.api.websocket import websocket_manager
    
    set_assistant(assistant)
    websocket_manager.set_assistant(assistant)
    
    logger.info(f"API server configured: http://{host}:{port}")
    logger.info(f"API documentation: http://{host}:{port}/docs")
    logger.info(f"WebSocket endpoint: ws://{host}:{port}/ws")
    
    return app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    api_key: Optional[str] = None,
    reload: bool = False
):
    """
    Run the API server.
    
    Args:
        host: Server host
        port: Server port
        api_key: Optional API key for authentication
        reload: Enable auto-reload for development
    """
    app = create_api_server(
        host=host,
        port=port,
        api_key=api_key,
        reload=reload
    )
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jane AI Voice Assistant API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    run_server(
        host=args.host,
        port=args.port,
        api_key=args.api_key,
        reload=args.reload
    )

