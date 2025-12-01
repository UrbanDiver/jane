# Jane AI Voice Assistant - User Guide

**Complete guide to using Jane AI Voice Assistant**

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Voice Interaction](#voice-interaction)
4. [Features](#features)
5. [Configuration](#configuration)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

Jane AI Voice Assistant is a fully functional voice-controlled AI assistant that can:

- **Listen** to your voice commands
- **Understand** natural language
- **Respond** with text and speech
- **Control** your computer (files, apps, input)
- **Search** the web
- **Provide** system information
- **Remember** conversation context

---

## Getting Started

### First Run

1. **Start the assistant:**
   ```powershell
   python jane.py
   ```

2. **Wait for initialization:**
   - STT engine loads (Whisper model)
   - TTS engine loads (Tacotron2 model)
   - LLM engine loads (Qwen2.5 model)
   - First time: 2-3 minutes
   - Subsequent runs: ~30 seconds

3. **You'll hear:** "Hello! I'm Jane, your AI assistant. I'm ready to help you."

4. **Start speaking!** The assistant listens for 5 seconds by default.

### Basic Interaction Flow

```
You speak → STT transcribes → LLM processes → Assistant responds (text + speech)
```

---

## Voice Interaction

### Standard Mode

In standard mode, the assistant continuously listens:

1. **Speak your command** (within 5 seconds)
2. **Wait for transcription** (shown on screen)
3. **Receive response** (text displayed + speech)

### Wake Word Mode

Enable wake word detection for energy-efficient operation:

```yaml
# config.yaml
wake_word:
  enabled: true
  wake_words: ["jane", "hey jane"]
```

**How it works:**
1. Assistant listens for wake word (low-power mode)
2. When wake word detected, full STT activates
3. Process your command
4. Return to wake word listening

**Example:**
- You: "Jane, what time is it?"
- Assistant: "It's 3:45 PM"
- Assistant: Returns to wake word listening

### Voice Commands

#### Time and Date
- "What time is it?"
- "What's today's date?"
- "What's the current date and time?"

#### File Operations
- "List files in Documents"
- "Read the file test.txt"
- "Create a file called notes.txt"
- "Search for Python files in Downloads"

#### Application Control
- "Open calculator"
- "Launch notepad"
- "Close calculator"
- "What applications are running?"

#### System Information
- "What's my system information?"
- "Show CPU usage"
- "How much memory do I have?"
- "What's my disk usage?"

#### Web Search
- "Search the web for Python programming"
- "Look up artificial intelligence"
- "Find information about machine learning"

#### General Conversation
- "Hello"
- "What can you help me with?"
- "Tell me a joke"
- "Explain quantum computing"

---

## Features

### 🎯 Native Function Calling

The assistant intelligently decides when to use functions:

- **Automatic detection** of when functions are needed
- **Multi-step chains** (e.g., search web → read file → summarize)
- **Context-aware** function selection

### 💾 Conversation Context

The assistant remembers:

- **Topics** discussed in conversation
- **User preferences** (theme, language, etc.)
- **Important keywords** and context
- **Conversation history** (with smart pruning)

### 🔄 Streaming Responses

- **Real-time text** appears as it's generated
- **Early TTS** starts speaking before full response
- **Reduced latency** for better user experience

### 🎤 Wake Word Detection

- **Energy-efficient** continuous listening
- **Configurable** wake words
- **Command extraction** from wake word phrases

### 🌐 Web Search

- **DuckDuckGo** integration
- **Formatted results** for easy reading
- **Multiple results** with snippets

### 💻 System Control

- **File operations** (read, write, list, search)
- **Application control** (launch, close, list)
- **Input control** (screenshot, typing)
- **Safe mode** enabled by default

### 🔌 Plugin System

Extend functionality with plugins:

- **Dynamic loading** of plugins
- **Hook system** for customization
- **Function registration** from plugins

---

## Configuration

### Configuration File

Create `config.yaml`:

```yaml
# LLM Configuration
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
  n_gpu_layers: -1  # All layers on GPU
  n_ctx: 4096  # Context window
  temperature: 0.7  # Creativity (0.0-1.0)
  max_tokens: 512

# STT Configuration
stt:
  model_size: "medium"  # tiny, base, small, medium, large-v2, large-v3
  device: "cuda"  # cuda or cpu
  compute_type: "float16"  # float16, int8, int8_float16
  sample_rate: 16000

# TTS Configuration
tts:
  model_name: "tts_models/en/ljspeech/tacotron2-DDC"
  device: "cuda"  # Auto-detects if None

# Wake Word Configuration
wake_word:
  enabled: false
  wake_words: ["jane", "hey jane"]
  sensitivity: 0.5
  check_interval: 1.0

# Conversation Settings
max_conversation_history: 20
summarize_threshold: 30
memory_cleanup_interval: 10

# File Controller (Safe Mode)
file_controller:
  safe_mode: true
  allowed_directories:
    - "C:/Users/YourName/Documents"
    - "C:/Users/YourName/Desktop"
    - "C:/Users/YourName/Downloads"
```

### Environment Variables

Override any setting:

```powershell
# Windows PowerShell
$env:JANE_LLM_MODEL_PATH = "models/custom.gguf"
$env:JANE_STT_MODEL_SIZE = "large"
$env:JANE_WAKE_WORD_ENABLED = "true"
$env:JANE_STT_DEVICE = "cuda"
```

```bash
# Linux/macOS
export JANE_LLM_MODEL_PATH="models/custom.gguf"
export JANE_STT_MODEL_SIZE="large"
export JANE_WAKE_WORD_ENABLED="true"
```

### Configuration Priority

1. **Environment variables** (highest priority)
2. **config.yaml** file
3. **Default values** (lowest priority)

---

## Advanced Features

### API Access

Start the API server:

```powershell
python -m src.api.server --host 0.0.0.0 --port 8000
```

**Access:**
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **WebSocket:** ws://localhost:8000/ws

**Example API Client:**

```python
from examples.api_client_example import JaneAPIClient

client = JaneAPIClient()
response = client.chat("Hello, Jane!")
print(response)
```

### Plugin Development

Create custom plugins in `src/plugins/`:

```python
from src.plugins.plugin_base import BasePlugin, PluginHook

class MyPlugin(BasePlugin):
    name = "My Plugin"
    version = "1.0.0"
    description = "My custom plugin"
    
    def register_functions(self):
        return [{
            "name": "my_function",
            "function": self.my_function,
            "description": "Does something",
            "parameters": {}
        }]
    
    def register_hooks(self):
        return {
            PluginHook.ON_MESSAGE_RECEIVED: self.on_message
        }
```

### Logging

Logs are written to:
- **Console:** Colored output with timestamps
- **File:** `logs/jane.log` (rotated daily)

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Warnings (non-critical)
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

**Configure logging in `config.yaml`:**

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/jane.log"
  console: true
```

### Error Handling

The assistant includes comprehensive error handling:

- **Automatic retries** for transient errors
- **Error classification** (TRANSIENT, PERMANENT, RESOURCE, etc.)
- **Graceful degradation** when components fail
- **Fallback mechanisms** (e.g., CPU fallback for GPU errors)

---

## Troubleshooting

### Common Issues

#### 1. Model Not Found

**Problem:** LLM model file not found

**Solution:**
```powershell
# Check model path
python -c "from pathlib import Path; print(Path('models/Qwen2.5-7B-Instruct-Q4_K_M.gguf').exists())"

# Download model if missing
# See README.md for download links
```

#### 2. GPU Not Detected

**Problem:** CUDA not available

**Solution:**
```powershell
# Check GPU
nvidia-smi

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU fallback
# Set in config.yaml: device: "cpu"
```

#### 3. Audio Not Working

**Problem:** No audio input/output

**Solution:**
```powershell
# List devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test audio
python test_audio_capture.py

# Check default device
python -c "import sounddevice as sd; print(sd.default.device)"
```

#### 4. Slow Performance

**Problem:** Assistant is slow

**Solutions:**
- Use smaller STT model (`tiny` or `base`)
- Use CPU quantization (`int8`)
- Reduce context window size
- Enable wake word mode (reduces continuous processing)

#### 5. Memory Issues

**Problem:** Out of memory errors

**Solutions:**
- Use smaller models
- Enable memory cleanup: `memory_cleanup_interval: 5`
- Reduce context window: `n_ctx: 2048`
- Use CPU for some components

### Performance Tips

1. **First Run:** Models download and cache (2-3 minutes)
2. **Subsequent Runs:** Much faster (~30 seconds)
3. **GPU Memory:** Monitor with `nvidia-smi`
4. **Context Window:** Smaller = faster, but less context
5. **Streaming:** Enabled by default for better UX

### Getting Help

- **Check Logs:** `logs/jane.log`
- **Run Tests:** `python test_assistant_complete.py`
- **Verify Setup:** `python test_imports.py`
- **Check Status:** See `TEST_RESULTS.md`

---

## Best Practices

### 1. Clear Speech

- Speak clearly and at normal pace
- Minimize background noise
- Use a good microphone

### 2. Specific Commands

- **Better:** "List files in Documents folder"
- **Worse:** "Show me files"

### 3. Context Awareness

- The assistant remembers conversation context
- Reference previous topics: "What did we discuss about Python?"
- Set preferences: "I prefer dark mode"

### 4. Safe Mode

- File operations are restricted to safe directories
- Disable safe mode only if needed (not recommended)
- Always verify file paths

### 5. Resource Management

- Close the assistant when not in use
- Monitor GPU memory with `nvidia-smi`
- Use wake word mode for extended sessions

---

## Examples

### Example Session

```
You: "Hello, Jane!"
Jane: "Hello! I'm Jane, your AI assistant. How can I help you today?"

You: "What time is it?"
Jane: "It's currently 3:45 PM."

You: "Search the web for Python best practices"
Jane: [Searches web and provides results]

You: "Save this information to a file"
Jane: "I'll save the search results to a file for you."

You: "What files are in Documents?"
Jane: [Lists files in Documents directory]

You: "Goodbye"
Jane: "Goodbye! Have a great day!"
```

### Function Chaining

The assistant can chain multiple functions:

```
You: "Search for Python tutorials, then create a file with the results"
Jane: [Searches web] → [Creates file] → [Writes results]
```

---

## Security Considerations

1. **Safe Mode:** Enabled by default for file operations
2. **API Keys:** Store securely if using API authentication
3. **Model Files:** Keep model files secure (they may contain training data)
4. **Logs:** Review logs for sensitive information
5. **Network:** API server should use authentication in production

---

## Updates and Maintenance

### Updating

```powershell
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Test after update
python test_assistant_complete.py
```

### Backup

Important files to backup:
- `config.yaml` - Your configuration
- `data/conversation_state.json` - Conversation history
- `logs/` - Log files (optional)

---

## Support

For issues, questions, or contributions:

1. Check documentation first
2. Review `TEST_RESULTS.md` for known issues
3. Check logs: `logs/jane.log`
4. Run diagnostic tests: `python test_imports.py`

---

**Enjoy using Jane AI Voice Assistant!** 🎉

