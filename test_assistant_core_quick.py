"""
Quick test for Assistant Core initialization.

This test verifies that all components can be imported and initialized
without actually loading the full models (which takes time).
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Quick Test: Assistant Core Components")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    from src.backend.streaming_stt import StreamingSTT
    print("   [OK] StreamingSTT imported")
except Exception as e:
    print(f"   [FAIL] StreamingSTT import failed: {e}")

try:
    from src.backend.tts_engine import TTSEngine
    print("   [OK] TTSEngine imported")
except Exception as e:
    print(f"   [FAIL] TTSEngine import failed: {e}")

try:
    from src.backend.llm_engine import LLMEngine
    print("   [OK] LLMEngine imported")
except Exception as e:
    print(f"   [FAIL] LLMEngine import failed: {e}")

try:
    from src.backend.function_handler import FunctionHandler
    print("   [OK] FunctionHandler imported")
except Exception as e:
    print(f"   [FAIL] FunctionHandler import failed: {e}")

try:
    from src.backend.file_controller import FileController
    print("   [OK] FileController imported")
except Exception as e:
    print(f"   [FAIL] FileController import failed: {e}")

try:
    from src.backend.app_controller import AppController
    print("   [OK] AppController imported")
except Exception as e:
    print(f"   [FAIL] AppController import failed: {e}")

try:
    from src.backend.input_controller import InputController
    print("   [OK] InputController imported")
except Exception as e:
    print(f"   [FAIL] InputController import failed: {e}")

try:
    from src.backend.assistant_core import AssistantCore
    print("   [OK] AssistantCore imported")
except Exception as e:
    print(f"   [FAIL] AssistantCore import failed: {e}")

# Test function handler initialization
print("\n2. Testing FunctionHandler initialization...")
try:
    from src.backend.function_handler import FunctionHandler
    handler = FunctionHandler()
    functions = handler.list_functions()
    print(f"   [OK] FunctionHandler initialized with {len(functions)} functions")
    print(f"   Functions: {', '.join(functions)}")
except Exception as e:
    print(f"   [FAIL] FunctionHandler initialization failed: {e}")

# Test controllers initialization
print("\n3. Testing Controllers initialization...")
try:
    from src.backend.file_controller import FileController
    fc = FileController(safe_mode=True)
    print("   [OK] FileController initialized")
except Exception as e:
    print(f"   [FAIL] FileController initialization failed: {e}")

try:
    from src.backend.app_controller import AppController
    ac = AppController()
    print("   [OK] AppController initialized")
except Exception as e:
    print(f"   [FAIL] AppController initialization failed: {e}")

try:
    from src.backend.input_controller import InputController
    ic = InputController(safe_mode=True)
    print("   [OK] InputController initialized")
except Exception as e:
    print(f"   [FAIL] InputController initialization failed: {e}")

print("\n" + "=" * 60)
print("[OK] Quick test complete!")
print("=" * 60)
print("\nNote: This test only verifies imports and basic initialization.")
print("Full initialization with models requires running:")
print("  python src/backend/assistant_core.py")

