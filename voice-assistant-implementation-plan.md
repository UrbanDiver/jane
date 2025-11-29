# Voice-Based AI Personal Assistant - Implementation Plan

**Target Platform:** Windows Desktop (MSI Studio with RTX 4090)
**Architecture:** Self-hosted, GPU-accelerated, Privacy-first
**Estimated Timeline:** 8-12 weeks

---

## Prerequisites

### Hardware Requirements
- ✅ MSI Studio with RTX 4090 (24GB VRAM)
- ✅ 32GB+ RAM recommended
- ✅ 100GB+ free storage for models
- ✅ Quality microphone and speakers

### Software Requirements
- Windows 11 (latest updates)
- Python 3.11+
- CUDA Toolkit 12.x
- Git
- Visual Studio Build Tools (for C++ compilation)
- Node.js 18+ (for Tauri frontend)
- Rust (latest stable)

---

## Phase 0: Environment Setup

### Step 0.1: Install Core Dependencies

**Actions:**
1. Install Python 3.11 from python.org
2. Install CUDA Toolkit 12.1+
   ```powershell
   # Download from: https://developer.nvidia.com/cuda-downloads
   # Verify installation
   nvcc --version
   nvidia-smi
   ```
3. Install Git for Windows
4. Install Visual Studio Build Tools 2022
   - Select "Desktop development with C++"
5. Install Node.js LTS (v20+)
6. Install Rust
   ```powershell
   # Download from: https://rustup.rs/
   rustup default stable
   ```

**Testing:**
```powershell
python --version  # Should show 3.11+
nvcc --version    # Should show CUDA 12.x
node --version    # Should show v20+
cargo --version   # Should show latest Rust
```

**Success Criteria:**
- ✅ All version commands return expected versions
- ✅ nvidia-smi shows RTX 4090 with CUDA 12.x
- ✅ No PATH or environment variable issues

---

### Step 0.2: Create Project Structure

**Actions:**
```powershell
# Create project directory
mkdir voice-assistant
cd voice-assistant

# Create Python virtual environment
python -m venv venv
.\venv\Scripts\activate

# Create directory structure
mkdir src
mkdir src\backend
mkdir src\frontend
mkdir models
mkdir tests
mkdir config
mkdir docs

# Initialize git
git init
```

**Create `.gitignore`:**
```
venv/
models/
__pycache__/
*.pyc
.env
*.log
node_modules/
dist/
target/
```

**Testing:**
```powershell
# Verify structure
tree /F
# Verify venv activation
where python  # Should point to venv
```

**Success Criteria:**
- ✅ Virtual environment activated
- ✅ Directory structure created
- ✅ Git initialized

---

### Step 0.3: Install Python Dependencies

**Actions:**

Create `requirements.txt`:
```txt
# GPU-accelerated inference
torch>=2.1.0
faster-whisper>=1.0.0
transformers>=4.35.0
accelerate>=0.25.0

# Audio processing
sounddevice>=0.4.6
soundfile>=0.12.1
pyaudio>=0.2.14
webrtcvad>=2.0.10

# TTS
TTS>=0.21.0

# Computer control
pywinauto>=0.6.8
pyautogui>=0.9.54
pygetwindow>=0.0.9
keyboard>=0.13.5
mouse>=0.7.1

# Web automation
playwright>=1.40.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.1
requests>=2.31.0
pillow>=10.1.0

# Database
sqlalchemy>=2.0.23

# Vector DB & RAG
chromadb>=0.4.18
sentence-transformers>=2.2.2

# Development
pytest>=7.4.3
black>=23.12.0
```

Install dependencies:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

**Testing:**
```python
# Create test_imports.py
import torch
import faster_whisper
import sounddevice as sd
import pyautogui
from transformers import pipeline

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Audio devices: {sd.query_devices()}")
print("All imports successful!")
```

Run test:
```powershell
python test_imports.py
```

**Success Criteria:**
- ✅ All packages installed without errors
- ✅ PyTorch detects CUDA and RTX 4090
- ✅ Audio devices detected
- ✅ No import errors

---

## Phase 1: Speech-to-Text Pipeline

### Step 1.1: Install and Test Faster-Whisper

**Actions:**

Create `src/backend/stt_engine.py`:
```python
from faster_whisper import WhisperModel
import time

class STTEngine:
    def __init__(self, model_size="large-v3", device="cuda", compute_type="float16"):
        print(f"Loading Whisper {model_size} on {device}...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            num_workers=4
        )
        print("Whisper model loaded!")

    def transcribe(self, audio_path):
        start_time = time.time()
        segments, info = self.model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )

        text = " ".join([segment.text for segment in segments])
        elapsed = time.time() - start_time

        return {
            "text": text.strip(),
            "language": info.language,
            "duration": elapsed
        }

if __name__ == "__main__":
    engine = STTEngine(model_size="medium")  # Start with medium for testing
    # Test with a sample audio file
    result = engine.transcribe("test_audio.wav")
    print(f"Transcription: {result['text']}")
    print(f"Time: {result['duration']:.2f}s")
```

**Testing:**

1. Record a test audio file (5-10 seconds):
```python
# Create record_test_audio.py
import sounddevice as sd
import soundfile as sf
import numpy as np

duration = 5  # seconds
sample_rate = 16000

print("Recording in 3 seconds...")
sd.sleep(3000)
print("Recording NOW! Speak something...")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype=np.float32
)
sd.wait()

sf.write("test_audio.wav", audio, sample_rate)
print("Recording saved to test_audio.wav")
```

2. Run tests:
```powershell
python record_test_audio.py
python src/backend/stt_engine.py
```

**Success Criteria:**
- ✅ Whisper model loads on GPU (check GPU memory with `nvidia-smi`)
- ✅ Transcription accuracy >95% for clear speech
- ✅ Latency <500ms for 5-second audio
- ✅ VRAM usage ~3GB

---

### Step 1.2: Real-time Audio Capture with VAD

**Actions:**

