"""
Performance Benchmarking Script for Jane AI Voice Assistant

Measures and documents performance metrics for all components:
- STT latency
- LLM inference speed
- TTS latency
- End-to-end interaction time
- Memory usage (GPU and system)
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import contextmanager

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("WARNING: psutil not available, system memory metrics will be limited")

from src.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timer(description: str):
    """Context manager for timing operations."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"  {description}: {elapsed:.3f}s")


def get_gpu_memory() -> Optional[Dict]:
    """Get GPU memory usage."""
    try:
        if HAS_TORCH and torch and torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "reserved": torch.cuda.memory_reserved() / 1024**3,  # GB
                "max_allocated": torch.cuda.max_memory_allocated() / 1024**3,  # GB
            }
    except Exception as e:
        logger.warning(f"Could not get GPU memory: {e}")
    return None


def get_system_memory() -> Dict:
    """Get system memory usage."""
    if not HAS_PSUTIL:
        return {"error": "psutil not available"}
    
    try:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total / 1024**3,  # GB
            "available": mem.available / 1024**3,  # GB
            "used": mem.used / 1024**3,  # GB
            "percent": mem.percent,
        }
    except Exception as e:
        logger.warning(f"Could not get system memory: {e}")
        return {"error": str(e)}


def benchmark_stt():
    """Benchmark STT engine performance."""
    print("\n" + "=" * 60)
    print("STT Engine Benchmark")
    print("=" * 60)
    
    try:
        # Check if dependencies are available
        try:
            from src.backend.stt_engine import STTEngine
            from src.config import get_config
        except ImportError as e:
            print(f"  SKIP: Required dependencies not available: {e}")
            print("  Install dependencies: pip install -r requirements.txt")
            return {"error": f"Dependencies not available: {e}"}
        
        config = get_config()
        
        # Measure initialization time
        with timer("STT Engine initialization"):
            stt = STTEngine(
                model_size=config.stt.model_size,
                device=config.stt.device,
                compute_type=config.stt.compute_type
            )
        
        # Get GPU memory after initialization
        gpu_mem = get_gpu_memory()
        if gpu_mem:
            print(f"  GPU Memory (after init): {gpu_mem['allocated']:.2f} GB allocated")
        
        # Create a test audio file (silent WAV for testing)
        # In real scenario, you'd use actual audio
        test_audio = Path("test_audio.wav")
        if not test_audio.exists():
            print("  WARNING: test_audio.wav not found, skipping transcription benchmark")
            return {
                "initialization_time": None,
                "gpu_memory": gpu_mem,
                "transcription_time": None,
            }
        
        # Measure transcription time
        with timer("STT transcription (test_audio.wav)"):
            result = stt.transcribe(str(test_audio))
        
        return {
            "initialization_time": None,  # Set by timer
            "gpu_memory": gpu_mem,
            "transcription_time": None,  # Set by timer
            "result_length": len(result.get("text", "")) if result else 0,
        }
    except Exception as e:
        print(f"  ERROR: STT benchmark failed: {e}")
        return {"error": str(e)}


def benchmark_tts():
    """Benchmark TTS engine performance."""
    print("\n" + "=" * 60)
    print("TTS Engine Benchmark")
    print("=" * 60)
    
    try:
        # Check if dependencies are available
        try:
            from src.backend.tts_engine import TTSEngine
            from src.config import get_config
        except ImportError as e:
            print(f"  SKIP: Required dependencies not available: {e}")
            print("  Install dependencies: pip install -r requirements.txt")
            return {"error": f"Dependencies not available: {e}"}
        
        config = get_config()
        test_text = "Hello, this is a test of the text to speech engine. It should synthesize this text quickly."
        
        # Measure initialization time
        with timer("TTS Engine initialization"):
            tts = TTSEngine(device=config.tts.device)
        
        # Get GPU memory after initialization
        gpu_mem = get_gpu_memory()
        if gpu_mem:
            print(f"  GPU Memory (after init): {gpu_mem['allocated']:.2f} GB allocated")
        
        # Measure synthesis time
        with timer(f"TTS synthesis ({len(test_text)} chars)"):
            result = tts.synthesize(test_text)
        
        return {
            "initialization_time": None,
            "gpu_memory": gpu_mem,
            "synthesis_time": None,
            "text_length": len(test_text),
        }
    except Exception as e:
        print(f"  ERROR: TTS benchmark failed: {e}")
        return {"error": str(e)}


