"""
Function Handler Interface

Abstract base class for function handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional, Any


class FunctionHandlerInterface(ABC):
    """
    Interface for function handlers.
    
    All function handlers must implement these methods.
    """
    
    @abstractmethod
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        Register a function that the LLM can call.
        
        Args:
            name: Function name (must be unique)
            func: Python function to execute
            description: Description of what the function does
            parameters: JSON Schema for function parameters
        """
        pass
    
    @abstractmethod
    def execute(
        self,
        function_name: str,
        arguments: Optional[Dict] = None
    ) -> Dict:
        """
        Execute a registered function.
        
        Args:
            function_name: Name of the function to execute
            arguments: Dictionary of arguments to pass to the function
            
        Returns:
            Dictionary with execution results:
            {
                "success": bool,
                "result": Any,      # Function return value (if success)
                "error": str         # Error message (if failure)
            }
        """
        pass
    
    @abstractmethod
    def format_functions_for_llm(self) -> List[Dict]:
        """
        Format functions for LLM function calling.
        
        Returns:
            List of function definitions in LLM format
        """
        pass
    
    @abstractmethod
    def list_functions(self) -> List[str]:
        """
        Get list of all registered function names.
        
        Returns:
            List of function names
        """
        pass

