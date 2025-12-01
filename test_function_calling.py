"""
Test script for LLM function calling.

Tests:
- Function detection
- Function execution
- Result injection
- Multi-step chains
- Error handling
"""

import json
from src.backend.function_handler import FunctionHandler
from src.config.config_schema import STTConfig, TTSConfig, LLMConfig, AssistantConfig


def test_function_formatting():
    """Test formatting functions for LLM."""
    print("\n" + "=" * 60)
    print("Test 1: Function Formatting")
    print("=" * 60)
    
    handler = FunctionHandler()
    tools = handler.format_functions_for_llm()
    
    assert len(tools) > 0, "Should have at least some functions"
    assert all("type" in tool for tool in tools), "All tools should have type"
    assert all("function" in tool for tool in tools), "All tools should have function"
    
    # Check structure
    for tool in tools:
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
    
    print(f"✅ Function formatting works: {len(tools)} functions formatted")
    print(f"   Example function: {tools[0]['function']['name']}")


def test_function_execution():
    """Test function execution."""
    print("\n" + "=" * 60)
    print("Test 2: Function Execution")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # Test time function
    result = handler.execute("get_current_time")
    assert result["success"], "Function should execute successfully"
    assert "result" in result, "Result should contain 'result'"
    assert result["result"] is not None, "Result should not be None"
    
    print(f"✅ Function execution works: {result['result']}")


def test_function_with_args():
    """Test function execution with arguments."""
    print("\n" + "=" * 60)
    print("Test 3: Function with Arguments")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # Register a test function with arguments
    def test_add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    handler.register(
        "test_add",
        test_add,
        "Add two numbers together",
        {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "First number"},
                "b": {"type": "integer", "description": "Second number"}
            },
            "required": ["a", "b"]
        }
    )
    
    result = handler.execute("test_add", {"a": 5, "b": 3})
    assert result["success"], "Function should execute successfully"
    assert result["result"] == 8, f"Expected 8, got {result['result']}"
    
    print(f"✅ Function with arguments works: 5 + 3 = {result['result']}")


def test_function_error_handling():
    """Test function error handling."""
    print("\n" + "=" * 60)
    print("Test 4: Function Error Handling")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # Test non-existent function
    result = handler.execute("nonexistent_function")
    assert not result["success"], "Non-existent function should fail"
    assert "error" in result, "Error should be in result"
    
    # Test function with wrong arguments
    result = handler.execute("get_current_time", {"invalid": "arg"})
    # Should still succeed (function doesn't take args)
    assert result["success"], "Function should handle extra args gracefully"
    
    print("✅ Error handling works correctly")


def test_function_list():
    """Test listing functions."""
    print("\n" + "=" * 60)
    print("Test 5: Function Listing")
    print("=" * 60)
    
    handler = FunctionHandler()
    functions = handler.list_functions()  # Returns list of function names
    
    assert len(functions) > 0, "Should have functions"
    assert all(isinstance(f, str) for f in functions), "All functions should be strings (names)"
    
    # Test get_function_definitions which returns full info
    definitions = handler.get_function_definitions()
    assert len(definitions) > 0, "Should have function definitions"
    assert all("name" in f for f in definitions), "All definitions should have name"
    assert all("description" in f for f in definitions), "All definitions should have description"
    assert all("parameters" in f for f in definitions), "All definitions should have parameters"
    
    print(f"✅ Function listing works: {len(functions)} functions")
    print(f"   Functions: {', '.join(functions[:5])}...")


def test_multi_function_chain():
    """Test multi-function chain (simulated)."""
    print("\n" + "=" * 60)
    print("Test 6: Multi-Function Chain (Simulated)")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # Simulate a chain: get time, then get date
    result1 = handler.execute("get_current_time")
    assert result1["success"]
    
    result2 = handler.execute("get_current_date")
    assert result2["success"]
    
    # Both should work independently
    print(f"✅ Multi-function chain works:")
    print(f"   Time: {result1['result']}")
    print(f"   Date: {result2['result']}")


def test_function_schema():
    """Test function schema structure."""
    print("\n" + "=" * 60)
    print("Test 7: Function Schema")
    print("=" * 60)
    
    handler = FunctionHandler()
    tools = handler.format_functions_for_llm()
    
    # Check that schema is valid
    for tool in tools:
        func = tool["function"]
        params = func["parameters"]
        
        assert "type" in params, "Parameters should have type"
        assert params["type"] == "object", "Parameters type should be object"
        assert "properties" in params, "Parameters should have properties"
    
    print("✅ Function schema is valid")


if __name__ == "__main__":
    print("=" * 60)
    print("LLM Function Calling Tests")
    print("=" * 60)
    
    try:
        test_function_formatting()
        test_function_execution()
        test_function_with_args()
        test_function_error_handling()
        test_function_list()
        test_multi_function_chain()
        test_function_schema()
        
        print("\n" + "=" * 60)
        print("✅ All Function Calling Tests Passed!")
        print("=" * 60)
        print("\nNote: Full LLM function calling integration requires")
        print("testing with actual LLM responses. Function formatting")
        print("and execution are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
