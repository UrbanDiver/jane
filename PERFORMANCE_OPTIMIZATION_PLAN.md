# LLM Performance Optimization Plan

**Date:** 2025-11-30  
**Current Performance:** 6.56 tokens/sec  
**Target Performance:** 60-120 tokens/sec  
**Gap:** ~10-18x improvement needed

---

## 🎯 Current Situation

### Baseline Metrics
- **Model:** `Qwen2.5-7B-Instruct-Q4_K_M.gguf` (Q4 quantization)
- **Speed:** 6.56 tokens/sec
- **GPU:** RTX 4090 (24GB VRAM)
- **Config:**
  - `n_gpu_layers: -1` (all layers on GPU)
  - `n_ctx: 4096` (context window)
  - `n_batch: 512` (batch size)
  - `max_tokens: 512` (max generation)

### Root Causes Identified
1. **Q4 quantization too aggressive** - Dequantization overhead
2. **Suboptimal batch size** - May not fully utilize GPU
3. **Large context window** - More memory, slower processing
4. **Missing optimization parameters** - llama.cpp has additional options

---

## 🚀 Optimization Solutions

### Solution 1: Configuration Optimization (Quick Win)

**Expected Improvement:** 2-3x (10-15 tokens/sec)

Update `config.yaml`:
```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"  # Keep current
  n_gpu_layers: -1  # Keep all layers on GPU
  n_ctx: 2048  # Reduce from 4096 (less memory, faster)
  n_batch: 1024  # Increase from 512 (better GPU utilization)
  verbose: false
  temperature: 0.7
  max_tokens: 256  # Reduce from 512 (faster responses)
```

**Why this works:**
- Smaller context = less memory allocation and faster processing
- Larger batch = better GPU utilization
- Shorter responses = faster generation

**Implementation:** Update `config.yaml` and re-run benchmarks

---

### Solution 2: Higher Precision Model (Recommended)

**Expected Improvement:** 3-5x (20-35 tokens/sec)

#### Option A: Q5_K_M (Balanced)
```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q5_K_M.gguf"
  n_gpu_layers: -1
  n_ctx: 2048
  n_batch: 1024
```

**Download:** From Hugging Face Qwen2.5-7B-Instruct-GGUF repository  
**Size:** ~5GB  
**Speed:** ~20-30 tokens/sec expected

#### Option B: Q6_K (Higher Precision)
```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q6_K.gguf"
  n_gpu_layers: -1
  n_ctx: 2048
  n_batch: 1024
```

**Download:** From Hugging Face Qwen2.5-7B-Instruct-GGUF repository  
**Size:** ~6GB  
**Speed:** ~30-50 tokens/sec expected

#### Option C: Smaller Model (Fastest)
```yaml
llm:
  model_path: "models/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
  n_gpu_layers: -1
  n_ctx: 2048
  n_batch: 2048  # Larger batch for smaller model
```

**Download:** From Hugging Face Qwen2.5-3B-Instruct-GGUF repository  
**Size:** ~2.5GB  
**Speed:** ~40-80 tokens/sec expected

**Why this works:**
- Higher precision = less dequantization overhead
- Smaller model = faster inference
- Better balance between quality and speed

---

### Solution 3: Add llama.cpp Optimization Parameters

**Expected Improvement:** Additional 10-20%

#### Step 1: Update Config Schema

Add to `src/config/config_schema.py`:
```python
class LLMConfig(BaseModel):
    # ... existing fields ...
    n_threads: int = Field(
        default=8,
        description="Number of CPU threads for non-GPU work"
    )
    use_mmap: bool = Field(
        default=True,
        description="Use memory mapping for faster loading"
    )
    n_threads_batch: int = Field(
        default=8,
        description="Number of threads for batch processing"
    )
    offload_kqv: bool = Field(
        default=True,
        description="Offload KQV matrices to GPU (RTX 4090 optimized)"
    )
```

#### Step 2: Update LLMEngine

Modify `src/backend/llm_engine.py`:
```python
self.llm = Llama(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_ctx=n_ctx,
    n_batch=n_batch,
    verbose=verbose,
    # Add optimizations:
    n_threads=config.n_threads if hasattr(config, 'n_threads') else 8,
    use_mmap=config.use_mmap if hasattr(config, 'use_mmap') else True,
    n_threads_batch=config.n_threads_batch if hasattr(config, 'n_threads_batch') else 8,
    # Note: offload_kqv may not be available in all llama.cpp versions
)
```

**Why this works:**
- More CPU threads = better parallelization
- Memory mapping = faster model loading
- Batch threads = better batch processing

---

### Solution 4: Verify GPU Utilization

