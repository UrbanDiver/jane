"""
Quick LLM performance test without function calling overhead.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.backend.llm_engine import LLMEngine
from src.config import get_config

print("=" * 60)
print("LLM Performance Test (No Function Calling)")
print("=" * 60)

config = get_config()

print(f"\nModel: {config.llm.model_path}")
print(f"Context: {config.llm.n_ctx}")
print(f"Batch: {config.llm.n_batch}")

# Initialize
print("\nInitializing LLM...")
start = time.time()
llm = LLMEngine(config=config.llm)
init_time = time.time() - start
print(f"Initialization: {init_time:.3f}s")

# Test 1: Simple generation
print("\nTest 1: Simple generation (no function calling)")
messages = [{"role": "user", "content": "What is artificial intelligence? Please provide a brief explanation."}]
start = time.time()
result = llm.chat(messages, max_tokens=100, temperature=0.7, tools=None)
elapsed = time.time() - start
tokens = result.get('tokens', 0)
tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
print(f"Time: {elapsed:.3f}s")
print(f"Tokens: {tokens}")
print(f"Tokens/sec: {tokens_per_sec:.2f}")

# Test 2: With function calling (but no actual functions)
print("\nTest 2: With function calling format (but no tools)")
messages2 = [{"role": "user", "content": "What time is it?"}]
start = time.time()
result2 = llm.chat(messages2, max_tokens=100, temperature=0.7, tools=None)
elapsed2 = time.time() - start
tokens2 = result2.get('tokens', 0)
tokens_per_sec2 = tokens2 / elapsed2 if elapsed2 > 0 else 0
print(f"Time: {elapsed2:.3f}s")
print(f"Tokens: {tokens2}")
print(f"Tokens/sec: {tokens_per_sec2:.2f}")

# Test 3: Multiple generations (warm-up effect)
print("\nTest 3: Second generation (warm-up)")
start = time.time()
result3 = llm.chat(messages, max_tokens=100, temperature=0.7, tools=None)
elapsed3 = time.time() - start
tokens3 = result3.get('tokens', 0)
tokens_per_sec3 = tokens3 / elapsed3 if elapsed3 > 0 else 0
print(f"Time: {elapsed3:.3f}s")
print(f"Tokens: {tokens3}")
print(f"Tokens/sec: {tokens_per_sec3:.2f}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print(f"Initialization: {init_time:.3f}s")
print(f"First generation: {elapsed:.3f}s ({tokens_per_sec:.2f} tok/s)")
print(f"Second generation: {elapsed3:.3f}s ({tokens_per_sec3:.2f} tok/s)")
print(f"Warm-up improvement: {((elapsed - elapsed3) / elapsed * 100):.1f}%")

