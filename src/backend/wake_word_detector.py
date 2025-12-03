"""
Wake Word Detector

Provides wake word detection for energy-efficient listening.
Can use keyword matching or integrate with wake word detection libraries.
"""

from typing import Optional, Callable, List
from threading import Thread, Event
import threading
import time
import re
from difflib import SequenceMatcher
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
        self.logger.info(f"Detection sensitivity: {self.sensitivity}")
        
        # Common transcription variations to help with detection
        self.transcription_variations = {
            "jane": ["jane", "jain", "jayne", "jane.", "jane,", "jane!", "jane?"],
            "hey jane": ["hey jane", "hey jain", "hey jayne", "hey jane.", "hey jane,", "hey jane!"]
        }
    
    def set_stt_engine(self, stt_engine):
        """
        Set the STT engine for keyword-based detection.
        
        Args:
            stt_engine: STT engine instance
        """
        self.stt_engine = stt_engine
        self.logger.debug("STT engine set for wake word detection")
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def detect_wake_word(self, text: str) -> bool:
        """
        Detect if wake word is present in text.
        
        Uses multiple strategies:
        1. Exact word boundary matching
        2. Fuzzy matching for common transcription errors
        3. Partial matching for wake words within longer phrases
        
        Args:
            text: Text to check for wake word
            
        Returns:
            True if wake word detected, False otherwise
        """
        if not text:
            return False
        
        # Normalize text: remove punctuation, convert to lowercase, normalize whitespace
        text_normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        text_normalized = ' '.join(text_normalized.split())  # Normalize whitespace
        
        # Check if any wake word is in the text
        for wake_word in self.wake_words:
            wake_word_lower = wake_word.lower()
            
            # Strategy 1: Exact word boundary matching (most reliable)
            # Check if wake word is at the start
            if text_normalized.startswith(wake_word_lower):
                # Check if it's followed by space or end of string
                if len(text_normalized) == len(wake_word_lower) or text_normalized[len(wake_word_lower)] == ' ':
                    self.logger.info(f"Wake word detected (start): '{wake_word}' in '{text}'")
                    return True
            
            # Check if wake word appears as a whole word (with word boundaries)
            # Use word boundary regex pattern
            pattern = r'\b' + re.escape(wake_word_lower) + r'\b'
            if re.search(pattern, text_normalized):
                self.logger.info(f"Wake word detected (word boundary): '{wake_word}' in '{text}'")
                return True
            
            # Strategy 2: Fuzzy matching for common transcription errors
            # Split text into words and check similarity
            words = text_normalized.split()
            for word in words:
                # Check if word is similar to wake word (for single-word wake words)
                if len(wake_word_lower.split()) == 1:
                    similarity = self._similarity(word, wake_word_lower)
                    # Use sensitivity to adjust threshold (lower sensitivity = more lenient)
                    # Lower threshold for better detection (0.70 to 0.55)
                    threshold = 0.70 - (self.sensitivity * 0.15)  # Range: 0.70 to 0.55
                    if similarity >= threshold:
                        self.logger.info(f"Wake word detected (fuzzy): '{wake_word}' matched '{word}' (similarity: {similarity:.2f}, threshold: {threshold:.2f}) in '{text}'")
                        return True
            
            # Strategy 3: Check for multi-word wake words (e.g., "hey jane")
            if len(wake_word_lower.split()) > 1:
                # Check if all words of wake word appear in sequence
                wake_words_list = wake_word_lower.split()
                text_words = text_normalized.split()
                
                # Try to find the sequence of wake word parts
                for i in range(len(text_words) - len(wake_words_list) + 1):
                    # Check if sequence matches
                    sequence = ' '.join(text_words[i:i+len(wake_words_list)])
                    similarity = self._similarity(sequence, wake_word_lower)
                    # Use sensitivity to adjust threshold (lower sensitivity = more lenient)
                    threshold = 0.80 - (self.sensitivity * 0.15)  # Range: 0.80 to 0.65
                    if similarity >= threshold:
                        self.logger.info(f"Wake word detected (multi-word fuzzy): '{wake_word}' matched '{sequence}' (similarity: {similarity:.2f}, threshold: {threshold:.2f}) in '{text}'")
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
                
                # Listen for a short duration (use slightly longer duration for better capture)
                try:
                    # Use longer duration to capture wake word better (wake words are short, need time to speak)
                    listen_duration = max(check_interval * 1.5, 2.0)  # At least 2 seconds, or 1.5x check_interval
                    result = self.stt_engine.listen_and_transcribe(duration=listen_duration)
                    text = result.get('text', '').strip()
                    
                    # Log all transcription attempts for debugging (use info level for visibility)
                    if text:
                        self.logger.info(f"🔍 Listening... Transcribed: '{text}'")
                        # Check if text contains any part of wake words (for debugging)
                        for wake_word in self.wake_words:
                            if wake_word.lower() in text.lower():
                                self.logger.debug(f"  → Contains wake word part '{wake_word}' but didn't match detection logic")
                    else:
                        # Only log empty transcriptions at debug level to reduce noise
                        self.logger.debug("🔍 Listening... No speech detected in this interval")
                    
                    if text:
                        # Check for wake word
                        if self.detect_wake_word(text):
                            detected = True
                            command = self.extract_command(text)
                            
                            # Call callback with command (wrap in try-except to prevent breaking the loop)
                            if self.callback:
                                try:
                                    self.callback(command)
                                except Exception as callback_error:
                                    error_info = handle_error(callback_error, logger=self.logger)
                                    self.logger.error(f"Error in wake word callback: {error_info['message']}")
                            
                            break
                
                except Exception as e:
                    error_info = handle_error(e, logger=self.logger)
                    self.logger.debug(f"Error during wake word listening: {error_info['message']}")
                    continue
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            self.logger.info("Wake word listening interrupted")
        # Don't clear stop_event here - it's managed by start_continuous_listening/stop_continuous_listening
        
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
            try:
                while self.is_listening and not self.stop_event.is_set():
                    try:
                        detected = self.listen_for_wake_word(
                            callback=self.callback,
                            duration=check_interval * 2,  # Listen for 2 intervals
                            check_interval=check_interval
                        )
                        if detected:
                            # Continue listening after wake word
                            self.logger.debug("Wake word detected, continuing to listen...")
                            time.sleep(0.5)
                        else:
                            time.sleep(0.1)
                    except Exception as e:
                        error_info = handle_error(e, logger=self.logger)
                        self.logger.error(f"Error in continuous listening loop: {error_info['message']}")
                        # Continue listening even if there's an error
                        time.sleep(0.5)
            except Exception as e:
                error_info = handle_error(e, logger=self.logger)
                self.logger.error(f"Fatal error in continuous listening loop: {error_info['message']}")
            finally:
                self.logger.info("Continuous wake word listening loop ended")
                self.is_listening = False
        
        self.listening_thread = Thread(target=listen_loop, daemon=True)
        self.listening_thread.start()
        self.logger.info("Continuous wake word listening started")
    
    def stop_continuous_listening(self) -> None:
        """Stop continuous listening for wake word."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.stop_event.set()
        
        # Don't try to join if we're in the same thread (check thread identity)
        if self.listening_thread and self.listening_thread.is_alive():
            current_thread = threading.current_thread()
            if self.listening_thread != current_thread:
                # Only join if we're in a different thread
                self.listening_thread.join(timeout=2.0)
            else:
                # We're in the listening thread itself, just set flags and let it exit naturally
                self.logger.debug("Stopping wake word detection from within listening thread")
        
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