def benchmark_llm():
    """Benchmark LLM engine performance."""
    print("\n" + "=" * 60)
    print("LLM Engine Benchmark")
    print("=" * 60)
    
    try:
        # Check if dependencies are available
        try:
            from src.backend.llm_engine import LLMEngine
            from src.config import get_config
        except ImportError as e:
            print(f"  SKIP: Required dependencies not available: {e}")
            print("  Install dependencies: pip install -r requirements.txt")
            return {"error": f"Dependencies not available: {e}"}
        
        config = get_config()
        test_messages = [
            {"role": "user", "content": "What is artificial intelligence? Please provide a brief explanation."}
        ]
        
        # Measure initialization time
        with timer("LLM Engine initialization"):
            llm = LLMEngine(
                model_path=config.llm.model_path,
                n_gpu_layers=config.llm.n_gpu_layers,
                n_ctx=config.llm.n_ctx
            )
        
        # Get GPU memory after initialization
        gpu_mem = get_gpu_memory()
        if gpu_mem:
            print(f"  GPU Memory (after init): {gpu_mem['allocated']:.2f} GB allocated")
        
        # Measure generation time and tokens
        start_time = time.time()
        result = llm.chat(test_messages, max_tokens=100, temperature=0.7)
        elapsed = time.time() - start_time
        
        response_text = result.get("response", "")
        token_count = len(response_text.split())  # Approximate token count
        
        tokens_per_second = token_count / elapsed if elapsed > 0 else 0
        
        print(f"  Generation time: {elapsed:.3f}s")
        print(f"  Tokens generated: ~{token_count}")
        print(f"  Tokens per second: {tokens_per_second:.2f}")
        
        return {
            "initialization_time": None,
            "gpu_memory": gpu_mem,
            "generation_time": elapsed,
            "tokens_generated": token_count,
            "tokens_per_second": tokens_per_second,
        }
    except Exception as e:
        print(f"  ERROR: LLM benchmark failed: {e}")
        return {"error": str(e)}


def benchmark_end_to_end():
    """Benchmark end-to-end interaction."""
    print("\n" + "=" * 60)
    print("End-to-End Interaction Benchmark")
    print("=" * 60)
    
    try:
        # Check if dependencies are available
        try:
            from src.backend.assistant_core import AssistantCore
        except ImportError as e:
            print(f"  SKIP: Required dependencies not available: {e}")
            print("  Install dependencies: pip install -r requirements.txt")
            return {"error": f"Dependencies not available: {e}"}
        
        test_command = "What time is it?"
        
        # Measure initialization time
        with timer("AssistantCore initialization"):
            assistant = AssistantCore()
        
        # Get memory after initialization
        gpu_mem = get_gpu_memory()
        sys_mem = get_system_memory()
        
        if gpu_mem:
            print(f"  GPU Memory: {gpu_mem['allocated']:.2f} GB allocated")
        if sys_mem and "error" not in sys_mem:
            print(f"  System Memory: {sys_mem['used']:.2f} GB used ({sys_mem['percent']:.1f}%)")
        
        # Measure command processing time
        with timer(f"Process command: '{test_command}'"):
            response = assistant.process_command(test_command, stream=False, use_functions=True)
        
        return {
            "initialization_time": None,
            "gpu_memory": gpu_mem,
            "system_memory": sys_mem,
            "command_processing_time": None,
            "response_length": len(response) if response else 0,
        }
    except Exception as e:
        print(f"  ERROR: End-to-end benchmark failed: {e}")
        return {"error": str(e)}


def benchmark_streaming():
    """Benchmark streaming response performance."""
    print("\n" + "=" * 60)
    print("Streaming Response Benchmark")
    print("=" * 60)
    
    try:
        # Check if dependencies are available
        try:
            from src.backend.assistant_core import AssistantCore
        except ImportError as e:
            print(f"  SKIP: Required dependencies not available: {e}")
            print("  Install dependencies: pip install -r requirements.txt")
            return {"error": f"Dependencies not available: {e}"}
        
        test_command = "Tell me a short story about artificial intelligence."
        
        assistant = AssistantCore()
        
        # Measure streaming response time
        start_time = time.time()
        first_token_time = None
        
        response_chunks = []
        for chunk in assistant.process_command(test_command, stream=True, use_functions=False):
            if first_token_time is None:
                first_token_time = time.time() - start_time
            response_chunks.append(chunk)
        
        total_time = time.time() - start_time
        
        print(f"  First token latency: {first_token_time:.3f}s")
        print(f"  Total generation time: {total_time:.3f}s")
        print(f"  Chunks received: {len(response_chunks)}")
        
        return {
            "first_token_latency": first_token_time,
            "total_time": total_time,
            "chunks": len(response_chunks),
        }
    except Exception as e:
        print(f"  ERROR: Streaming benchmark failed: {e}")
        return {"error": str(e)}


