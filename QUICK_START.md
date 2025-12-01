# Jane AI Voice Assistant - Quick Start Guide

**Get up and running in minutes!**

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+** (3.11.9 recommended)
- **NVIDIA GPU** with CUDA support (RTX 4090 or similar recommended)
- **Windows 10/11** (Linux/macOS support coming soon)
- **8GB+ RAM** (16GB+ recommended)
- **10GB+ free disk space** (for models)

### Step 1: Clone and Setup

```powershell
# Clone the repository
git clone <repository-url>
cd jane

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download Models

The assistant needs three models:

1. **Whisper STT Model** (auto-downloaded on first use)
   - Model: `medium` (1.53GB)
   - Location: Hugging Face cache

2. **TTS Model** (auto-downloaded on first use)
   - Model: Tacotron2-DDC (113MB + 3.8MB vocoder)
   - Location: TTS cache

3. **LLM Model** (manual download required)
   ```powershell
   # Download Qwen2.5-7B-Instruct model
   # Place in models/ directory
   # Recommended: Qwen2.5-7B-Instruct-Q4_K_M.gguf (4.36GB)
   ```

### Step 3: Configure

Create `config.yaml` from `config.yaml.example`:

```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

stt:
  model_size: "medium"
  device: "cuda"

tts:
  model_name: "tts_models/en/ljspeech/tacotron2-DDC"
  device: "cuda"
```

### Step 4: Run!

```powershell
python jane.py
```

The assistant will:
1. Initialize all components (STT, TTS, LLM)
2. Load models (first time may take 2-3 minutes)
3. Start listening for your voice commands

---

## 🎤 Basic Usage

### Voice Commands

Just speak naturally! The assistant will:

1. **Listen** to your voice (5 seconds by default)
2. **Transcribe** your speech to text
3. **Process** your command with the LLM
4. **Respond** with text and speech

### Example Commands

- **"What time is it?"** - Get current time
- **"What's today's date?"** - Get current date
- **"List files in Documents"** - List directory contents
- **"Open calculator"** - Launch an application
- **"Search the web for Python programming"** - Web search
- **"What's my system information?"** - Get system stats

### Exit

Say **"goodbye"**, **"exit"**, or **"quit"** to stop the assistant.

---

## ⚙️ Configuration

### Environment Variables

Override any config setting:

```powershell
# Set STT model size
$env:JANE_STT_MODEL_SIZE = "large"

# Set LLM model path
$env:JANE_LLM_MODEL_PATH = "models/custom-model.gguf"

# Enable wake word detection
$env:JANE_WAKE_WORD_ENABLED = "true"
$env:JANE_WAKE_WORD_WAKE_WORDS = '["jane", "hey jane"]'
```

### Config File

Edit `config.yaml` for persistent settings:

```yaml
llm:
  model_path: "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
  temperature: 0.7
  max_tokens: 512

stt:
  model_size: "medium"
  device: "cuda"
  compute_type: "float16"

wake_word:
  enabled: true
  wake_words: ["jane", "hey jane"]
  check_interval: 1.0
```

---

## 🔧 Troubleshooting

### Model Not Found

```powershell
# Check model path
python -c "from pathlib import Path; print(Path('models').exists())"

# Download model manually if needed
# See README.md for model download links
```

### GPU Not Detected

```powershell
# Check GPU status
nvidia-smi

# Verify CUDA in Python
python -c "import torch; print(torch.cuda.is_available())"
```

### Audio Issues

```powershell
# List audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test audio capture
python test_audio_capture.py
```

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify installation
python test_imports.py
```

---

## 📚 Next Steps

- Read **[USER_GUIDE.md](USER_GUIDE.md)** for detailed usage
- Read **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** to extend the assistant
- Check **[IMPROVEMENTS_COMPLETE_SUMMARY.md](IMPROVEMENTS_COMPLETE_SUMMARY.md)** for features

---

## 🆘 Getting Help

- **Issues:** Check `TEST_RESULTS.md` for test status
- **Configuration:** See `config.yaml.example` for all options
- **Features:** See `IMPROVEMENTS_STATUS.md` for implementation status

---

**Ready to go!** Start the assistant and begin talking. 🎉

