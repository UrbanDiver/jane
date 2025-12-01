# Performance Benchmark Report
**Date:** 2025-11-30 23:32:33
**System:** win32
**GPU:** NVIDIA GeForce RTX 4090 Laptop GPU
**CUDA Version:** 12.1

## Results

### STT Engine
- Initialization: 2.7360599040985107
- Transcription: None
- GPU Memory: 0.00 GB

### TTS Engine
- Initialization: 0.5116291046142578
- Synthesis: 0.7579872608184814
- GPU Memory: 0.37 GB

### LLM Engine
- Initialization: 2.082853078842163
- Generation Time: 12.044970989227295s
- Tokens per Second: 6.558753862558533
- GPU Memory: 0.24 GB

### End-to-End Interaction
- Initialization: None
- Command Processing: None
- GPU Memory: 0.61 GB

### Streaming Response
- First Token Latency: 45.337762117385864s
- Total Time: 45.337762117385864s

## Performance Targets

- STT Latency: <500ms
- LLM Inference: 60-120 tokens/second
- TTS Latency: <2s
- End-to-End: <5s
