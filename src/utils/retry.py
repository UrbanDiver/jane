"""
Retry utility with exponential backoff.

Provides decorators and functions for retrying operations that may fail
due to transient errors.
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional, Any, List
from src.utils.logger import get_logger


def retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    non_retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        retryable_exceptions: Tuple of exception types that should be retried.
                             If None, retries all exceptions except non_retryable_exceptions.
        non_retryable_exceptions: Tuple of exception types that should NOT be retried.
                                  If None, uses default (ValueError, TypeError, KeyError).
    
    Example:
        @retry(max_retries=5, initial_delay=2.0)
        def unreliable_function():
            ...
    """
    if non_retryable_exceptions is None:
        non_retryable_exceptions = (ValueError, TypeError, KeyError, AttributeError)
    
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if exception should not be retried
                    if isinstance(e, non_retryable_exceptions):
                        logger.debug(f"{func.__name__} failed with non-retryable exception: {type(e).__name__}")
                        raise
                    
                    # Check if exception should be retried
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.debug(f"{func.__name__} failed with non-retryable exception: {type(e).__name__}")
                        raise
                    
                    # If this was the last attempt, raise the exception
                    if attempt >= max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Simple retry decorator with fixed delay.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Fixed delay between retries in seconds
        exceptions: Tuple of exception types to retry. If None, retries all.
    
    Example:
        @retry_on_failure(max_retries=5, delay=2.0)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if exceptions and not isinstance(e, exceptions):
                        raise
                    
                    # If this was the last attempt, raise the exception
                    if attempt >= max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

