"""
Error handling and recovery utilities.

Provides error classification, recovery strategies, and fallback mechanisms.
"""

from typing import Type, Optional, Callable, Any, Dict, List
from enum import Enum
from src.utils.logger import get_logger


class ErrorType(Enum):
    """Classification of error types."""
    TRANSIENT = "transient"  # Temporary error, should retry
    PERMANENT = "permanent"  # Permanent error, don't retry
    CONFIGURATION = "configuration"  # Configuration error
    RESOURCE = "resource"  # Resource unavailable (GPU, memory, etc.)
    NETWORK = "network"  # Network-related error
    UNKNOWN = "unknown"  # Unknown error type


class ErrorHandler:
    """
    Handler for error classification and recovery.
    
    Classifies errors and provides recovery strategies.
    """
    
    def __init__(self):
        """Initialize error handler."""
        self.logger = get_logger(__name__)
        
        # Map exception types to error classifications
        self.error_classifications = {
            # Transient errors
            TimeoutError: ErrorType.TRANSIENT,
            ConnectionError: ErrorType.TRANSIENT,
            OSError: ErrorType.TRANSIENT,  # Some OSErrors are transient
            
            # Resource errors
            MemoryError: ErrorType.RESOURCE,
            RuntimeError: ErrorType.RESOURCE,  # Often GPU-related
            
            # Configuration errors
            ValueError: ErrorType.CONFIGURATION,
            TypeError: ErrorType.CONFIGURATION,
            KeyError: ErrorType.CONFIGURATION,
            AttributeError: ErrorType.CONFIGURATION,
            FileNotFoundError: ErrorType.CONFIGURATION,
            
            # Network errors
            ConnectionRefusedError: ErrorType.NETWORK,
            ConnectionResetError: ErrorType.NETWORK,
        }
    
    def classify_error(self, error: Exception) -> ErrorType:
        """
        Classify an error type.
        
        Args:
            error: Exception to classify
        
        Returns:
            ErrorType classification
        """
        error_type = type(error)
        
        # Check direct type match
        if error_type in self.error_classifications:
            return self.error_classifications[error_type]
        
        # Check parent classes
        for exc_type, classification in self.error_classifications.items():
            if issubclass(error_type, exc_type):
                return classification
        
        # Check error message for hints
        error_msg = str(error).lower()
        
        if any(keyword in error_msg for keyword in ['timeout', 'temporary', 'retry', 'busy']):
            return ErrorType.TRANSIENT
        
        if any(keyword in error_msg for keyword in ['gpu', 'cuda', 'memory', 'out of memory']):
            return ErrorType.RESOURCE
        
        if any(keyword in error_msg for keyword in ['network', 'connection', 'dns']):
            return ErrorType.NETWORK
        
        if any(keyword in error_msg for keyword in ['config', 'invalid', 'missing', 'not found']):
            return ErrorType.CONFIGURATION
        
        return ErrorType.UNKNOWN
    
    def is_retryable(self, error: Exception) -> bool:
        """
        Check if an error should be retried.
        
        Args:
            error: Exception to check
        
        Returns:
            True if error is retryable, False otherwise
        """
        error_type = self.classify_error(error)
        return error_type in [ErrorType.TRANSIENT, ErrorType.RESOURCE, ErrorType.NETWORK]
    
    def get_recovery_strategy(self, error: Exception) -> Optional[str]:
        """
        Get recovery strategy suggestion for an error.
        
        Args:
            error: Exception to analyze
        
        Returns:
            Recovery strategy string or None
        """
        error_type = self.classify_error(error)
        error_msg = str(error).lower()
        
        strategies = {
            ErrorType.RESOURCE: self._get_resource_recovery_strategy(error_msg),
            ErrorType.TRANSIENT: "Retry the operation after a short delay",
            ErrorType.NETWORK: "Check network connection and retry",
            ErrorType.CONFIGURATION: "Check configuration and fix invalid values",
            ErrorType.PERMANENT: "This is a permanent error. Check logs for details.",
            ErrorType.UNKNOWN: "Unknown error. Check logs for details.",
        }
        
        return strategies.get(error_type, "Unknown error type")
    
    def _get_resource_recovery_strategy(self, error_msg: str) -> str:
        """Get resource-specific recovery strategy."""
        if 'gpu' in error_msg or 'cuda' in error_msg:
            return "GPU unavailable. Try using CPU fallback or check GPU availability."
        if 'memory' in error_msg or 'out of memory' in error_msg:
            return "Out of memory. Try using a smaller model or reducing batch size."
        return "Resource unavailable. Check system resources."
    
    def create_error_message(self, error: Exception, context: Optional[Dict] = None) -> str:
        """
        Create a user-friendly error message with context.
        
        Args:
            error: Exception that occurred
            context: Additional context dictionary
        
        Returns:
            Formatted error message
        """
        error_type = self.classify_error(error)
        error_class = type(error).__name__
        error_msg = str(error)
        
        message_parts = [
            f"Error: {error_class}",
            f"Message: {error_msg}",
            f"Type: {error_type.value}",
        ]
        
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            message_parts.append(f"Context: {context_str}")
        
        recovery = self.get_recovery_strategy(error)
        if recovery:
            message_parts.append(f"Recovery: {recovery}")
        
        return " | ".join(message_parts)


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(
    error: Exception,
    context: Optional[Dict] = None,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle an error with classification and logging.
    
    Args:
        error: Exception to handle
        context: Additional context
        logger: Logger instance (creates one if not provided)
    
    Returns:
        Dictionary with error information:
        {
            "error_type": ErrorType,
            "is_retryable": bool,
            "recovery_strategy": str,
            "message": str
        }
    """
    handler = get_error_handler()
    
    if logger is None:
        from src.utils.logger import get_logger
        logger = get_logger()
    
    error_type = handler.classify_error(error)
    is_retryable = handler.is_retryable(error)
    recovery = handler.get_recovery_strategy(error)
    message = handler.create_error_message(error, context)
    
    # Log based on error type
    if error_type == ErrorType.CONFIGURATION:
        logger.error(message)
    elif error_type == ErrorType.PERMANENT:
        logger.error(message)
    elif is_retryable:
        logger.warning(message)
    else:
        logger.error(message)
    
    return {
        "error_type": error_type,
        "is_retryable": is_retryable,
        "recovery_strategy": recovery,
        "message": message,
        "exception": error
    }