Create `src/backend/audio_capture.py`:
```python
import sounddevice as sd
import numpy as np
import webrtcvad
from collections import deque
import queue
import threading

class AudioCapture:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(3)  # Aggressiveness: 0-3

        self.audio_queue = queue.Queue()
        self.is_recording = False

    def start(self):
        """Start continuous audio capture"""
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            callback=self._audio_callback
        )
        self.stream.start()
        print("Audio capture started")

    def _audio_callback(self, indata, frames, time_info, status):
        """Called for each audio chunk"""
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def stop(self):
        """Stop audio capture"""
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        print("Audio capture stopped")

    def detect_speech(self, audio_chunk):
        """Detect speech in audio chunk using VAD"""
        audio_bytes = (audio_chunk * 32767).astype(np.int16).tobytes()
        return self.vad.is_speech(audio_bytes, self.sample_rate)

    def get_audio_chunks(self):
        """Generator that yields audio chunks"""
        while self.is_recording:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                yield chunk
            except queue.Empty:
                continue

if __name__ == "__main__":
    capture = AudioCapture()
    capture.start()

    print("Listening... Speak to test VAD (Ctrl+C to stop)")
    speech_count = 0
    silence_count = 0

    try:
        for chunk in capture.get_audio_chunks():
            has_speech = capture.detect_speech(chunk)
            if has_speech:
                speech_count += 1
                print(f"🎤 Speech detected! ({speech_count} frames)")
            else:
                silence_count += 1
                if silence_count % 100 == 0:
                    print(f"🔇 Silence... ({silence_count} frames)")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        capture.stop()
```

**Testing:**
```powershell
python src/backend/audio_capture.py
```

Speak and verify:
1. Speech is detected when talking
2. Silence is detected when quiet
3. No audio dropouts or glitches

**Success Criteria:**
- ✅ Real-time audio capture working
- ✅ VAD correctly detects speech vs silence
- ✅ No buffer overflows or underruns
- ✅ Latency <100ms

---

### Step 1.3: Streaming STT Integration

**Actions:**

Create `src/backend/streaming_stt.py`:
```python
import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel
from collections import deque
import time
import tempfile
import os

class StreamingSTT:
    def __init__(self, model_size="medium"):
        self.model = WhisperModel(model_size, device="cuda", compute_type="float16")
        self.sample_rate = 16000
        self.is_listening = False
        self.audio_buffer = deque(maxlen=100)  # ~3 seconds at 30ms chunks

    def listen_and_transcribe(self, duration=5):
        """Record for specified duration and transcribe"""
        print(f"Recording for {duration} seconds...")

        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()

        # Save to temp file (faster-whisper needs file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            sf.write(temp_path, audio, self.sample_rate)

        # Transcribe
        start_time = time.time()
        segments, info = self.model.transcribe(temp_path, language="en", beam_size=5)
        text = " ".join([segment.text for segment in segments])
        elapsed = time.time() - start_time

        # Cleanup
        os.unlink(temp_path)

        return {
            "text": text.strip(),
            "latency": elapsed,
            "language": info.language
        }

if __name__ == "__main__":
    stt = StreamingSTT(model_size="medium")

    print("Ready! Press Enter to start recording...")
    input()

    result = stt.listen_and_transcribe(duration=5)
    print(f"\n✅ Transcription: '{result['text']}'")
    print(f"⏱️  Latency: {result['latency']:.2f}s")
```

**Testing:**

Run multiple tests with different speech patterns:
```powershell
python src/backend/streaming_stt.py
```

Test cases:
1. Clear speech, normal speed
2. Fast speech
3. Speech with pauses
4. Background noise
5. Multiple sentences

**Success Criteria:**
- ✅ Transcription accuracy >95% for clear speech
- ✅ Latency <1 second for 5-second clips
- ✅ Handles pauses gracefully
- ✅ GPU utilization visible in nvidia-smi

---

## Phase 2: Text-to-Speech Pipeline

### Step 2.1: Install and Test Coqui TTS

**Actions:**

Create `src/backend/tts_engine.py`:
```python
import torch
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import time

class TTSEngine:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        print(f"Loading TTS model: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(model_name).to(self.device)
        print(f"TTS loaded on {self.device}")

    def synthesize(self, text, output_path="output.wav"):
        """Convert text to speech and save to file"""
        start_time = time.time()
        self.tts.tts_to_file(text=text, file_path=output_path)
        elapsed = time.time() - start_time
        return elapsed

    def speak(self, text):
        """Synthesize and play audio"""
        print(f"🔊 Speaking: '{text}'")
        latency = self.synthesize(text, "temp_tts.wav")

        # Load and play
        audio, sample_rate = sf.read("temp_tts.wav")
        sd.play(audio, sample_rate)
        sd.wait()

        print(f"⏱️  TTS latency: {latency:.2f}s")
        return latency

if __name__ == "__main__":
    # List available models
    print("Available TTS models:")
    print(TTS().list_models())

    # Test TTS
    tts = TTSEngine()

    test_phrases = [
        "Hello, I am your AI assistant.",
        "How can I help you today?",
        "I can control your computer, answer questions, and much more."
    ]

    for phrase in test_phrases:
        latency = tts.speak(phrase)
        time.sleep(1)
```

**Testing:**
```powershell
python src/backend/tts_engine.py
```

**Success Criteria:**
- ✅ TTS model loads on GPU
- ✅ Audio quality is natural and clear
- ✅ Synthesis latency <2 seconds for short phrases
- ✅ Audio plays without glitches

---

### Step 2.2: Optimize TTS with Better Models

**Actions:**

Test faster models:
```python
# Update tts_engine.py to try different models
alternative_models = [
    "tts_models/en/ljspeech/fast_pitch",  # Faster
    "tts_models/en/vctk/vits",            # Multi-speaker
    "tts_models/en/jenny/jenny",          # High quality
]
```

Benchmark each model for:
- Speed
- Quality
- VRAM usage
- Naturalness

**Testing:**

Create `tests/benchmark_tts.py`:
```python
from src.backend.tts_engine import TTSEngine
import time

models_to_test = [
    "tts_models/en/ljspeech/tacotron2-DDC",
    "tts_models/en/ljspeech/fast_pitch",
]

test_text = "The quick brown fox jumps over the lazy dog."

for model in models_to_test:
    print(f"\n{'='*50}")
    print(f"Testing: {model}")
    print(f"{'='*50}")

    try:
        tts = TTSEngine(model_name=model)
        latency = tts.speak(test_text)
        print(f"✅ Latency: {latency:.2f}s")
        input("Press Enter for next model...")
    except Exception as e:
        print(f"❌ Error: {e}")
```

