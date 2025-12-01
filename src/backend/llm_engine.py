"""
Language Model Engine using llama.cpp

This module provides GPU-accelerated LLM inference using llama.cpp.
"""

from llama_cpp import Llama
import time
from pathlib import Path
from typing import Dict, List, Optional
import json
import torch
from src.config.config_schema import LLMConfig
from src.utils.logger import get_logger, log_performance, log_timing
from src.utils.retry import retry
from src.utils.error_handler import handle_error, ErrorType


class LLMEngine:
    """
    Language Model engine using llama.cpp.
    
    Supports GPU acceleration and chat completions.
    """
    
    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        model_path: Optional[str] = None,
        n_gpu_layers: Optional[int] = None,
        n_ctx: Optional[int] = None,
        n_batch: Optional[int] = None,
        verbose: Optional[bool] = None
    ):
        """
        Initialize the LLM engine.
        
        Args:
            config: LLMConfig object (takes precedence over individual params)
            model_path: Path to GGUF model file
            n_gpu_layers: Number of layers to offload to GPU (-1 = all layers)
            n_ctx: Context window size
            n_batch: Batch size for processing
            verbose: Enable verbose logging
        """
        # Use config if provided, otherwise use individual params or defaults
        if config:
            model_path = config.model_path
            n_gpu_layers = config.n_gpu_layers
            n_ctx = config.n_ctx
            n_batch = config.n_batch
            verbose = config.verbose
        else:
            # Require model_path if no config
            if model_path is None:
                raise ValueError("model_path is required if config is not provided")
            n_gpu_layers = n_gpu_layers if n_gpu_layers is not None else -1
            n_ctx = n_ctx if n_ctx is not None else 4096
            n_batch = n_batch if n_batch is not None else 512
            verbose = verbose if verbose is not None else False
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.logger = get_logger(__name__)
        self.logger.info(f"Loading LLM from: {model_path}")
        self.logger.debug(f"  GPU layers: {n_gpu_layers} ({'all' if n_gpu_layers == -1 else n_gpu_layers} layers)")
        self.logger.debug(f"  Context size: {n_ctx}")
        self.logger.debug(f"  Batch size: {n_batch}")
        
        try:
            with log_timing("LLM model loading", self.logger):
                self.llm = Llama(
                    model_path=model_path,
                    n_gpu_layers=n_gpu_layers,
                    n_ctx=n_ctx,
                    n_batch=n_batch,
                    verbose=verbose
                )
            self.logger.info("✅ LLM loaded successfully!")
            
            # Store configuration
            self.model_path = model_path
            self.n_gpu_layers = n_gpu_layers
            self.n_ctx = n_ctx
            
        except Exception as e:
            error_info = handle_error(e, context={"model_path": model_path}, logger=self.logger)
            
            # Try CPU fallback if GPU error
            if error_info["error_type"] == ErrorType.RESOURCE and "gpu" in str(e).lower():
                self.logger.warning("GPU error detected, attempting CPU fallback...")
                try:
                    self.llm = Llama(
                        model_path=model_path,
                        n_gpu_layers=0,  # Force CPU
                        n_ctx=n_ctx,
                        n_batch=n_batch,
                        verbose=verbose
                    )
                    self.logger.info("✅ LLM loaded successfully on CPU (GPU fallback)")
                    self.n_gpu_layers = 0
                    return
                except Exception as fallback_error:
                    self.logger.error(f"CPU fallback also failed: {fallback_error}")
            
            self.logger.error(f"❌ Error loading LLM: {error_info['message']}", exc_info=True)
            raise
    
    @log_performance("LLM Generation")
    @retry(max_retries=2, initial_delay=0.5, retryable_exceptions=(RuntimeError,))
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
        self.logger.debug(f"Generating text (max_tokens={max_tokens}, temp={temperature})")
        self.logger.debug(f"Prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
        
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
            
            text = response['choices'][0]['text']
            tokens = response['usage']['completion_tokens']
            
            result = {
                'text': text.strip(),
                'tokens': tokens,
                'time': 0,  # Will be set by decorator
                'tokens_per_second': 0  # Will be calculated by decorator
            }
            
            self.logger.info(f"Generated {tokens} tokens: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            return result
            
        except Exception as e:
            error_info = handle_error(
                e,
                context={"prompt_length": len(prompt), "max_tokens": max_tokens},
                logger=self.logger
            )
            self.logger.error(f"❌ Error during generation: {error_info['message']}", exc_info=True)
            raise
    
    @log_performance("LLM Chat")
    @retry(max_retries=2, initial_delay=0.5, retryable_exceptions=(RuntimeError,))
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict]] = None
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
            tools: Optional list of function definitions for function calling
            
        Returns:
            Dictionary with chat results:
            {
                'response': str,                # Assistant's response
                'time': float,                  # Generation time
                'tokens': int,                  # Tokens generated
                'tokens_per_second': float,     # Generation speed
                'function_calls': List[Dict]    # List of function calls if any
            }
        """
        self.logger.debug(f"Chat completion (messages={len(messages)}, max_tokens={max_tokens}, tools={len(tools) if tools else 0})")
        
        try:
            # Prepare chat completion kwargs
            completion_kwargs = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if stop:
                completion_kwargs["stop"] = stop
            
            if tools:
                completion_kwargs["tools"] = tools
            
            response = self.llm.create_chat_completion(**completion_kwargs)
            
            message = response['choices'][0]['message']
            content = message.get('content', '')
            tokens = response['usage']['completion_tokens']
            
            # Check for function calls
            function_calls = []
            if 'tool_calls' in message:
                for tool_call in message['tool_calls']:
                    function_calls.append({
                        'id': tool_call.get('id'),
                        'function': {
                            'name': tool_call['function']['name'],
                            'arguments': tool_call['function'].get('arguments', '{}')
                        }
                    })
            
            result = {
                'response': content.strip() if content else '',
                'time': 0,  # Will be set by decorator
                'tokens': tokens,
                'tokens_per_second': 0,  # Will be calculated by decorator
                'function_calls': function_calls
            }
            
            if function_calls:
                self.logger.info(f"Chat response with {len(function_calls)} function call(s): {tokens} tokens")
                for fc in function_calls:
                    self.logger.debug(f"  Function call: {fc['function']['name']}")
            else:
                self.logger.info(f"Chat response: {tokens} tokens")
                self.logger.debug(f"Response: '{content[:100]}{'...' if len(content) > 100 else ''}'")
            
            return result
            
        except Exception as e:
            error_info = handle_error(
                e,
                context={"message_count": len(messages), "max_tokens": max_tokens},
                logger=self.logger
            )
            self.logger.error(f"❌ Error during chat: {error_info['message']}", exc_info=True)
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
            self.logger.error(f"❌ Error during streaming: {e}", exc_info=True)
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