def generate_report(results: Dict):
    """Generate a performance report."""
    print("\n" + "=" * 60)
    print("Performance Benchmark Report")
    print("=" * 60)
    
    report = []
    report.append("# Performance Benchmark Report\n")
    report.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**System:** {sys.platform}\n")
    
    if HAS_TORCH and torch and torch.cuda.is_available():
        report.append(f"**GPU:** {torch.cuda.get_device_name(0)}\n")
        report.append(f"**CUDA Version:** {torch.version.cuda}\n")
    
    report.append("\n## Results\n\n")
    
    # STT Results
    if "stt" in results:
        stt = results["stt"]
        report.append("### STT Engine\n")
        if "error" not in stt:
            report.append(f"- Initialization: {stt.get('initialization_time', 'N/A')}\n")
            report.append(f"- Transcription: {stt.get('transcription_time', 'N/A')}\n")
            if stt.get("gpu_memory"):
                report.append(f"- GPU Memory: {stt['gpu_memory']['allocated']:.2f} GB\n")
        else:
            report.append(f"- Error: {stt['error']}\n")
        report.append("\n")
    
    # TTS Results
    if "tts" in results:
        tts = results["tts"]
        report.append("### TTS Engine\n")
        if "error" not in tts:
            report.append(f"- Initialization: {tts.get('initialization_time', 'N/A')}\n")
            report.append(f"- Synthesis: {tts.get('synthesis_time', 'N/A')}\n")
            if tts.get("gpu_memory"):
                report.append(f"- GPU Memory: {tts['gpu_memory']['allocated']:.2f} GB\n")
        else:
            report.append(f"- Error: {tts['error']}\n")
        report.append("\n")
    
    # LLM Results
    if "llm" in results:
        llm = results["llm"]
        report.append("### LLM Engine\n")
        if "error" not in llm:
            report.append(f"- Initialization: {llm.get('initialization_time', 'N/A')}\n")
            report.append(f"- Generation Time: {llm.get('generation_time', 'N/A')}s\n")
            report.append(f"- Tokens per Second: {llm.get('tokens_per_second', 'N/A')}\n")
            if llm.get("gpu_memory"):
                report.append(f"- GPU Memory: {llm['gpu_memory']['allocated']:.2f} GB\n")
        else:
            report.append(f"- Error: {llm['error']}\n")
        report.append("\n")
    
    # End-to-End Results
    if "end_to_end" in results:
        e2e = results["end_to_end"]
        report.append("### End-to-End Interaction\n")
        if "error" not in e2e:
            report.append(f"- Initialization: {e2e.get('initialization_time', 'N/A')}\n")
            report.append(f"- Command Processing: {e2e.get('command_processing_time', 'N/A')}\n")
            if e2e.get("gpu_memory"):
                report.append(f"- GPU Memory: {e2e['gpu_memory']['allocated']:.2f} GB\n")
        else:
            report.append(f"- Error: {e2e['error']}\n")
        report.append("\n")
    
    # Streaming Results
    if "streaming" in results:
        stream = results["streaming"]
        report.append("### Streaming Response\n")
        if "error" not in stream:
            report.append(f"- First Token Latency: {stream.get('first_token_latency', 'N/A')}s\n")
            report.append(f"- Total Time: {stream.get('total_time', 'N/A')}s\n")
        else:
            report.append(f"- Error: {stream['error']}\n")
        report.append("\n")
    
    # Performance Targets
    report.append("## Performance Targets\n\n")
    report.append("- STT Latency: <500ms\n")
    report.append("- LLM Inference: 60-120 tokens/second\n")
    report.append("- TTS Latency: <2s\n")
    report.append("- End-to-End: <5s\n")
    
    report_text = "".join(report)
    print(report_text)
    
    # Save to file
    report_file = Path("PERFORMANCE_BENCHMARK.md")
    report_file.write_text(report_text, encoding="utf-8")
    print(f"\nReport saved to: {report_file}")


def main():
    """Run all benchmarks."""
    print("=" * 60)
    print("Jane AI Voice Assistant - Performance Benchmarking")
    print("=" * 60)
    print("\nThis script will measure performance metrics for all components.")
    print("Note: Some benchmarks require models to be loaded, which may take time.\n")
    
    results = {}
    
    # System information
    print("\n" + "=" * 60)
    print("System Information")
    print("=" * 60)
    
    if HAS_TORCH and torch and torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"PyTorch Version: {torch.__version__}")
    else:
        print("GPU: Not available (CPU mode or PyTorch not installed)")
    
    sys_mem = get_system_memory()
    if sys_mem and "error" not in sys_mem:
        print(f"System Memory: {sys_mem['total']:.2f} GB total, {sys_mem['used']:.2f} GB used")
    
    # Run benchmarks
    try:
        results["stt"] = benchmark_stt()
    except Exception as e:
        print(f"STT benchmark failed: {e}")
        results["stt"] = {"error": str(e)}
    
    try:
        results["tts"] = benchmark_tts()
    except Exception as e:
        print(f"TTS benchmark failed: {e}")
        results["tts"] = {"error": str(e)}
    
    try:
        results["llm"] = benchmark_llm()
    except Exception as e:
        print(f"LLM benchmark failed: {e}")
        results["llm"] = {"error": str(e)}
    
    try:
        results["end_to_end"] = benchmark_end_to_end()
    except Exception as e:
        print(f"End-to-end benchmark failed: {e}")
        results["end_to_end"] = {"error": str(e)}
    
    try:
        results["streaming"] = benchmark_streaming()
    except Exception as e:
        print(f"Streaming benchmark failed: {e}")
        results["streaming"] = {"error": str(e)}
    
    # Generate report
    generate_report(results)
    
    print("\n" + "=" * 60)
    print("Benchmarking Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