**Success Criteria:**
- ✅ Identified fastest model with acceptable quality
- ✅ Latency <1 second for 10-word sentences
- ✅ Selected model for production use

---

## Phase 3: LLM Integration

### Step 3.1: Install llama.cpp with CUDA

**Actions:**

```powershell
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CUDA support
mkdir build
cd build
cmake .. -DLLAMA_CUBLAS=ON
cmake --build . --config Release

# Verify CUDA build
.\bin\Release\main.exe --version
```

Install Python bindings:
```powershell
pip install llama-cpp-python --force-reinstall --no-cache-dir --config-settings cmake.args="-DLLAMA_CUBLAS=on"
```

**Testing:**
```python
# test_llama.py
from llama_cpp import Llama

print("Testing llama-cpp-python with CUDA...")

# This will work once you download a model
# For now, just verify import works
print("✅ llama-cpp-python imported successfully")
print("⚠️  Need to download a GGUF model for full test")
```

**Success Criteria:**
- ✅ llama.cpp compiled with CUDA support
- ✅ Python bindings installed
- ✅ Import successful

---

### Step 3.2: Download and Test LLM

**Actions:**

Download Qwen 2.5 32B (recommended):
```powershell
# Install huggingface-cli
pip install huggingface-hub[cli]

# Download model (will take time - ~20GB)
huggingface-cli download \
  bartowski/Qwen2.5-32B-Instruct-GGUF \
  Qwen2.5-32B-Instruct-Q4_K_M.gguf \
  --local-dir models
```

Create `src/backend/llm_engine.py`:
```python
from llama_cpp import Llama
import time

class LLMEngine:
    def __init__(self, model_path, n_gpu_layers=-1, n_ctx=4096):
        print("Loading LLM...")
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,  # -1 = all layers on GPU
            n_ctx=n_ctx,
            n_batch=512,
            verbose=False
        )
        print("✅ LLM loaded!")

    def generate(self, prompt, max_tokens=256, temperature=0.7):
        start_time = time.time()

        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            echo=False
        )

        elapsed = time.time() - start_time
        text = response['choices'][0]['text']
        tokens = response['usage']['completion_tokens']

        return {
            'text': text,
            'tokens': tokens,
            'time': elapsed,
            'tokens_per_second': tokens / elapsed
        }

    def chat(self, messages, max_tokens=256):
        """Chat completion with message history"""
        start_time = time.time()

        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )

        elapsed = time.time() - start_time
        return {
            'response': response['choices'][0]['message']['content'],
            'time': elapsed
        }

if __name__ == "__main__":
    model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
    llm = LLMEngine(model_path)

    # Test 1: Simple generation
    print("\n" + "="*50)
    print("Test 1: Simple prompt")
    print("="*50)

    result = llm.generate("Explain what a personal AI assistant can do in one sentence:")
    print(f"Response: {result['text']}")
    print(f"Speed: {result['tokens_per_second']:.1f} tokens/sec")

    # Test 2: Chat
    print("\n" + "="*50)
    print("Test 2: Chat mode")
    print("="*50)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What's 15 multiplied by 23?"}
    ]

    result = llm.chat(messages)
    print(f"Response: {result['response']}")
    print(f"Time: {result['time']:.2f}s")
```

**Testing:**
```powershell
python src/backend/llm_engine.py
```

Monitor GPU usage:
```powershell
# In another terminal
nvidia-smi -l 1
```

**Success Criteria:**
- ✅ Model loads fully on GPU (~18-20GB VRAM)
- ✅ Inference speed 60-120 tokens/second
- ✅ Coherent, relevant responses
- ✅ Chat mode working correctly

---

### Step 3.3: Implement Function Calling

**Actions:**

Create `src/backend/function_handler.py`:
```python
import json
from typing import Dict, List, Callable

class FunctionHandler:
    def __init__(self):
        self.functions = {}
        self.register_default_functions()

    def register(self, name: str, func: Callable, description: str, parameters: dict):
        """Register a function that the LLM can call"""
        self.functions[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }

    def register_default_functions(self):
        """Register built-in functions"""

        def get_current_time():
            from datetime import datetime
            return datetime.now().strftime("%I:%M %p")

        def get_current_date():
            from datetime import datetime
            return datetime.now().strftime("%A, %B %d, %Y")

        self.register(
            "get_current_time",
            get_current_time,
            "Get the current time",
            {"type": "object", "properties": {}}
        )

        self.register(
            "get_current_date",
            get_current_date,
            "Get today's date",
            {"type": "object", "properties": {}}
        )

    def get_function_definitions(self) -> List[Dict]:
        """Get function definitions in OpenAI format"""
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in self.functions.items()
        ]

    def execute(self, function_name: str, arguments: dict = None):
        """Execute a registered function"""
        if function_name not in self.functions:
            raise ValueError(f"Unknown function: {function_name}")

        func = self.functions[function_name]["function"]
        args = arguments or {}

        try:
            result = func(**args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    handler = FunctionHandler()

    # Test functions
    print("Available functions:")
    for func_def in handler.get_function_definitions():
        print(f"  - {func_def['name']}: {func_def['description']}")

    print("\nTesting functions:")
    print(f"Time: {handler.execute('get_current_time')}")
    print(f"Date: {handler.execute('get_current_date')}")
```

**Testing:**
```powershell
python src/backend/function_handler.py
```

**Success Criteria:**
- ✅ Functions registered successfully
- ✅ Function execution works
- ✅ Error handling in place

---

## Phase 4: Computer Control

### Step 4.1: File System Operations

**Actions:**

