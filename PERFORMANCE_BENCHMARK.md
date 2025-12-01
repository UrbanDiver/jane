# Performance Benchmark Report
**Date:** 2025-11-30 23:24:29
**System:** win32
**GPU:** NVIDIA GeForce RTX 4090 Laptop GPU
**CUDA Version:** 12.1

## Results

### STT Engine
- Error: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>

### TTS Engine
- Initialization: 0.5340375900268555
- Synthesis: 0.7837264537811279
- GPU Memory: 0.37 GB

### LLM Engine
- Initialization: 2.1913809776306152
- Generation Time: 10.791870832443237s
- Tokens per Second: 7.320324828435211
- GPU Memory: 0.24 GB

### End-to-End Interaction
- Error: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>

### Streaming Response
- Error: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>

## Performance Targets

- STT Latency: <500ms
- LLM Inference: 60-120 tokens/second
- TTS Latency: <2s
- End-to-End: <5s
