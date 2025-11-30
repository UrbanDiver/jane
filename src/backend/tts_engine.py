"""
Text-to-Speech Engine using Coqui TTS

This module provides GPU-accelerated text-to-speech synthesis using Coqui TTS.
"""

import torch
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import time
from pathlib import Path
from typing import Optional, Dict, List
import tempfile
import os


class TTSEngine:
    """
    Text-to-Speech engine using Coqui TTS.
    
    Supports multiple TTS models with GPU acceleration.
    """
    
    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        device: Optional[str] = None
    ):
        """
        Initialize the TTS engine.
        
        Args:
            model_name: TTS model name (see TTS.list_models() for options)
            device: Device to use ("cuda" or "cpu"). Auto-detects if None.
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.model_name = model_name
        
        print(f"Loading TTS model: {model_name}")
        print(f"  Device: {device}")
        
        try:
            self.tts = TTS(model_name).to(device)
            print(f"✅ TTS model loaded successfully!")
            
            # Get model info
            self.speaker = None
            self.language = None
            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                self.speaker = self.tts.speakers[0] if len(self.tts.speakers) > 0 else None
            if hasattr(self.tts, 'language'):
                self.language = self.tts.language
            
        except Exception as e:
            print(f"❌ Error loading TTS model: {e}")
            raise
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        speaker: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Output file path (creates temp file if None)
            speaker: Speaker ID (for multi-speaker models)
            language: Language code (for multi-language models)
            
        Returns:
            Dictionary with synthesis results:
            {
                "output_path": str,      # Path to audio file
                "duration": float,        # Synthesis time in seconds
                "text": str,              # Original text
                "sample_rate": int        # Audio sample rate
            }
        """
        start_time = time.time()
        
        # Use temp file if no output path provided
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name
            temp_file = True
        else:
            temp_file = False
        
        try:
            # Synthesize
            if speaker and hasattr(self.tts, 'speakers') and speaker in self.tts.speakers:
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker=speaker
                )
            elif language and hasattr(self.tts, 'language'):
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language
                )
            else:
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            elapsed = time.time() - start_time
            
            # Get sample rate from audio file
            try:
                audio_data, sample_rate = sf.read(output_path)
            except:
                sample_rate = 22050  # Default for most TTS models
            
            result = {
                "output_path": output_path,
                "duration": elapsed,
                "text": text,
                "sample_rate": sample_rate,
                "is_temp": temp_file
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error during synthesis: {e}")
            # Cleanup temp file on error
            if temp_file and Path(output_path).exists():
                os.unlink(output_path)
            raise
    
    def speak(
        self,
        text: str,
        speaker: Optional[str] = None,
        language: Optional[str] = None,
        wait: bool = True
    ) -> Dict:
        """
        Synthesize and play audio.
        
        Args:
            text: Text to speak
            speaker: Speaker ID (for multi-speaker models)
            language: Language code (for multi-language models)
            wait: Whether to wait for playback to finish
            
        Returns:
            Dictionary with synthesis results
        """
        print(f"🔊 Speaking: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Synthesize
        result = self.synthesize(text, speaker=speaker, language=language)
        
        # Load and play audio
        try:
            audio_data, sample_rate = sf.read(result["output_path"])
            sd.play(audio_data, sample_rate)
            
            if wait:
                sd.wait()
            
            print(f"⏱️  TTS latency: {result['duration']:.2f}s")
            
            # Cleanup temp file
            if result.get("is_temp") and Path(result["output_path"]).exists():
                os.unlink(result["output_path"])
            
            return result
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            # Cleanup temp file on error
            if result.get("is_temp") and Path(result["output_path"]).exists():
                os.unlink(result["output_path"])
            raise
    
    def synthesize_to_bytes(
        self,
        text: str,
        speaker: Optional[str] = None,
        language: Optional[str] = None
    ) -> bytes:
        """
        Synthesize text to audio bytes.
        
        Args:
            text: Text to synthesize
            speaker: Speaker ID (for multi-speaker models)
            language: Language code (for multi-language models)
            
        Returns:
            Audio data as bytes (WAV format)
        """
        result = self.synthesize(text, speaker=speaker, language=language)
        
        try:
            with open(result["output_path"], "rb") as f:
                audio_bytes = f.read()
            
            # Cleanup
            if result.get("is_temp") and Path(result["output_path"]).exists():
                os.unlink(result["output_path"])
            
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Error reading audio bytes: {e}")
            if result.get("is_temp") and Path(result["output_path"]).exists():
                os.unlink(result["output_path"])
            raise
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "cuda_available": self.device == "cuda" and torch.cuda.is_available()
        }
        
        if self.speaker:
            info["speaker"] = self.speaker
        if self.language:
            info["language"] = self.language
        
        if hasattr(self.tts, 'speakers') and self.tts.speakers:
            info["available_speakers"] = list(self.tts.speakers)
        
        return info
    
    @staticmethod
    def list_models() -> List[str]:
        """List all available TTS models."""
        try:
            tts = TTS()
            models = tts.list_models()
            return models
        except Exception as e:
            print(f"⚠️  Error listing models: {e}")
            return []


if __name__ == "__main__":
    # Test the TTS engine
    print("=" * 60)
    print("Testing TTS Engine")
    print("=" * 60)
    
    # List available models
    print("\nAvailable TTS models:")
    models = TTSEngine.list_models()
    if models:
        print(f"  Found {len(models)} models")
        print("  Sample models:")
        for model in models[:5]:
            print(f"    - {model}")
    else:
        print("  Could not list models")
    
    # Initialize with default model
    print("\n" + "=" * 60)
    print("Initializing TTS engine...")
    print("=" * 60)
    
    try:
        tts = TTSEngine()
        
        # Display model info
        print("\nModel Information:")
        info = tts.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test synthesis
        print("\n" + "=" * 60)
        print("Testing Synthesis")
        print("=" * 60)
        
        test_phrases = [
            "Hello, I am your AI assistant.",
            "How can I help you today?",
            "I can control your computer, answer questions, and much more."
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\nTest {i}: '{phrase}'")
            result = tts.synthesize(phrase, output_path=f"test_tts_{i}.wav")
            print(f"  ✅ Synthesized in {result['duration']:.2f}s")
            print(f"  📁 Saved to: {result['output_path']}")
            
            # Optionally play
            play = input("  Play audio? (y/n): ").strip().lower()
            if play == 'y':
                tts.speak(phrase, wait=True)
        
        print("\n" + "=" * 60)
        print("✅ TTS Engine test complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