Create `src/backend/file_controller.py`:
```python
import os
import shutil
from pathlib import Path
from typing import List, Optional

class FileController:
    def __init__(self, safe_mode=True):
        self.safe_mode = safe_mode
        self.allowed_dirs = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads"
        ]

    def _check_path_safety(self, path: Path) -> bool:
        """Ensure path is in allowed directories"""
        if not self.safe_mode:
            return True

        path = Path(path).resolve()
        return any(str(path).startswith(str(allowed)) for allowed in self.allowed_dirs)

    def read_file(self, file_path: str) -> dict:
        """Read a file's contents"""
        path = Path(file_path)

        if not self._check_path_safety(path):
            return {"success": False, "error": "Path not allowed"}

        if not path.exists():
            return {"success": False, "error": "File not found"}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, file_path: str, content: str) -> dict:
        """Write content to a file"""
        path = Path(file_path)

        if not self._check_path_safety(path):
            return {"success": False, "error": "Path not allowed"}

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "path": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, dir_path: str) -> dict:
        """List files in a directory"""
        path = Path(dir_path)

        if not self._check_path_safety(path):
            return {"success": False, "error": "Path not allowed"}

        if not path.is_dir():
            return {"success": False, "error": "Not a directory"}

        try:
            files = [
                {
                    "name": f.name,
                    "type": "dir" if f.is_dir() else "file",
                    "size": f.stat().st_size if f.is_file() else None
                }
                for f in path.iterdir()
            ]
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, directory: str, pattern: str) -> dict:
        """Search for files matching a pattern"""
        path = Path(directory)

        if not self._check_path_safety(path):
            return {"success": False, "error": "Path not allowed"}

        try:
            matches = list(path.rglob(pattern))
            results = [str(m.relative_to(path)) for m in matches]
            return {"success": True, "matches": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    fc = FileController(safe_mode=True)

    # Test 1: List Desktop
    print("Test 1: List Desktop")
    result = fc.list_directory(str(Path.home() / "Desktop"))
    if result["success"]:
        print(f"Found {len(result['files'])} items")
        for item in result['files'][:5]:
            print(f"  - {item['name']} ({item['type']})")

    # Test 2: Create test file
    print("\nTest 2: Create test file")
    test_file = Path.home() / "Documents" / "assistant_test.txt"
    result = fc.write_file(str(test_file), "Hello from AI Assistant!")
    print(result)

    # Test 3: Read test file
    print("\nTest 3: Read test file")
    result = fc.read_file(str(test_file))
    if result["success"]:
        print(f"Content: {result['content']}")

    # Test 4: Search for .txt files
    print("\nTest 4: Search for .txt files")
    result = fc.search_files(str(Path.home() / "Documents"), "*.txt")
    if result["success"]:
        print(f"Found {result['count']} .txt files")
```

**Testing:**
```powershell
python src/backend/file_controller.py
```

Verify:
1. File creation works
2. File reading works
3. Directory listing works
4. Search works
5. Safety checks prevent access outside allowed dirs

**Success Criteria:**
- ✅ All file operations working
- ✅ Safety checks enforced
- ✅ Proper error handling
- ✅ Test file created and read successfully

---

### Step 4.2: Application Control

**Actions:**

Create `src/backend/app_controller.py`:
```python
import subprocess
import psutil
from typing import List, Optional
import pywinauto
from pywinauto.application import Application

class AppController:
    def __init__(self):
        self.common_apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe",
            "calculator": "calc.exe",
        }

    def launch_app(self, app_name: str, args: List[str] = None) -> dict:
        """Launch an application"""
        try:
            # Check if it's a known app
            if app_name.lower() in self.common_apps:
                exe_path = self.common_apps[app_name.lower()]
            else:
                exe_path = app_name

            # Launch
            cmd = [exe_path] + (args or [])
            process = subprocess.Popen(cmd)

            return {
                "success": True,
                "pid": process.pid,
                "message": f"Launched {app_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_running_apps(self) -> dict:
        """Get list of running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    info = proc.info
                    if info['exe'] and '.exe' in info['name'].lower():
                        apps.append({
                            "name": info['name'],
                            "pid": info['pid'],
                            "exe": info['exe']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {"success": True, "apps": apps, "count": len(apps)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_app(self, app_name: str) -> dict:
        """Close an application by name"""
        try:
            closed = 0
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed += 1

            return {
                "success": True,
                "closed": closed,
                "message": f"Closed {closed} instance(s) of {app_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def focus_window(self, title_substring: str) -> dict:
        """Bring a window to focus"""
        try:
            app = pywinauto.Desktop(backend="uia")
            windows = app.windows()

            for window in windows:
                if title_substring.lower() in window.window_text().lower():
                    window.set_focus()
                    return {
                        "success": True,
                        "window": window.window_text()
                    }

            return {"success": False, "error": "Window not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    ac = AppController()

    # Test 1: Get running apps
    print("Test 1: Get running applications")
    result = ac.get_running_apps()
    if result["success"]:
        print(f"Found {result['count']} running apps")
        # Show first 5
        for app in result['apps'][:5]:
            print(f"  - {app['name']} (PID: {app['pid']})")

    # Test 2: Launch Calculator
    print("\nTest 2: Launch Calculator")
    result = ac.launch_app("calculator")
    print(result)

    input("\nPress Enter to close calculator...")

    # Test 3: Close Calculator
    print("Test 3: Close Calculator")
    result = ac.close_app("calculator")
    print(result)
```

**Testing:**
```powershell
python src/backend/app_controller.py
```

**Success Criteria:**
- ✅ Can list running applications
- ✅ Can launch applications
- ✅ Can close applications
- ✅ Calculator launches and closes successfully

---

### Step 4.3: Keyboard and Mouse Control

**Actions:**

