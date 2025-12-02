# Jane AI Voice Assistant

**A fully functional, GPU-accelerated voice-controlled AI assistant**

A self-hosted AI assistant that runs entirely on your local machine, powered by your GPU. No cloud services, complete privacy, and full computer control capabilities.

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](QUICK_START.md)** ⚡ - Get up and running in minutes
- **[User Guide](USER_GUIDE.md)** 📖 - Complete user documentation with all features
- **[Developer Guide](DEVELOPER_GUIDE.md)** 🔧 - Architecture, APIs, and extension guide

### Project Status
- **[Improvements Status](IMPROVEMENTS_STATUS.md)** - Current implementation status
- **[Complete Summary](IMPROVEMENTS_COMPLETE_SUMMARY.md)** - All improvements summary
- **[Where We Left Off](WHERE_WE_LEFT_OFF.md)** - Session status and next steps
- **[Performance Optimization Plan](PERFORMANCE_OPTIMIZATION_PLAN.md)** - LLM performance optimization strategy

---

## 🚀 Quick Start

```powershell
# 1. Setup environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Download LLM model to models/ directory
# Recommended: Qwen2.5-7B-Instruct-Q4_K_M.gguf (4.36GB)

# 3. Create config.yaml (see config.yaml.example)

# 4. Run!
python jane.py
```

**See [QUICK_START.md](QUICK_START.md) for detailed instructions.**

---

## ✨ Features

### Core Capabilities
- 🎤 **Voice Control** - Natural voice interaction with wake word detection
- 🧠 **LLM Integration** - Qwen2.5-7B-Instruct with native function calling
- 🔊 **Text-to-Speech** - Coqui TTS with GPU acceleration
- 🎯 **Function Calling** - Intelligent LLM-driven function selection
- 💾 **Context Management** - Smart conversation history pruning
- 🔄 **Streaming Responses** - Real-time response generation with early TTS

### Advanced Features
- 🔌 **Plugin System** - Extensible architecture with hooks
- 🌐 **Web Search** - Integrated DuckDuckGo search
- 💻 **System Control** - File, app, and input control
- 🎤 **Wake Word Detection** - Energy-efficient continuous listening
- 🌐 **API Layer** - REST API and WebSocket support
- 🔐 **Configuration System** - YAML + environment variables
- 📝 **Structured Logging** - Comprehensive logging with performance metrics
- 🛡️ **Error Handling** - Retry logic and graceful degradation

---

## 📋 Requirements

### Hardware
- **GPU:** NVIDIA GPU with CUDA support (RTX 4090 recommended)
- **RAM:** 8GB+ (16GB+ recommended)
- **Storage:** 10GB+ free space (for models)
- **OS:** Windows 10/11 (Linux/macOS support coming)

### Software
- **Python:** 3.11+ (3.11.9 recommended)
- **CUDA:** 12.x
- **Dependencies:** See `requirements.txt`

---

## 🏗️ Architecture

The assistant uses a modular, extensible architecture:

```
┌─────────────────────────────────────────┐
│         AssistantCore                    │
│    (Main Orchestrator)                   │
└──────┬───────────────────────────────────┘
       │
   ┌───┼───┬──────┬──────┬────────┐
   │   │   │      │      │        │
┌──▼──▼──▼──▼──▼──▼──▼──▼──▼──┐
│  STT  │  TTS  │  LLM  │ Func │ Plugin │
│Engine │Engine │Engine │Handler│Manager│
└───┬───┴───┬───┴───┬───┴───┬───┴───┬───┘
    │       │       │       │       │
┌───▼───────▼───────▼───────▼───────▼───┐
│  Controllers (File, App, Input)          │
└─────────────────────────────────────────┘
```

**Key Components:**
- **STT Engine** - Whisper-based speech-to-text
- **TTS Engine** - Coqui TTS text-to-speech
- **LLM Engine** - llama.cpp with Qwen2.5
- **Function Handler** - Function management and execution
- **Plugin System** - Dynamic plugin loading
- **API Layer** - REST and WebSocket APIs

**See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed architecture.**

---

## 🎯 Usage Examples

### Basic Voice Interaction

```powershell
python jane.py

# Speak: "What time is it?"
# Assistant: "It's currently 3:45 PM."
```

### API Usage

```powershell
# Start API server
python -m src.api.server --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

### Plugin Development

```python
from src.plugins.plugin_base import BasePlugin

class MyPlugin(BasePlugin):
    name = "My Plugin"
    # ... implement plugin
