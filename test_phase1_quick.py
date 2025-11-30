"""
Quick non-interactive test for Phase 1 components.
Tests initialization and basic functionality without requiring user input.
"""

import sys
import time

def test_stt_engine():
    """Test STT engine initialization."""
    print("=" * 60)
    print("Test 1: STT Engine")
    print("=" * 60)
    
    try:
        from src.backend.stt_engine import STTEngine
        
        print("\nInitializing STT engine with 'medium' model...")
        engine = STTEngine(model_size="medium", device="cuda", compute_type="float16")
        
        info = engine.get_model_info()
        print("\n✅ STT Engine initialized successfully!")
        print(f"   Model: {info['model_size']}")
        print(f"   Device: {info['device']}")
        print(f"   CUDA: {info['cuda_available']}")
        
        return True, engine
        
    except Exception as e:
        print(f"\n❌ STT Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_audio_capture_init():
    """Test audio capture initialization."""
    print("\n" + "=" * 60)
    print("Test 2: Audio Capture Initialization")
    print("=" * 60)
    
    try:
        from src.backend.audio_capture import AudioCapture
        import sounddevice as sd
        
        print("\nChecking audio devices...")
        devices = sd.query_devices()
        print(f"   Found {len(devices)} audio devices")
        print(f"   Default input: {sd.default.device[0]}")
        
        print("\nInitializing AudioCapture...")
        capture = AudioCapture(sample_rate=16000, frame_duration=30, vad_aggressiveness=3)
        
        print("\n✅ Audio Capture initialized successfully!")
        print(f"   Sample rate: {capture.sample_rate} Hz")
        print(f"   Frame duration: {capture.frame_duration} ms")
        
        return True, capture
        
    except Exception as e:
        print(f"\n❌ Audio Capture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_streaming_stt_init():
    """Test streaming STT initialization."""
    print("\n" + "=" * 60)
    print("Test 3: Streaming STT Initialization")
    print("=" * 60)
    
    try:
        from src.backend.streaming_stt import StreamingSTT
        
        print("\nInitializing Streaming STT...")
        # This will initialize both STT engine and audio capture
        stt = StreamingSTT(model_size="medium")
        
        print("\n✅ Streaming STT initialized successfully!")
        print(f"   Sample rate: {stt.sample_rate} Hz")
        print(f"   STT engine ready: {stt.stt_engine is not None}")
        print(f"   Audio capture ready: {stt.audio_capture is not None}")
        
        return True, stt
        
    except Exception as e:
        print(f"\n❌ Streaming STT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_module_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("Test 0: Module Imports")
    print("=" * 60)
    
    modules = [
        "src.backend.stt_engine",
        "src.backend.audio_capture",
        "src.backend.streaming_stt"
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all quick tests."""
    print("\n" + "=" * 60)
    print("Phase 1 Quick Test Suite")
    print("=" * 60)
    print("\nThis test verifies initialization without requiring user input.")
    print("For full testing with audio, use the individual test scripts.\n")
    
    results = {}
    
    # Test 0: Imports
    results['imports'] = test_module_imports()
    
    # Test 1: STT Engine
    results['stt'], engine = test_stt_engine()
    
    # Test 2: Audio Capture
    results['audio'], capture = test_audio_capture_init()
    
    # Test 3: Streaming STT
    results['streaming'], stt = test_streaming_stt_init()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name.upper()}: {status}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All Phase 1 components initialized successfully!")
        print("\nNext steps:")
        print("  1. Test audio capture: python test_audio_capture.py")
        print("  2. Record test audio: python record_test_audio.py")
        print("  3. Test transcription: python test_stt_engine.py test_audio.wav")
        print("  4. Test streaming: python src/backend/streaming_stt.py")
    else:
        print("❌ Some tests failed. Check errors above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()

