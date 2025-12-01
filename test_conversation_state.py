"""
Test script for conversation state management.

Tests:
- Topic tracking
- Preference storage
- State persistence
- Conversation resumption
"""

import json
import os
from pathlib import Path
from src.backend.conversation_state import ConversationState


def test_topic_tracking():
    """Test topic extraction and tracking."""
    print("\n" + "=" * 60)
    print("Test 1: Topic Tracking")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    state.topics.clear()  # Clear for test
    state.recent_topics.clear()
    
    # Add messages with different topics
    state.add_message("user", "I need to search for files on my computer")
    state.add_message("user", "Can you open an application for me?")
    state.add_message("user", "What time is it?")
    
    topics = state.get_topics(5)
    assert len(topics) > 0, "Should have extracted topics"
    
    recent = state.get_recent_topics(3)
    assert len(recent) > 0, "Should have recent topics"
    
    print(f"✅ Topic tracking works: {len(topics)} topics found")
    print(f"   Top topics: {[t[0] for t in topics[:3]]}")
    print(f"   Recent topics: {recent}")


def test_preference_tracking():
    """Test preference extraction and storage."""
    print("\n" + "=" * 60)
    print("Test 2: Preference Tracking")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    state.preferences.clear()  # Clear for test
    
    # Add messages with preferences
    state.add_message("user", "I prefer dark mode")
    state.add_message("user", "I like quiet notifications")
    
    preferences = state.get_preferences()
    assert len(preferences) > 0, "Should have extracted preferences"
    
    # Test setting preferences directly
    state.set_preference("language", "en")
    preferences = state.get_preferences()
    assert "language" in preferences, "Should have language preference"
    
    print(f"✅ Preference tracking works: {len(preferences)} preferences")
    print(f"   Preferences: {preferences}")


def test_state_persistence():
    """Test state saving and loading."""
    print("\n" + "=" * 60)
    print("Test 3: State Persistence")
    print("=" * 60)
    
    test_file = "data/test_state_persistence.json"
    
    # Create state and add data
    state1 = ConversationState(state_file=test_file)
    state1.add_message("user", "Test message about files")
    state1.set_preference("test_pref", "test_value")
    state1.save()
    
    # Create new state instance and load
    state2 = ConversationState(state_file=test_file)
    
    # Check that data was loaded
    assert len(state2.topics) > 0, "Topics should be loaded"
    assert "test_pref" in state2.preferences, "Preferences should be loaded"
    assert state2.preferences["test_pref"] == "test_value", "Preference value should match"
    
    print("✅ State persistence works")
    print(f"   Topics loaded: {len(state2.topics)}")
    print(f"   Preferences loaded: {len(state2.preferences)}")
    
    # Cleanup
    if Path(test_file).exists():
        Path(test_file).unlink()


def test_context_summary():
    """Test context summary generation."""
    print("\n" + "=" * 60)
    print("Test 4: Context Summary")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    state.topics.clear()
    state.recent_topics.clear()
    state.preferences.clear()
    state.context_keywords.clear()
    
    state.add_message("user", "I need to search for files")
    state.add_message("user", "I prefer dark mode")
    
    summary = state.get_context_summary()
    assert len(summary) > 0, "Should have context summary"
    
    print(f"✅ Context summary works: {summary}")


def test_session_management():
    """Test session counting."""
    print("\n" + "=" * 60)
    print("Test 5: Session Management")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    initial_count = state.session_count
    
    state.start_session()
    assert state.session_count == initial_count + 1, "Session count should increment"
    
    print(f"✅ Session management works: session #{state.session_count}")


def test_statistics():
    """Test statistics generation."""
    print("\n" + "=" * 60)
    print("Test 6: Statistics")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    state.add_message("user", "Test message")
    state.add_message("assistant", "Test response")
    
    stats = state.get_stats()
    
    assert "session_count" in stats
    assert "total_messages" in stats
    assert "unique_topics" in stats
    assert stats["total_messages"] >= 2
    
    print("✅ Statistics work")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Unique topics: {stats['unique_topics']}")


def test_keyword_extraction():
    """Test keyword extraction."""
    print("\n" + "=" * 60)
    print("Test 7: Keyword Extraction")
    print("=" * 60)
    
    state = ConversationState(state_file="data/test_state.json")
    state.context_keywords.clear()
    
    state.add_message("user", "I need to work on my Python project")
    state.add_message("user", "The database connection is failing")
    
    assert len(state.context_keywords) > 0, "Should have extracted keywords"
    
    print(f"✅ Keyword extraction works: {len(state.context_keywords)} keywords")
    print(f"   Sample keywords: {list(state.context_keywords)[:5]}")


if __name__ == "__main__":
    print("=" * 60)
    print("Conversation State Management Tests")
    print("=" * 60)
    
    try:
        test_topic_tracking()
        test_preference_tracking()
        test_state_persistence()
        test_context_summary()
        test_session_management()
        test_statistics()
        test_keyword_extraction()
        
        print("\n" + "=" * 60)
        print("✅ All Conversation State Tests Passed!")
        print("=" * 60)
        
        # Cleanup test files
        test_files = ["data/test_state.json", "data/test_state_persistence.json"]
        for test_file in test_files:
            if Path(test_file).exists():
                Path(test_file).unlink()
                print(f"   Cleaned up: {test_file}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

