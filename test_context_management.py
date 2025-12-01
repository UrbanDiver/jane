"""
Test script for context management system.

Tests:
- Context pruning
- Summarization
- Important message retention
- Performance with long conversations
"""

from src.backend.context_manager import ContextManager


def create_test_messages(count: int) -> list:
    """Create a list of test messages."""
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]
    
    for i in range(count):
        messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i+1}: This is test message number {i+1}"
        })
    
    return messages


def test_context_pruning():
    """Test that context pruning works correctly."""
    print("\n" + "=" * 60)
    print("Test 1: Context Pruning")
    print("=" * 60)
    
    manager = ContextManager(max_messages=10)
    
    # Create 20 messages
    messages = create_test_messages(20)
    
    # Prune context
    pruned = manager.prune_context(messages)
    
    assert len(pruned) <= 10, f"Expected <= 10 messages, got {len(pruned)}"
    assert pruned[0]["role"] == "system", "System message should be first"
    
    print(f"✅ Context pruning works: {len(messages)} -> {len(pruned)} messages")
    print(f"   System message retained: {pruned[0]['role'] == 'system'}")


def test_important_message_retention():
    """Test that important messages are retained."""
    print("\n" + "=" * 60)
    print("Test 2: Important Message Retention")
    print("=" * 60)
    
    manager = ContextManager(max_messages=5)
    
    messages = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "Regular message 1"},
        {"role": "assistant", "content": "Function result: success", "important": True},
        {"role": "user", "content": "Regular message 2"},
        {"role": "assistant", "content": "Regular response 2"},
        {"role": "user", "content": "Regular message 3"},
        {"role": "assistant", "content": "Regular response 3"},
        {"role": "user", "content": "Regular message 4"},
        {"role": "assistant", "content": "Regular response 4"},
    ]
    
    pruned = manager.prune_context(messages)
    
    # Check that important message is retained
    important_found = any(
        "Function result" in msg.get("content", "") for msg in pruned
    )
    
    assert important_found, "Important message should be retained"
    assert pruned[0]["role"] == "system", "System message should be first"
    
    print(f"✅ Important messages retained: {len(pruned)} messages")
    print(f"   Important message found: {important_found}")


def test_is_important():
    """Test important message detection."""
    print("\n" + "=" * 60)
    print("Test 3: Important Message Detection")
    print("=" * 60)
    
    manager = ContextManager()
    
    # System message is important
    assert manager.is_important({"role": "system", "content": "test"}) is True
    
    # Function result is important
    assert manager.is_important({"role": "assistant", "content": "Function result: success"}) is True
    
    # Explicitly marked important
    assert manager.is_important({"role": "user", "content": "test", "important": True}) is True
    
    # Regular message is not important
    assert manager.is_important({"role": "user", "content": "regular message"}) is False
    
    print("✅ Important message detection works correctly")


def test_context_stats():
    """Test context statistics."""
    print("\n" + "=" * 60)
    print("Test 4: Context Statistics")
    print("=" * 60)
    
    manager = ContextManager(max_messages=10)
    
    messages = [
        {"role": "system", "content": "System"},
        {"role": "user", "content": "User 1"},
        {"role": "assistant", "content": "Assistant 1"},
        {"role": "user", "content": "User 2"},
        {"role": "assistant", "content": "Function result", "important": True},
    ]
    
    stats = manager.get_context_stats(messages)
    
    assert stats["total_messages"] == 5
    assert stats["system_messages"] == 1
    assert stats["user_messages"] == 2
    assert stats["assistant_messages"] == 2
    assert stats["important_messages"] == 2  # System + function result
    assert stats["needs_pruning"] is False
    
    print("✅ Context statistics work correctly")
    print(f"   Total: {stats['total_messages']}, "
          f"System: {stats['system_messages']}, "
          f"Important: {stats['important_messages']}")


def test_manage_context():
    """Test full context management."""
    print("\n" + "=" * 60)
    print("Test 5: Full Context Management")
    print("=" * 60)
    
    manager = ContextManager(max_messages=10, summarize_threshold=15)
    
    # Create 20 messages
    messages = create_test_messages(20)
    
    # Manage context (without summarization callback, should just prune)
    managed = manager.manage_context(messages, add_summary=False)
    
    assert len(managed) <= 10, f"Expected <= 10 messages, got {len(managed)}"
    assert managed[0]["role"] == "system", "System message should be first"
    
    print(f"✅ Context management works: {len(messages)} -> {len(managed)} messages")


def test_summarization_callback():
    """Test summarization callback."""
    print("\n" + "=" * 60)
    print("Test 6: Summarization Callback")
    print("=" * 60)
    
    def simple_summarizer(messages):
        """Simple summarizer for testing."""
        return f"Summary of {len(messages)} messages"
    
    manager = ContextManager(
        max_messages=5,
        summarize_threshold=10,
        summarize_callback=simple_summarizer
    )
    
    messages = create_test_messages(15)
    
    # Manage with summarization
    managed = manager.manage_context(messages, add_summary=True)
    
    # Should have summary message
    summary_found = any("summary" in msg.get("content", "").lower() for msg in managed)
    
    print(f"✅ Summarization callback works")
    print(f"   Managed messages: {len(managed)}")
    print(f"   Summary found: {summary_found}")


def test_performance():
    """Test performance with long conversations."""
    print("\n" + "=" * 60)
    print("Test 7: Performance with Long Conversations")
    print("=" * 60)
    
    import time
    
    manager = ContextManager(max_messages=20)
    
    # Create 100 messages
    messages = create_test_messages(100)
    
    start = time.time()
    pruned = manager.prune_context(messages)
    elapsed = time.time() - start
    
    assert len(pruned) <= 20
    assert elapsed < 0.1, f"Pruning took too long: {elapsed:.3f}s"
    
    print(f"✅ Performance is good: {len(messages)} -> {len(pruned)} in {elapsed:.3f}s")


if __name__ == "__main__":
    print("=" * 60)
    print("Context Management Tests")
    print("=" * 60)
    
    try:
        test_context_pruning()
        test_important_message_retention()
        test_is_important()
        test_context_stats()
        test_manage_context()
        test_summarization_callback()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ All Context Management Tests Passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

