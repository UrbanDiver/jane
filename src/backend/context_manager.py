"""
Context Manager for Conversation History

Manages conversation history with smart pruning, summarization, and
important message retention to prevent unbounded memory growth.
"""

from typing import List, Dict, Optional, Callable
from src.utils.logger import get_logger


class ContextManager:
    """
    Manages conversation context with pruning and summarization.
    
    Prevents conversation history from growing unbounded while
    maintaining important context.
    """
    
    def __init__(
        self,
        max_messages: int = 20,
        summarize_threshold: int = 30,
        summarize_callback: Optional[Callable] = None
    ):
        """
        Initialize context manager.
        
        Args:
            max_messages: Maximum number of messages to keep in active context
            summarize_threshold: Number of messages before summarization is triggered
            summarize_callback: Optional callback function for summarization.
                               Should accept (messages: List[Dict]) -> str
        """
        self.max_messages = max_messages
        self.summarize_threshold = summarize_threshold
        self.summarize_callback = summarize_callback
        self.logger = get_logger(__name__)
        
        # Track important message indices
        self.important_indices = set()
        
        self.logger.debug(f"ContextManager initialized: max_messages={max_messages}, "
                         f"summarize_threshold={summarize_threshold}")
    
    def is_important(self, message: Dict[str, str]) -> bool:
        """
        Determine if a message is important and should be retained.
        
        Important messages include:
        - System messages
        - Messages with function call results
        - Messages marked as important
        
        Args:
            message: Message dictionary with 'role' and 'content'
        
        Returns:
            True if message is important
        """
        role = message.get("role", "")
        content = message.get("content", "")
        
        # System messages are always important
        if role == "system":
            return True
        
        # Messages with function results are important
        if "function" in content.lower() or "result" in content.lower():
            return True
        
        # Check for explicit importance marker
        if message.get("important", False):
            return True
        
        return False
    
    def prune_context(
        self,
        messages: List[Dict[str, str]],
        keep_system: bool = True,
        keep_important: bool = True
    ) -> List[Dict[str, str]]:
        """
        Prune conversation history to fit within max_messages.
        
        Args:
            messages: List of message dictionaries
            keep_system: Whether to always keep system message
            keep_important: Whether to keep important messages
        
        Returns:
            Pruned list of messages
        """
        if len(messages) <= self.max_messages:
            return messages
        
        self.logger.debug(f"Pruning context: {len(messages)} -> {self.max_messages} messages")
        
        # Separate messages by type
        system_messages = []
        important_messages = []
        regular_messages = []
        
        for i, msg in enumerate(messages):
            if msg.get("role") == "system":
                system_messages.append((i, msg))
            elif self.is_important(msg):
                important_messages.append((i, msg))
            else:
                regular_messages.append((i, msg))
        
        # Build pruned list
        pruned = []
        
        # Always keep system message(s) at the start
        if keep_system:
            pruned.extend([msg for _, msg in system_messages])
        
        # Calculate how many slots remain
        remaining_slots = self.max_messages - len(pruned)
        
        # Keep important messages (up to limit)
        if keep_important and important_messages:
            # Keep most recent important messages
            important_to_keep = important_messages[-min(len(important_messages), remaining_slots // 2):]
            pruned.extend([msg for _, msg in important_to_keep])
            remaining_slots -= len(important_to_keep)
        
        # Fill remaining slots with most recent regular messages
        if regular_messages and remaining_slots > 0:
            regular_to_keep = regular_messages[-remaining_slots:]
            pruned.extend([msg for _, msg in regular_to_keep])
        
        self.logger.info(f"Pruned context: {len(messages)} -> {len(pruned)} messages "
                        f"({len(system_messages)} system, {len(important_messages)} important, "
                        f"{len(regular_messages)} regular)")
        
        return pruned
    
    def summarize_context(
        self,
        messages: List[Dict[str, str]],
        summary_role: str = "system"
    ) -> Optional[str]:
        """
        Summarize old conversation context.
        
        Args:
            messages: List of messages to summarize
            summary_role: Role to assign to summary message
        
        Returns:
            Summary string or None if summarization not available
        """
        if not self.summarize_callback:
            self.logger.debug("No summarization callback available")
            return None
        
        if len(messages) < 2:
            return None
        
        self.logger.info(f"Summarizing {len(messages)} messages...")
        
        try:
            summary = self.summarize_callback(messages)
            self.logger.info(f"Summary created: {len(summary)} characters")
            return summary
        except Exception as e:
            self.logger.error(f"Error during summarization: {e}", exc_info=True)
            return None
    
    def manage_context(
        self,
        messages: List[Dict[str, str]],
        add_summary: bool = True
    ) -> List[Dict[str, str]]:
        """
        Manage conversation context with pruning and optional summarization.
        
        Args:
            messages: Current conversation history
            add_summary: Whether to add summary if context is pruned
        
        Returns:
            Managed conversation history
        """
        if len(messages) <= self.max_messages:
            return messages
        
        # Check if we should summarize
        should_summarize = len(messages) >= self.summarize_threshold and add_summary
        
        if should_summarize and self.summarize_callback:
            # Separate old messages for summarization
            system_msg = [m for m in messages if m.get("role") == "system"]
            old_messages = messages[:len(messages) - self.max_messages // 2]
            recent_messages = messages[len(messages) - self.max_messages // 2:]
            
            # Summarize old messages
            summary = self.summarize_context(old_messages)
            
            if summary:
                # Create summary message
                summary_message = {
                    "role": "system",
                    "content": f"Previous conversation summary: {summary}"
                }
                
                # Combine: system message, summary, recent messages
                managed = system_msg + [summary_message] + recent_messages
                
                # Prune if still too long
                if len(managed) > self.max_messages:
                    managed = self.prune_context(managed)
                
                self.logger.info(f"Context managed with summarization: {len(messages)} -> {len(managed)} messages")
                return managed
        
        # Just prune without summarization
        return self.prune_context(messages)
    
    def mark_important(self, message_index: int):
        """
        Mark a message as important.
        
        Args:
            message_index: Index of message to mark as important
        """
        self.important_indices.add(message_index)
        self.logger.debug(f"Marked message {message_index} as important")
    
    def get_context_stats(self, messages: List[Dict[str, str]]) -> Dict:
        """
        Get statistics about the conversation context.
        
        Args:
            messages: Conversation history
        
        Returns:
            Dictionary with context statistics
        """
        system_count = sum(1 for m in messages if m.get("role") == "system")
        user_count = sum(1 for m in messages if m.get("role") == "user")
        assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
        important_count = sum(1 for m in messages if self.is_important(m))
        
        return {
            "total_messages": len(messages),
            "system_messages": system_count,
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "important_messages": important_count,
            "max_messages": self.max_messages,
            "needs_pruning": len(messages) > self.max_messages,
            "needs_summarization": len(messages) >= self.summarize_threshold
        }

