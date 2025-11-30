"""
Quick test for function calling in assistant core.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.backend.assistant_core import AssistantCore

print("=" * 60)
print("Testing Function Calling")
print("=" * 60)

# Check if model exists
model_path = Path("models/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
if not model_path.exists():
    print(f"❌ Model not found: {model_path}")
    sys.exit(1)

print(f"\nInitializing assistant...")
assistant = AssistantCore(llm_model_path=str(model_path))

# Test function calling
test_queries = [
    "What time is it?",
    "What's the date?",
    "What date and time is it?"
]

print("\n" + "=" * 60)
print("Testing Function Calls")
print("=" * 60)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    result = assistant._try_function_call(query)
    if result:
        print(f"✅ Function called: {result}")
    else:
        print("❌ No function called")

print("\n" + "=" * 60)
print("✅ Function calling test complete!")
print("=" * 60)

