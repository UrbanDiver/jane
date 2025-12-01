"""
Conversation State Management

Tracks conversation topics, user preferences, and maintains state
across sessions for better context awareness.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from collections import defaultdict
from src.utils.logger import get_logger


class ConversationState:
    """
    Manages conversation state including topics, preferences, and context.
    """
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize conversation state.
        
        Args:
            state_file: Optional path to state file for persistence
        """
        self.logger = get_logger(__name__)
        self.state_file = state_file or "data/conversation_state.json"
        
        # Topic tracking
        self.topics: Dict[str, int] = defaultdict(int)  # topic -> count
        self.recent_topics: List[str] = []  # Most recent topics
        
        # User preferences
        self.preferences: Dict[str, any] = {}
        
        # Conversation metadata
        self.session_count: int = 0
        self.total_messages: int = 0
        self.last_activity: Optional[str] = None
        
        # Context keywords (important terms to remember)
        self.context_keywords: Set[str] = set()
        
        # Load existing state if available
        self.load()
    
    def add_message(self, role: str, content: str):
        """
        Add a message and extract topics/preferences.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.total_messages += 1
        self.last_activity = datetime.now().isoformat()
        
        if role == "user":
            # Extract topics from user messages
            topics = self._extract_topics(content)
            for topic in topics:
                self.topics[topic] += 1
                if topic not in self.recent_topics:
                    self.recent_topics.append(topic)
                # Keep only last 20 topics
                if len(self.recent_topics) > 20:
                    self.recent_topics.pop(0)
            
            # Extract preferences (simple pattern matching for now)
            self._extract_preferences(content)
            
            # Extract context keywords
            keywords = self._extract_keywords(content)
            self.context_keywords.update(keywords)
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract topics from text (simple keyword-based approach).
        
        Args:
            text: Text to analyze
        
        Returns:
            List of topic strings
        """
        # Simple keyword extraction (can be enhanced with NLP)
        text_lower = text.lower()
        topics = []
        
        # Common topic keywords
        topic_keywords = {
            "file": ["file", "files", "document", "documents"],
            "application": ["app", "application", "program", "software"],
            "system": ["system", "computer", "pc", "machine"],
            "network": ["network", "internet", "connection", "wifi"],
            "time": ["time", "clock", "schedule", "calendar"],
            "email": ["email", "mail", "message", "inbox"],
            "search": ["search", "find", "look", "query"],
            "code": ["code", "programming", "script", "function"],
            "music": ["music", "song", "audio", "playlist"],
            "video": ["video", "movie", "film", "youtube"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_preferences(self, text: str):
        """
        Extract user preferences from text.
        
        Args:
            text: Text to analyze
        """
        text_lower = text.lower()
        
        # Extract preference patterns
        if "prefer" in text_lower or "like" in text_lower or "favorite" in text_lower:
            # Simple extraction - can be enhanced
            if "dark mode" in text_lower or "dark theme" in text_lower:
                self.preferences["theme"] = "dark"
            elif "light mode" in text_lower or "light theme" in text_lower:
                self.preferences["theme"] = "light"
            
            if "quiet" in text_lower or "silent" in text_lower:
                self.preferences["notifications"] = "quiet"
            elif "loud" in text_lower or "notify" in text_lower:
                self.preferences["notifications"] = "loud"
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Set of keyword strings
        """
        # Simple keyword extraction (can be enhanced)
        words = text.lower().split()
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"}
        
        keywords = {word for word in words if len(word) > 3 and word not in stop_words}
        return keywords
    
    def get_topics(self, limit: int = 10) -> List[tuple]:
        """
        Get most frequent topics.
        
        Args:
            limit: Maximum number of topics to return
        
        Returns:
            List of (topic, count) tuples sorted by frequency
        """
        sorted_topics = sorted(self.topics.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:limit]
    
    def get_recent_topics(self, limit: int = 5) -> List[str]:
        """
        Get most recent topics.
        
        Args:
            limit: Maximum number of topics to return
        
        Returns:
            List of recent topic strings
        """
        return self.recent_topics[-limit:]
    
    def get_preferences(self) -> Dict[str, any]:
        """
        Get user preferences.
        
        Returns:
            Dictionary of preferences
        """
        return self.preferences.copy()
    
    def set_preference(self, key: str, value: any):
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value
        self.logger.debug(f"Set preference: {key} = {value}")
    
    def get_context_summary(self) -> str:
        """
        Get a summary of conversation context.
        
        Returns:
            Context summary string
        """
        parts = []
        
        if self.recent_topics:
            parts.append(f"Recent topics: {', '.join(self.recent_topics[-5:])}")
        
        if self.preferences:
            pref_str = ", ".join([f"{k}={v}" for k, v in self.preferences.items()])
            parts.append(f"Preferences: {pref_str}")
        
        if self.context_keywords:
            keywords_str = ", ".join(list(self.context_keywords)[:10])
            parts.append(f"Keywords: {keywords_str}")
        
        return " | ".join(parts) if parts else "No context available"
    
    def save(self):
        """Save state to file."""
        try:
            state_dir = Path(self.state_file).parent
            state_dir.mkdir(parents=True, exist_ok=True)
            
            state_data = {
                "topics": dict(self.topics),
                "recent_topics": self.recent_topics,
                "preferences": self.preferences,
                "session_count": self.session_count,
                "total_messages": self.total_messages,
                "last_activity": self.last_activity,
                "context_keywords": list(self.context_keywords)
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.debug(f"Saved conversation state to {self.state_file}")
        except Exception as e:
            self.logger.warning(f"Failed to save conversation state: {e}")
    
    def load(self):
        """Load state from file."""
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                self.topics = defaultdict(int, state_data.get("topics", {}))
                self.recent_topics = state_data.get("recent_topics", [])
                self.preferences = state_data.get("preferences", {})
                self.session_count = state_data.get("session_count", 0)
                self.total_messages = state_data.get("total_messages", 0)
                self.last_activity = state_data.get("last_activity")
                self.context_keywords = set(state_data.get("context_keywords", []))
                
                self.logger.debug(f"Loaded conversation state from {self.state_file}")
        except Exception as e:
            self.logger.warning(f"Failed to load conversation state: {e}")
    
    def start_session(self):
        """Mark the start of a new session."""
        self.session_count += 1
        self.logger.debug(f"Started session #{self.session_count}")
    
    def get_stats(self) -> Dict:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "session_count": self.session_count,
            "total_messages": self.total_messages,
            "unique_topics": len(self.topics),
            "preferences_count": len(self.preferences),
            "context_keywords_count": len(self.context_keywords),
            "last_activity": self.last_activity,
            "top_topics": self.get_topics(5)
        }

