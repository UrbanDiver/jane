# Jane - AI Voice Assistant

A GPU-accelerated, privacy-first voice-based personal assistant for Windows desktop.

## Overview

Jane is a self-hosted AI assistant that runs entirely on your local machine, powered by your RTX 4090. No cloud services, complete privacy, and full computer control capabilities.

## Features

- **Voice Control**: Natural voice commands with wake word detection
- **Computer Automation**: Control files, applications, keyboard, and mouse
- **Information Retrieval**: Answer questions and provide assistance
- **Screen Understanding**: Vision-based screen analysis
- **Privacy-First**: All processing happens locally on your machine

## Hardware Requirements

- MSI Studio with RTX 4090 (24GB VRAM)
- 32GB+ RAM
- 100GB+ free storage
- Quality microphone and speakers

## Technology Stack

- **STT**: faster-whisper (GPU-accelerated Whisper)
- **LLM**: Qwen 2.5 32B or Llama 3.1 70B (via llama.cpp)
- **TTS**: Coqui TTS / StyleTTS2
- **Frontend**: Tauri (Rust + Web)
- **Backend**: Python with CUDA acceleration

## Current Status

🚧 **In Development** - See [Implementation Plan](voice-assistant-implementation-plan.md) for detailed roadmap.

## Quick Start

*Coming soon - project is in early development*

## Documentation

- [Implementation Plan](voice-assistant-implementation-plan.md) - Detailed step-by-step development plan
- More documentation coming as development progresses

## Performance Targets

- STT latency: <500ms
- LLM inference: 60-120 tokens/second
- TTS latency: <2s
- End-to-end interaction: <5s

## License

MIT

## Acknowledgments

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [Tauri](https://tauri.app/)
