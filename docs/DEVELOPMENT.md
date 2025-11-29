# Jane Development Notes

This document captures development setup, conventions, and high-level decisions for Jane.

---

## Local Development Setup

- Windows 11 with RTX 4090 and recent NVIDIA drivers.
- Python 3.11+ with virtual environment.
- CUDA Toolkit 12.x installed and on `PATH`.
- Node.js 18+ and Rust (latest stable) for the Tauri UI.

See `voice-assistant-implementation-plan.md` for detailed step-by-step environment setup and tooling verification.

---

## Configuration

- All runtime configuration should be driven through `config/settings.yaml` (user-local) with `config/settings.example.yaml` checked into source as the template.
- Major configuration areas:
  - **Models**: STT, LLM, TTS selection and context/fast-mode toggles.
  - **Conversation**: style (concise vs chatty), response limits.
  - **Safety**: trusted directories, destructive action confirmations, “always allow” toggles.
  - **Interaction**: wake word and push-to-talk flags.
  - **Logging**: enable/disable, level, and whether to include LLM prompts/responses.

On first run, the backend should:
- Look for `config/settings.yaml`.
- If missing, copy from `config/settings.example.yaml` and log that default settings were created.

---

## Logging

- Default log directory: `logs/`.
- Logs should be structured and machine-parseable (JSON lines is preferred).
- At minimum, log:
  - Timestamp and log level.
  - Source component (STT, LLM, TTS, assistant core, controllers).
  - Correlation ID for a single user interaction (voice → STT → LLM → TTS).
  - Errors/exceptions with stack traces.
  - Basic performance metrics (latency, tokens/sec, VRAM usage snapshots where possible).

The “panic switch” is a configuration and/or runtime control that:
- Deletes existing logs.
- Disables further logging until explicitly re-enabled.

---

## Safety Model

- Treat **trusted directories** as the primary scope for file operations.
- Any access outside trusted directories must:
  - Prompt the user for one-off confirmation, and
  - Optionally allow adding that path (or its parent) to `trusted_directories`.
- Destructive operations (delete/move/overwrite, closing applications, sending key sequences that could lead to data loss) require confirmation by default.
- Keep a clear separation between:
  - Parsing user intent (LLM),
  - Selecting a function to call, and
  - Executing that function under safety checks.

---

## UI & Interaction

- The Tauri app should default to:
  - A **system tray** presence with status and quick actions.
  - A minimal visible window with:
    - Status indicator (idle, listening, thinking, speaking, error).
    - Conversation history.
    - Push-to-talk button and a way to open Settings.
- The full chat window should support:
  - Switching conversation style (concise/chatty).
  - Toggling fast mode vs quality-first.
  - Viewing recent logs/metrics for debugging (developer mode).

---

## Testing Strategy

- Unit tests for:
  - STT/LLM/TTS wrappers (basic import and call success).
  - File/app/input controllers (with mocks where possible).
  - Safety logic (trusted directory checks, confirmation gating).
- Integration tests for:
  - File operations via natural language prompts.
  - Application launch/close.
  - Conversation context retention.
  - Time/date and utility functions.
- Performance tests for:
  - STT latency.
  - LLM tokens/sec.
  - TTS latency.
  - End-to-end interaction time.


