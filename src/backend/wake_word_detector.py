"""
Wake Word Detector

Provides wake word detection for energy-efficient listening.
Can use keyword matching or integrate with wake word detection libraries.
"""

from typing import Optional, Callable, List
from threading import Thread, Event
import time
from src.utils.logger import get_logger, log_performance
from src.utils.error_handler import handle_error


class WakeWordDetector:
    """
    Wake word detector for continuous listening.
    
    Supports:
    - Simple keyword-based detection (using STT)
    - Configurable wake words
    - Energy-efficient continuous listening
    """
    
    def __init__(
        self,
        wake_words: Optional[List[str]] = None,
        detection_method: str = "keyword",
        sensitivity: float = 0.5
    ):
        """
        Initialize the wake word detector.
        
        Args:
            wake_words: List of wake words to detect (default: ["jane", "hey jane"])
            detection_method: Detection method ("keyword" or "library")
            sensitivity: Detection sensitivity (0.0 to 1.0)
        """
        self.logger = get_logger(__name__)
        self.wake_words = wake_words or ["jane", "hey jane"]
        self.detection_method = detection_method
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.is_listening = False
        self.listening_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.callback: Optional[Callable] = None
        self.stt_engine = None  # Will be set when integrated
        
        # Normalize wake words to lowercase
        self.wake_words = [w.lower() for w in self.wake_words]
        
        self.logger.info(f"WakeWordDetector initialized with wake words: {self.wake_words}")
    
    def set_stt_engine(self, stt_engine):
        """
        Set the STT engine for keyword-based detection.
        
        Args:
            stt_engine: STT engine instance
        """
        self.stt_engine = stt_engine
        self.logger.debug("STT engine set for wake word detection")
    
    def detect_wake_word(self, text: str) -> bool:
        """
        Detect if wake word is present in text.
        
        Args:
            text: Text to check for wake word
            
        Returns:
            True if wake word detected, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Check if any wake word is in the text
        for wake_word in self.wake_words:
            # Check if wake word is at the start
            if text_lower.startswith(wake_word):
                # Check if it's followed by space, comma, or end of string
                if len(text_lower) == len(wake_word) or text_lower[len(wake_word)] in [' ', ',', '.', '!', '?']:
                    self.logger.info(f"Wake word detected: '{wake_word}'")
                    return True
            
            # Check if wake word appears as a whole word (with spaces around it)
            pattern = f" {wake_word} "
            if pattern in text_lower:
                self.logger.info(f"Wake word detected: '{wake_word}'")
                return True
            
            # Check if wake word is at the end
            if text_lower.endswith(f" {wake_word}") or text_lower.endswith(f",{wake_word}"):
                self.logger.info(f"Wake word detected: '{wake_word}'")
                return True
        
        return False
    
    def extract_command(self, text: str) -> str:
        """
        Extract command text after wake word.
        
        Args:
            text: Text containing wake word and command
            
        Returns:
            Command text without wake word
        """
        if not text:
            return ""
        
        text_lower = text.lower()
        
        # Find the longest matching wake word
        matched_wake_word = None
        for wake_word in sorted(self.wake_words, key=len, reverse=True):
            # Check if wake word is at the start
            if text_lower.startswith(wake_word):
                # Check if it's followed by space, comma, or end of string
                if len(text_lower) == len(wake_word) or text_lower[len(wake_word)] in [' ', ',', '.', '!', '?']:
                    matched_wake_word = wake_word
                    break
            # Check if wake word appears as a whole word
            elif f" {wake_word} " in text_lower:
                matched_wake_word = wake_word
                break
        
        if not matched_wake_word:
            return text.strip()
        
        # Remove wake word from text
        # Try to remove from start first
        if text_lower.startswith(matched_wake_word):
            command = text[len(matched_wake_word):].strip()
            # Remove leading punctuation
            command = command.lstrip(',.!? ')
        else:
            # Remove from anywhere in the text (whole word only)
            # Find the position of the wake word
            pos = text_lower.find(f" {matched_wake_word} ")
            if pos != -1:
                # Remove wake word and surrounding spaces
                before = text[:pos].strip()
                after = text[pos + len(f" {matched_wake_word} "):].strip()
                command = f"{before} {after}".strip()
            else:
                command = text.strip()
        
        # Clean up extra spaces
        command = " ".join(command.split())
        
        return command
    
    @log_performance()
    def listen_for_wake_word(
        self,
        callback: Callable,
        duration: float = 30.0,
        check_interval: float = 1.0
    ) -> bool:
        """
        Listen for wake word and call callback when detected.
        
        Args:
            callback: Function to call when wake word is detected
            duration: Maximum duration to listen in seconds (0 = infinite)
            check_interval: Interval between checks in seconds
            
        Returns:
            True if wake word was detected, False otherwise
        """
        if not self.stt_engine:
            self.logger.error("STT engine not set. Cannot listen for wake word.")
            return False
        
        self.callback = callback
        self.logger.info(f"Listening for wake word(s): {self.wake_words}")
        
        start_time = time.time()
        detected = False
        
        try:
            while not self.stop_event.is_set():
                # Check duration
                if duration > 0 and (time.time() - start_time) >= duration:
                    self.logger.debug("Wake word listening timeout")
                    break
                
                # Listen for a short duration
                try:
                    result = self.stt_engine.listen_and_transcribe(duration=check_interval)
                    text = result.get('text', '').strip()
                    
                    if text:
                        self.logger.debug(f"Heard: '{text}'")
                        
                        # Check for wake word
                        if self.detect_wake_word(text):
                            detected = True
                            command = self.extract_command(text)
                            
                            # Call callback with command
                            if self.callback:
                                self.callback(command)
                            
                            break
                
                except Exception as e:
                    error_info = handle_error(e, logger=self.logger)
                    self.logger.debug(f"Error during wake word listening: {error_info['message']}")
                    continue
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            self.logger.info("Wake word listening interrupted")
        finally:
            self.stop_event.clear()
        
        return detected
    
    def start_continuous_listening(
        self,
        callback: Callable,
        check_interval: float = 1.0
    ) -> None:
        """
        Start continuous listening for wake word in background thread.
        
        Args:
            callback: Function to call when wake word is detected
            check_interval: Interval between checks in seconds
        """
        if self.is_listening:
            self.logger.warning("Already listening for wake word")
            return
        
        self.is_listening = True
        self.stop_event.clear()
        self.callback = callback
        
        def listen_loop():
            """Background listening loop."""
            self.logger.info("Starting continuous wake word listening...")
            while self.is_listening and not self.stop_event.is_set():
                detected = self.listen_for_wake_word(
                    callback=self.callback,
                    duration=check_interval * 2,  # Listen for 2 intervals
                    check_interval=check_interval
                )
                if detected:
                    # Continue listening after wake word
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)
        
        self.listening_thread = Thread(target=listen_loop, daemon=True)
        self.listening_thread.start()
        self.logger.info("Continuous wake word listening started")
    
    def stop_continuous_listening(self) -> None:
        """Stop continuous listening for wake word."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.stop_event.set()
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        
        self.logger.info("Continuous wake word listening stopped")
    
    def add_wake_word(self, wake_word: str) -> None:
        """
        Add a wake word to the detection list.
        
        Args:
            wake_word: Wake word to add
        """
        wake_word_lower = wake_word.lower()
        if wake_word_lower not in self.wake_words:
            self.wake_words.append(wake_word_lower)
            self.logger.info(f"Added wake word: '{wake_word}'")
    
    def remove_wake_word(self, wake_word: str) -> None:
        """
        Remove a wake word from the detection list.
        
        Args:
            wake_word: Wake word to remove
        """
        wake_word_lower = wake_word.lower()
        if wake_word_lower in self.wake_words:
            self.wake_words.remove(wake_word_lower)
            self.logger.info(f"Removed wake word: '{wake_word}'")
    
    def get_wake_words(self) -> List[str]:
        """
        Get list of configured wake words.
        
        Returns:
            List of wake words
        """
        return self.wake_words.copy()


