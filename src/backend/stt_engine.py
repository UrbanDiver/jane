"""
Speech-to-Text Engine using Faster-Whisper

This module provides GPU-accelerated speech transcription using Faster-Whisper,
which is an optimized implementation of OpenAI's Whisper model.
"""

from faster_whisper import WhisperModel
import time
from pathlib import Path
from typing import Dict, Optional


class STTEngine:
    """
    Speech-to-Text engine using Faster-Whisper.
    
    Supports GPU acceleration and various model sizes for different
    accuracy/speed trade-offs.
    """
    
    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
        num_workers: int = 4
    ):
        """
        Initialize the STT engine.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
            device: Device to use ("cuda" or "cpu")
            compute_type: Computation type ("float16", "int8", "int8_float16")
            num_workers: Number of workers for processing
        """
        print(f"Loading Whisper {model_size} on {device}...")
        print(f"  Compute type: {compute_type}")
        print(f"  Workers: {num_workers}")
        
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=num_workers
            )
            print(f"✅ Whisper model loaded successfully!")
            
            # Store configuration
            self.model_size = model_size
            self.device = device
            self.compute_type = compute_type
            
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = True,
        initial_prompt: Optional[str] = None
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
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        start_time = time.time()
        
        try:
            # Transcribe with options
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=beam_size,
                vad_filter=vad_filter,
                initial_prompt=initial_prompt
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
            elapsed = time.time() - start_time
            
            return {
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": elapsed,
                "segments": segment_list,
                "audio_duration": info.duration if hasattr(info, 'duration') else None
            }
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            raise
    
    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = True
    ) -> Dict:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            sample_rate: Sample rate of audio (default 16000 for Whisper)
            language: Language code
            beam_size: Beam size for beam search
            vad_filter: Enable voice activity detection filter
            
        Returns:
            Dictionary with transcription results
        """
        import tempfile
        import soundfile as sf
        import numpy as np
        
        start_time = time.time()
        
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Save to temporary file (faster-whisper needs file path)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                sf.write(temp_path, audio_array, sample_rate)
            
            # Transcribe
            result = self.transcribe(
                temp_path,
                language=language,
                beam_size=beam_size,
                vad_filter=vad_filter
            )
            
            # Cleanup
            Path(temp_path).unlink()
            
            return result
            
        except Exception as e:
            print(f"❌ Error transcribing bytes: {e}")
            raise
    
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

