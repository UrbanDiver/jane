"""
WebSocket Manager for Real-time Communication

Handles WebSocket connections for real-time assistant interaction.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from src.utils.logger import get_logger


class WebSocketManager:
    """
    Manages WebSocket connections for real-time communication.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Set[WebSocket] = set()
        self.logger = get_logger(__name__)
        self._assistant = None
    
    def set_assistant(self, assistant):
        """Set the assistant instance."""
        self._assistant = assistant
        self.logger.info("Assistant instance set for WebSocket manager")
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to Jane AI Voice Assistant"
        }))
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def handle_text_message(self, text: str) -> Dict[str, Any]:
        """
        Handle a text message from WebSocket.
        
        Args:
            text: Text message from client
            
        Returns:
            Response dictionary
        """
        if not self._assistant:
            return {
                "type": "error",
                "message": "Assistant not initialized"
            }
        
        try:
            # Process command
            response = self._assistant.process_command(
                user_input=text,
                stream=False
            )
            
            return {
                "type": "response",
                "text": response,
                "success": True
            }
        
        except Exception as e:
            self.logger.error(f"Error handling text message: {e}", exc_info=True)
            return {
                "type": "error",
                "message": str(e),
                "success": False
            }
    
    async def handle_audio_message(self, audio_data: str) -> Dict[str, Any]:
        """
        Handle an audio message from WebSocket.
        
        Args:
            audio_data: Base64 encoded audio data
            
        Returns:
            Response dictionary
        """
        if not self._assistant:
            return {
                "type": "error",
                "message": "Assistant not initialized"
            }
        
        try:
            import base64
            import tempfile
            import os
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe
                result = self._assistant.stt.transcribe(tmp_path)
                text = result.get('text', '').strip()
                
                if text:
                    # Process command
                    response = self._assistant.process_command(
                        user_input=text,
                        stream=False
                    )
                    
                    return {
                        "type": "response",
                        "transcription": text,
                        "response": response,
                        "success": True
                    }
                else:
                    return {
                        "type": "error",
                        "message": "No speech detected in audio",
                        "success": False
                    }
            
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        except Exception as e:
            self.logger.error(f"Error handling audio message: {e}", exc_info=True)
            return {
                "type": "error",
                "message": str(e),
                "success": False
            }
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message dictionary to broadcast
        """
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                self.logger.warning(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

