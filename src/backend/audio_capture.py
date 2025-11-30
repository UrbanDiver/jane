"""
Real-time Audio Capture with Voice Activity Detection (VAD)

This module provides continuous audio capture with WebRTC VAD for
detecting speech vs silence.
"""

import sounddevice as sd
import numpy as np
import webrtcvad
from collections import deque
import queue
import threading
from typing import Optional, Callable
import time


class AudioCapture:
    """
    Real-time audio capture with Voice Activity Detection.
    
    Continuously captures audio and uses VAD to detect speech segments.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration: int = 30,
        vad_aggressiveness: int = 3,
        channels: int = 1
    ):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate (16000 Hz recommended for Whisper)
            frame_duration: Frame duration in milliseconds (10, 20, or 30)
            vad_aggressiveness: VAD aggressiveness (0-3, 3 is most aggressive)
            channels: Number of audio channels (1 = mono, 2 = stereo)
        """
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.channels = channels
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        
        # Audio buffer
        self.audio_queue = queue.Queue(maxsize=100)
        self.audio_buffer = deque(maxlen=1000)  # Store recent audio chunks
        
        # State
        self.is_recording = False
        self.stream = None
        self._thread = None
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        
        print(f"AudioCapture initialized:")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Frame duration: {frame_duration} ms")
        print(f"  Frame size: {self.frame_size} samples")
        print(f"  VAD aggressiveness: {vad_aggressiveness}")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function called for each audio chunk.
        
        This is called by sounddevice for each audio frame.
        """
        if status:
            print(f"⚠️  Audio callback status: {status}")
        
        # Copy audio data (indata is a reference that gets reused)
        audio_chunk = indata.copy()
        
        # Add to queue
        try:
            self.audio_queue.put_nowait(audio_chunk)
        except queue.Full:
            print("⚠️  Audio queue full, dropping frame")
        
        # Add to buffer
        self.audio_buffer.append(audio_chunk)
    
    def start(self):
        """Start continuous audio capture."""
        if self.is_recording:
            print("⚠️  Already recording!")
            return
        
        print("Starting audio capture...")
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.frame_size,
                callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start()
            print("✅ Audio capture started")
            
        except Exception as e:
            print(f"❌ Error starting audio capture: {e}")
            self.is_recording = False
            raise
    
    def stop(self):
        """Stop audio capture."""
        if not self.is_recording:
            return
        
        print("Stopping audio capture...")
        self.is_recording = False
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"⚠️  Error stopping stream: {e}")
        
        self.stream = None
        print("✅ Audio capture stopped")
    
    def detect_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect speech in audio chunk using VAD.
        
        Args:
            audio_chunk: Audio data as numpy array (float32, shape: [samples] or [samples, channels])
            
        Returns:
            True if speech detected, False otherwise
        """
        # Convert to int16 (required by VAD)
        if audio_chunk.dtype != np.int16:
            # Normalize to [-1, 1] range, then convert to int16
            if audio_chunk.dtype == np.float32:
                # Clip to valid range
                audio_chunk = np.clip(audio_chunk, -1.0, 1.0)
                # Convert to int16
                audio_chunk = (audio_chunk * 32767).astype(np.int16)
            else:
                audio_chunk = audio_chunk.astype(np.int16)
        
        # Handle multi-channel audio (take first channel)
        if len(audio_chunk.shape) > 1:
            audio_chunk = audio_chunk[:, 0]
        
        # Ensure correct length for frame duration
        expected_length = self.frame_size
        if len(audio_chunk) != expected_length:
            # Pad or truncate if necessary
            if len(audio_chunk) < expected_length:
                audio_chunk = np.pad(audio_chunk, (0, expected_length - len(audio_chunk)))
            else:
                audio_chunk = audio_chunk[:expected_length]
        
        # Convert to bytes
        audio_bytes = audio_chunk.tobytes()
        
        try:
            return self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception as e:
            print(f"⚠️  VAD error: {e}")
            return False
    
    def get_audio_chunks(self, timeout: float = 0.1):
        """
        Generator that yields audio chunks from the queue.
        
        Args:
            timeout: Timeout in seconds for getting chunks
            
        Yields:
            Audio chunks as numpy arrays
        """
        while self.is_recording:
            try:
                chunk = self.audio_queue.get(timeout=timeout)
                yield chunk
            except queue.Empty:
                continue
    
    def get_recent_audio(self, duration_seconds: float) -> Optional[np.ndarray]:
        """
        Get recent audio from buffer.
        
        Args:
            duration_seconds: Duration of audio to retrieve in seconds
            
        Returns:
            Concatenated audio array or None if not enough audio
        """
        samples_needed = int(duration_seconds * self.sample_rate)
        chunks_needed = int(samples_needed / self.frame_size) + 1
        
        if len(self.audio_buffer) < chunks_needed:
            return None
        
        # Get recent chunks
        recent_chunks = list(self.audio_buffer)[-chunks_needed:]
        
        # Concatenate
        audio = np.concatenate(recent_chunks, axis=0)
        
        # Trim to exact duration
        if len(audio) > samples_needed:
            audio = audio[-samples_needed:]
        
        return audio
    
    def monitor_speech(
        self,
        speech_threshold: int = 3,
        silence_threshold: int = 10,
        on_speech_start: Optional[Callable] = None,
        on_speech_end: Optional[Callable] = None
    ):
        """
        Monitor audio stream for speech segments.
        
        Args:
            speech_threshold: Number of consecutive speech frames to trigger speech start
            silence_threshold: Number of consecutive silence frames to trigger speech end
            on_speech_start: Callback when speech starts (called with audio chunk)
            on_speech_end: Callback when speech ends (called with audio array)
        """
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        
        speech_frames = 0
        silence_frames = 0
        in_speech = False
        speech_audio = []
        
        print(f"Monitoring speech... (speech threshold: {speech_threshold}, silence: {silence_threshold})")
        
        for chunk in self.get_audio_chunks():
            has_speech = self.detect_speech(chunk)
            
            if has_speech:
                speech_frames += 1
                silence_frames = 0
                
                if not in_speech:
                    if speech_frames >= speech_threshold:
                        # Speech started
                        in_speech = True
                        speech_audio = [chunk]
                        print("🎤 Speech detected!")
                        
                        if self.on_speech_start:
                            self.on_speech_start(chunk)
                else:
                    # Continue speech
                    speech_audio.append(chunk)
            else:
                silence_frames += 1
                speech_frames = 0
                
                if in_speech:
                    if silence_frames >= silence_threshold:
                        # Speech ended
                        in_speech = False
                        audio_array = np.concatenate(speech_audio, axis=0)
                        print(f"🔇 Speech ended ({len(audio_array) / self.sample_rate:.2f}s)")
                        
                        if self.on_speech_end:
                            self.on_speech_end(audio_array)
                        
                        speech_audio = []
                else:
                    # Continue silence
                    pass


if __name__ == "__main__":
    # Test audio capture
    print("=" * 50)
    print("Testing Audio Capture with VAD")
    print("=" * 50)
    
    capture = AudioCapture(sample_rate=16000, frame_duration=30, vad_aggressiveness=3)
    
    try:
        capture.start()
        
        print("\nListening... Speak to test VAD (Ctrl+C to stop)")
        print("You should see '🎤 Speech detected!' when you speak")
        print("and '🔇 Speech ended' when you stop.\n")
        
        speech_count = 0
        silence_count = 0
        
        for chunk in capture.get_audio_chunks():
            has_speech = capture.detect_speech(chunk)
            
            if has_speech:
                speech_count += 1
                if speech_count % 10 == 0:
                    print(f"🎤 Speech detected! ({speech_count} frames)")
            else:
                silence_count += 1
                if silence_count % 100 == 0:
                    print(f"🔇 Silence... ({silence_count} frames)")
                    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        capture.stop()
        print("✅ Test complete")

