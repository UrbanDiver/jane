"""
FastAPI Application for Jane AI Voice Assistant

Main API application with REST and WebSocket endpoints.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import json
import asyncio
from src.utils.logger import get_logger
from src.api.routes import router
from src.api.websocket import websocket_manager


# Security
security = HTTPBearer(auto_error=False)

# Global app instance
_app: Optional[FastAPI] = None


def create_app(
    title: str = "Jane AI Voice Assistant API",
    version: str = "1.0.0",
    description: str = "REST API and WebSocket interface for Jane AI Voice Assistant",
    enable_cors: bool = True,
    api_key: Optional[str] = None
) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        title: API title
        version: API version
        description: API description
        enable_cors: Enable CORS middleware
        api_key: Optional API key for authentication (None = no auth)
        
    Returns:
        Configured FastAPI application
    """
    global _app
    
    app = FastAPI(
        title=title,
        version=version,
        description=description
    )
    
    logger = get_logger(__name__)
    
    # CORS middleware
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("CORS middleware enabled")
    
    # Store API key for authentication
    app.state.api_key = api_key
    
    # Include routers
    app.include_router(router, prefix="/api/v1", tags=["assistant"])
    
    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time communication.
        
        Supports:
        - Text messages
        - Voice commands (audio data)
        - Streaming responses
        """
        await websocket_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get("type", "text")
                
                if message_type == "text":
                    # Text command
                    text = message.get("text", "")
                    response = await websocket_manager.handle_text_message(text)
                    await websocket.send_text(json.dumps(response))
                
                elif message_type == "audio":
                    # Audio command (base64 encoded)
                    audio_data = message.get("audio", "")
                    response = await websocket_manager.handle_audio_message(audio_data)
                    await websocket.send_text(json.dumps(response))
                
                elif message_type == "ping":
                    # Keep-alive
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": version,
            "service": "Jane AI Voice Assistant API"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": title,
            "version": version,
            "description": description,
            "endpoints": {
                "health": "/health",
                "api_docs": "/docs",
                "websocket": "/ws"
            }
        }
    
    _app = app
    logger.info(f"FastAPI application created: {title} v{version}")
    
    return app


def get_app() -> Optional[FastAPI]:
    """
    Get the global FastAPI application instance.
    
    Returns:
        FastAPI application or None if not created
    """
    return _app


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> bool:
    """
    Verify API key for authentication.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        True if authenticated, False otherwise
        
    Raises:
        HTTPException: If authentication fails
    """
    app = get_app()
    
    if app is None or app.state.api_key is None:
        # No authentication required
        return True
    
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if credentials.credentials != app.state.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

