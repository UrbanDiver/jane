# Jane AI Voice Assistant - Developer Guide

**Complete guide for developers extending and contributing to Jane AI**

---

## 📖 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Extending the Assistant](#extending-the-assistant)
5. [Plugin Development](#plugin-development)
6. [API Development](#api-development)
7. [Testing](#testing)
8. [Contributing](#contributing)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AssistantCore                         │
│  (Orchestrates all components)                          │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    │          │          │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│  STT  │ │  TTS  │ │  LLM  │ │ Func  │ │Plugin │
│Engine │ │Engine │ │Engine │ │Handler│ │Manager│
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │          │          │          │          │
┌───▼──────────▼──────────▼──────────▼──────────▼───┐
│         Controllers (File, App, Input)             │
└────────────────────────────────────────────────────┘
```

### Component Interaction

1. **Audio Input** → STT Engine → Text
2. **Text** → LLM Engine → Response + Function Calls
3. **Function Calls** → Function Handler → Results
4. **Response** → TTS Engine → Audio Output

### Data Flow

```
User Voice
    ↓
Audio Capture (VAD)
    ↓
STT Engine (Whisper)
    ↓
Text Transcription
    ↓
Context Manager (Pruning)
    ↓
LLM Engine (Qwen2.5)
    ↓
Response + Function Calls
    ↓
Function Handler (Execute)
    ↓
Response Generation
    ↓
TTS Engine (Tacotron2)
    ↓
Audio Output
```

---

## Project Structure

```
jane/
├── src/
│   ├── backend/          # Core engine implementations
│   │   ├── assistant_core.py      # Main orchestrator
│   │   ├── stt_engine.py          # Speech-to-Text
│   │   ├── tts_engine.py           # Text-to-Speech
│   │   ├── llm_engine.py           # Language Model
│   │   ├── function_handler.py     # Function management
│   │   ├── context_manager.py      # Context pruning
│   │   ├── conversation_state.py  # State management
│   │   ├── wake_word_detector.py  # Wake word detection
│   │   └── controllers/            # File, App, Input
│   ├── config/           # Configuration system
│   │   ├── config_schema.py        # Pydantic models
│   │   └── config_loader.py        # YAML + env loading
│   ├── utils/            # Utilities
│   │   ├── logger.py               # Logging system
│   │   ├── retry.py                # Retry logic
│   │   ├── error_handler.py        # Error handling
│   │   ├── memory_manager.py       # Memory management
│   │   ├── sentence_splitter.py    # Sentence detection
│   │   └── factories.py             # Component factories
│   ├── interfaces/       # Abstract base classes
│   │   ├── engines.py              # Engine interfaces
│   │   ├── controllers.py          # Controller interfaces
│   │   └── function_handler.py     # Function handler interface
│   ├── plugins/          # Plugin system
│   │   ├── plugin_base.py          # Base plugin class
│   │   ├── plugin_manager.py       # Plugin manager
│   │   └── example_plugin.py       # Example plugin
│   └── api/              # API layer
│       ├── main.py                 # FastAPI app
│       ├── routes.py               # REST endpoints
│       ├── websocket.py            # WebSocket handler
│       └── server.py               # Server entry point
├── examples/             # Example code
│   └── api_client_example.py
├── models/               # LLM model files
├── data/                 # Data files (state, etc.)
├── logs/                 # Log files
├── config.yaml           # Configuration file
├── requirements.txt      # Dependencies
└── jane.py              # Main entry point
```

---

## Core Components

### AssistantCore

**Location:** `src/backend/assistant_core.py`

**Purpose:** Main orchestrator that coordinates all components

**Key Methods:**
- `process_command(text)` - Process text command
- `listen(duration)` - Listen for voice input
- `speak(text)` - Synthesize and play speech
- `run_voice_loop()` - Main voice interaction loop

**Dependencies:**
- STT Engine
- TTS Engine
- LLM Engine
- Function Handler
- Controllers
- Context Manager
- Conversation State
- Plugin Manager

### STT Engine

**Location:** `src/backend/stt_engine.py`

**Interface:** `STTEngineInterface`

**Features:**
- Whisper model integration
- GPU acceleration
- Model caching
- Quantization support
- Chunked processing

**Usage:**
```python
from src.backend.stt_engine import STTEngine

stt = STTEngine(model_size="medium", device="cuda")
result = stt.transcribe("audio.wav")
print(result["text"])
```

### TTS Engine

**Location:** `src/backend/tts_engine.py`

**Interface:** `TTSEngineInterface`

**Features:**
- Coqui TTS integration
- GPU acceleration
- Streaming synthesis
- Multiple model support

**Usage:**
```python
from src.backend.tts_engine import TTSEngine

tts = TTSEngine(device="cuda")
tts.speak("Hello, world!")
```

### LLM Engine

**Location:** `src/backend/llm_engine.py`

**Interface:** `LLMEngineInterface`

**Features:**
- llama.cpp integration
- Function calling support
- Streaming responses
- GPU acceleration

**Usage:**
```python
from src.backend.llm_engine import LLMEngine

llm = LLMEngine(model_path="models/model.gguf")
response = llm.chat(messages, tools=functions)
```

### Function Handler

**Location:** `src/backend/function_handler.py`

**Interface:** `FunctionHandlerInterface`

**Features:**
- Function registration
- LLM-compatible format
- Function execution
- Result formatting

**Usage:**
```python
from src.backend.function_handler import FunctionHandler

handler = FunctionHandler()
handler.register("my_function", my_func, "Description", {})
functions = handler.format_functions_for_llm()
```

---

## Extending the Assistant

### Adding New Functions

1. **Create the function:**
   ```python
   def my_custom_function(param1: str, param2: int) -> str:
       """Does something custom."""
       return f"Result: {param1} {param2}"
   ```

2. **Register with FunctionHandler:**
   ```python
   # In assistant_core.py _register_functions()
   self.function_handler.register(
       "my_custom_function",
       my_custom_function,
       "Does something custom",
       {
           "type": "object",
           "properties": {
               "param1": {"type": "string"},
               "param2": {"type": "integer"}
           },
           "required": ["param1", "param2"]
       }
   )
   ```

3. **Test:**
   ```python
   # The LLM will automatically detect when to use it
   # Test with: "Use my_custom_function with param1='test' and param2=42"
   ```

### Creating Custom Controllers

1. **Implement the interface:**
   ```python
   from src.interfaces.controllers import FileControllerInterface
   from src.interfaces import implements

   @implements(FileControllerInterface)
   class CustomFileController:
       def read_file(self, file_path: str) -> dict:
           # Implementation
           pass
   ```

2. **Register in AssistantCore:**
   ```python
   assistant = AssistantCore(
       file_controller=CustomFileController()
   )
   ```

### Adding New Engines

1. **Implement the interface:**
   ```python
   from src.interfaces.engines import STTEngineInterface
   from src.interfaces import implements

   @implements(STTEngineInterface)
   class CustomSTTEngine:
       def transcribe(self, audio_path: str) -> dict:
           # Implementation
           pass
   ```

2. **Use dependency injection:**
   ```python
   assistant = AssistantCore(
       stt_engine=CustomSTTEngine()
   )
   ```

---

## Plugin Development

### Creating a Plugin

1. **Create plugin file** in `src/plugins/`:
   ```python
   from src.plugins.plugin_base import BasePlugin, PluginHook
   from typing import Dict, List, Callable

   class MyPlugin(BasePlugin):
       name = "My Plugin"
       version = "1.0.0"
       description = "My custom plugin description"
       
       def register_functions(self) -> List[Dict]:
           return [{
               "name": "plugin_function",
               "function": self.my_function,
               "description": "Does something",
               "parameters": {
                   "type": "object",
                   "properties": {},
                   "required": []
               }
           }]
       
       def register_hooks(self) -> Dict[PluginHook, Callable]:
           return {
               PluginHook.ON_MESSAGE_RECEIVED: self.on_message,
               PluginHook.AFTER_LLM_RESPONSE: self.after_response
           }
       
       def my_function(self) -> str:
           return "Plugin function result"
       
       def on_message(self, message: Dict) -> Dict:
           # Modify message before processing
           message["content"] += " (modified by plugin)"
           return message
       
       def after_response(self, response: Dict) -> Dict:
           # Modify response after LLM
           response["response"] += "\n(Plugin note)"
           return response
   ```

2. **Plugin is automatically discovered and loaded**

### Plugin Hooks

Available hooks:

- `ON_INIT` - Plugin initialization
- `ON_CLEANUP` - Plugin cleanup
- `ON_MESSAGE_RECEIVED` - Before message processing
- `BEFORE_LLM_RESPONSE` - Before LLM processing
- `AFTER_LLM_RESPONSE` - After LLM processing
- `BEFORE_TTS` - Before TTS synthesis
- `AFTER_TTS` - After TTS synthesis
- `BEFORE_FUNCTION_CALL` - Before function execution
- `AFTER_FUNCTION_CALL` - After function execution
- `ON_RESPONSE_SENT` - After response sent
- `ON_ERROR` - On error occurrence

### Plugin Example

See `src/plugins/example_plugin.py` for a complete example.

---

## API Development

### REST API

**Base URL:** `http://localhost:8000/api/v1`

**Endpoints:**
- `POST /chat` - Send text message
- `POST /transcribe` - Transcribe audio
- `POST /synthesize` - Synthesize text to speech
- `POST /functions/call` - Call function directly
- `GET /functions` - List all functions
- `GET /status` - Get assistant status

**Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"text": "Hello, Jane!"}
)
print(response.json())
```

### WebSocket API

**Endpoint:** `ws://localhost:8000/ws`

**Message Format:**
```json
{
    "type": "text",
    "text": "Hello, Jane!"
}
```

**Response Format:**
```json
{
    "type": "response",
    "text": "Hello! How can I help you?",
    "success": true
}
```

**Example:**
```python
import websockets
import json

async with websockets.connect("ws://localhost:8000/ws") as ws:
    await ws.send(json.dumps({
        "type": "text",
        "text": "Hello!"
    }))
    response = await ws.recv()
    print(json.loads(response))
```

### API Authentication

Enable API key authentication:

```powershell
python -m src.api.server --api-key "your-secret-key"
```

**Usage:**
```python
headers = {"Authorization": "Bearer your-secret-key"}
response = requests.post(url, json=data, headers=headers)
```

---

## Testing

### Running Tests

```powershell
# Run all tests
pytest

# Run specific test file
pytest test_config_system.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration test
python test_integration_all_improvements.py
```

### Test Structure

```
test_*.py              # Unit tests for each component
test_integration_*.py  # Integration tests
test_assistant_*.py    # End-to-end tests
```

### Writing Tests

**Example Unit Test:**
```python
import pytest
from src.backend.function_handler import FunctionHandler

def test_function_registration():
    handler = FunctionHandler()
    handler.register("test_func", lambda: "test", "Test", {})
    assert "test_func" in handler.list_functions()
```

**Example Integration Test:**
```python
def test_assistant_with_plugin():
    assistant = AssistantCore()
    # Test plugin integration
    assert len(assistant.plugin_manager.get_all_plugins()) > 0
```

### Test Coverage

Target: **80%+ coverage**

```powershell
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

---

## Contributing

### Development Setup

1. **Fork and clone:**
   ```powershell
   git clone <your-fork-url>
   cd jane
   ```

2. **Create branch:**
   ```powershell
   git checkout -b feature/my-feature
   ```

3. **Make changes:**
   - Follow code style (Black formatter)
   - Add tests
   - Update documentation

4. **Test:**
   ```powershell
   pytest
   python test_integration_all_improvements.py
   ```

5. **Commit:**
   ```powershell
   git add .
   git commit -m "feat: Add my feature"
   ```

6. **Push and create PR:**
   ```powershell
   git push origin feature/my-feature
   ```

### Code Style

- **Formatter:** Black
- **Linter:** flake8, pylint
- **Type hints:** Use type hints for all functions
- **Docstrings:** Google style

**Format code:**
```powershell
black src/
```

**Lint:**
```powershell
flake8 src/
pylint src/
```

### Commit Messages

Follow conventional commits:

```
feat: Add new feature
fix: Fix bug
perf: Performance improvement
refactor: Code refactoring
docs: Documentation changes
test: Test additions
chore: Maintenance tasks
```

### Pull Request Process

1. **Update tests** - Add tests for new features
2. **Update docs** - Update relevant documentation
3. **Run tests** - Ensure all tests pass
4. **Check coverage** - Maintain or improve coverage
5. **Update status** - Update `IMPROVEMENTS_STATUS.md` if applicable

---

## Architecture Details

### Dependency Injection

All components use dependency injection:

```python
# Factory functions
from src.utils.factories import (
    create_stt_engine,
    create_tts_engine,
    create_llm_engine
)

# Or inject directly
assistant = AssistantCore(
    stt_engine=CustomSTTEngine(),
    tts_engine=CustomTTSEngine()
)
```

### Configuration System

**Loading:**
```python
from src.config import get_config

config = get_config()
# Access: config.stt.model_size, config.llm.temperature, etc.
```

**Schema:**
```python
from src.config.config_schema import AssistantConfig, STTConfig

config = AssistantConfig(
    stt=STTConfig(model_size="large"),
    llm=LLMConfig(model_path="models/model.gguf")
)
```

### Logging System

**Usage:**
```python
from src.utils.logger import get_logger, log_performance

logger = get_logger(__name__)

@log_performance()
def my_function():
    logger.info("Processing...")
    # Function code
```

### Error Handling

**Usage:**
```python
from src.utils.error_handler import handle_error, ErrorType

try:
    # Risky operation
    pass
except Exception as e:
    result = handle_error(e, ErrorType.TRANSIENT, logger=logger)
    # result contains: error_type, is_retryable, recovery_strategy, message
```

### Retry Logic

**Usage:**
```python
from src.utils.retry import retry

@retry(max_retries=3, initial_delay=1.0, exponential_base=2.0)
def unreliable_function():
    # May fail, will retry automatically
    pass
```

---

## Advanced Topics

### Custom LLM Integration

Replace the LLM engine:

```python
from src.interfaces.engines import LLMEngineInterface

@implements(LLMEngineInterface)
class CustomLLMEngine:
    def chat(self, messages, max_tokens, temperature, tools=None):
        # Your LLM integration
        pass
```

### Custom STT Integration

Replace the STT engine:

```python
from src.interfaces.engines import STTEngineInterface

@implements(STTEngineInterface)
class CustomSTTEngine:
    def transcribe(self, audio_path: str) -> dict:
        # Your STT integration
        pass
```

### Streaming Implementation

Implement streaming in your engine:

```python
def stream_chat(self, messages, max_tokens, temperature, tools=None):
    for chunk in self.llm.stream(messages):
        yield {"response": chunk}
```

### Context Management

Custom context pruning:

```python
from src.backend.context_manager import ContextManager

def custom_summarize(messages):
    # Your summarization logic
    return "Summary..."

manager = ContextManager(
    summarize_callback=custom_summarize
)
```

---

## Performance Optimization

### STT Optimization

- Use smaller models for faster transcription
- Enable quantization: `compute_type: "int8"`
- Use chunked processing for long audio

### LLM Optimization

- Reduce context window: `n_ctx: 2048`
- Use smaller models
- Enable GPU offloading: `n_gpu_layers: -1`

### Memory Management

- Enable automatic cleanup: `memory_cleanup_interval: 5`
- Monitor GPU memory: `nvidia-smi`
- Use context pruning to limit history

---

## Debugging

### Enable Debug Logging

```yaml
# config.yaml
logging:
  level: "DEBUG"
```

### Common Debugging Steps

1. **Check logs:** `logs/jane.log`
2. **Run tests:** `pytest -v`
3. **Test components:** Individual test files
4. **Monitor resources:** `nvidia-smi`, `htop`
5. **Use debugger:** `pdb` or IDE debugger

### Debugging Tips

- Use `logger.debug()` for detailed logging
- Test components in isolation
- Use mock objects for testing
- Check GPU memory with `nvidia-smi`
- Monitor CPU/memory with `psutil`

---

## Resources

- **API Documentation:** http://localhost:8000/docs (when API server running)
- **Implementation Plan:** `IMPROVEMENTS_IMPLEMENTATION_PLAN.md`
- **Status:** `IMPROVEMENTS_STATUS.md`
- **Test Results:** `TEST_RESULTS.md`
- **Complete Summary:** `IMPROVEMENTS_COMPLETE_SUMMARY.md`

---

## Getting Help

- Review existing code for patterns
- Check test files for usage examples
- Review plugin examples
- Check interface definitions for contracts

---

**Happy coding!** 🚀

