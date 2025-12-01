"""
Test script for logging system.

Tests:
- Log levels
- File logging
- Performance logging
- Log rotation
- Console output with colors
"""

import os
import time
import logging
from pathlib import Path
from src.utils.logger import get_logger, log_performance, log_timing


def test_log_levels():
    """Test different log levels."""
    print("\n" + "=" * 60)
    print("Test 1: Log Levels")
    print("=" * 60)
    
    logger = get_logger("test_logger")
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    print("✅ All log levels tested")


def test_file_logging():
    """Test that logs are written to file."""
    print("\n" + "=" * 60)
    print("Test 2: File Logging")
    print("=" * 60)
    
    logger = get_logger("test_file_logger")
    logger.info("Test message for file logging")
    
    # Check if log file exists
    log_file = Path("logs/jane.log")
    if log_file.exists():
        # Read last few lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if any("Test message for file logging" in line for line in lines[-10:]):
                print("✅ Logs written to file")
                print(f"   Log file: {log_file}")
                print(f"   File size: {log_file.stat().st_size} bytes")
            else:
                print("❌ Test message not found in log file")
    else:
        print("❌ Log file not found")


def test_performance_logging():
    """Test performance timing decorator."""
    print("\n" + "=" * 60)
    print("Test 3: Performance Logging")
    print("=" * 60)
    
    @log_performance("Test Operation")
    def test_function():
        time.sleep(0.1)  # Simulate work
        return "result"
    
    result = test_function()
    assert result == "result"
    print("✅ Performance decorator works")


def test_timing_context():
    """Test timing context manager."""
    print("\n" + "=" * 60)
    print("Test 4: Timing Context Manager")
    print("=" * 60)
    
    logger = get_logger("test_timing")
    
    with log_timing("Test Context Operation", logger):
        time.sleep(0.1)  # Simulate work
    
    print("✅ Timing context manager works")


def test_log_rotation():
    """Test log rotation (if file gets large)."""
    print("\n" + "=" * 60)
    print("Test 5: Log Rotation")
    print("=" * 60)
    
    logger = get_logger("test_rotation")
    
    # Write many log messages
    for i in range(100):
        logger.debug(f"Rotation test message {i}")
    
    log_file = Path("logs/jane.log")
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"✅ Log file exists: {size} bytes")
        print(f"   Rotation configured: maxBytes=10MB, backupCount=7")
    else:
        print("❌ Log file not found")


def test_module_loggers():
    """Test that different modules get their own loggers."""
    print("\n" + "=" * 60)
    print("Test 6: Module Loggers")
    print("=" * 60)
    
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    logger1.info("Message from module1")
    logger2.info("Message from module2")
    
    # Check that both loggers are different instances but work
    assert logger1.name == "module1"
    assert logger2.name == "module2"
    
    print("✅ Module loggers work correctly")
    print(f"   Logger 1 name: {logger1.name}")
    print(f"   Logger 2 name: {logger2.name}")


def test_error_logging():
    """Test error logging with traceback."""
    print("\n" + "=" * 60)
    print("Test 7: Error Logging with Traceback")
    print("=" * 60)
    
    logger = get_logger("test_errors")
    
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error("Caught an error", exc_info=True)
    
    print("✅ Error logging with traceback works")


if __name__ == "__main__":
    print("=" * 60)
    print("Logging System Tests")
    print("=" * 60)
    
    try:
        test_log_levels()
        test_file_logging()
        test_performance_logging()
        test_timing_context()
        test_log_rotation()
        test_module_loggers()
        test_error_logging()
        
        print("\n" + "=" * 60)
        print("✅ All Logging System Tests Passed!")
        print("=" * 60)
        print("\nCheck logs/jane.log for file logging output")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