```

**See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for plugin development.**

---

## ⚙️ Configuration

### Quick Configuration

Create `config.yaml`:

```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

stt:
  model_size: "medium"
  device: "cuda"

wake_word:
  enabled: true
  wake_words: ["jane", "hey jane"]
```

### Environment Variables

```powershell
$env:JANE_LLM_MODEL_PATH = "models/custom.gguf"
$env:JANE_STT_MODEL_SIZE = "large"
$env:JANE_WAKE_WORD_ENABLED = "true"
```

**See [USER_GUIDE.md](USER_GUIDE.md) for complete configuration guide.**

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run integration test
python test_integration_all_improvements.py

# Run specific test
pytest test_config_system.py
```

**All tests passing:** ✅ 11/11 integration tests

---

## 📊 Project Status

### ✅ All Improvements Complete

- ✅ **Phase 1:** Foundation & Infrastructure (3/3 steps)
- ✅ **Phase 2:** Performance Optimizations (4/4 steps)
- ✅ **Phase 3:** Functionality Enhancements (3/3 steps)
- ✅ **Phase 4:** Extensibility Improvements (3/3 steps)
- ✅ **Phase 5:** Advanced Features (2/2 steps)

**Total:** 15/15 steps (100% complete)

**See [IMPROVEMENTS_STATUS.md](IMPROVEMENTS_STATUS.md) for detailed status.**

---

## 🔧 Technology Stack

- **STT:** faster-whisper (GPU-accelerated Whisper)
- **LLM:** Qwen2.5-7B-Instruct (via llama.cpp)
- **TTS:** Coqui TTS (Tacotron2-DDC)
- **Backend:** Python 3.11+ with CUDA acceleration
- **API:** FastAPI with WebSocket support
- **Configuration:** Pydantic + YAML

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Submit pull request

**See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for contribution guidelines.**

---

## 📝 Documentation Index

### User Documentation
- [Quick Start Guide](QUICK_START.md) - Installation and basic usage
- [User Guide](USER_GUIDE.md) - Complete feature documentation

### Developer Documentation
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture, APIs, and extension guide
- [Implementation Plan](IMPROVEMENTS_IMPLEMENTATION_PLAN.md) - Development roadmap
- [Improvements Status](IMPROVEMENTS_STATUS.md) - Current implementation status

### Project Documentation
- [Where We Left Off](WHERE_WE_LEFT_OFF.md) - Session status
- [Complete Summary](IMPROVEMENTS_COMPLETE_SUMMARY.md) - All improvements summary
- [Test Results](TEST_RESULTS.md) - Test status and results

---

## 🆘 Troubleshooting

### Common Issues

**Model Not Found:**
```powershell
# Check model path
python -c "from pathlib import Path; print(Path('models/model.gguf').exists())"
```

**GPU Not Detected:**
```powershell
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**Audio Issues:**
```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**See [USER_GUIDE.md](USER_GUIDE.md) for detailed troubleshooting.**

---

## 📈 Performance

### Targets
- **STT Latency:** <500ms
- **LLM Inference:** 60-120 tokens/second
- **TTS Latency:** <2s
- **End-to-End:** <5s

### Current Status
- ✅ **TTS:** Excellent (0.76s, meets target)
- ⚠️ **LLM:** Below target (6.56 tokens/sec, optimization in progress)
- ⚠️ **End-to-End:** Above target (32.22s, improving with LLM optimization)

**See:** [Performance Benchmark Results](BENCHMARK_RESULTS_SUMMARY.md) | [Optimization Plan](PERFORMANCE_OPTIMIZATION_PLAN.md)

### Optimization
- GPU acceleration enabled by default
- Model caching for faster startup
- Streaming responses for reduced latency
- Smart context pruning for memory efficiency
- **In Progress:** LLM performance optimization (config tuning, higher precision models)

---

## 🔐 Security

- **Safe Mode:** Enabled by default for file operations
- **API Authentication:** Optional API key support
- **Local Processing:** All data stays on your machine
- **No Cloud Services:** Complete privacy

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - STT
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM inference
- [Coqui TTS](https://github.com/coqui-ai/TTS) - TTS
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Qwen2.5](https://github.com/QwenLM/Qwen2.5) - Language model

---

## 🎉 Getting Started

**New to Jane?** Start with the [Quick Start Guide](QUICK_START.md)

**Want to extend Jane?** Check out the [Developer Guide](DEVELOPER_GUIDE.md)

**Need help?** See the [User Guide](USER_GUIDE.md)

---

**Ready to use Jane?** Run `python jane.py` and start talking! 🎤
