"""
Sentence boundary detection for streaming text.

Helps identify complete sentences in streaming text for early TTS synthesis.
"""

import re
from typing import List, Tuple


class SentenceSplitter:
    """
    Detects sentence boundaries in streaming text.
    
    Buffers text until complete sentences are detected, allowing
    for early TTS synthesis of complete sentences.
    """
    
    # Sentence ending patterns
    SENTENCE_ENDINGS = re.compile(r'[.!?]+\s+')
    
    # Abbreviations that shouldn't end sentences
    ABBREVIATIONS = {
        'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'sr.', 'jr.',
        'vs.', 'etc.', 'e.g.', 'i.e.', 'a.m.', 'p.m.',
        'inc.', 'ltd.', 'corp.', 'st.', 'ave.', 'blvd.',
    }
    
    def __init__(self, min_sentence_length: int = 10):
        """
        Initialize sentence splitter.
        
        Args:
            min_sentence_length: Minimum characters before considering a sentence complete
        """
        self.min_sentence_length = min_sentence_length
        self.buffer = ""
    
    def add_text(self, text: str) -> List[str]:
        """
        Add text and return complete sentences.
        
        Args:
            text: New text to add
        
        Returns:
            List of complete sentences (may be empty if no complete sentences yet)
        """
        self.buffer += text
        
        sentences = []
        
        # Find all potential sentence endings
        matches = list(self.SENTENCE_ENDINGS.finditer(self.buffer))
        
        for match in matches:
            end_pos = match.end()
            potential_sentence = self.buffer[:end_pos].strip()
            
            # Check if it's a real sentence (not an abbreviation)
            if self._is_complete_sentence(potential_sentence):
                sentences.append(potential_sentence)
                self.buffer = self.buffer[end_pos:]
                break  # Process one sentence at a time
        
        return sentences
    
    def _is_complete_sentence(self, text: str) -> bool:
        """
        Check if text is a complete sentence.
        
        Args:
            text: Text to check
        
        Returns:
            True if text is a complete sentence
        """
        if len(text) < self.min_sentence_length:
            return False
        
        # Check if it ends with an abbreviation
        words = text.lower().split()
        if words:
            last_word = words[-1].rstrip('.,!?;:')
            if last_word in self.ABBREVIATIONS:
                return False
        
        return True
    
    def get_remaining(self) -> str:
        """
        Get remaining buffered text that hasn't formed a complete sentence.
        
        Returns:
            Remaining text in buffer
        """
        return self.buffer
    
    def flush(self) -> str:
        """
        Flush buffer and return all remaining text.
        
        Returns:
            All remaining text in buffer
        """
        remaining = self.buffer
        self.buffer = ""
        return remaining.strip() if remaining.strip() else None
    
    def reset(self):
        """Reset the buffer."""
        self.buffer = ""

