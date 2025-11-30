"""
Test script for Audio Capture module.
"""

import sys
import time

def test_audio_capture_init():
    """Test audio capture initialization."""
    print("=" * 50)
    print("Testing Audio Capture Initialization")
    print("=" * 50)
    
    try:
        from src.backend.audio_capture import AudioCapture
        import sounddevice as sd
        
        print("\n1. Checking audio devices...")
        devices = sd.query_devices()
        print(f"   Found {len(devices)} audio devices")
        print(f"   Default input: {sd.default.device[0]}")
        print(f"   Default output: {sd.default.device[1]}")
        
        print("\n2. Initializing AudioCapture...")
        capture = AudioCapture(sample_rate=16000, frame_duration=30, vad_aggressiveness=3)
        
        print("\n✅ Audio Capture initialized successfully!")
        return capture
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_audio_capture_short(capture, duration: float = 2.0):
    """Test audio capture for a short duration."""
    print("\n" + "=" * 50)
    print(f"Testing Audio Capture ({duration}s)")
    print("=" * 50)
    print("\nThis will record audio for a short duration.")
    print("Speak into your microphone when prompted.\n")
    
    try:
        capture.start()
        
        print(f"🎤 Recording for {duration} seconds...")
        print("   Speak now!\n")
        
        speech_count = 0
        silence_count = 0
        total_chunks = 0
        
        start_time = time.time()
        for chunk in capture.get_audio_chunks():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
            
            has_speech = capture.detect_speech(chunk)
            total_chunks += 1
            
            if has_speech:
                speech_count += 1
                if speech_count <= 5:  # Only print first few
                    print(f"   🎤 Speech detected (chunk {total_chunks})")
            else:
                silence_count += 1
        
        capture.stop()
        
        print(f"\n✅ Recording complete!")
        print(f"\nStatistics:")
        print(f"   Total chunks: {total_chunks}")
        print(f"   Speech chunks: {speech_count} ({speech_count/total_chunks*100:.1f}%)")
        print(f"   Silence chunks: {silence_count} ({silence_count/total_chunks*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during capture: {e}")
        import traceback
        traceback.print_exc()
        capture.stop()
        return False

if __name__ == "__main__":
    # Test initialization
    capture = test_audio_capture_init()
    
    if capture is None:
        sys.exit(1)
    
    # Ask if user wants to test recording
    print("\n" + "=" * 50)
    response = input("Test audio recording? (y/n): ").strip().lower()
    
    if response == 'y':
        duration = 3.0
        try:
            duration_input = input(f"Recording duration in seconds (default {duration}): ").strip()
            if duration_input:
                duration = float(duration_input)
        except ValueError:
            print(f"Invalid input, using default: {duration}s")
        
        test_audio_capture_short(capture, duration)
    else:
        print("\n✅ Initialization test complete. Audio capture is ready to use.")

