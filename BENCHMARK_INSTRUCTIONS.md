# Performance Benchmarking Instructions

**How to run performance benchmarks for Jane AI Voice Assistant**

---

## Prerequisites

To run the full performance benchmarks, you need:

1. **Virtual Environment** with all dependencies installed
2. **GPU** with CUDA support (for accurate benchmarks)
3. **Models** downloaded:
   - STT model (auto-downloaded on first use)
   - TTS model (auto-downloaded on first use)
   - LLM model (manual download required)

---

## Setup Steps

### 1. Activate Virtual Environment

```powershell
# If virtual environment exists
.\venv\Scripts\Activate.ps1

# If virtual environment doesn't exist, create it
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
# Install all dependencies
pip install -r requirements.txt

# This will install:
# - torch (PyTorch with CUDA)
# - faster-whisper (STT)
# - llama-cpp-python (LLM)
# - TTS (Coqui TTS)
# - sounddevice, soundfile (Audio)
# - And all other dependencies
```

**Note:** Some dependencies may take time to install, especially PyTorch with CUDA support.

### 3. Download LLM Model

The LLM model needs to be downloaded manually:

```powershell
# Recommended model: Qwen2.5-7B-Instruct-Q4_K_M.gguf (4.36GB)
# Place in models/ directory

# Or use the download script if available
python download_llm_model.py
```

### 4. Configure

Create `config.yaml` from `config.yaml.example`:

```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

stt:
  model_size: "medium"
  device: "cuda"

tts:
  model_name: "tts_models/en/ljspeech/tacotron2-DDC"
  device: "cuda"
```

---

## Running Benchmarks

### Basic Run

```powershell
python benchmark_performance.py
```

This will:
1. Check system information (GPU, memory)
2. Benchmark STT engine (initialization, transcription)
3. Benchmark TTS engine (initialization, synthesis)
4. Benchmark LLM engine (initialization, generation speed)
5. Benchmark end-to-end interaction
6. Benchmark streaming responses
7. Generate performance report

### Expected Output

The script will output:
- System information
- Timing for each component
- Memory usage (GPU and system)
- Performance metrics (tokens/sec, latency, etc.)
- Generated report in `PERFORMANCE_BENCHMARK.md`

### Benchmark Duration

- **First Run:** 5-10 minutes (models need to download/load)
- **Subsequent Runs:** 2-5 minutes (models cached)

---

## What Gets Measured

### STT Engine
- Initialization time
- Transcription latency
- GPU memory usage

### TTS Engine
- Initialization time
- Synthesis latency
- GPU memory usage

### LLM Engine
- Initialization time
- Generation speed (tokens/second)
- First token latency
- GPU memory usage

### End-to-End
- Full interaction time
- Component breakdown
- Memory usage

### Streaming
- First token latency
- Total generation time
- Chunk count

---

## Performance Targets

Compare your results against:

- **STT Latency:** <500ms
- **LLM Inference:** 60-120 tokens/second
- **TTS Latency:** <2s
- **End-to-End:** <5s

**See [PERFORMANCE_TARGETS.md](PERFORMANCE_TARGETS.md) for details.**

---

## Troubleshooting

### Dependencies Not Found

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### GPU Not Detected

```powershell
# Check GPU
nvidia-smi

# Verify CUDA in Python
python -c "import torch; print(torch.cuda.is_available())"
```

### Model Not Found

```powershell
# Check model path
python -c "from pathlib import Path; print(Path('models/Qwen2.5-7B-Instruct-Q4_K_M.gguf').exists())"

# Download model if missing
# See README.md for download links
```

### Out of Memory

- Use smaller models (tiny/base for STT)
- Use CPU for some components
- Reduce context window size
- Close other applications

---

## Interpreting Results

### Good Performance
- STT latency < 500ms
- LLM tokens/sec > 60
- TTS latency < 2s
- End-to-end < 5s

### Needs Optimization
- STT latency > 1s
- LLM tokens/sec < 30
- TTS latency > 3s
- End-to-end > 10s

### Optimization Tips
- Use GPU acceleration
- Enable model caching
- Use quantization (int8)
- Reduce context window
- Use smaller models

---

## Report Location

Benchmark results are saved to:
- **PERFORMANCE_BENCHMARK.md** - Detailed report

Review the report to:
- Compare against targets
- Identify bottlenecks
- Plan optimizations

---

## Next Steps

After running benchmarks:

1. **Review Report** - Check `PERFORMANCE_BENCHMARK.md`
2. **Compare Targets** - See [PERFORMANCE_TARGETS.md](PERFORMANCE_TARGETS.md)
3. **Optimize** - If needed, adjust configuration
4. **Document** - Update performance documentation

---

**For more information:**
- [QUICK_START.md](QUICK_START.md) - Setup guide
- [PERFORMANCE_TARGETS.md](PERFORMANCE_TARGETS.md) - Performance goals
- [USER_GUIDE.md](USER_GUIDE.md) - Configuration guide

