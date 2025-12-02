"""
Centralized logging system for Jane AI Assistant.

Provides structured logging with file and console handlers,
performance timing, and log rotation.
"""

import logging
import sys
import time
import functools
import os
import platform
from pathlib import Path
from logging.handlers import RotatingFileHandler
from logging import FileHandler
from typing import Optional, Callable, Any
from datetime import datetime


# Log directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / "jane.log"

# Configure root logger
_root_logger: Optional[logging.Logger] = None


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


class SafeRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that handles Windows file locking errors gracefully."""
    
    def emit(self, record):
        """Emit a record, handling rotation errors gracefully."""
        try:
            super().emit(record)
        except (PermissionError, OSError) as e:
            # If rotation fails due to file locking (Windows), 
            # try to continue with current file
            try:
                # Try to emit without rotation
                if self.stream:
                    self.stream.write(self.format(record) + self.terminator)
                    self.stream.flush()
            except Exception:
                # If even that fails, just skip file logging for this record
                # The console handler will still work
                pass


def _setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation (Windows-safe)
    # On Windows, file locking can prevent rotation, so we use a safe handler
    try:
        file_handler = SafeRotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # Keep 7 backup files (7 days)
            encoding='utf-8',
            delay=True  # Delay file opening until first write (helps with Windows locking)
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception:
        # If handler creation fails, fall back to simple FileHandler
        try:
            file_handler = FileHandler(LOG_FILE, encoding='utf-8', mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If file logging completely fails, just use console
            pass
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger for a module.
    
    Args:
        name: Logger name (typically __name__). If None, uses caller's module.
    
    Returns:
        Configured logger instance
    """
    if name is None:
        # Get caller's module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'jane')
    
    return _setup_logger(name)


def log_performance(operation_name: Optional[str] = None):
    """
    Decorator to log performance metrics for function execution.
    
    Args:
        operation_name: Custom name for the operation. If None, uses function name.
    
    Example:
        @log_performance("STT Transcription")
        def transcribe(audio_path):
            ...
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            logger.debug(f"Starting {op_name}...")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                # Update timing in result if it's a dict (for LLM/STT/TTS results)
                if isinstance(result, dict) and 'time' in result:
                    result['time'] = elapsed
                    # Calculate tokens_per_second if tokens are present
                    if 'tokens' in result and elapsed > 0:
                        result['tokens_per_second'] = result['tokens'] / elapsed
                
                logger.info(f"{op_name} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{op_name} failed after {elapsed:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


def log_timing(operation_name: str, logger: Optional[logging.Logger] = None):
    """
    Context manager for timing operations.
    
    Args:
        operation_name: Name of the operation
        logger: Logger instance (creates one if not provided)
    
    Example:
        with log_timing("LLM Generation"):
            result = llm.generate(prompt)
    """
    if logger is None:
        logger = get_logger()
    
    class TimingContext:
        def __init__(self, name: str, log: logging.Logger):
            self.name = name
            self.log = log
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            self.log.debug(f"Starting {self.name}...")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.time() - self.start_time
            if exc_type is None:
                self.log.info(f"{self.name} completed in {elapsed:.3f}s")
            else:
                self.log.error(f"{self.name} failed after {elapsed:.3f}s: {exc_val}")
            return False  # Don't suppress exceptions
    
    return TimingContext(operation_name, logger)


# Initialize root logger
_root_logger = _setup_logger("jane", logging.INFO)

