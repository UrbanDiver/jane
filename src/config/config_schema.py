"""
Configuration schema using Pydantic for type validation.

Defines all configuration models for the Jane AI Assistant.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path


class STTConfig(BaseModel):
    """Speech-to-Text engine configuration."""
    
    model_size: str = Field(
        default="medium",
        description="Whisper model size (tiny, base, small, medium, large-v2, large-v3)"
    )
    device: str = Field(
        default="cuda",
        description="Device to use (cuda or cpu)"
    )
    compute_type: str = Field(
        default="float16",
        description="Computation type (float16, int8, int8_float16)"
    )
    num_workers: int = Field(
        default=4,
        description="Number of workers for processing"
    )
    sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz"
    )


class TTSConfig(BaseModel):
    """Text-to-Speech engine configuration."""
    
    model_name: str = Field(
        default="tts_models/en/ljspeech/tacotron2-DDC",
        description="TTS model name"
    )
    device: Optional[str] = Field(
        default=None,
        description="Device to use (cuda or cpu). Auto-detects if None."
    )


class LLMConfig(BaseModel):
    """Language Model engine configuration."""
    
    model_path: str = Field(
        default="models/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        description="Path to LLM GGUF model file"
    )
    n_gpu_layers: int = Field(
        default=-1,
        description="Number of layers to offload to GPU (-1 = all layers)"
    )
    n_ctx: int = Field(
        default=4096,
        description="Context window size"
    )
    n_batch: int = Field(
        default=512,
        description="Batch size for processing"
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose logging"
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature (0.0-1.0)"
    )
    max_tokens: int = Field(
        default=512,
        description="Maximum tokens to generate"
    )


class FileControllerConfig(BaseModel):
    """File controller configuration."""
    
    safe_mode: bool = Field(
        default=True,
        description="Enable safe mode with directory restrictions"
    )
    allowed_directories: List[str] = Field(
        default_factory=lambda: [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Downloads"),
            str(Path.home() / "Pictures"),
            str(Path.home() / "Videos"),
            str(Path.home() / "Music"),
        ],
        description="List of allowed directories in safe mode"
    )


class AppControllerConfig(BaseModel):
    """Application controller configuration."""
    
    common_apps: dict = Field(
        default_factory=lambda: {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
        },
        description="Dictionary of common app names to executable paths"
    )


class InputControllerConfig(BaseModel):
    """Input controller configuration."""
    
    safe_mode: bool = Field(
        default=True,
        description="Enable safe mode with failsafe"
    )
    pause: float = Field(
        default=0.1,
        description="Pause between actions in seconds"
    )


class WakeWordConfig(BaseModel):
    """Wake word detection configuration."""
    
    enabled: bool = Field(
        default=False,
        description="Enable wake word detection"
    )
    wake_words: List[str] = Field(
        default_factory=lambda: ["jane", "hey jane"],
        description="List of wake words to detect"
    )
    sensitivity: float = Field(
        default=0.5,
        description="Sensitivity for wake word detection (0.0-1.0)"
    )
    check_interval: float = Field(
        default=0.1,
        description="Interval in seconds to check for wake word"
    )


class AssistantConfig(BaseModel):
    """Main assistant configuration."""
    
    stt: STTConfig = Field(
        default_factory=STTConfig,
        description="STT engine configuration"
    )
    tts: TTSConfig = Field(
        default_factory=TTSConfig,
        description="TTS engine configuration"
    )
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM engine configuration"
    )
    file_controller: FileControllerConfig = Field(
        default_factory=FileControllerConfig,
        description="File controller configuration"
    )
    app_controller: AppControllerConfig = Field(
        default_factory=AppControllerConfig,
        description="App controller configuration"
    )
    input_controller: InputControllerConfig = Field(
        default_factory=InputControllerConfig,
        description="Input controller configuration"
    )
    max_conversation_history: int = Field(
        default=20,
        description="Maximum number of messages to keep in conversation history"
    )
    wake_word: WakeWordConfig = Field(
        default_factory=WakeWordConfig,
        description="Wake word detection configuration"
    )

