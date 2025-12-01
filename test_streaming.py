"""
Test script for streaming responses.

Tests:
- Streaming responses
- Sentence boundary detection
- Early TTS start
- Error handling during streaming
"""

import time
from src.utils.sentence_splitter import SentenceSplitter


def test_sentence_splitter():
    """Test sentence boundary detection."""
    print("\n" + "=" * 60)
    print("Test 1: Sentence Boundary Detection")
    print("=" * 60)
    
    splitter = SentenceSplitter()
    
    # Test streaming text
    text_chunks = [
        "Hello, ",
        "how are ",
        "you? ",
        "I'm doing ",
        "well. ",
        "Thanks for asking!"
    ]
    
    sentences = []
    for chunk in text_chunks:
        new_sentences = splitter.add_text(chunk)
        sentences.extend(new_sentences)
    
    # Flush remaining
    remaining = splitter.flush()
    if remaining:
        sentences.append(remaining)
    
    assert len(sentences) >= 2, f"Expected at least 2 sentences, got {len(sentences)}"
    assert "Hello, how are you?" in sentences[0] or "you?" in sentences[0]
    
    print(f"✅ Sentence detection works: {len(sentences)} sentences detected")
    for i, sent in enumerate(sentences, 1):
        print(f"   Sentence {i}: '{sent[:50]}...'")


def test_sentence_abbreviations():
    """Test that abbreviations don't break sentences."""
    print("\n" + "=" * 60)
    print("Test 2: Abbreviation Handling")
    print("=" * 60)
    
    splitter = SentenceSplitter()
    
    # Text with abbreviation
    text = "Dr. Smith is here. He's a professor."
    
    sentences = splitter.add_text(text)
    
    # Should detect sentence after "here" not after "Dr."
    assert len(sentences) >= 1
    assert "Dr. Smith is here" in sentences[0] or "here" in sentences[0]
    
    print(f"✅ Abbreviations handled correctly: {len(sentences)} sentences")
    print(f"   First sentence: '{sentences[0][:50]}...'")


def test_minimum_length():
    """Test minimum sentence length requirement."""
    print("\n" + "=" * 60)
    print("Test 3: Minimum Sentence Length")
    print("=" * 60)
    
    splitter = SentenceSplitter(min_sentence_length=20)
    
    # Short sentence
    short = "Hi. "
    sentences = splitter.add_text(short)
    
    # Should not be detected as complete (too short)
    assert len(sentences) == 0, "Short sentence should not be detected"
    
    # Longer sentence
    long_sentence = "This is a much longer sentence that should be detected. "
    sentences = splitter.add_text(long_sentence)
    
    assert len(sentences) >= 1, "Long sentence should be detected"
    
    print("✅ Minimum length requirement works")


def test_buffer_management():
    """Test buffer management."""
    print("\n" + "=" * 60)
    print("Test 4: Buffer Management")
    print("=" * 60)
    
    splitter = SentenceSplitter()
    
    # Add incomplete sentence
    sentences1 = splitter.add_text("This is an incomplete")
    remaining = splitter.get_remaining()
    
    assert "incomplete" in remaining
    assert len(sentences1) == 0, "Incomplete sentence should not be detected yet"
    
    # Complete the sentence (needs space after period for detection)
    sentences2 = splitter.add_text(" sentence. ")
    assert len(sentences2) >= 1, "Complete sentence should be detected"
    
    # Flush should clear buffer
    remaining_after = splitter.flush()
    assert splitter.get_remaining() == ""
    
    print("✅ Buffer management works correctly")


def test_streaming_simulation():
    """Simulate streaming response processing."""
    print("\n" + "=" * 60)
    print("Test 5: Streaming Simulation")
    print("=" * 60)
    
    splitter = SentenceSplitter()
    
    # Simulate streaming tokens
    response_text = "Hello! How are you? I'm doing well. Thanks for asking!"
    tokens = list(response_text)  # Character by character
    
    sentences_found = []
    for token in tokens:
        new_sentences = splitter.add_text(token)
        sentences_found.extend(new_sentences)
    
    # Flush remaining
    remaining = splitter.flush()
    if remaining:
        sentences_found.append(remaining)
    
    assert len(sentences_found) >= 2
    
    print(f"✅ Streaming simulation works: {len(sentences_found)} sentences found")
    print(f"   Total characters: {len(response_text)}")


def test_reset():
    """Test reset functionality."""
    print("\n" + "=" * 60)
    print("Test 6: Reset Functionality")
    print("=" * 60)
    
    splitter = SentenceSplitter()
    
    # Add incomplete text (no sentence ending)
    splitter.add_text("Some incomplete text")
    assert splitter.get_remaining() != ""
    
    splitter.reset()
    assert splitter.get_remaining() == ""
    
    print("✅ Reset functionality works")


def test_performance():
    """Test performance with long text."""
    print("\n" + "=" * 60)
    print("Test 7: Performance")
    print("=" * 60)
    
    import time
    
    splitter = SentenceSplitter()
    
    # Long text
    long_text = ". ".join([f"Sentence {i}" for i in range(100)]) + "."
    
    start = time.time()
    sentences = splitter.add_text(long_text)
    elapsed = time.time() - start
    
    assert len(sentences) > 0
    assert elapsed < 0.1, f"Processing took too long: {elapsed:.3f}s"
    
    print(f"✅ Performance is good: {len(sentences)} sentences in {elapsed:.3f}s")


if __name__ == "__main__":
    print("=" * 60)
    print("Streaming Response Tests")
    print("=" * 60)
    
    try:
        test_sentence_splitter()
        test_sentence_abbreviations()
        test_minimum_length()
        test_buffer_management()
        test_streaming_simulation()
        test_reset()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ All Streaming Response Tests Passed!")
        print("=" * 60)
        print("\nNote: Full streaming integration requires LLM with stream_chat support.")
        print("Sentence boundary detection is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

