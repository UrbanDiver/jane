"""
Language Model Engine using llama.cpp

This module provides GPU-accelerated LLM inference using llama.cpp.
"""

from llama_cpp import Llama
import time
from pathlib import Path
from typing import Dict, List, Optional
import json


class LLMEngine:
    """
    Language Model engine using llama.cpp.
    
    Supports GPU acceleration and chat completions.
    """
    
    def __init__(
        self,
        model_path: str,
        n_gpu_layers: int = -1,
        n_ctx: int = 4096,
        n_batch: int = 512,
        verbose: bool = False
    ):
        """
        Initialize the LLM engine.
        
        Args:
            model_path: Path to GGUF model file
            n_gpu_layers: Number of layers to offload to GPU (-1 = all layers)
            n_ctx: Context window size
            n_batch: Batch size for processing
            verbose: Enable verbose logging
        """
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading LLM from: {model_path}")
        print(f"  GPU layers: {n_gpu_layers} ({'all' if n_gpu_layers == -1 else n_gpu_layers} layers)")
        print(f"  Context size: {n_ctx}")
        print(f"  Batch size: {n_batch}")
        
        try:
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                n_batch=n_batch,
                verbose=verbose
            )
            print("✅ LLM loaded successfully!")
            
            # Store configuration
            self.model_path = model_path
            self.n_gpu_layers = n_gpu_layers
            self.n_ctx = n_ctx
            
        except Exception as e:
            print(f"❌ Error loading LLM: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        stop: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Penalty for repetition
            stop: List of stop sequences
            
        Returns:
            Dictionary with generation results:
            {
                'text': str,                    # Generated text
                'tokens': int,                   # Number of tokens generated
                'time': float,                   # Generation time in seconds
                'tokens_per_second': float       # Generation speed
            }
        """
        start_time = time.time()
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop=stop,
                echo=False
            )
            
            elapsed = time.time() - start_time
            text = response['choices'][0]['text']
            tokens = response['usage']['completion_tokens']
            
            return {
                'text': text.strip(),
                'tokens': tokens,
                'time': elapsed,
                'tokens_per_second': tokens / elapsed if elapsed > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> Dict:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
                     Example: [{"role": "system", "content": "..."}, ...]
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stop: List of stop sequences
            
        Returns:
            Dictionary with chat results:
            {
                'response': str,                # Assistant's response
                'time': float,                  # Generation time
                'tokens': int,                  # Tokens generated
                'tokens_per_second': float      # Generation speed
            }
        """
        start_time = time.time()
        
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop
            )
            
            elapsed = time.time() - start_time
            content = response['choices'][0]['message']['content']
            tokens = response['usage']['completion_tokens']
            
            return {
                'response': content.strip(),
                'time': elapsed,
                'tokens': tokens,
                'tokens_per_second': tokens / elapsed if elapsed > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error during chat: {e}")
            raise
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        temperature: float = 0.7
    ):
        """
        Stream chat completion (generator).
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Dictionary with partial response:
            {
                'delta': str,                   # New text chunk
                'text': str,                    # Full text so far
                'done': bool                    # Whether generation is complete
            }
        """
        try:
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            full_text = ""
            for chunk in stream:
                delta = chunk['choices'][0]['delta'].get('content', '')
                if delta:
                    full_text += delta
                    yield {
                        'delta': delta,
                        'text': full_text,
                        'done': False
                    }
            
            yield {
                'delta': '',
                'text': full_text,
                'done': True
            }
            
        except Exception as e:
            print(f"❌ Error during streaming: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_path": self.model_path,
            "n_gpu_layers": self.n_gpu_layers,
            "n_ctx": self.n_ctx,
            "context_size": self.n_ctx
        }


if __name__ == "__main__":
    # Test the LLM engine
    print("=" * 60)
    print("Testing LLM Engine")
    print("=" * 60)
    
    # Check if model exists
    model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
    
    if not Path(model_path).exists():
        print(f"\n⚠️  Model not found: {model_path}")
        print("\nTo download the model, run:")
        print("  pip install huggingface-hub[cli]")
        print("  huggingface-cli download \\")
        print("    bartowski/Qwen2.5-32B-Instruct-GGUF \\")
        print("    Qwen2.5-32B-Instruct-Q4_K_M.gguf \\")
        print("    --local-dir models")
        print("\nOr use a smaller model for testing.")
        print("\nFor now, testing import only...")
        
        from src.backend.llm_engine import LLMEngine
        print("✅ LLM Engine module imported successfully!")
    else:
        print(f"\nFound model: {model_path}")
        print("Initializing LLM engine...")
        
        llm = LLMEngine(model_path)
        
        # Test 1: Simple generation
        print("\n" + "=" * 60)
        print("Test 1: Simple prompt")
        print("=" * 60)
        
        result = llm.generate("Explain what a personal AI assistant can do in one sentence:")
        print(f"\nResponse: {result['text']}")
        print(f"Speed: {result['tokens_per_second']:.1f} tokens/sec")
        print(f"Time: {result['time']:.2f}s")
        
        # Test 2: Chat
        print("\n" + "=" * 60)
        print("Test 2: Chat mode")
        print("=" * 60)
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "What's 15 multiplied by 23?"}
        ]
        
        result = llm.chat(messages)
        print(f"\nResponse: {result['response']}")
        print(f"Time: {result['time']:.2f}s")
        print(f"Speed: {result['tokens_per_second']:.1f} tokens/sec")

