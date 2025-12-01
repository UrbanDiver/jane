"""
Engine Interfaces

Abstract base classes for STT, TTS, and LLM engines.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Iterator, Any
from pathlib import Path


class STTEngineInterface(ABC):
    """
    Interface for Speech-to-Text engines.
    
    All STT engines must implement these methods.
    """
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results:
            {
                "text": str,  # Transcribed text
                "language": str,  # Detected language (optional)
                "time": float  # Processing time (optional)
            }
        """
        pass
    
    @abstractmethod
    def transcribe_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Audio data as bytes
            sample_rate: Audio sample rate in Hz
            
        Returns:
            Dictionary with transcription results (same format as transcribe)
        """
        pass
    
    @abstractmethod
    def listen_and_transcribe(self, duration: float = 5.0) -> Dict[str, Any]:
        """
        Listen for audio and transcribe in real-time.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Dictionary with transcription results (same format as transcribe)
        """
        pass


class TTSEngineInterface(ABC):
    """
    Interface for Text-to-Speech engines.
    
    All TTS engines must implement these methods.
    """
    
    @abstractmethod
    def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file
        """
        pass
    
    @abstractmethod
    def synthesize_to_bytes(self, text: str) -> bytes:
        """
        Synthesize speech from text and return as bytes.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        pass
    
    @abstractmethod
    def play(self, audio_path: str) -> None:
        """
        Play an audio file.
        
        Args:
            audio_path: Path to audio file to play
        """
        pass


class LLMEngineInterface(ABC):
    """
    Interface for Large Language Model engines.
    
    All LLM engines must implement these methods.
    """
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (optional)
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Chat with the LLM using a conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of function/tool definitions for function calling
            
        Returns:
            Dictionary with response:
            {
                "content": str,  # LLM response text
                "function_calls": List[Dict],  # Function calls if any (optional)
                "time": float  # Processing time (optional)
            }
        """
        pass
    
    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None
    ) -> Iterator[str]:
        """
        Stream chat responses token by token.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of function/tool definitions for function calling
            
        Yields:
            Text tokens as they are generated
        """
        pass