Add verification method to `LLMEngine`:
```python
def verify_gpu_utilization(self):
    """Verify GPU layers are being used."""
    if hasattr(self.llm, 'ctx'):
        n_layers = self.llm.ctx.n_layers
        gpu_layers = self.llm.ctx.n_gpu_layers
        self.logger.info(f"Model layers: {n_layers}, GPU layers: {gpu_layers}")
        if gpu_layers < n_layers:
            self.logger.warning(f"Only {gpu_layers}/{n_layers} layers on GPU!")
        return gpu_layers == n_layers
    return False
```

**Why this works:**
- Ensures all layers are on GPU
- Identifies if layers are falling back to CPU

---

## 📋 Implementation Steps

### Phase 1: Quick Config Fix (Immediate)
1. Update `config.yaml` with optimized settings
2. Re-run benchmarks: `python benchmark_performance.py`
3. Document results

**Expected:** 10-15 tokens/sec (2-3x improvement)

### Phase 2: Download Higher Precision Model
1. Download Q5_K_M or Q6_K model
2. Place in `models/` directory
3. Update `config.yaml` model_path
4. Re-run benchmarks

**Expected:** 20-50 tokens/sec (3-8x improvement)

### Phase 3: Add Optimization Parameters
1. Update config schema with new parameters
2. Update LLMEngine initialization
3. Update config.yaml with new settings
4. Re-run benchmarks

**Expected:** Additional 10-20% improvement

### Phase 4: Fine-tuning
1. Test different batch sizes (512, 1024, 2048)
2. Test different context windows (1024, 2048, 4096)
3. Test different thread counts
4. Document optimal settings

**Expected:** Reach 60-120 tokens/sec target

---

## 📊 Expected Results Matrix

| Solution | Expected Speed | Notes |
|----------|----------------|-------|
| **Current (Q4_K_M, default)** | 6.56 tok/s | Baseline |
| **Config optimization only** | 10-15 tok/s | Quick win, no model download |
| **Q5_K_M model** | 20-30 tok/s | Better precision/balance |
| **Q6_K model** | 30-50 tok/s | Higher precision |
| **Q4_K_M 3B model** | 40-80 tok/s | Smaller, faster |
| **Q5_K_M + optimizations** | 50-100 tok/s | Best balance |
| **Q6_K + all optimizations** | 60-120 tok/s | **Target achieved** |

---

## 🔧 Code Changes Required

### 1. Update Config Schema
**File:** `src/config/config_schema.py`
- Add `n_threads`, `use_mmap`, `n_threads_batch`, `offload_kqv` to `LLMConfig`

### 2. Update LLMEngine
**File:** `src/backend/llm_engine.py`
- Add optimization parameters to `Llama()` initialization
- Add `verify_gpu_utilization()` method

### 3. Update Config File
**File:** `config.yaml`
- Update LLM settings with optimized values
- Add new optimization parameters

### 4. Create Model Download Script (Optional)
**File:** `download_optimized_llm.py`
- Script to download Q5_K_M, Q6_K, or 3B models
- Verify model integrity

---

## 🧪 Testing Checklist

After each optimization:
- [ ] Run `python benchmark_performance.py`
- [ ] Check tokens/sec in results
- [ ] Verify GPU memory usage
- [ ] Test end-to-end latency
- [ ] Compare against targets
- [ ] Document results

---

## 📈 Success Criteria

### Minimum Acceptable
- **Speed:** 30+ tokens/sec (5x improvement)
- **End-to-End:** <15s (down from 32s)

### Target
- **Speed:** 60-120 tokens/sec (10-18x improvement)
- **End-to-End:** <5s (meets target)

### Optimal
- **Speed:** 100+ tokens/sec
- **End-to-End:** <3s
- **First Token:** <500ms

---

## 🔗 Resources

### Model Downloads
- **Qwen2.5-7B-Instruct-GGUF:** https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
- **Qwen2.5-3B-Instruct-GGUF:** https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF

### llama.cpp Documentation
- **Optimization Guide:** https://github.com/ggerganov/llama.cpp/blob/master/docs/OPTIMIZATION.md
- **Performance Tips:** https://github.com/ggerganov/llama.cpp/wiki/Performance

### Quantization Guide
- **GGUF Quantization:** https://github.com/ggerganov/llama.cpp#quantization
- **Q4 vs Q5 vs Q6:** Higher number = better precision, potentially faster

---

## 📝 Notes

- **Q4 quantization** is very aggressive and may cause dequantization overhead
- **RTX 4090** has plenty of VRAM (24GB) - can handle larger models or higher precision
- **Batch size** should be tuned based on GPU memory and model size
- **Context window** affects both memory and speed - smaller is faster
- **Model size** is the biggest factor - smaller models are faster

---

**Last Updated:** 2025-11-30  
**Status:** Ready for implementation