Create `src/backend/input_controller.py`:
```python
import pyautogui
import time
from typing import Tuple, Optional

# Fail-safe: move mouse to corner to abort
pyautogui.FAILSAFE = True

class InputController:
    def __init__(self, safe_mode=True):
        self.safe_mode = safe_mode
        pyautogui.PAUSE = 0.1  # Small pause between actions

    def type_text(self, text: str, interval: float = 0.0) -> dict:
        """Type text"""
        try:
            pyautogui.typewrite(text, interval=interval)
            return {"success": True, "typed": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def press_key(self, key: str) -> dict:
        """Press a single key"""
        try:
            pyautogui.press(key)
            return {"success": True, "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def hotkey(self, *keys) -> dict:
        """Press a hotkey combination (e.g., ctrl, c)"""
        try:
            pyautogui.hotkey(*keys)
            return {"success": True, "keys": keys}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> dict:
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return {"success": True, "position": (x, y)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click(self, x: Optional[int] = None, y: Optional[int] = None,
              button: str = 'left', clicks: int = 1) -> dict:
        """Click at current position or specified coordinates"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
            else:
                pyautogui.click(clicks=clicks, button=button)
            return {"success": True, "clicks": clicks, "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_mouse_position(self) -> dict:
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def screenshot(self, filename: Optional[str] = None) -> dict:
        """Take a screenshot"""
        try:
            img = pyautogui.screenshot()
            if filename:
                img.save(filename)
                return {"success": True, "saved": filename}
            return {"success": True, "image": img}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    ic = InputController()

    print("Test 1: Get mouse position")
    print("Move your mouse around...")
    for i in range(5):
        time.sleep(1)
        result = ic.get_mouse_position()
        print(f"  Position: ({result['x']}, {result['y']})")

    print("\nTest 2: Screenshot")
    result = ic.screenshot("test_screenshot.png")
    print(result)

    print("\nTest 3: Open Notepad and type")
    from src.backend.app_controller import AppController
    ac = AppController()
    ac.launch_app("notepad")
    time.sleep(2)

    ic.type_text("Hello from AI Assistant!", interval=0.05)
    print("✅ Text typed in Notepad")

    input("\nPress Enter to close Notepad (without saving)...")
    ic.hotkey('alt', 'F4')
    time.sleep(0.5)
    ic.press_key('n')  # Don't save
```

**Testing:**
```powershell
python src/backend/input_controller.py
```

**Success Criteria:**
- ✅ Mouse position tracking works
- ✅ Screenshot captured
- ✅ Text typed in Notepad
- ✅ Hotkeys work (Alt+F4)
- ✅ Fail-safe activates when mouse moved to corner

---

## Phase 5: Integration & Conversation

### Step 5.1: Create Unified Assistant Core

**Actions:**

Create `src/backend/assistant_core.py`:
```python
from src.backend.streaming_stt import StreamingSTT
from src.backend.tts_engine import TTSEngine
from src.backend.llm_engine import LLMEngine
from src.backend.function_handler import FunctionHandler
from src.backend.file_controller import FileController
from src.backend.app_controller import AppController
from src.backend.input_controller import InputController
import json

class AssistantCore:
    def __init__(self, llm_model_path):
        print("Initializing AI Assistant Core...")

        # Core engines
        self.stt = StreamingSTT(model_size="medium")
        self.tts = TTSEngine()
        self.llm = LLMEngine(llm_model_path)

        # Controllers
        self.file_ctrl = FileController(safe_mode=True)
        self.app_ctrl = AppController()
        self.input_ctrl = InputController(safe_mode=True)

        # Function handler
        self.function_handler = FunctionHandler()
        self._register_functions()

        # Conversation history
        self.conversation_history = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant with the ability to control the computer.
You can:
- Answer questions and provide information
- Read, write, and search files
- Launch and control applications
- Control keyboard and mouse
- Take screenshots

Always confirm before taking potentially destructive actions.
Be concise and helpful."""
            }
        ]

        print("✅ Assistant Core initialized!")

    def _register_functions(self):
        """Register all control functions"""
        # File operations
        self.function_handler.register(
            "read_file",
            self.file_ctrl.read_file,
            "Read the contents of a file",
            {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["file_path"]
            }
        )

        self.function_handler.register(
            "write_file",
            self.file_ctrl.write_file,
            "Write content to a file",
            {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["file_path", "content"]
            }
        )

        self.function_handler.register(
            "list_directory",
            self.file_ctrl.list_directory,
            "List files in a directory",
            {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Path to directory"}
                },
                "required": ["dir_path"]
            }
        )

        # App control
        self.function_handler.register(
            "launch_app",
            self.app_ctrl.launch_app,
            "Launch an application",
            {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"}
                },
                "required": ["app_name"]
            }
        )

        # Screenshot
        self.function_handler.register(
            "take_screenshot",
            lambda filename="screenshot.png": self.input_ctrl.screenshot(filename),
            "Take a screenshot",
            {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename for screenshot"}
                }
            }
        )

    def listen(self, duration=5):
        """Listen for voice input and return transcription"""
        print("🎤 Listening...")
        result = self.stt.listen_and_transcribe(duration)
        return result['text']

    def speak(self, text):
        """Speak the given text"""
        self.tts.speak(text)

    def process_command(self, user_input: str) -> str:
        """Process user input and generate response"""
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Get LLM response
        print("🤔 Thinking...")
        result = self.llm.chat(self.conversation_history[-5:], max_tokens=512)
        response = result['response']

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def run_voice_loop(self):
        """Main voice interaction loop"""
        print("\n" + "="*50)
        print("AI Assistant Ready!")
        print("="*50)
        self.speak("Hello! I'm ready to assist you.")

        while True:
            try:
                # Listen
                user_input = self.listen(duration=5)

                if not user_input.strip():
                    continue

                print(f"\n👤 You: {user_input}")

                # Check for exit
                if "goodbye" in user_input.lower() or "exit" in user_input.lower():
                    self.speak("Goodbye!")
                    break

                # Process
                response = self.process_command(user_input)
                print(f"🤖 Assistant: {response}")

                # Speak
                self.speak(response)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

if __name__ == "__main__":
    model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
    assistant = AssistantCore(model_path)
    assistant.run_voice_loop()
```

**Testing:**
```powershell
python src/backend/assistant_core.py
```

Test conversation flow:
1. "Hello, how are you?"
2. "What time is it?"
3. "List files on my desktop"
4. "Open calculator"
5. "Goodbye"

**Success Criteria:**
- ✅ Voice loop works end-to-end
- ✅ STT → LLM → TTS pipeline smooth
- ✅ Conversation context maintained
- ✅ Functions registered and callable
- ✅ Total latency <3 seconds per interaction

---

## Phase 6: Desktop Application

### Step 6.1: Set up Tauri Project

**Actions:**

```powershell
# Create Tauri app
npx create-tauri-app

# Options:
# Project name: voice-assistant-ui
# Package manager: npm
# UI framework: vanilla (or your preference)
# Language: TypeScript

cd voice-assistant-ui

# Install dependencies
npm install

# Test dev build
npm run tauri dev
```

