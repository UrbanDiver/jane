"""
Simple script to record test audio for STT engine testing.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import time

def record_audio(duration: int = 5, sample_rate: int = 16000, output_file: str = "test_audio.wav"):
    """
    Record audio from the default microphone.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate (16000 is optimal for Whisper)
        output_file: Output file path
    """
    print("=" * 50)
    print("Audio Recording Test")
    print("=" * 50)
    print(f"\nRecording settings:")
    print(f"  Duration: {duration} seconds")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Output: {output_file}")
    
    # List available audio devices
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    print(f"  Default input device: {sd.default.device[0]}")
    print(f"  Default output device: {sd.default.device[1]}")
    
    print("\n" + "=" * 50)
    print("Recording will start in 3 seconds...")
    print("Speak clearly into your microphone.")
    print("=" * 50)
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\n🎤 Recording NOW! Speak something...")
    
    try:
        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait until recording is finished
        
        print("✅ Recording complete!")
        
        # Save to file
        sf.write(output_file, audio, sample_rate)
        print(f"✅ Audio saved to: {output_file}")
        
        # Display some info
        print(f"\nAudio info:")
        print(f"  Duration: {len(audio) / sample_rate:.2f} seconds")
        print(f"  Samples: {len(audio)}")
        print(f"  Max amplitude: {np.max(np.abs(audio)):.4f}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error during recording: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    # Get duration from command line or use default
    duration = 5
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}. Using default: 5 seconds")
    
    record_audio(duration=duration)

