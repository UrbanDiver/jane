"""
Factory Functions for Component Creation

Provides factory functions for creating components with dependency injection.
"""

from typing import Optional
from src.config import AssistantConfig, get_config
from src.backend.streaming_stt import StreamingSTT
from src.backend.tts_engine import TTSEngine
from src.backend.llm_engine import LLMEngine
from src.backend.file_controller import FileController
from src.backend.app_controller import AppController
from src.backend.input_controller import InputController
from src.backend.function_handler import FunctionHandler
from src.backend.context_manager import ContextManager
from src.backend.conversation_state import ConversationState
from src.utils.logger import get_logger


def create_stt_engine(config: Optional[AssistantConfig] = None) -> StreamingSTT:
    """
    Factory function to create an STT engine.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        StreamingSTT instance
    """
    if config is None:
        config = get_config()
    return StreamingSTT(config=config.stt)


def create_tts_engine(config: Optional[AssistantConfig] = None) -> TTSEngine:
    """
    Factory function to create a TTS engine.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        TTSEngine instance
    """
    if config is None:
        config = get_config()
    return TTSEngine(config=config.tts)


def create_llm_engine(config: Optional[AssistantConfig] = None) -> LLMEngine:
    """
    Factory function to create an LLM engine.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        LLMEngine instance
    """
    if config is None:
        config = get_config()
    return LLMEngine(config=config.llm)


def create_file_controller(config: Optional[AssistantConfig] = None) -> FileController:
    """
    Factory function to create a file controller.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        FileController instance
    """
    if config is None:
        config = get_config()
    return FileController(config=config.file_controller)


def create_app_controller(config: Optional[AssistantConfig] = None) -> AppController:
    """
    Factory function to create an app controller.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        AppController instance
    """
    if config is None:
        config = get_config()
    return AppController(config=config.app_controller)


def create_input_controller(config: Optional[AssistantConfig] = None) -> InputController:
    """
    Factory function to create an input controller.
    
    Args:
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        InputController instance
    """
    if config is None:
        config = get_config()
    return InputController(config=config.input_controller)


def create_function_handler() -> FunctionHandler:
    """
    Factory function to create a function handler.
    
    Returns:
        FunctionHandler instance
    """
    return FunctionHandler()


def create_conversation_state() -> ConversationState:
    """
    Factory function to create a conversation state.
    
    Returns:
        ConversationState instance
    """
    state = ConversationState()
    state.start_session()
    return state


def create_context_manager(
    llm: LLMEngine,
    conversation_state: ConversationState,
    config: Optional[AssistantConfig] = None
) -> ContextManager:
    """
    Factory function to create a context manager.
    
    Args:
        llm: LLM engine instance for summarization
        conversation_state: Conversation state instance
        config: AssistantConfig object (uses default if not provided)
        
    Returns:
        ContextManager instance
    """
    if config is None:
        config = get_config()
    
    logger = get_logger(__name__)
    
    # Create summarization callback using LLM
    def summarize_messages(messages):
        """Summarize conversation messages using LLM."""
        try:
            # Format messages for summarization
            summary_prompt = "Summarize the following conversation in 2-3 sentences, focusing on key topics and decisions:\n\n"
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]  # Truncate long messages
                summary_prompt += f"{role}: {content}\n"
            
            summary_prompt += "\nSummary:"
            
            # Use LLM to generate summary
            result = llm.generate(
                summary_prompt,
                max_tokens=100,
                temperature=0.3
            )
            
            return result.get("text", "").strip()
        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
            return "Previous conversation context (summarization unavailable)"
    
    return ContextManager(
        max_messages=config.max_conversation_history,
        summarize_threshold=int(config.max_conversation_history * 1.5),
        summarize_callback=summarize_messages,
        conversation_state=conversation_state
    )

