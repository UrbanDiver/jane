"""
Quick test for Assistant Core initialization.

This test verifies that all components can be imported and initialized
without actually loading the full models (which takes time).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Quick Test: Assistant Core Components")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    from src.backend.streaming_stt import StreamingSTT
    print("   ✅ StreamingSTT imported")
except Exception as e:
    print(f"   ❌ StreamingSTT import failed: {e}")

try:
    from src.backend.tts_engine import TTSEngine
    print("   ✅ TTSEngine imported")
except Exception as e:
    print(f"   ❌ TTSEngine import failed: {e}")

try:
    from src.backend.llm_engine import LLMEngine
    print("   ✅ LLMEngine imported")
except Exception as e:
    print(f"   ❌ LLMEngine import failed: {e}")

try:
    from src.backend.function_handler import FunctionHandler
    print("   ✅ FunctionHandler imported")
except Exception as e:
    print(f"   ❌ FunctionHandler import failed: {e}")

try:
    from src.backend.file_controller import FileController
    print("   ✅ FileController imported")
except Exception as e:
    print(f"   ❌ FileController import failed: {e}")

try:
    from src.backend.app_controller import AppController
    print("   ✅ AppController imported")
except Exception as e:
    print(f"   ❌ AppController import failed: {e}")

try:
    from src.backend.input_controller import InputController
    print("   ✅ InputController imported")
except Exception as e:
    print(f"   ❌ InputController import failed: {e}")

try:
    from src.backend.assistant_core import AssistantCore
    print("   ✅ AssistantCore imported")
except Exception as e:
    print(f"   ❌ AssistantCore import failed: {e}")

# Test function handler initialization
print("\n2. Testing FunctionHandler initialization...")
try:
    from src.backend.function_handler import FunctionHandler
    handler = FunctionHandler()
    functions = handler.list_functions()
    print(f"   ✅ FunctionHandler initialized with {len(functions)} functions")
    print(f"   Functions: {', '.join(functions)}")
except Exception as e:
    print(f"   ❌ FunctionHandler initialization failed: {e}")

# Test controllers initialization
print("\n3. Testing Controllers initialization...")
try:
    from src.backend.file_controller import FileController
    fc = FileController(safe_mode=True)
    print("   ✅ FileController initialized")
except Exception as e:
    print(f"   ❌ FileController initialization failed: {e}")

try:
    from src.backend.app_controller import AppController
    ac = AppController()
    print("   ✅ AppController initialized")
except Exception as e:
    print(f"   ❌ AppController initialization failed: {e}")

try:
    from src.backend.input_controller import InputController
    ic = InputController(safe_mode=True)
    print("   ✅ InputController initialized")
except Exception as e:
    print(f"   ❌ InputController initialization failed: {e}")

print("\n" + "=" * 60)
print("✅ Quick test complete!")
print("=" * 60)
print("\nNote: This test only verifies imports and basic initialization.")
print("Full initialization with models requires running:")
print("  python src/backend/assistant_core.py")

