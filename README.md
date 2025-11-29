# Jane - AI Voice Assistant

A GPU-accelerated, privacy-first voice-based personal assistant for Windows desktop.

## Overview

Jane is a self-hosted AI assistant that runs entirely on your local machine, powered by your RTX 4090. No cloud services are required for core operation: speech recognition, language understanding, and speech synthesis all run locally. Jane is designed to be both:
- A **Jarvis-style PC automation copilot** (apps, files, keyboard/mouse), and
- A **conversational Q&A / coding / reasoning helper**.

## Core Experience

- **Interaction Modes**:
  - **Wake word** (hands-free) and **push-to-talk** (precise, good for noisy environments).
  - **Configurable conversation style**: concise/neutral vs more chatty/personable.
- **Model Strategy**:
  - **Quality-first** by default (larger local models, better reasoning).
  - Optional **Fast Mode** that prioritizes latency over maximum quality.

## Features (Planned Roadmap)

- **Voice Control**: Natural voice commands with wake word detection and push-to-talk.
- **Computer Automation**: Control files, applications, keyboard, and mouse (with safety checks).
- **Information Retrieval**: Answer questions, help with coding, and provide explanations.
- **Screen Understanding**: Vision-based screen analysis (later phase).
- **Privacy-First**: All core processing happens locally on your machine.

## Safety & Permissions

- **Conservative by default**:
  - Destructive actions (deleting/moving files, closing apps, etc.) require explicit confirmation.
  - Ability to mark some actions as “always allow” after explicit opt-in.
- **Trusted Locations**:
  - Out of the box, Jane operates primarily in user-owned folders like `Desktop`, `Documents`, and `Downloads`.
  - Additional folders can be added to a **trusted list** in settings.
  - Access outside trusted locations always requires explicit permission.

## Logging & Debugging

- **Detailed local logging** (no data leaves your machine):
  - STT transcripts, parsed commands, function calls, and errors.
  - Performance metrics (latency, VRAM usage, tokens/sec) for tuning.
- Configurable log levels (info/debug/trace) and a **panic switch** to clear logs and/or turn logging off.

## Hardware Requirements

- MSI Studio with RTX 4090 (24GB VRAM)
- 32GB+ RAM
- 100GB+ free storage
- Quality microphone and speakers

## Technology Stack

- **STT**: faster-whisper (GPU-accelerated Whisper)
- **LLM**: Qwen 2.5 32B (GGUF via llama.cpp) or similar high-quality local model
- **TTS**: Coqui TTS / StyleTTS2
- **Frontend**: Tauri (Rust + Web)
- **Backend**: Python with CUDA acceleration

## Current Status

🚧 **In Development** – See [Implementation Plan](voice-assistant-implementation-plan.md) for the detailed roadmap and phases.

## Quick Start

*Coming soon – project is in early development.*

## Documentation

- [Implementation Plan](voice-assistant-implementation-plan.md) – Detailed step-by-step development plan
- `PROJECT_CHECKLIST.md` – High-level checklist tracking progress across phases

## Performance Targets

- STT latency: <500ms
- LLM inference: 60–120 tokens/second
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
