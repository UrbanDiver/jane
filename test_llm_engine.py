"""
Test script for LLM Engine.

Tests LLM engine initialization and inference.
"""

import sys
from pathlib import Path

def test_llm_engine_init():
    """Test LLM engine initialization."""
    print("=" * 60)
    print("Testing LLM Engine Initialization")
    print("=" * 60)
    
    # Check for model
    model_path = "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    if not Path(model_path).exists():
        print(f"\n❌ Model not found: {model_path}")
        print("\nPlease download a model first:")
        print("  python download_llm_model.py")
        return False, None
    
    print(f"\nFound model: {model_path}")
    print(f"  Size: {Path(model_path).stat().st_size / (1024**3):.2f} GB")
    
    try:
        from src.backend.llm_engine import LLMEngine
        import torch
        
        print("\nChecking CUDA availability...")
        cuda_available = torch.cuda.is_available()
        print(f"  CUDA available: {cuda_available}")
        if cuda_available:
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        
        print("\nInitializing LLM engine...")
        print("  (This may take a minute to load the model)")
        
        # Use GPU layers if CUDA available
        n_gpu_layers = -1 if cuda_available else 0
        
        llm = LLMEngine(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=4096
        )
        
        print("\n✅ LLM Engine initialized successfully!")
        info = llm.get_model_info()
        print("\nModel Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        return True, llm
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_generation(llm):
    """Test text generation."""
    print("\n" + "=" * 60)
    print("Test 1: Text Generation")
    print("=" * 60)
    
    prompt = "Explain what a personal AI assistant can do in one sentence:"
    print(f"\nPrompt: {prompt}")
    print("\nGenerating...")
    
    try:
        result = llm.generate(prompt, max_tokens=100, temperature=0.7)
        
        print(f"\n✅ Generation successful!")
        print(f"\nResponse: {result['text']}")
        print(f"\nStatistics:")
        print(f"  Tokens generated: {result['tokens']}")
        print(f"  Time: {result['time']:.2f}s")
        print(f"  Speed: {result['tokens_per_second']:.1f} tokens/sec")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat(llm):
    """Test chat completion."""
    print("\n" + "=" * 60)
    print("Test 2: Chat Completion")
    print("=" * 60)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant named Jane."},
        {"role": "user", "content": "What's 15 multiplied by 23? Show your work."}
    ]
    
    print("\nMessages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    
    print("\nGenerating response...")
    
    try:
        result = llm.chat(messages, max_tokens=150, temperature=0.7)
        
        print(f"\n✅ Chat successful!")
        print(f"\nResponse: {result['response']}")
        print(f"\nStatistics:")
        print(f"  Tokens generated: {result['tokens']}")
        print(f"  Time: {result['time']:.2f}s")
        print(f"  Speed: {result['tokens_per_second']:.1f} tokens/sec")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run LLM engine tests."""
    print("\n" + "=" * 60)
    print("LLM Engine Test Suite")
    print("=" * 60)
    print("\nThis test verifies LLM engine initialization and inference.")
    print("Note: Model loading may take 1-2 minutes.\n")
    
    # Test initialization
    success, llm = test_llm_engine_init()
    
    if not success or llm is None:
        print("\n❌ Initialization failed. Cannot proceed with inference tests.")
        sys.exit(1)
    
    # Ask if user wants to test inference
    print("\n" + "=" * 60)
    response = input("Test inference? (y/n): ").strip().lower()
    
    if response == 'y':
        # Test generation
        test_generation(llm)
        
        # Test chat
        print("\n" + "=" * 60)
        response2 = input("Test chat completion? (y/n): ").strip().lower()
        if response2 == 'y':
            test_chat(llm)
    else:
        print("\n✅ Initialization test complete. LLM engine is ready to use.")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

