# Python Version Compatibility Note

## Issue
Python 3.14.0 is very new (released October 2024) and many packages required for this project don't have builds for it yet:
- PyTorch (no CUDA builds for Python 3.14)
- faster-whisper (depends on onnxruntime, which doesn't support Python 3.14)
- Coqui TTS (requires Python <3.12)

## Recommended Solution

**Use Python 3.11 or 3.12** for this project. These versions are well-supported by all required packages.

### Steps to Fix:

1. **Install Python 3.11 or 3.12:**
   - Download from: https://www.python.org/downloads/
   - Choose Python 3.11.9 or Python 3.12.x
   - During installation, check "Add Python to PATH"

2. **Recreate virtual environment:**
   ```powershell
   # Remove old venv
   Remove-Item -Recurse -Force venv
   
   # Create new venv with Python 3.11/3.12
   py -3.11 -m venv venv
   # OR
   py -3.12 -m venv venv
   
   # Activate and install
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Verify:**
   ```powershell
   python --version  # Should show 3.11.x or 3.12.x
   python test_imports.py
   ```

## Alternative: Wait for Package Updates

If you prefer to stick with Python 3.14, you'll need to wait for:
- PyTorch to release Python 3.14 builds
- onnxruntime to support Python 3.14
- Coqui TTS to support Python 3.14

This may take several months.

---

**Recommendation:** Use Python 3.11 or 3.12 for now, as they are stable and fully supported.

