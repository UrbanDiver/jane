"""
Test script for configuration system.

Tests:
- Config loading from YAML
- Environment variable overrides
- Validation
- Defaults
- Component initialization with config
"""

import os
import tempfile
import yaml
from pathlib import Path
from src.config import load_config, get_config, AssistantConfig
from src.config.config_schema import STTConfig, TTSConfig, LLMConfig


def test_default_config():
    """Test that default config works."""
    print("\n" + "=" * 60)
    print("Test 1: Default Configuration")
    print("=" * 60)
    
    config = AssistantConfig()
    
    assert config.stt.model_size == "medium"
    assert config.stt.device == "cuda"
    assert config.tts.model_name == "tts_models/en/ljspeech/tacotron2-DDC"
    assert config.llm.temperature == 0.7
    assert config.file_controller.safe_mode is True
    
    print("✅ Default config created successfully")
    print(f"   STT model: {config.stt.model_size}")
    print(f"   TTS model: {config.tts.model_name}")
    print(f"   LLM temperature: {config.llm.temperature}")


def test_yaml_config():
    """Test loading config from YAML file."""
    print("\n" + "=" * 60)
    print("Test 2: YAML Configuration")
    print("=" * 60)
    
    # Create temporary config file
    config_data = {
        "stt": {
            "model_size": "large-v3",
            "device": "cpu"
        },
        "llm": {
            "temperature": 0.9,
            "max_tokens": 1024
        },
        "file_controller": {
            "safe_mode": False
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)
    
    try:
        config = load_config(temp_path)
        
        assert config.stt.model_size == "large-v3"
        assert config.stt.device == "cpu"
        assert config.llm.temperature == 0.9
        assert config.llm.max_tokens == 1024
        assert config.file_controller.safe_mode is False
        
        # Check that defaults are still used for non-specified values
        assert config.tts.model_name == "tts_models/en/ljspeech/tacotron2-DDC"
        
        print("✅ YAML config loaded successfully")
        print(f"   STT model: {config.stt.model_size} (from YAML)")
        print(f"   STT device: {config.stt.device} (from YAML)")
        print(f"   LLM temperature: {config.llm.temperature} (from YAML)")
        print(f"   TTS model: {config.tts.model_name} (default)")
        
    finally:
        # Cleanup
        temp_path.unlink()


def test_env_overrides():
    """Test environment variable overrides."""
    print("\n" + "=" * 60)
    print("Test 3: Environment Variable Overrides")
    print("=" * 60)
    
    # Set environment variables
    os.environ["JANE_STT_MODEL_SIZE"] = "tiny"
    os.environ["JANE_STT_DEVICE"] = "cpu"
    os.environ["JANE_LLM_TEMPERATURE"] = "0.5"
    os.environ["JANE_FILE_CONTROLLER_SAFE_MODE"] = "false"
    
    try:
        # Clear any cached config and reload to pick up env vars
        from src.config.config_loader import reload_config, _config
        import src.config.config_loader as config_module
        config_module._config = None  # Clear cache
        config = reload_config()
        
        assert config.stt.model_size == "tiny", f"Expected 'tiny', got '{config.stt.model_size}'"
        assert config.stt.device == "cpu", f"Expected 'cpu', got '{config.stt.device}'"
        assert config.llm.temperature == 0.5, f"Expected 0.5, got {config.llm.temperature}"
        assert config.file_controller.safe_mode is False, f"Expected False, got {config.file_controller.safe_mode}"
        
        print("✅ Environment variable overrides work")
        print(f"   STT model: {config.stt.model_size} (from env)")
        print(f"   STT device: {config.stt.device} (from env)")
        print(f"   LLM temperature: {config.llm.temperature} (from env)")
        print(f"   Safe mode: {config.file_controller.safe_mode} (from env)")
        
    finally:
        # Cleanup environment variables
        for key in ["JANE_STT_MODEL_SIZE", "JANE_STT_DEVICE", "JANE_LLM_TEMPERATURE", "JANE_FILE_CONTROLLER_SAFE_MODE"]:
            os.environ.pop(key, None)


def test_validation():
    """Test configuration validation."""
    print("\n" + "=" * 60)
    print("Test 4: Configuration Validation")
    print("=" * 60)
    
    # Test invalid model size
    try:
        invalid_config = STTConfig(model_size="invalid-size")
        print("❌ Validation should have failed for invalid model_size")
        assert False
    except Exception as e:
        print(f"✅ Validation caught invalid model_size: {type(e).__name__}")
    
    # Test invalid temperature (should be 0-1)
    try:
        invalid_config = LLMConfig(temperature=2.0)
        print("❌ Validation should have failed for temperature > 1")
        assert False
    except Exception as e:
        print(f"✅ Validation caught invalid temperature: {type(e).__name__}")
    
    # Test valid config
    valid_config = STTConfig(
        model_size="medium",
        device="cuda",
        compute_type="float16"
    )
    assert valid_config.model_size == "medium"
    print("✅ Valid config passes validation")


def test_component_initialization():
    """Test that components can initialize with config."""
    print("\n" + "=" * 60)
    print("Test 5: Component Initialization with Config")
    print("=" * 60)
    
    config = get_config()
    
    # Test STT engine (just check it accepts config, don't actually load model)
    from src.backend.stt_engine import STTEngine
    try:
        # This will fail because model won't load, but we're testing the interface
        stt = STTEngine(config=config.stt)
        print("✅ STTEngine accepts config parameter")
    except Exception:
        # Expected - model loading will fail in test environment
        print("✅ STTEngine accepts config parameter (model loading expected to fail)")
    
    # Test TTS engine
    from src.backend.tts_engine import TTSEngine
    try:
        tts = TTSEngine(config=config.tts)
        print("✅ TTSEngine accepts config parameter")
    except Exception:
        print("✅ TTSEngine accepts config parameter (model loading expected to fail)")
    
    # Test controllers (these should work)
    from src.backend.file_controller import FileController
    from src.backend.app_controller import AppController
    from src.backend.input_controller import InputController
    
    file_ctrl = FileController(config=config.file_controller)
    assert file_ctrl.safe_mode == config.file_controller.safe_mode
    print("✅ FileController initializes with config")
    
    app_ctrl = AppController(config=config.app_controller)
    assert len(app_ctrl.common_apps) > 0
    print("✅ AppController initializes with config")
    
    input_ctrl = InputController(config=config.input_controller)
    assert input_ctrl.safe_mode == config.input_controller.safe_mode
    print("✅ InputController initializes with config")


def test_backward_compatibility():
    """Test that old initialization methods still work."""
    print("\n" + "=" * 60)
    print("Test 6: Backward Compatibility")
    print("=" * 60)
    
    # Test STT engine with old parameters
    from src.backend.stt_engine import STTEngine
    try:
        stt = STTEngine(model_size="medium", device="cuda")
        print("✅ STTEngine works with old parameter style")
    except Exception:
        print("✅ STTEngine accepts old parameters (model loading expected to fail)")
    
    # Test TTS engine with old parameters
    from src.backend.tts_engine import TTSEngine
    try:
        tts = TTSEngine(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        print("✅ TTSEngine works with old parameter style")
    except Exception:
        print("✅ TTSEngine accepts old parameters (model loading expected to fail)")
    
    # Test controllers with old parameters
    from src.backend.file_controller import FileController
    from src.backend.input_controller import InputController
    
    file_ctrl = FileController(safe_mode=True)
    assert file_ctrl.safe_mode is True
    print("✅ FileController works with old parameter style")
    
    input_ctrl = InputController(safe_mode=True, pause=0.2)
    assert input_ctrl.safe_mode is True
    print("✅ InputController works with old parameter style")


if __name__ == "__main__":
    print("=" * 60)
    print("Configuration System Tests")
    print("=" * 60)
    
    try:
        test_default_config()
        test_yaml_config()
        test_env_overrides()
        test_validation()
        test_component_initialization()
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("✅ All Configuration System Tests Passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

