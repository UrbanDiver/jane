"""
Test script for TTS Engine.

Tests TTS engine initialization and basic functionality.
"""

import sys
from pathlib import Path

def test_tts_engine_init():
    """Test TTS engine initialization."""
    print("=" * 60)
    print("Testing TTS Engine Initialization")
    print("=" * 60)
    
    try:
        from src.backend.tts_engine import TTSEngine
        import torch
        
        print("\n1. Checking CUDA availability...")
        cuda_available = torch.cuda.is_available()
        print(f"   CUDA available: {cuda_available}")
        if cuda_available:
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
        print("\n2. Listing available TTS models...")
        models = TTSEngine.list_models()
        if models:
            print(f"   Found {len(models)} models")
            print("   Sample models:")
            for model in models[:5]:
                print(f"     - {model}")
        else:
            print("   Could not list models (will try default)")
        
        print("\n3. Initializing TTS engine with default model...")
        print("   (This may take a moment to download the model)")
        tts = TTSEngine()
        
        print("\n4. Getting model info...")
        info = tts.get_model_info()
        print("   Model Information:")
        for key, value in info.items():
            if key == "available_speakers" and isinstance(value, list):
                print(f"     {key}: {len(value)} speakers")
            else:
                print(f"     {key}: {value}")
        
        print("\n✅ TTS Engine initialized successfully!")
        return True, tts
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_synthesis(tts, text: str = "Hello, this is a test of the text to speech system."):
    """Test text synthesis."""
    print("\n" + "=" * 60)
    print("Testing Text Synthesis")
    print("=" * 60)
    
    try:
        print(f"\nSynthesizing: '{text}'")
        result = tts.synthesize(text, output_path="test_tts_output.wav")
        
        print("\n✅ Synthesis successful!")
        print(f"   Output file: {result['output_path']}")
        print(f"   Synthesis time: {result['duration']:.2f}s")
        print(f"   Sample rate: {result['sample_rate']} Hz")
        
        # Check if file exists
        if Path(result['output_path']).exists():
            file_size = Path(result['output_path']).stat().st_size
            print(f"   File size: {file_size / 1024:.2f} KB")
        
        return True, result
        
    except Exception as e:
        print(f"\n❌ Synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Run TTS engine tests."""
    print("\n" + "=" * 60)
    print("TTS Engine Test Suite")
    print("=" * 60)
    print("\nThis test verifies TTS engine initialization and synthesis.")
    print("Note: First run may download the model (can take a few minutes).\n")
    
    # Test initialization
    success, tts = test_tts_engine_init()
    
    if not success or tts is None:
        print("\n❌ Initialization failed. Cannot proceed with synthesis test.")
        sys.exit(1)
    
    # Ask if user wants to test synthesis
    print("\n" + "=" * 60)
    response = input("Test text synthesis? (y/n): ").strip().lower()
    
    if response == 'y':
        test_text = "Hello, I am your AI assistant. How can I help you today?"
        try:
            custom_text = input(f"Enter text to synthesize (default: '{test_text[:30]}...'): ").strip()
            if custom_text:
                test_text = custom_text
        except:
            pass
        
        success, result = test_synthesis(tts, test_text)
        
        if success:
            print("\n" + "=" * 60)
            play = input("Play the synthesized audio? (y/n): ").strip().lower()
            if play == 'y':
                try:
                    print("\n🔊 Playing audio...")
                    tts.speak(test_text, wait=True)
                    print("✅ Playback complete!")
                except Exception as e:
                    print(f"❌ Playback error: {e}")
    else:
        print("\n✅ Initialization test complete. TTS engine is ready to use.")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