**Testing:**

Verify Tauri window opens with default UI.

**Success Criteria:**
- ✅ Tauri app compiles and runs
- ✅ Window displays correctly
- ✅ Hot reload works

---

### Step 6.2: Create UI Components

**Actions:**

Create `src-tauri/src/main.rs` additions for system tray:

```rust
use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::Manager;

fn main() {
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let listen = CustomMenuItem::new("listen".to_string(), "Start Listening");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(listen)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "show" => {
                        let window = app.get_window("main").unwrap();
                        window.show().unwrap();
                    }
                    "listen" => {
                        // Trigger listening
                        println!("Start listening...");
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

Create simple UI in `src/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        #status {
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }

        #conversation {
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
            padding: 20px;
            flex-grow: 1;
            overflow-y: auto;
            margin-bottom: 20px;
        }

        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }

        .user {
            background: #e3f2fd;
            text-align: right;
        }

        .assistant {
            background: #f3e5f5;
        }

        #controls {
            display: flex;
            gap: 10px;
        }

        button {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            background: #fff;
            transition: transform 0.1s;
        }

        button:hover {
            transform: scale(1.05);
        }

        button:active {
            transform: scale(0.95);
        }

        #listen-btn {
            background: #4CAF50;
            color: white;
        }

        #listen-btn.listening {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div id="status">
        <h2>AI Assistant</h2>
        <p id="status-text">Ready</p>
    </div>

    <div id="conversation"></div>

    <div id="controls">
        <button id="listen-btn">🎤 Push to Talk</button>
        <button id="settings-btn">⚙️ Settings</button>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

**Testing:**

```powershell
npm run tauri dev
```

Verify UI displays correctly.

**Success Criteria:**
- ✅ UI renders properly
- ✅ System tray icon appears
- ✅ Buttons are clickable
- ✅ Styling looks good

---

### Step 6.3: Connect Frontend to Backend

**Actions:**

Create Python backend server (`src/backend/server.py`):

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from assistant_core import AssistantCore
import threading

app = Flask(__name__)
CORS(app)

# Initialize assistant
model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
assistant = AssistantCore(model_path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/listen', methods=['POST'])
def listen():
    data = request.json
    duration = data.get('duration', 5)

    try:
        text = assistant.listen(duration)
        return jsonify({"success": True, "text": text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_input = data.get('input', '')

    try:
        response = assistant.process_command(user_input)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')

    try:
        # Run in thread to not block
        thread = threading.Thread(target=assistant.speak, args=(text,))
        thread.start()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("Starting backend server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
```

Install Flask:
```powershell
pip install flask flask-cors
```

Update `src/app.js`:

```javascript
const API_URL = 'http://localhost:5000';

const statusText = document.getElementById('status-text');
const conversation = document.getElementById('conversation');
const listenBtn = document.getElementById('listen-btn');

let isListening = false;

function addMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.textContent = text;
    conversation.appendChild(msg);
    conversation.scrollTop = conversation.scrollHeight;
}

async function listen() {
    isListening = true;
    listenBtn.classList.add('listening');
    listenBtn.textContent = '🔴 Listening...';
    statusText.textContent = 'Listening...';

    try {
        const response = await fetch(`${API_URL}/listen`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({duration: 5})
        });

        const data = await response.json();

        if (data.success && data.text) {
            addMessage(data.text, 'user');
            await processInput(data.text);
        }
    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = 'Error: ' + error.message;
    } finally {
        isListening = false;
        listenBtn.classList.remove('listening');
        listenBtn.textContent = '🎤 Push to Talk';
        statusText.textContent = 'Ready';
    }
}

async function processInput(text) {
    statusText.textContent = 'Thinking...';

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({input: text})
        });

        const data = await response.json();

        if (data.success) {
            addMessage(data.response, 'assistant');
            await speak(data.response);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function speak(text) {
    statusText.textContent = 'Speaking...';

    try {
        await fetch(`${API_URL}/speak`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text})
        });
    } catch (error) {
        console.error('Error:', error);
    }

    statusText.textContent = 'Ready';
}

listenBtn.addEventListener('click', () => {
    if (!isListening) {
        listen();
    }
});

// Check backend health on startup
fetch(`${API_URL}/health`)
    .then(r => r.json())
    .then(data => {
        statusText.textContent = 'Connected - Ready';
    })
    .catch(err => {
        statusText.textContent = 'Backend not connected';
    });
```

**Testing:**

Terminal 1:
```powershell
cd voice-assistant
.\venv\Scripts\activate
python src/backend/server.py
```

Terminal 2:
```powershell
cd voice-assistant-ui
npm run tauri dev
```

Test full voice interaction through UI.

**Success Criteria:**
- ✅ Backend server starts successfully
- ✅ Frontend connects to backend
- ✅ Push-to-talk button works
- ✅ Voice recorded and transcribed
- ✅ Response displayed and spoken
- ✅ End-to-end latency <5 seconds

---

## Phase 7: Advanced Features

### Step 7.1: Wake Word Detection

**Actions:**

Install Porcupine wake word:
```powershell
pip install pvporcupine
```

Create `src/backend/wake_word.py`:

```python
import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, access_key, keyword_path=None):
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=['jarvis']  # or custom keyword
        )
        self.pa = pyaudio.PyAudio()
        self.audio_stream = None

    def start(self, callback):
        """Start listening for wake word"""
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        print(f"Listening for wake word... (say 'Jarvis')")

        try:
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Wake word detected!")
                    callback()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop()

    def stop(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.porcupine:
            self.porcupine.delete()
        if self.pa:
            self.pa.terminate()

if __name__ == "__main__":
    # Get free access key from https://console.picovoice.ai/
    ACCESS_KEY = "YOUR_ACCESS_KEY"

    def on_wake_word():
        print("Assistant activated!")

    detector = WakeWordDetector(ACCESS_KEY)
    detector.start(on_wake_word)
```

**Testing:**

Sign up for Porcupine access key, then:
```powershell
python src/backend/wake_word.py
```

Say "Jarvis" and verify detection.

**Success Criteria:**
- ✅ Wake word detected reliably
- ✅ False positive rate low
- ✅ Latency <200ms
- ✅ Integrates with assistant core

---

### Step 7.2: Screen Understanding with Vision

**Actions:**

Download vision model:
```powershell
huggingface-cli download \
  bartowski/Llama-3.2-11B-Vision-Instruct-GGUF \
  Llama-3.2-11B-Vision-Instruct-Q4_K_M.gguf \
  --local-dir models
```

Create `src/backend/vision_engine.py`:

```python
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
import base64
from PIL import Image
import io

class VisionEngine:
    def __init__(self, model_path):
        print("Loading vision model...")
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,
            n_ctx=4096,
            chat_handler=Llava15ChatHandler(clip_model_path="path_to_clip_model")
        )
        print("Vision model loaded!")

    def analyze_image(self, image_path, question):
        """Analyze an image and answer a question about it"""
        with Image.open(image_path) as img:
            # Encode image
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}},
                    {"type": "text", "text": question}
                ]
            }
        ]

        response = self.llm.create_chat_completion(messages=messages)
        return response['choices'][0]['message']['content']

    def analyze_screenshot(self, screenshot_path):
        """Analyze a screenshot and describe what's visible"""
        return self.analyze_image(
            screenshot_path,
            "Describe what you see on this screen in detail. What applications are open? What is the user likely doing?"
        )