if __name__ == "__main__":
    # Test the wake word detector
    print("=" * 60)
    print("Testing Wake Word Detector")
    print("=" * 60)
    
    detector = WakeWordDetector(wake_words=["jane", "hey jane"])
    
    # Test 1: Wake word detection
    print("\n1. Testing wake word detection:")
    test_cases = [
        ("jane", True),
        ("hey jane", True),
        ("jane, what time is it?", True),
        ("hello jane", True),
        ("hello", False),
        ("janet", False),
        ("", False)
    ]
    
    for text, expected in test_cases:
        result = detector.detect_wake_word(text)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{text}' -> {result} (expected {expected})")
        assert result == expected, f"Failed for '{text}'"
    
    # Test 2: Command extraction
    print("\n2. Testing command extraction:")
    test_cases = [
        ("jane", ""),
        ("jane what time is it", "what time is it"),
        ("hey jane open calculator", "open calculator"),
        ("jane, tell me a joke", "tell me a joke")
    ]
    
    for text, expected in test_cases:
        result = detector.extract_command(text)
        print(f"   ✅ '{text}' -> '{result}' (expected '{expected}')")
        assert result == expected or (not expected and not result), f"Failed for '{text}'"
    
    # Test 3: Wake word management
    print("\n3. Testing wake word management:")
    detector.add_wake_word("computer")
    assert "computer" in detector.get_wake_words(), "Wake word not added"
    print("   ✅ Wake word added")
    
    detector.remove_wake_word("computer")
    assert "computer" not in detector.get_wake_words(), "Wake word not removed"
    print("   ✅ Wake word removed")
    
    print("\n" + "=" * 60)
    print("✅ Wake Word Detector test complete!")
    print("=" * 60)

