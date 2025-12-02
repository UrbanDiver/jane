# Model Performance Comparison

**Date:** 2025-12-01  
**System:** RTX 4090 Laptop GPU, CUDA 12.1

---

## Performance Results

| Model | Size | Init Time | Tokens/sec (first) | Tokens/sec (warm) | Notes |
|-------|------|-----------|-------------------|-------------------|-------|
| **Q4_K_M** | 4.36 GB | 2.32s | 6.77 | 6.77 | Baseline |
| **Q5_K_M** | 5.07 GB | 0.60s | 8.64 | **10.11** | ✅ Best performance |
| **Q6_K** | 5.82 GB | 0.71s | 7.22 | 8.54 | ⚠️ Slower than Q5_K_M |

---

## Analysis

### Q5_K_M is Optimal for 7B Model
- **Best tokens/sec:** 10.11 (warm)
- **Fastest initialization:** 0.60s
- **Best balance:** Quality vs Speed

### Q6_K Performance Issue
- Higher precision but slower than Q5_K_M
- Possible causes:
  - More dequantization overhead
  - Different memory access patterns
  - GPU utilization differences

### Recommendation
- **Use Q5_K_M** for 7B model (best performance)
- **Try 3B model** for faster inference (expected 40-80 tokens/sec)

---

## Next Steps

1. ✅ Tested Q4_K_M, Q5_K_M, Q6_K
2. ⏳ Try 3B model (Qwen2.5-3B-Instruct) for speed
3. ⏳ Optimize function calling overhead

---

**Conclusion:** Q5_K_M provides the best performance for the 7B model size.