if __name__ == "__main__":
    from src.backend.input_controller import InputController

    # Take screenshot
    ic = InputController()
    ic.screenshot("test_screen.png")

    # Analyze
    vision = VisionEngine("models/Llama-3.2-11B-Vision-Instruct-Q4_K_M.gguf")
    analysis = vision.analyze_screenshot("test_screen.png")
    print(f"\nScreen Analysis:\n{analysis}")
```

**Testing:**
```powershell
python src/backend/vision_engine.py
```

**Success Criteria:**
- ✅ Vision model loads on GPU
- ✅ Accurately describes screen contents
- ✅ Can identify applications and UI elements
- ✅ Response time <5 seconds

---

## Phase 8: Testing & Optimization

### Step 8.1: Performance Benchmarking

**Actions:**

Create `tests/benchmark.py`:

```python
import time
import statistics
from src.backend.assistant_core import AssistantCore

def benchmark_stt(assistant, iterations=5):
    """Benchmark speech-to-text"""
    print("\n📊 Benchmarking STT...")
    times = []

    for i in range(iterations):
        start = time.time()
        result = assistant.stt.listen_and_transcribe(duration=3)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.2f}s - '{result['text']}'")

    print(f"  Average: {statistics.mean(times):.2f}s")
    print(f"  Min: {min(times):.2f}s, Max: {max(times):.2f}s")

def benchmark_llm(assistant, iterations=5):
    """Benchmark LLM inference"""
    print("\n📊 Benchmarking LLM...")

    prompts = [
        "What's 15 times 23?",
        "Explain photosynthesis in one sentence.",
        "What's the capital of France?",
    ]

    for prompt in prompts:
        print(f"\n  Prompt: '{prompt}'")
        tokens_per_sec = []

        for i in range(iterations):
            result = assistant.llm.generate(prompt, max_tokens=50)
            tokens_per_sec.append(result['tokens_per_second'])
            print(f"    Run {i+1}: {result['tokens_per_second']:.1f} tok/s")

        print(f"    Average: {statistics.mean(tokens_per_sec):.1f} tok/s")

def benchmark_tts(assistant, iterations=5):
    """Benchmark text-to-speech"""
    print("\n📊 Benchmarking TTS...")
    times = []

    text = "Hello, this is a test of the text to speech system."

    for i in range(iterations):
        latency = assistant.tts.synthesize(text, f"test_tts_{i}.wav")
        times.append(latency)
        print(f"  Run {i+1}: {latency:.2f}s")

    print(f"  Average: {statistics.mean(times):.2f}s")

def benchmark_end_to_end(assistant, iterations=3):
    """Benchmark full voice interaction"""
    print("\n📊 Benchmarking End-to-End...")

    for i in range(iterations):
        print(f"\n  Run {i+1}:")
        print("  Press Enter when ready to speak...")
        input()

        total_start = time.time()

        # STT
        stt_start = time.time()
        text = assistant.listen(duration=5)
        stt_time = time.time() - stt_start
        print(f"    STT: {stt_time:.2f}s - '{text}'")

        # LLM
        llm_start = time.time()
        response = assistant.process_command(text)
        llm_time = time.time() - llm_start
        print(f"    LLM: {llm_time:.2f}s - '{response[:50]}...'")

        # TTS
        tts_start = time.time()
        assistant.speak(response)
        tts_time = time.time() - tts_start
        print(f"    TTS: {tts_time:.2f}s")

        total_time = time.time() - total_start
        print(f"    Total: {total_time:.2f}s")

if __name__ == "__main__":
    model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
    assistant = AssistantCore(model_path)

    print("="*50)
    print("PERFORMANCE BENCHMARK")
    print("="*50)

    # Run benchmarks
    # benchmark_stt(assistant)
    # benchmark_llm(assistant)
    # benchmark_tts(assistant)
    benchmark_end_to_end(assistant)
```

**Testing:**
```powershell
python tests/benchmark.py
```

**Success Criteria:**
- ✅ STT latency <500ms
- ✅ LLM throughput >60 tok/s
- ✅ TTS latency <2s
- ✅ End-to-end <5s total

---

### Step 8.2: Integration Tests

**Actions:**

Create `tests/test_integration.py`:

```python
import pytest
from src.backend.assistant_core import AssistantCore
from pathlib import Path
import time

@pytest.fixture
def assistant():
    model_path = "models/Qwen2.5-32B-Instruct-Q4_K_M.gguf"
    return AssistantCore(model_path)

def test_file_operations(assistant):
    """Test file read/write/list"""
    test_file = Path.home() / "Documents" / "test_assistant.txt"
    test_content = "This is a test file created by the assistant."

    # Write file
    response = assistant.process_command(f"Create a file at {test_file} with content: {test_content}")
    assert "success" in response.lower() or "created" in response.lower()

    # Read file
    response = assistant.process_command(f"Read the file {test_file}")
    assert test_content in response or "test" in response.lower()

    # Cleanup
    test_file.unlink()

