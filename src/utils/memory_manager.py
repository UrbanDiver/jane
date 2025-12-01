"""
Memory Management Utilities

Provides temporary file cleanup, GPU memory monitoring, and memory leak detection.
"""

import os
import gc
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
from contextlib import contextmanager
from src.utils.logger import get_logger

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryManager:
    """
    Manages memory usage including temporary files and GPU memory.
    """
    
    def __init__(self):
        """Initialize memory manager."""
        self.logger = get_logger(__name__)
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []
    
    @contextmanager
    def temp_file(self, suffix: str = "", prefix: str = "jane_", delete: bool = True):
        """
        Context manager for temporary files.
        
        Args:
            suffix: File suffix (e.g., '.wav')
            prefix: File prefix
            delete: Whether to delete file on exit
        
        Yields:
            Path to temporary file
        """
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        file_path = Path(path)
        
        try:
            os.close(fd)
            if not delete:
                self.temp_files.append(file_path)
            yield file_path
        finally:
            if delete and file_path.exists():
                try:
                    file_path.unlink()
                    self.logger.debug(f"Cleaned up temp file: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete temp file {file_path}: {e}")
    
    @contextmanager
    def temp_directory(self, delete: bool = True):
        """
        Context manager for temporary directories.
        
        Args:
            delete: Whether to delete directory on exit
        
        Yields:
            Path to temporary directory
        """
        dir_path = Path(tempfile.mkdtemp(prefix="jane_"))
        
        try:
            if not delete:
                self.temp_dirs.append(dir_path)
            yield dir_path
        finally:
            if delete and dir_path.exists():
                try:
                    import shutil
                    shutil.rmtree(dir_path)
                    self.logger.debug(f"Cleaned up temp directory: {dir_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete temp directory {dir_path}: {e}")
    
    def cleanup_temp_files(self):
        """Clean up all tracked temporary files."""
        cleaned = 0
        for file_path in self.temp_files[:]:
            try:
                if file_path.exists():
                    file_path.unlink()
                    cleaned += 1
                    self.logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete temp file {file_path}: {e}")
            finally:
                self.temp_files.remove(file_path)
        
        if cleaned > 0:
            self.logger.info(f"Cleaned up {cleaned} temporary files")
    
    def cleanup_temp_dirs(self):
        """Clean up all tracked temporary directories."""
        import shutil
        cleaned = 0
        for dir_path in self.temp_dirs[:]:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    cleaned += 1
                    self.logger.debug(f"Cleaned up temp directory: {dir_path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete temp directory {dir_path}: {e}")
            finally:
                self.temp_dirs.remove(dir_path)
        
        if cleaned > 0:
            self.logger.info(f"Cleaned up {cleaned} temporary directories")
    
    def get_gpu_memory_info(self) -> Optional[Dict]:
        """
        Get GPU memory usage information.
        
        Returns:
            Dictionary with GPU memory info or None if not available
        """
        if not TORCH_AVAILABLE:
            return None
        
        if not torch.cuda.is_available():
            return None
        
        try:
            device = torch.cuda.current_device()
            allocated = torch.cuda.memory_allocated(device) / (1024**3)  # GB
            reserved = torch.cuda.memory_reserved(device) / (1024**3)  # GB
            max_allocated = torch.cuda.max_memory_allocated(device) / (1024**3)  # GB
            
            return {
                "device": device,
                "allocated_gb": allocated,
                "reserved_gb": reserved,
                "max_allocated_gb": max_allocated,
                "free_gb": reserved - allocated
            }
        except Exception as e:
            self.logger.warning(f"Failed to get GPU memory info: {e}")
            return None
    
    def get_system_memory_info(self) -> Optional[Dict]:
        """
        Get system memory usage information.
        
        Returns:
            Dictionary with system memory info or None if not available
        """
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": mem.total / (1024**3),
                "available_gb": mem.available / (1024**3),
                "used_gb": mem.used / (1024**3),
                "percent": mem.percent
            }
        except Exception as e:
            self.logger.warning(f"Failed to get system memory info: {e}")
            return None
    
    def log_memory_usage(self, context: str = ""):
        """
        Log current memory usage.
        
        Args:
            context: Additional context string for log message
        """
        gpu_info = self.get_gpu_memory_info()
        sys_info = self.get_system_memory_info()
        
        if gpu_info:
            self.logger.info(
                f"GPU Memory {context}: "
                f"Allocated: {gpu_info['allocated_gb']:.2f}GB, "
                f"Reserved: {gpu_info['reserved_gb']:.2f}GB, "
                f"Free: {gpu_info['free_gb']:.2f}GB"
            )
        
        if sys_info:
            self.logger.info(
                f"System Memory {context}: "
                f"Used: {sys_info['used_gb']:.2f}GB / {sys_info['total_gb']:.2f}GB "
                f"({sys_info['percent']:.1f}%)"
            )
    
    def clear_gpu_cache(self):
        """Clear GPU memory cache."""
        if not TORCH_AVAILABLE:
            return
        
        if not torch.cuda.is_available():
            return
        
        try:
            torch.cuda.empty_cache()
            gc.collect()
            self.logger.debug("GPU cache cleared")
        except Exception as e:
            self.logger.warning(f"Failed to clear GPU cache: {e}")
    
    def force_garbage_collection(self):
        """Force Python garbage collection."""
        collected = gc.collect()
        if collected > 0:
            self.logger.debug(f"Garbage collected {collected} objects")
        return collected


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


@contextmanager
def temp_file(suffix: str = "", prefix: str = "jane_", delete: bool = True):
    """
    Convenience function for temporary file context manager.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        delete: Whether to delete on exit
    
    Yields:
        Path to temporary file
    """
    manager = get_memory_manager()
    with manager.temp_file(suffix=suffix, prefix=prefix, delete=delete) as path:
        yield path


@contextmanager
def temp_directory(delete: bool = True):
    """
    Convenience function for temporary directory context manager.
    
    Args:
        delete: Whether to delete on exit
    
    Yields:
        Path to temporary directory
    """
    manager = get_memory_manager()
    with manager.temp_directory(delete=delete) as path:
        yield path

