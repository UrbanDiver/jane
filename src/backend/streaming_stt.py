"""
Streaming Speech-to-Text Integration

This module combines audio capture with STT engine for real-time
voice transcription.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel
from collections import deque
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Optional, Callable

from src.backend.audio_capture import AudioCapture
from src.backend.stt_engine import STTEngine
from src.config.config_schema import STTConfig
from src.utils.memory_manager import temp_file
from typing import Optional


class StreamingSTT:
    """
    Streaming Speech-to-Text that combines audio capture with transcription.
    
    Can work in two modes:
    1. Push-to-talk: Record for fixed duration and transcribe
    2. VAD-triggered: Automatically detect speech and transcribe
    """
    
    def __init__(
        self,
        config: Optional[STTConfig] = None,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        sample_rate: Optional[int] = None
    ):
        """
        Initialize streaming STT.
        
        Args:
            config: STTConfig object (takes precedence over individual params)
            model_size: Whisper model size
            device: Device ("cuda" or "cpu")
            compute_type: Computation type
            sample_rate: Audio sample rate
        """
        # Use config if provided, otherwise use individual params or defaults
        if config:
            model_size = config.model_size
            device = config.device
            compute_type = config.compute_type
            sample_rate = config.sample_rate
        else:
            model_size = model_size or "medium"
            device = device or "cuda"
            compute_type = compute_type or "float16"
            sample_rate = sample_rate or 16000
        
        print("Initializing Streaming STT...")
        
        # Initialize STT engine
        self.stt_engine = STTEngine(
            config=config,
            model_size=model_size,
            device=device,
            compute_type=compute_type
        )
        
        # Initialize audio capture
        self.audio_capture = AudioCapture(sample_rate=sample_rate)
        
        self.sample_rate = sample_rate
        self.is_listening = False
        
        print("Streaming STT initialized")
    
    def listen_and_transcribe(
        self,
        duration: float = 5.0,
        language: str = "en",
        beam_size: int = 5
    ) -> Dict:
        """
        Record for specified duration and transcribe.
        
        Args:
            duration: Recording duration in seconds
            language: Language code
            beam_size: Beam size for transcription
            
        Returns:
            Dictionary with transcription results
        """
        print(f"Recording for {duration} seconds...")
        
        try:
            # Record audio
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            
            print("Recording complete. Transcribing...")
            
            # Save to temp file (faster-whisper needs file path)
            with temp_file(suffix=".wav") as temp_path:
                sf.write(str(temp_path), audio, self.sample_rate)
                
                # Transcribe
                result = self.stt_engine.transcribe(
                    str(temp_path),
                    language=language,
                    beam_size=beam_size
                )
            
            # Temp file automatically cleaned up by context manager
            
            return result
            
        except Exception as e:
            print(f"❌ Error in listen_and_transcribe: {e}")
            raise
    
    def start_listening(
        self,
        on_transcription: Optional[Callable] = None,
        language: str = "en",
        beam_size: int = 5,
        speech_threshold: int = 3,
        silence_threshold: int = 10
    ):
        """
        Start continuous listening with VAD-triggered transcription.
        
        Args:
            on_transcription: Callback function called with transcription result
            language: Language code
            beam_size: Beam size for transcription
            speech_threshold: Frames of speech to trigger recording
            silence_threshold: Frames of silence to end recording
        """
        if self.is_listening:
            print("⚠️  Already listening!")
            return
        
        self.is_listening = True
        self.on_transcription = on_transcription
        self.language = language
        self.beam_size = beam_size
        
        # Start audio capture
        self.audio_capture.start()
        
        # Define speech end handler
        def on_speech_end(audio_array: np.ndarray):
            """Called when speech segment ends."""
            if not self.is_listening:
                return
            
            print(f"\n🎤 Processing speech segment ({len(audio_array) / self.sample_rate:.2f}s)...")
            
            try:
                # Save audio to temp file
                with temp_file(suffix=".wav") as temp_path:
                    sf.write(str(temp_path), audio_array, self.sample_rate)
                    
                    # Transcribe
                    result = self.stt_engine.transcribe(
                        str(temp_path),
                        language=self.language,
                        beam_size=self.beam_size
                    )
                
                # Temp file automatically cleaned up by context manager
                
                # Call callback
                if self.on_transcription:
                    self.on_transcription(result)
                else:
                    print(f"📝 Transcription: {result['text']}")
                
            except Exception as e:
                print(f"❌ Transcription error: {e}")
        
        # Start monitoring speech
        print("\n🎤 Listening for speech... (Ctrl+C to stop)")
        try:
            self.audio_capture.monitor_speech(
                speech_threshold=speech_threshold,
                silence_threshold=silence_threshold,
                on_speech_end=on_speech_end
            )
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.stop_listening()
    
    def stop_listening(self):
        """Stop continuous listening."""
        if not self.is_listening:
            return
        
        print("Stopping listening...")
        self.is_listening = False
        self.audio_capture.stop()
        print("Listening stopped")
    
    def transcribe_audio_file(self, audio_path: str, language: str = "en") -> Dict:
        """
        Transcribe an existing audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            Transcription result dictionary
        """
        return self.stt_engine.transcribe(audio_path, language=language)


if __name__ == "__main__":
    # Test streaming STT
    print("=" * 50)
    print("Testing Streaming STT")
    print("=" * 50)
    
    # Initialize with medium model for faster testing
    stt = StreamingSTT(model_size="medium")
    
    print("\nChoose test mode:")
    print("1. Push-to-talk (record for 5 seconds)")
    print("2. VAD-triggered (automatic speech detection)")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n" + "=" * 50)
            print("Push-to-Talk Test")
            print("=" * 50)
            print("Press Enter to start recording...")
            input()
            
            result = stt.listen_and_transcribe(duration=5)
            
            print("\n" + "=" * 50)
            print("Transcription Results")
            print("=" * 50)
            print(f"Text: {result['text']}")
            print(f"Language: {result['language']}")
            print(f"Processing time: {result['duration']:.2f}s")
            
        elif choice == "2":
            print("\n" + "=" * 50)
            print("VAD-Triggered Test")
            print("=" * 50)
            
            def on_transcription(result):
                print(f"\n📝 Transcription: {result['text']}")
                print(f"   Language: {result['language']}")
                print(f"   Time: {result['duration']:.2f}s")
            
            stt.start_listening(on_transcription=on_transcription)
            
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
        stt.stop_listening()

