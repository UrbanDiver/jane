# Python Version Requirements for Jane AI Voice Assistant

## Recommended Python Version

**Python 3.11** is the recommended version for this project.

## Why Python 3.11?

Based on package compatibility:

1. **PyTorch (with CUDA)**: Supports Python 3.8 - 3.11 (and 3.12 in newer versions)
2. **faster-whisper**: Requires Python 3.9+
3. **Coqui TTS**: 
   - Original: Supports Python 3.7 - 3.10
   - Maintained fork (idiap/coqui-ai-TTS): Supports Python 3.10, 3.11, and 3.12
4. **onnxruntime** (dependency of faster-whisper): Supports Python 3.8 - 3.11

## Version Compatibility Matrix

| Package | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.14 |
|---------|-------------|-------------|-------------|-------------|
| PyTorch | ✅ | ✅ | ✅ (newer) | ❌ |
| faster-whisper | ✅ | ✅ | ⚠️ (may work) | ❌ |
| Coqui TTS (original) | ✅ | ❌ | ❌ | ❌ |
| Coqui TTS (fork) | ✅ | ✅ | ✅ | ❌ |
| onnxruntime | ✅ | ✅ | ⚠️ | ❌ |

## Recommendation

**Use Python 3.11** because:
- ✅ Fully supported by all critical packages
- ✅ Stable and well-tested
- ✅ Matches the implementation plan requirement (Python 3.11+)
- ✅ CUDA builds available for PyTorch
- ✅ All dependencies have proven compatibility

## Alternative: Python 3.12

Python 3.12 may work if you:
- Use the maintained Coqui TTS fork (idiap/coqui-ai-TTS)
- Use newer versions of PyTorch and onnxruntime
- Accept potential compatibility issues

**Not recommended** for initial setup due to potential edge cases.

## Installation Steps

1. **Download Python 3.11:**
   - Go to: https://www.python.org/downloads/release/python-3119/
   - Download "Windows installer (64-bit)"
   - During installation, check ✅ "Add Python to PATH"

2. **Verify Installation:**
   ```powershell
   py -3.11 --version
   # Should show: Python 3.11.x
   ```

3. **Recreate Virtual Environment:**
   ```powershell
   # Remove old venv (if exists)
   Remove-Item -Recurse -Force venv
   
   # Create new venv with Python 3.11
   py -3.11 -m venv venv
   
   # Activate
   .\venv\Scripts\Activate.ps1
   
   # Verify Python version
   python --version  # Should show 3.11.x
   ```

4. **Install Dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **Test Installation:**
   ```powershell
   python test_imports.py
   ```

## Current Status

- **Your Current Python:** 3.14.0 ❌ (too new)
- **Required Python:** 3.11.x ✅ (or 3.12.x with caveats)
- **Action Needed:** Install Python 3.11 and recreate virtual environment

---

**Last Updated:** 2025-11-30

