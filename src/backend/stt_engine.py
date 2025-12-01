"""
Speech-to-Text Engine using Faster-Whisper

This module provides GPU-accelerated speech transcription using Faster-Whisper,
which is an optimized implementation of OpenAI's Whisper model.
"""

from faster_whisper import WhisperModel
import time
from pathlib import Path
from typing import Dict, Optional
from src.config.config_schema import STTConfig
from src.utils.logger import get_logger, log_performance, log_timing
from src.utils.retry import retry
from src.utils.error_handler import handle_error, ErrorType
from src.utils.memory_manager import get_memory_manager
from src.interfaces.engines import STTEngineInterface

# Global model cache
_model_cache: Dict[str, WhisperModel] = {}


class STTEngine(STTEngineInterface):
    """
    Speech-to-Text engine using Faster-Whisper.
    
    Supports GPU acceleration and various model sizes for different
    accuracy/speed trade-offs.
    """
    
    def __init__(
        self,
        config: Optional[STTConfig] = None,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        num_workers: Optional[int] = None,
        use_cache: bool = True,
        auto_quantize: bool = True
    ):
        """
        Initialize the STT engine.
        
        Args:
            config: STTConfig object (takes precedence over individual params)
            model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to use ("cuda" or "cpu")
            compute_type: Computation type ("float16", "int8", "int8_float16")
            num_workers: Number of workers for processing
            use_cache: Whether to use cached model if available
            auto_quantize: Whether to auto-select quantization based on GPU memory
        """
        # Use config if provided, otherwise use individual params or defaults
        if config:
            model_size = config.model_size
            device = config.device
            compute_type = config.compute_type
            num_workers = config.num_workers
        else:
            # Use provided params or defaults
            model_size = model_size or "medium"
            device = device or "cuda"
            compute_type = compute_type or "float16"
            num_workers = num_workers or 4
        
        # Store device early for auto-quantization check
        self.device = device
        self.logger = get_logger(__name__)
        
        # Auto-select quantization if enabled
        if auto_quantize:
            compute_type = self._auto_select_quantization(compute_type)
        
        # Check cache
        cache_key = f"{model_size}_{device}_{compute_type}"
        if use_cache and cache_key in _model_cache:
            self.logger.info(f"Using cached Whisper {model_size} model")
            self.model = _model_cache[cache_key]
        else:
            self.logger.info(f"Loading Whisper {model_size} on {device}...")
            self.logger.debug(f"  Compute type: {compute_type}")
            self.logger.debug(f"  Workers: {num_workers}")
            
            try:
                with log_timing(f"Whisper model loading ({model_size})", self.logger):
                    self.model = WhisperModel(
                        model_size,
                        device=device,
                        compute_type=compute_type,
                        num_workers=num_workers
                    )
                
                # Cache the model
                if use_cache:
                    _model_cache[cache_key] = self.model
                    self.logger.debug(f"Cached model: {cache_key}")
                
                self.logger.info(f"✅ Whisper model loaded successfully!")
                
            except Exception as e:
                self.logger.error(f"❌ Error loading Whisper model: {e}", exc_info=True)
                raise
        
        # Store configuration
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.num_workers = num_workers
    
    def _auto_select_quantization(self, preferred: str) -> str:
        """
        Auto-select quantization based on GPU memory availability.
        
        Args:
            preferred: Preferred compute type
        
        Returns:
            Selected compute type
        """
        # CPU only supports int8
        if self.device == "cpu":
            if preferred not in ["int8", "float32"]:
                self.logger.info(f"CPU device detected, using int8 instead of {preferred}")
                return "int8"
            return preferred
        
        try:
            memory_manager = get_memory_manager()
            gpu_info = memory_manager.get_gpu_memory_info()
            
            if gpu_info:
                free_gb = gpu_info.get("free_gb", 0)
                
                # If low on GPU memory, use int8
                if free_gb < 2.0:
                    self.logger.info(f"Low GPU memory ({free_gb:.2f}GB free), using int8 quantization")
                    return "int8"
                elif free_gb < 4.0:
                    self.logger.info(f"Moderate GPU memory ({free_gb:.2f}GB free), using int8_float16")
                    return "int8_float16"
                else:
                    self.logger.debug(f"Sufficient GPU memory ({free_gb:.2f}GB free), using {preferred}")
                    return preferred
            else:
                # No GPU info, use preferred
                return preferred
        except Exception as e:
            self.logger.warning(f"Could not determine GPU memory, using {preferred}: {e}")
            return preferred
    
    @log_performance("STT Transcription")
    @retry(max_retries=2, initial_delay=1.0, retryable_exceptions=(RuntimeError, OSError))
    def transcribe(
        self,
        audio_path: str,
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = True,
        initial_prompt: Optional[str] = None,
        chunk_length_s: Optional[float] = None
    ) -> Dict:
        """
        Transcribe audio from a file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en", "es", "fr")
            beam_size: Beam size for beam search (higher = more accurate, slower)
            vad_filter: Enable voice activity detection filter
            initial_prompt: Optional text prompt to guide transcription
            
        Returns:
            Dictionary with transcription results:
            {
                "text": str,           # Transcribed text
                "language": str,       # Detected language
                "duration": float,      # Processing time in seconds
                "segments": list       # List of segment dictionaries
            }
        """
        if not Path(audio_path).exists():
            self.logger.error(f"Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        self.logger.debug(f"Transcribing audio: {audio_path}")
        self.logger.debug(f"  Language: {language}, Beam size: {beam_size}, VAD: {vad_filter}")
        
        try:
            # Use chunked processing for long audio
            transcribe_kwargs = {
                "language": language,
                "beam_size": beam_size,
                "vad_filter": vad_filter
            }
            
            if initial_prompt:
                transcribe_kwargs["initial_prompt"] = initial_prompt
            
            # Add chunk length if specified (faster-whisper uses seconds)
            if chunk_length_s is not None:
                transcribe_kwargs["chunk_length"] = chunk_length_s
            
            segments, info = self.model.transcribe(
                audio_path,
                **transcribe_kwargs
            )
            
            # Collect segments
            segment_list = []
            text_parts = []
            
            for segment in segments:
                segment_dict = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                segment_list.append(segment_dict)
                text_parts.append(segment.text.strip())
            
            # Combine all text
            full_text = " ".join(text_parts)
            
            result = {
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": 0,  # Will be set by decorator
                "segments": segment_list,
                "audio_duration": info.duration if hasattr(info, 'duration') else None
            }
            
            self.logger.info(f"Transcription complete: {len(full_text)} characters, "
                           f"language: {info.language} ({info.language_probability:.2%})")
            
            return result
            
        except Exception as e:
            error_info = handle_error(e, context={"audio_path": audio_path, "language": language}, logger=self.logger)
            self.logger.error(f"❌ Error during transcription: {error_info['message']}", exc_info=True)
            raise
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = True,
        chunk_length_s: Optional[float] = None
    ) -> Dict:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            sample_rate: Sample rate of audio (default 16000 for Whisper)
            language: Language code
            beam_size: Beam size for beam search
            vad_filter: Enable voice activity detection filter
            chunk_length_s: Optional chunk length in seconds for long audio
        
        Returns:
            Dictionary with transcription results
        """
        import soundfile as sf
        import numpy as np
        from src.utils.memory_manager import temp_file
        
        try:
            # Convert bytes to numpy array (optimized - no copy if possible)
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Save to temporary file (faster-whisper needs file path)
            with temp_file(suffix=".wav") as temp_path:
                sf.write(str(temp_path), audio_array, sample_rate)
                
                # Transcribe with chunked processing if needed
                result = self.transcribe(
                    str(temp_path),
                    language=language,
                    beam_size=beam_size,
                    vad_filter=vad_filter,
                    chunk_length_s=chunk_length_s
                )
            
            # Temp file automatically cleaned up by context manager
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error transcribing bytes: {e}", exc_info=True)
            raise
    
    @staticmethod
    def clear_cache():
        """Clear the model cache."""
        global _model_cache
        _model_cache.clear()
        logger = get_logger(__name__)
        logger.info("STT model cache cleared")
    
    @staticmethod
    def get_cache_size() -> int:
        """Get the number of cached models."""
        return len(_model_cache)
    
    def listen_and_transcribe(self, duration: float = 5.0) -> Dict:
        """
        Listen for audio and transcribe in real-time.
        
        Note: This is a convenience method that uses StreamingSTT internally.
        For better control, use StreamingSTT directly.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Dictionary with transcription results (same format as transcribe)
        """
        # Import here to avoid circular dependency
        from src.backend.streaming_stt import StreamingSTT
        
        # Create a temporary StreamingSTT instance for this operation
        streaming_stt = StreamingSTT(
            config=self.config,
            model_size=self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )
        
        return streaming_stt.listen_and_transcribe(duration=duration)
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "cuda_available": self.device == "cuda"
        }


if __name__ == "__main__":
    # Test the STT engine
    print("=" * 50)
    print("Testing STT Engine")
    print("=" * 50)
    
    # Initialize with medium model for testing (faster than large-v3)
    print("\nInitializing STT engine with 'medium' model...")
    engine = STTEngine(model_size="medium", device="cuda", compute_type="float16")
    
    # Display model info
    print("\nModel Information:")
    info = engine.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("STT Engine ready!")
    print("=" * 50)
    print("\nTo test transcription, provide an audio file:")
    print("  result = engine.transcribe('path/to/audio.wav')")
    print("  print(result['text'])")

