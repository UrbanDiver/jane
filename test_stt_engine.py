"""
Test script for STT Engine.

This script tests the STT engine initialization and basic functionality.
For full testing, you'll need to record an audio file first using record_test_audio.py
"""

import sys
from pathlib import Path

def test_stt_engine_init():
    """Test STT engine initialization."""
    print("=" * 50)
    print("Testing STT Engine Initialization")
    print("=" * 50)
    
    try:
        from src.backend.stt_engine import STTEngine
        
        print("\n1. Testing initialization with 'medium' model...")
        engine = STTEngine(model_size="medium", device="cuda", compute_type="float16")
        
        print("\n2. Getting model info...")
        info = engine.get_model_info()
        print("   Model Information:")
        for key, value in info.items():
            print(f"     {key}: {value}")
        
        print("\n✅ STT Engine initialized successfully!")
        return engine
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_transcription(engine, audio_file: str = "test_audio.wav"):
    """Test transcription with an audio file."""
    if not Path(audio_file).exists():
        print(f"\n⚠️  Audio file not found: {audio_file}")
        print("   Run 'python record_test_audio.py' first to create a test audio file.")
        return False
    
    print("\n" + "=" * 50)
    print("Testing Transcription")
    print("=" * 50)
    
    try:
        print(f"\nTranscribing: {audio_file}")
        result = engine.transcribe(audio_file)
        
        print("\n✅ Transcription successful!")
        print(f"\nResults:")
        print(f"  Text: {result['text']}")
        print(f"  Language: {result['language']} (confidence: {result.get('language_probability', 'N/A')})")
        print(f"  Processing time: {result['duration']:.2f}s")
        if result.get('audio_duration'):
            print(f"  Audio duration: {result['audio_duration']:.2f}s")
            print(f"  Real-time factor: {result['duration'] / result['audio_duration']:.2f}x")
        
        print(f"\n  Segments: {len(result.get('segments', []))}")
        for i, segment in enumerate(result.get('segments', [])[:3], 1):
            print(f"    {i}. [{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test initialization
    engine = test_stt_engine_init()
    
    if engine is None:
        sys.exit(1)
    
    # Test transcription if audio file exists
    audio_file = "test_audio.wav"
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    
    if Path(audio_file).exists():
        test_transcription(engine, audio_file)
    else:
        print(f"\n💡 To test transcription:")
        print(f"   1. Record audio: python record_test_audio.py")
        print(f"   2. Run test: python test_stt_engine.py")
        print(f"   Or provide audio file: python test_stt_engine.py <audio_file.wav>")

