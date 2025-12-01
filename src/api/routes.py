"""
REST API Routes for Jane AI Voice Assistant

Defines REST endpoints for interacting with the assistant.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.utils.logger import get_logger
from src.api.main import verify_api_key

router = APIRouter()
logger = get_logger(__name__)

# Global assistant instance (will be set by API initialization)
_assistant = None


def set_assistant(assistant):
    """Set the assistant instance for API routes."""
    global _assistant
    _assistant = assistant
    logger.info("Assistant instance set for API routes")


class TextRequest(BaseModel):
    """Request model for text input."""
    text: str
    stream: bool = False
    max_tokens: Optional[int] = None


class TextResponse(BaseModel):
    """Response model for text output."""
    response: str
    success: bool = True
    error: Optional[str] = None


class AudioRequest(BaseModel):
    """Request model for audio input."""
    audio_data: str  # Base64 encoded audio
    sample_rate: int = 16000


class FunctionCallRequest(BaseModel):
    """Request model for function call."""
    function_name: str
    arguments: Dict[str, Any] = {}


class FunctionCallResponse(BaseModel):
    """Response model for function call."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


@router.post("/chat", response_model=TextResponse)
async def chat(
    request: TextRequest,
    authenticated: bool = Depends(verify_api_key)
) -> TextResponse:
    """
    Process a text message and get assistant response.
    
    Args:
        request: Text request with message and options
        authenticated: Authentication status
        
    Returns:
        Assistant's text response
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        response = _assistant.process_command(
            user_input=request.text,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        return TextResponse(
            response=response,
            success=True
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return TextResponse(
            response="",
            success=False,
            error=str(e)
        )


@router.post("/transcribe", response_model=TextResponse)
async def transcribe(
    request: AudioRequest,
    authenticated: bool = Depends(verify_api_key)
) -> TextResponse:
    """
    Transcribe audio to text.
    
    Args:
        request: Audio request with base64 encoded audio
        authenticated: Authentication status
        
    Returns:
        Transcribed text
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        import base64
        import numpy as np
        import soundfile as sf
        import tempfile
        import os
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe using STT engine
            result = _assistant.stt.transcribe(tmp_path)
            text = result.get('text', '').strip()
            
            return TextResponse(
                response=text,
                success=True
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        return TextResponse(
            response="",
            success=False,
            error=str(e)
        )


@router.post("/synthesize", response_model=Dict[str, Any])
async def synthesize(
    text: str,
    authenticated: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Synthesize text to speech.
    
    Args:
        text: Text to synthesize
        authenticated: Authentication status
        
    Returns:
        Dictionary with audio data (base64 encoded) and metadata
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        import base64
        
        # Synthesize to bytes
        audio_bytes = _assistant.tts.synthesize_to_bytes(text)
        
        # Encode to base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "success": True,
            "audio": audio_b64,
            "format": "wav",
            "sample_rate": 22050  # TTS default
        }
    
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/functions/call", response_model=FunctionCallResponse)
async def call_function(
    request: FunctionCallRequest,
    authenticated: bool = Depends(verify_api_key)
) -> FunctionCallResponse:
    """
    Call a function directly.
    
    Args:
        request: Function call request
        authenticated: Authentication status
        
    Returns:
        Function call result
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        result = _assistant.function_handler.execute(
            function_name=request.function_name,
            arguments=request.arguments
        )
        
        return FunctionCallResponse(
            success=result.get('success', False),
            result=result.get('result'),
            error=result.get('error')
        )
    
    except Exception as e:
        logger.error(f"Error calling function: {e}", exc_info=True)
        return FunctionCallResponse(
            success=False,
            error=str(e)
        )


@router.get("/functions", response_model=List[Dict[str, Any]])
async def list_functions(
    authenticated: bool = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """
    List all available functions.
    
    Args:
        authenticated: Authentication status
        
    Returns:
        List of function definitions
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        functions = _assistant.function_handler.format_functions_for_llm()
        return functions
    
    except Exception as e:
        logger.error(f"Error listing functions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_status(
    authenticated: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get assistant status and information.
    
    Args:
        authenticated: Authentication status
        
    Returns:
        Dictionary with assistant status
    """
    if _assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        return {
            "status": "ready",
            "functions_count": len(_assistant.function_handler.list_functions()),
            "plugins_count": len(_assistant.plugin_manager.get_all_plugins()) if hasattr(_assistant, 'plugin_manager') else 0,
            "conversation_history_length": len(_assistant.conversation_history),
            "wake_word_enabled": _assistant.wake_word_detector is not None if hasattr(_assistant, 'wake_word_detector') else False
        }
    
    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

