# Performance Benchmark Report
**Date:** 2025-12-01 17:23:03
**System:** win32
**GPU:** NVIDIA GeForce RTX 4090 Laptop GPU
**CUDA Version:** 12.1

## Results

### STT Engine
- Initialization: 3.0277912616729736
- Transcription: None
- GPU Memory: 0.00 GB

### TTS Engine
- Initialization: 0.5487043857574463
- Synthesis: 0.7661340236663818
- GPU Memory: 0.37 GB

### LLM Engine
- Initialization: 2.313567638397217
- Generation Time: 11.913233518600464s
- Tokens per Second: 6.631281077186567
- GPU Memory: 0.24 GB

### End-to-End Interaction
- Initialization: None
- Command Processing: None
- GPU Memory: 0.61 GB

### Streaming Response
- First Token Latency: 40.54173517227173s
- Total Time: 40.54173517227173s

## Performance Targets

- STT Latency: <500ms
- LLM Inference: 60-120 tokens/second
- TTS Latency: <2s
- End-to-End: <5s
