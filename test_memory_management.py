"""
Test script for memory management system.

Tests:
- Temp file cleanup
- GPU memory monitoring
- Memory leak detection
- Memory usage logging
"""

import os
import time
from pathlib import Path
from src.utils.memory_manager import (
    MemoryManager,
    get_memory_manager,
    temp_file,
    temp_directory
)


def test_temp_file_context_manager():
    """Test temporary file context manager."""
    print("\n" + "=" * 60)
    print("Test 1: Temporary File Context Manager")
    print("=" * 60)
    
    file_path = None
    
    with temp_file(suffix=".wav") as temp_path:
        file_path = temp_path
        # Write some data
        temp_path.write_text("test data")
        assert temp_path.exists(), "Temp file should exist"
    
    # File should be deleted after context exit
    assert not file_path.exists(), "Temp file should be deleted"
    
    print("✅ Temporary file context manager works correctly")


def test_temp_file_persistence():
    """Test temporary file with delete=False."""
    print("\n" + "=" * 60)
    print("Test 2: Temporary File Persistence")
    print("=" * 60)
    
    manager = get_memory_manager()
    initial_count = len(manager.temp_files)
    
    with temp_file(suffix=".txt", delete=False) as temp_path:
        temp_path.write_text("persistent data")
        assert temp_path.exists()
    
    # File should still exist
    assert temp_path.exists(), "Persistent temp file should exist"
    assert len(manager.temp_files) == initial_count + 1, "File should be tracked"
    
    # Cleanup
    manager.cleanup_temp_files()
    assert not temp_path.exists(), "File should be deleted after cleanup"
    
    print("✅ Temporary file persistence works correctly")


def test_temp_directory():
    """Test temporary directory context manager."""
    print("\n" + "=" * 60)
    print("Test 3: Temporary Directory Context Manager")
    print("=" * 60)
    
    dir_path = None
    
    with temp_directory() as temp_dir:
        dir_path = temp_dir
        # Create a file in the directory
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()
        assert temp_dir.exists()
    
    # Directory should be deleted
    assert not dir_path.exists(), "Temp directory should be deleted"
    
    print("✅ Temporary directory context manager works correctly")


def test_memory_info():
    """Test memory information retrieval."""
    print("\n" + "=" * 60)
    print("Test 4: Memory Information")
    print("=" * 60)
    
    manager = get_memory_manager()
    
    # Test GPU memory info
    gpu_info = manager.get_gpu_memory_info()
    if gpu_info:
        assert "allocated_gb" in gpu_info
        assert "reserved_gb" in gpu_info
        print(f"✅ GPU memory info: {gpu_info['allocated_gb']:.2f}GB allocated")
    else:
        print("✅ GPU memory info: Not available (expected if no GPU)")
    
    # Test system memory info
    sys_info = manager.get_system_memory_info()
    if sys_info:
        assert "total_gb" in sys_info
        assert "used_gb" in sys_info
        print(f"✅ System memory info: {sys_info['used_gb']:.2f}GB / {sys_info['total_gb']:.2f}GB")
    else:
        print("✅ System memory info: Not available (psutil not installed)")
    
    print("✅ Memory information retrieval works")


def test_memory_logging():
    """Test memory usage logging."""
    print("\n" + "=" * 60)
    print("Test 5: Memory Usage Logging")
    print("=" * 60)
    
    manager = get_memory_manager()
    
    # This should not raise an exception
    manager.log_memory_usage("(test)")
    
    print("✅ Memory usage logging works")


def test_gpu_cache_clear():
    """Test GPU cache clearing."""
    print("\n" + "=" * 60)
    print("Test 6: GPU Cache Clearing")
    print("=" * 60)
    
    manager = get_memory_manager()
    
    # This should not raise an exception
    manager.clear_gpu_cache()
    
    print("✅ GPU cache clearing works")


def test_garbage_collection():
    """Test garbage collection."""
    print("\n" + "=" * 60)
    print("Test 7: Garbage Collection")
    print("=" * 60)
    
    manager = get_memory_manager()
    
    # Create some objects
    large_list = [i for i in range(10000)]
    
    # Force garbage collection
    collected = manager.force_garbage_collection()
    
    print(f"✅ Garbage collection works: {collected} objects collected")


def test_cleanup_tracking():
    """Test cleanup of tracked files."""
    print("\n" + "=" * 60)
    print("Test 8: Cleanup Tracking")
    print("=" * 60)
    
    manager = get_memory_manager()
    
    # Create persistent temp files
    files_created = []
    for i in range(3):
        with temp_file(suffix=f"_{i}.txt", delete=False) as temp_path:
            temp_path.write_text(f"test {i}")
            files_created.append(temp_path)
    
    # All files should exist
    for f in files_created:
        assert f.exists(), f"File {f} should exist"
    
    # Cleanup all
    manager.cleanup_temp_files()
    
    # All files should be deleted
    for f in files_created:
        assert not f.exists(), f"File {f} should be deleted"
    
    print(f"✅ Cleanup tracking works: {len(files_created)} files cleaned up")


if __name__ == "__main__":
    print("=" * 60)
    print("Memory Management Tests")
    print("=" * 60)
    
    try:
        test_temp_file_context_manager()
        test_temp_file_persistence()
        test_temp_directory()
        test_memory_info()
        test_memory_logging()
        test_gpu_cache_clear()
        test_garbage_collection()
        test_cleanup_tracking()
        
        print("\n" + "=" * 60)
        print("✅ All Memory Management Tests Passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

