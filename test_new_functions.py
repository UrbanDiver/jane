"""
Test script for new functions (web search and system info)

Tests Step 3.3: Additional Functions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.backend.web_search import WebSearch, search_web
from src.backend.system_info import (
    SystemInfo, get_system_info, get_cpu_info, 
    get_memory_info, get_disk_usage, get_network_info
)
from src.backend.function_handler import FunctionHandler
import inspect


def test_web_search():
    """Test web search functionality."""
    print("=" * 60)
    print("Testing Web Search")
    print("=" * 60)
    
    searcher = WebSearch()
    
    # Test 1: Basic search
    print("\n1. Testing basic search:")
    result = searcher.search("Python programming", max_results=3)
    assert result["success"], f"Search failed: {result.get('error')}"
    assert "results" in result, "Results not in response"
    assert len(result["results"]) > 0, "No results returned"
    print(f"   ✅ Found {len(result['results'])} results")
    
    # Test 2: Empty query
    print("\n2. Testing empty query:")
    result = searcher.search("", max_results=3)
    assert not result["success"], "Empty query should fail"
    print("   ✅ Correctly rejected empty query")
    
    # Test 3: Convenience function
    print("\n3. Testing convenience function:")
    formatted = search_web("artificial intelligence", max_results=2)
    assert isinstance(formatted, str), "Should return string"
    assert len(formatted) > 0, "Should return non-empty string"
    print("   ✅ Convenience function works")
    print(f"   Sample output:\n{formatted[:200]}...")
    
    print("\n✅ Web search tests passed!")


def test_system_info():
    """Test system information functionality."""
    print("\n" + "=" * 60)
    print("Testing System Info")
    print("=" * 60)
    
    sys_info = SystemInfo()
    
    # Test 1: System info
    print("\n1. Testing get_system_info:")
    result = sys_info.get_system_info()
    assert result["success"], f"Failed: {result.get('error')}"
    assert "system" in result, "System info missing"
    assert "platform" in result, "Platform info missing"
    print(f"   ✅ System: {result['system']}")
    print(f"   ✅ Platform: {result['platform']}")
    
    # Test 2: CPU info
    print("\n2. Testing get_cpu_info:")
    result = sys_info.get_cpu_info()
    assert result["success"], f"Failed: {result.get('error')}"
    assert "cpu_count" in result, "CPU count missing"
    assert "cpu_percent" in result, "CPU percent missing"
    print(f"   ✅ CPU Cores: {result['cpu_count']} physical")
    print(f"   ✅ CPU Usage: {result['cpu_percent']:.1f}%")
    
    # Test 3: Memory info
    print("\n3. Testing get_memory_info:")
    result = sys_info.get_memory_info()
    assert result["success"], f"Failed: {result.get('error')}"
    assert "total" in result, "Memory total missing"
    assert "percent" in result, "Memory percent missing"
    print(f"   ✅ Memory Usage: {result['percent']:.1f}%")
    
    # Test 4: Disk info
    print("\n4. Testing get_disk_info:")
    result = sys_info.get_disk_info()
    assert result["success"], f"Failed: {result.get('error')}"
    assert "total" in result, "Disk total missing"
    assert "percent" in result, "Disk percent missing"
    print(f"   ✅ Disk Usage: {result['percent']:.1f}%")
    
    # Test 5: Network info
    print("\n5. Testing get_network_info:")
    result = sys_info.get_network_info()
    assert result["success"], f"Failed: {result.get('error')}"
    assert "interfaces" in result, "Network interfaces missing"
    assert len(result["interfaces"]) > 0, "No network interfaces found"
    print(f"   ✅ Found {len(result['interfaces'])} network interfaces")
    
    # Test 6: Convenience functions
    print("\n6. Testing convenience functions:")
    sys_str = get_system_info()
    assert isinstance(sys_str, str) and len(sys_str) > 0, "get_system_info() failed"
    print("   ✅ get_system_info() works")
    
    cpu_str = get_cpu_info()
    assert isinstance(cpu_str, str) and len(cpu_str) > 0, "get_cpu_info() failed"
    print("   ✅ get_cpu_info() works")
    
    mem_str = get_memory_info()
    assert isinstance(mem_str, str) and len(mem_str) > 0, "get_memory_info() failed"
    print("   ✅ get_memory_info() works")
    
    disk_str = get_disk_usage()
    assert isinstance(disk_str, str) and len(disk_str) > 0, "get_disk_usage() failed"
    print("   ✅ get_disk_usage() works")
    
    net_str = get_network_info()
    assert isinstance(net_str, str) and len(net_str) > 0, "get_network_info() failed"
    print("   ✅ get_network_info() works")
    
    print("\n✅ System info tests passed!")


def test_function_registration():
    """Test that functions are registered with FunctionHandler."""
    print("\n" + "=" * 60)
    print("Testing Function Registration")
    print("=" * 60)
    
    handler = FunctionHandler()
    
    # Register web search
    from src.backend.web_search import search_web
    handler.register(
        "search_web",
        search_web,
        "Search the web",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    )
    
    # Register system info functions
    from src.backend.system_info import get_system_info, get_cpu_info
    handler.register(
        "get_system_info",
        get_system_info,
        "Get system information",
        {"type": "object", "properties": {}, "required": []}
    )
    
    handler.register(
        "get_cpu_info",
        get_cpu_info,
        "Get CPU information",
        {"type": "object", "properties": {}, "required": []}
    )
    
    # Test 1: Functions are registered
    print("\n1. Testing function registration:")
    functions = handler.list_functions()
    assert "search_web" in functions, "search_web not registered"
    assert "get_system_info" in functions, "get_system_info not registered"
    assert "get_cpu_info" in functions, "get_cpu_info not registered"
    print(f"   ✅ All functions registered. Total: {len(functions)}")
    
    # Test 2: Function execution
    print("\n2. Testing function execution:")
    result = handler.execute("get_system_info")
    assert result["success"], f"Function execution failed: {result.get('error')}"
    assert "result" in result, "Result missing"
    print("   ✅ get_system_info() executed successfully")
    
    result = handler.execute("get_cpu_info")
    assert result["success"], f"Function execution failed: {result.get('error')}"
    print("   ✅ get_cpu_info() executed successfully")
    
    result = handler.execute("search_web", {"query": "Python"})
    assert result["success"], f"Function execution failed: {result.get('error')}"
    print("   ✅ search_web() executed successfully")
    
    # Test 3: Function definitions for LLM
    print("\n3. Testing function definitions for LLM:")
    definitions = handler.format_functions_for_llm()
    assert len(definitions) > 0, "No function definitions"
    web_search_def = next((d for d in definitions if d["function"]["name"] == "search_web"), None)
    assert web_search_def is not None, "search_web definition missing"
    assert web_search_def["function"]["name"] == "search_web", "Function name incorrect"
    print(f"   ✅ Function definitions formatted correctly. Total: {len(definitions)}")
    
    print("\n✅ Function registration tests passed!")


def test_assistant_core_integration():
    """Test that AssistantCore registers the new functions."""
    print("\n" + "=" * 60)
    print("Testing AssistantCore Integration")
    print("=" * 60)
    
    # Check that the source code includes the new functions
    print("\n1. Checking function registration in AssistantCore source:")
    try:
        # Read the source file directly
        from pathlib import Path
        assistant_core_path = Path(__file__).parent / "src" / "backend" / "assistant_core.py"
        source = assistant_core_path.read_text(encoding='utf-8')
        
        assert "search_web" in source, "search_web not in assistant_core.py"
        assert "get_system_info" in source, "get_system_info not in assistant_core.py"
        assert "get_cpu_info" in source, "get_cpu_info not in assistant_core.py"
        assert "get_memory_info" in source, "get_memory_info not in assistant_core.py"
        assert "get_disk_usage" in source, "get_disk_usage not in assistant_core.py"
        assert "get_network_info" in source, "get_network_info not in assistant_core.py"
        assert "from src.backend.web_search import search_web" in source, "web_search import missing"
        assert "from src.backend.system_info import" in source, "system_info import missing"
        print("   ✅ All new functions are registered in AssistantCore source")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        raise
    
    print("\n✅ AssistantCore integration tests passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing New Functions (Step 3.3)")
    print("=" * 60)
    
    try:
        test_web_search()
        test_system_info()
        test_function_registration()
        test_assistant_core_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nStep 3.3: Additional Functions - Implementation Complete")
        print("New functions available:")
        print("  - search_web(query, max_results=5)")
        print("  - get_system_info()")
        print("  - get_cpu_info()")
        print("  - get_memory_info()")
        print("  - get_disk_usage(path='/')")
        print("  - get_network_info()")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

