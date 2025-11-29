# Jane Project Checklist

High-level checklist to track progress across phases. Check items as you complete them.

---

## Phase 0 – Environment & Project Setup

- [ ] Python, CUDA, Git, Node, Rust installed and verified
- [ ] Project structure created (`src/backend`, `src/frontend`, `models`, `tests`, `config`, `docs`)
- [ ] Python virtual environment created and activated
- [ ] Core Python dependencies installed (STT, TTS, LLM, audio, utilities)
- [ ] `test_imports.py` runs successfully and detects CUDA + audio devices

---

## Phase 1 – Core Voice & Models (Quality-First)

- [ ] Faster-Whisper STT engine implemented and tested on GPU
- [ ] Real-time audio capture with VAD working reliably
- [ ] Basic streaming/record-and-transcribe STT pipeline tested
- [ ] TTS engine implemented (Coqui TTS) and verified on GPU
- [ ] Local LLM (e.g., Qwen 2.5 32B Instruct GGUF) downloaded
- [ ] LLM engine (llama.cpp Python binding) loads model on GPU
- [ ] Prompt/response generation and basic chat mode working
- [ ] End-to-end **voice → STT → LLM → TTS** loop works from CLI (no UI yet)

---

## Phase 2 – Configuration & Logging

- [ ] Config system defined (e.g., `config/settings.yaml` or equivalent)
- [ ] Settings for:
  - [ ] Conversation style (concise vs chatty)
  - [ ] Quality vs speed (model/parameters, STT/TTS options)
  - [ ] Safety level and trusted folders
  - [ ] Logging level (info/debug/trace)
- [ ] Centralized logging implemented (structured logs to disk)
- [ ] Logs include:
  - [ ] STT transcripts
  - [ ] Parsed commands / function calls
  - [ ] LLM prompts/responses (configurable/redactable)
  - [ ] Errors/exceptions and performance metrics
- [ ] “Panic switch” implemented to clear logs and/or disable logging

---

## Phase 3 – Computer Control (Guarded)

- [ ] File controller for read/write/list/search within trusted folders
- [ ] Safe path checks and enforcement of trusted directories
- [ ] App controller for launching/listing/closing/focusing apps
- [ ] Input controller for keyboard and mouse actions with fail-safes
- [ ] All destructive actions require explicit confirmation by default
- [ ] Ability to mark certain actions as “always allow” (user opt-in)
- [ ] Integration of controllers into the assistant core (function calling or equivalent)

---

## Phase 4 – Assistant Core & Conversation

- [ ] Unified `AssistantCore` (or equivalent) composing:
  - [ ] STT engine
  - [ ] TTS engine
  - [ ] LLM engine
  - [ ] Function/controller layer (files, apps, input)
- [ ] Conversation history maintained across turns
- [ ] Basic CLI conversation loop:
  - [ ] Push-to-talk style interaction
  - [ ] Ability to exit gracefully
- [ ] Computer control actions callable from natural language (with confirmations)

---

## Phase 5 – Desktop Application (Tauri UI)

- [ ] Tauri project created and runs dev build
- [ ] System tray integration:
  - [ ] Tray icon
  - [ ] Menu items (Show, Start/Stop Listening, Settings, Quit)
- [ ] Minimal UI:
  - [ ] Status area (Idle, Listening, Thinking, Speaking, Error)
  - [ ] Conversation view (history)
  - [ ] Push-to-talk button
  - [ ] Button to open settings
- [ ] Backend HTTP/IPC API wired to UI:
  - [ ] `/health`
  - [ ] `/listen`
  - [ ] `/process`
  - [ ] `/speak`
- [ ] End-to-end voice interaction works through the desktop UI

---

## Phase 6 – Wake Word & Advanced Features

- [ ] Wake word detector integrated (e.g., Porcupine)
- [ ] Wake word togglable in settings (on/off)
- [ ] Wake word activates listening flow reliably with low false positives
- [ ] (Optional) Vision pipeline for screenshot understanding
- [ ] (Optional) RAG/personal knowledge base

---

## Phase 7 – Testing & Optimization

- [ ] Performance benchmarks created and run:
  - [ ] STT latency
  - [ ] LLM throughput (tokens/sec)
  - [ ] TTS latency
  - [ ] End-to-end interaction time
- [ ] Integration tests for:
  - [ ] File operations
  - [ ] App control
  - [ ] Conversation context
  - [ ] Time/date and other utility functions
- [ ] Performance targets met or understood (with notes)

---

## Phase 8 – Packaging & Documentation

- [ ] Backend packaged as an executable (e.g., PyInstaller)
- [ ] Tauri app built for release
- [ ] Start script / launcher that brings up backend + UI together
- [ ] Models bundled or clearly documented for download
- [ ] `README.md` updated with:
  - [ ] Clear installation steps
  - [ ] Usage examples
  - [ ] Safety and privacy notes
- [ ] Additional docs (`docs/DEVELOPMENT.md`, etc.) created

---

## Meta / Project Management

- [ ] This checklist reviewed and adjusted after initial implementation begins
- [ ] Personal notes / decisions log (optional, but recommended)


