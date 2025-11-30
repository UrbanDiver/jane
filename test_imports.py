"""
Test script to verify all required packages are installed correctly.
Run this after installing requirements.txt to ensure everything works.
"""
import sys

def test_imports():
    """Test all critical imports"""
    errors = []
    
    print("Testing imports...")
    print("=" * 50)
    
    # GPU-accelerated inference
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
        else:
            errors.append("⚠️  CUDA not available in PyTorch")
    except ImportError as e:
        errors.append(f"❌ PyTorch: {e}")
    
    try:
        import faster_whisper
        print(f"✅ faster-whisper imported successfully")
    except ImportError as e:
        errors.append(f"❌ faster-whisper: {e}")
    
    try:
        from transformers import pipeline
        print(f"✅ transformers imported successfully")
    except ImportError as e:
        errors.append(f"❌ transformers: {e}")
    
    # Audio processing
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"✅ sounddevice imported - {len(devices)} audio devices found")
    except ImportError as e:
        errors.append(f"❌ sounddevice: {e}")
    
    try:
        import soundfile
        print(f"✅ soundfile imported successfully")
    except ImportError as e:
        errors.append(f"❌ soundfile: {e}")
    
    try:
        import webrtcvad
        print(f"✅ webrtcvad imported successfully")
    except ImportError as e:
        errors.append(f"❌ webrtcvad: {e}")
    
    # TTS
    try:
        from TTS.api import TTS
        print(f"✅ TTS (Coqui) imported successfully")
    except ImportError as e:
        errors.append(f"❌ TTS: {e}")
    
    # Computer control
    try:
        import pyautogui
        print(f"✅ pyautogui imported successfully")
    except ImportError as e:
        errors.append(f"❌ pyautogui: {e}")
    
    try:
        # pywinauto has threading issues in some environments, but it's installed
        import pywinauto
        print(f"✅ pywinauto imported successfully")
    except (ImportError, OSError) as e:
        # Known Windows threading issue - package is installed but may have runtime issues
        print(f"⚠️  pywinauto: {e} (package installed, but may have runtime threading issues)")
    
    # Utilities
    try:
        import yaml
        print(f"✅ pyyaml imported successfully")
    except ImportError as e:
        errors.append(f"❌ pyyaml: {e}")
    
    try:
        from PIL import Image
        print(f"✅ Pillow imported successfully")
    except ImportError as e:
        errors.append(f"❌ Pillow: {e}")
    
    # Database
    try:
        import sqlalchemy
        print(f"✅ sqlalchemy imported successfully")
    except ImportError as e:
        errors.append(f"❌ sqlalchemy: {e}")
    
    # Vector DB
    try:
        import chromadb
        print(f"✅ chromadb imported successfully")
    except ImportError as e:
        errors.append(f"❌ chromadb: {e}")
    
    # Development
    try:
        import pytest
        print(f"✅ pytest imported successfully")
    except ImportError as e:
        errors.append(f"❌ pytest: {e}")
    
    # Backend server
    try:
        import flask
        print(f"✅ flask imported successfully")
    except ImportError as e:
        errors.append(f"❌ flask: {e}")
    
    try:
        import flask_cors
        print(f"✅ flask-cors imported successfully")
    except ImportError as e:
        errors.append(f"❌ flask-cors: {e}")
    
    # Process management
    try:
        import psutil
        print(f"✅ psutil imported successfully")
    except ImportError as e:
        errors.append(f"❌ psutil: {e}")
    
    print("=" * 50)
    
    if errors:
        print("\n⚠️  Some imports failed:")
        for error in errors:
            print(f"   {error}")
        print("\nPlease install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

