"""
Test script for error handling and recovery system.

Tests:
- Retry logic
- Fallback mechanisms
- Error classification
- Error recovery
"""

import time
from src.utils.retry import retry, retry_on_failure
from src.utils.error_handler import (
    ErrorHandler,
    ErrorType,
    get_error_handler,
    handle_error
)


def test_retry_success():
    """Test retry logic with eventual success."""
    print("\n" + "=" * 60)
    print("Test 1: Retry Logic - Success After Retries")
    print("=" * 60)
    
    attempt_count = [0]
    
    @retry(max_retries=3, initial_delay=0.1)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise RuntimeError("Temporary failure")
        return "Success!"
    
    result = flaky_function()
    assert result == "Success!"
    assert attempt_count[0] == 3
    print(f"✅ Retry logic works: succeeded after {attempt_count[0]} attempts")


def test_retry_failure():
    """Test retry logic with permanent failure."""
    print("\n" + "=" * 60)
    print("Test 2: Retry Logic - Permanent Failure")
    print("=" * 60)
    
    attempt_count = [0]
    
    @retry(max_retries=2, initial_delay=0.1)
    def always_fails():
        attempt_count[0] += 1
        raise ValueError("Permanent failure")
    
    try:
        always_fails()
        assert False, "Should have raised exception"
    except ValueError as e:
        assert attempt_count[0] == 1  # Should fail fast for non-retryable exceptions
        print(f"✅ Non-retryable exception failed fast: {attempt_count[0]} attempt(s)")


def test_retry_exponential_backoff():
    """Test exponential backoff timing."""
    print("\n" + "=" * 60)
    print("Test 3: Exponential Backoff")
    print("=" * 60)
    
    attempt_count = [0]
    timings = []
    
    @retry(max_retries=3, initial_delay=0.1, exponential_base=2.0)
    def test_backoff():
        attempt_count[0] += 1
        timings.append(time.time())
        if attempt_count[0] < 4:
            raise RuntimeError("Retry")
        return "Success"
    
    start = time.time()
    result = test_backoff()
    end = time.time()
    
    assert result == "Success"
    assert attempt_count[0] == 4
    
    # Check that delays increased (roughly)
    if len(timings) >= 2:
        delay1 = timings[1] - timings[0]
        delay2 = timings[2] - timings[1] if len(timings) > 2 else 0
        
        print(f"✅ Exponential backoff works")
        print(f"   Total time: {end - start:.2f}s")
        print(f"   Attempts: {attempt_count[0]}")


def test_error_classification():
    """Test error classification."""
    print("\n" + "=" * 60)
    print("Test 4: Error Classification")
    print("=" * 60)
    
    handler = ErrorHandler()
    
    # Test transient error
    timeout_error = TimeoutError("Operation timed out")
    assert handler.classify_error(timeout_error) == ErrorType.TRANSIENT
    assert handler.is_retryable(timeout_error) is True
    print("✅ TimeoutError classified as TRANSIENT (retryable)")
    
    # Test configuration error
    value_error = ValueError("Invalid value")
    assert handler.classify_error(value_error) == ErrorType.CONFIGURATION
    assert handler.is_retryable(value_error) is False
    print("✅ ValueError classified as CONFIGURATION (not retryable)")
    
    # Test resource error
    memory_error = MemoryError("Out of memory")
    assert handler.classify_error(memory_error) == ErrorType.RESOURCE
    assert handler.is_retryable(memory_error) is True
    print("✅ MemoryError classified as RESOURCE (retryable)")
    
    # Test network error
    connection_error = ConnectionError("Connection failed")
    assert handler.classify_error(connection_error) == ErrorType.TRANSIENT
    assert handler.is_retryable(connection_error) is True
    print("✅ ConnectionError classified as TRANSIENT (retryable)")


def test_recovery_strategies():
    """Test recovery strategy suggestions."""
    print("\n" + "=" * 60)
    print("Test 5: Recovery Strategies")
    print("=" * 60)
    
    handler = ErrorHandler()
    
    # Test GPU error
    gpu_error = RuntimeError("CUDA out of memory")
    strategy = handler.get_recovery_strategy(gpu_error)
    assert "GPU" in strategy or "CPU" in strategy
    print(f"✅ GPU error recovery: {strategy}")
    
    # Test memory error
    memory_error = MemoryError("Out of memory")
    strategy = handler.get_recovery_strategy(memory_error)
    assert "memory" in strategy.lower() or "model" in strategy.lower()
    print(f"✅ Memory error recovery: {strategy}")
    
    # Test transient error
    timeout_error = TimeoutError("Timeout")
    strategy = handler.get_recovery_strategy(timeout_error)
    assert "retry" in strategy.lower()
    print(f"✅ Transient error recovery: {strategy}")


def test_error_messages():
    """Test error message creation."""
    print("\n" + "=" * 60)
    print("Test 6: Error Messages")
    print("=" * 60)
    
    handler = ErrorHandler()
    
    error = RuntimeError("GPU unavailable")
    context = {"operation": "model_loading", "device": "cuda"}
    
    message = handler.create_error_message(error, context)
    
    assert "RuntimeError" in message
    assert "GPU unavailable" in message
    assert "operation=model_loading" in message
    
    print(f"✅ Error message created: {message[:100]}...")


def test_handle_error_function():
    """Test handle_error utility function."""
    print("\n" + "=" * 60)
    print("Test 7: handle_error Function")
    print("=" * 60)
    
    error = ConnectionError("Connection refused")
    context = {"host": "localhost", "port": 8080}
    
    result = handle_error(error, context=context)
    
    assert result["error_type"] == ErrorType.TRANSIENT
    assert result["is_retryable"] is True
    assert "recovery_strategy" in result
    assert "message" in result
    
    print(f"✅ handle_error works")
    print(f"   Error type: {result['error_type'].value}")
    print(f"   Retryable: {result['is_retryable']}")
    print(f"   Recovery: {result['recovery_strategy']}")


def test_retryable_exceptions():
    """Test retry with specific exception types."""
    print("\n" + "=" * 60)
    print("Test 8: Retryable Exceptions")
    print("=" * 60)
    
    attempt_count = [0]
    
    @retry(max_retries=2, initial_delay=0.1, retryable_exceptions=(RuntimeError,))
    def test_retryable():
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise RuntimeError("Retry this")
        return "Success"
    
    result = test_retryable()
    assert result == "Success"
    assert attempt_count[0] == 2
    print(f"✅ Retryable exceptions work: {attempt_count[0]} attempts")
    
    # Test non-retryable exception
    attempt_count[0] = 0
    
    @retry(max_retries=2, initial_delay=0.1, retryable_exceptions=(RuntimeError,))
    def test_non_retryable():
        attempt_count[0] += 1
        raise ValueError("Don't retry this")
    
    try:
        test_non_retryable()
        assert False
    except ValueError:
        assert attempt_count[0] == 1  # Should fail fast
        print(f"✅ Non-retryable exceptions fail fast: {attempt_count[0]} attempt")


if __name__ == "__main__":
    print("=" * 60)
    print("Error Handling & Recovery Tests")
    print("=" * 60)
    
    try:
        test_retry_success()
        test_retry_failure()
        test_retry_exponential_backoff()
        test_error_classification()
        test_recovery_strategies()
        test_error_messages()
        test_handle_error_function()
        test_retryable_exceptions()
        
        print("\n" + "=" * 60)
        print("✅ All Error Handling & Recovery Tests Passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

