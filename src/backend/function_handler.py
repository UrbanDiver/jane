"""
Function Handler for LLM Function Calling

This module provides a system for registering and executing functions
that the LLM can call to control the computer and perform actions.
"""

import json
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
import inspect


class FunctionHandler:
    """
    Handler for LLM function calling.
    
    Registers functions that the LLM can call and provides execution
    capabilities with proper error handling.
    """
    
    def __init__(self):
        """Initialize the function handler."""
        self.functions = {}
        self.register_default_functions()
        print(f"FunctionHandler initialized with {len(self.functions)} functions")
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any]
    ):
        """
        Register a function that the LLM can call.
        
        Args:
            name: Function name (must be unique)
            func: Python function to execute
            description: Description of what the function does
            parameters: JSON Schema for function parameters
        """
        if name in self.functions:
            print(f"⚠️  Warning: Function '{name}' already registered, overwriting...")
        
        self.functions[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        print(f"✅ Registered function: {name}")
    
    def register_default_functions(self):
        """Register built-in utility functions."""
        
        def get_current_time() -> str:
            """Get the current time."""
            return datetime.now().strftime("%I:%M %p")
        
        def get_current_date() -> str:
            """Get today's date."""
            return datetime.now().strftime("%A, %B %d, %Y")
        
        def get_current_datetime() -> str:
            """Get current date and time."""
            return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        # Register time/date functions
        self.register(
            "get_current_time",
            get_current_time,
            "Get the current time in 12-hour format (e.g., '3:45 PM')",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.register(
            "get_current_date",
            get_current_date,
            "Get today's date in a readable format (e.g., 'Monday, November 30, 2025')",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.register(
            "get_current_datetime",
            get_current_datetime,
            "Get the current date and time in a readable format",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    
    def get_function_definitions(self) -> List[Dict]:
        """
        Get function definitions in OpenAI-compatible format.
        
        Returns:
            List of function definition dictionaries
        """
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in self.functions.items()
        ]
    
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
        if function_name not in self.functions:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }
        
        func_info = self.functions[function_name]
        func = func_info["function"]
        args = arguments or {}
        
        try:
            # Get function signature to validate arguments
            sig = inspect.signature(func)
            params = sig.parameters
            
            # Filter arguments to only include those the function accepts
            filtered_args = {}
            for param_name, param in params.items():
                if param_name in args:
                    filtered_args[param_name] = args[param_name]
                elif param.default == inspect.Parameter.empty:
                    # Required parameter missing
                    return {
                        "success": False,
                        "error": f"Missing required parameter: {param_name}"
                    }
            
            # Execute function
            result = func(**filtered_args)
            
            return {
                "success": True,
                "result": result
            }
            
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid arguments: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_functions(self) -> List[str]:
        """Get list of all registered function names."""
        return list(self.functions.keys())
    
    def get_function_info(self, function_name: str) -> Optional[Dict]:
        """Get information about a specific function."""
        if function_name not in self.functions:
            return None
        
        info = self.functions[function_name].copy()
        # Don't include the actual function object
        info.pop("function", None)
        return info


if __name__ == "__main__":
    # Test the function handler
    print("=" * 60)
    print("Testing Function Handler")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # List available functions
    print("\nAvailable functions:")
    for func_def in handler.get_function_definitions():
        print(f"  - {func_def['name']}: {func_def['description']}")
    
    # Test function execution
    print("\n" + "=" * 60)
    print("Testing Function Execution")
    print("=" * 60)
    
    # Test get_current_time
    print("\n1. Testing get_current_time:")
    result = handler.execute("get_current_time")
    if result["success"]:
        print(f"   ✅ Result: {result['result']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test get_current_date
    print("\n2. Testing get_current_date:")
    result = handler.execute("get_current_date")
    if result["success"]:
        print(f"   ✅ Result: {result['result']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test get_current_datetime
    print("\n3. Testing get_current_datetime:")
    result = handler.execute("get_current_datetime")
    if result["success"]:
        print(f"   ✅ Result: {result['result']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test unknown function
    print("\n4. Testing unknown function:")
    result = handler.execute("unknown_function")
    if not result["success"]:
        print(f"   ✅ Correctly rejected: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ Function Handler test complete!")
    print("=" * 60)