def test_app_control(assistant):
    """Test launching and closing applications"""
    # Launch calculator
    response = assistant.process_command("Launch calculator")
    time.sleep(2)

    # Close calculator
    response = assistant.process_command("Close calculator")
    assert "close" in response.lower() or "success" in response.lower()

def test_conversation_context(assistant):
    """Test that conversation maintains context"""
    # First message
    response1 = assistant.process_command("My name is John")

    # Second message - should remember name
    response2 = assistant.process_command("What's my name?")
    assert "john" in response2.lower()

def test_time_and_date(assistant):
    """Test time/date functions"""
    response = assistant.process_command("What time is it?")
    assert any(x in response.lower() for x in ["am", "pm", "time"])

    response = assistant.process_command("What's today's date?")
    assert any(x in response.lower() for x in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Install pytest:
```powershell
pip install pytest
```

**Testing:**
```powershell
pytest tests/test_integration.py -v
```

**Success Criteria:**
- ✅ All tests pass
- ✅ File operations work correctly
- ✅ App control functional
- ✅ Context maintained across turns
- ✅ Functions execute properly

---

## Phase 9: Deployment & Packaging

### Step 9.1: Create Installer

**Actions:**

Build Tauri application:
```powershell
cd voice-assistant-ui
npm run tauri build
```

Create installer script (`scripts/build_installer.ps1`):

```powershell
# Build Python backend as executable
pip install pyinstaller

pyinstaller --onefile `
  --add-data "models;models" `
  --hidden-import torch `
  --hidden-import faster_whisper `
  src/backend/server.py

# Copy to distribution folder
$distDir = "dist/VoiceAssistant"
New-Item -ItemType Directory -Force -Path $distDir

Copy-Item "dist/server.exe" $distDir
Copy-Item "voice-assistant-ui/src-tauri/target/release/voice-assistant-ui.exe" $distDir
Copy-Item "models" $distDir -Recurse

# Create start script
@"
@echo off
echo Starting AI Assistant Backend...
start /B server.exe
timeout /t 3
echo Starting AI Assistant UI...
voice-assistant-ui.exe
"@ | Out-File -FilePath "$distDir/start.bat" -Encoding ASCII

Write-Host "Build complete! Distribution in $distDir"
```

**Testing:**
```powershell
.\scripts\build_installer.ps1
cd dist\VoiceAssistant
.\start.bat
```

**Success Criteria:**
- ✅ Executable builds successfully
- ✅ All dependencies bundled
- ✅ Application runs from distribution folder
- ✅ Models included and loaded correctly

---

### Step 9.2: Documentation

**Actions:**

Create `README.md`:

```markdown
# AI Voice Assistant

GPU-accelerated, privacy-first voice assistant for Windows.

## Features

- Voice-controlled computer automation
- File management
- Application control
- Natural conversation
- On-device processing (no cloud required)

## Requirements

- Windows 11
- NVIDIA GPU (RTX 4090 recommended)
- 32GB RAM
- 100GB free disk space

## Installation

1. Download the latest release
2. Extract to desired location
3. Run `start.bat`

## Usage

- Click "Push to Talk" button to speak
- Or use wake word "Jarvis"
- Give natural commands:
  - "Open Chrome and search for AI news"
  - "What files are on my desktop?"
  - "Create a file called notes.txt"
  - "What time is it?"

## Configuration

Edit `config/settings.yaml` to customize:

```yaml
models:
  stt: medium  # or large-v3
  llm: Qwen2.5-32B-Instruct-Q4_K_M

safety:
  safe_mode: true
  allowed_directories:
    - Documents
    - Desktop
    - Downloads
```

## Troubleshooting

**High GPU memory usage:**
- Use smaller models
- Reduce context length

**Slow response:**
- Check GPU utilization
- Update CUDA drivers

## License

MIT
```

Create `docs/DEVELOPMENT.md` with setup instructions.

**Success Criteria:**
- ✅ Clear documentation
- ✅ Installation instructions
- ✅ Usage examples
- ✅ Troubleshooting guide

---

## Final Checklist

### Performance Targets
- [ ] STT latency: <500ms
- [ ] LLM inference: 60-120 tok/s
- [ ] TTS latency: <2s
- [ ] End-to-end: <5s
- [ ] VRAM usage: <22GB
- [ ] Wake word latency: <200ms

### Features
- [ ] Voice input (STT)
- [ ] Voice output (TTS)
- [ ] Natural language processing
- [ ] File operations
- [ ] App control
- [ ] Keyboard/mouse control
- [ ] Screenshot capability
- [ ] Conversation history
- [ ] Wake word detection
- [ ] Screen understanding (vision)

### Quality
- [ ] All integration tests passing
- [ ] No memory leaks
- [ ] Proper error handling
- [ ] Safe mode protections
- [ ] User permissions for sensitive operations

### Deployment
- [ ] Executable builds
- [ ] Models bundled
- [ ] Documentation complete
- [ ] Installer tested
- [ ] User guide written

---

## Next Steps & Extensions

### Future Enhancements
1. **Calendar Integration**: Sync with Google Calendar/Outlook
2. **Email Control**: Read and send emails
3. **Code Execution**: Sandboxed Python/JavaScript execution
4. **Browser Automation**: Advanced web scraping and control
5. **Multi-language Support**: Support languages beyond English
6. **Voice Customization**: Clone your own voice for TTS
7. **RAG System**: Personal knowledge base with embeddings
8. **Plugin System**: User-created extensions
9. **Mobile Companion**: Control from phone
10. **Meeting Assistant**: Real-time transcription and summarization

### Performance Optimizations
1. **Model Quantization**: Further compress models
2. **Streaming TTS**: Reduce latency with streaming
3. **Speculative Decoding**: Speed up LLM inference
4. **Continuous Batching**: Process multiple requests
5. **Tensor Parallelism**: Split model across multiple GPUs

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [your-repo]/issues
- Discussions: [your-repo]/discussions
- Documentation: [your-docs-site]

---

**Estimated Total Timeline:** 8-12 weeks

**Last Updated:** 2025-11-28
