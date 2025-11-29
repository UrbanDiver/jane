# Logs Directory

This directory is intended to hold all runtime logs for Jane.

- Default location is `logs/` at the project root (configurable in `config/settings.yaml`).
- Prefer structured logs (e.g., JSON lines) to simplify analysis and debugging.
- Consider separate files per component (e.g., `assistant.log`, `stt.log`, `llm.log`, `tts.log`, `control.log`) if it stays manageable.

The “panic switch” should:
- Clear existing log files under this directory.
- Disable further logging until the user explicitly re-enables it.


