"""
Quick non-interactive test for LLM Engine.
Tests initialization without requiring user input.
"""

import sys
from pathlib import Path

def test_llm_init():
    """Test LLM engine initialization."""
    print("=" * 60)
    print("Quick LLM Engine Test")
    print("=" * 60)
    
    model_path = "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    if not Path(model_path).exists():
        print(f"\n❌ Model not found: {model_path}")
        return False
    
    print(f"\n✅ Model found: {model_path}")
    print(f"   Size: {Path(model_path).stat().st_size / (1024**3):.2f} GB")
    
    try:
        from src.backend.llm_engine import LLMEngine
        import torch
        
        cuda_available = torch.cuda.is_available()
        print(f"\n✅ CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
        print("\n⏳ Loading LLM (this may take 1-2 minutes)...")
        print("   Please wait...\n")
        
        n_gpu_layers = -1 if cuda_available else 0
        llm = LLMEngine(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=2048  # Smaller context for faster loading
        )
        
        print("\n✅ LLM Engine loaded successfully!")
        
        # Quick generation test
        print("\n" + "=" * 60)
        print("Quick Generation Test")
        print("=" * 60)
        
        prompt = "Say hello in one sentence:"
        print(f"\nPrompt: {prompt}")
        print("Generating...\n")
        
        result = llm.generate(prompt, max_tokens=50, temperature=0.7)
        
        print(f"✅ Response: {result['text']}")
        print(f"\nStatistics:")
        print(f"   Tokens: {result['tokens']}")
        print(f"   Time: {result['time']:.2f}s")
        print(f"   Speed: {result['tokens_per_second']:.1f} tokens/sec")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_init()
    sys.exit(0 if success else 1)

