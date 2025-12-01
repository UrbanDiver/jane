"""
Unified Assistant Core

This module integrates all components (STT, TTS, LLM, Computer Control)
into a unified voice assistant system.
"""

from src.backend.streaming_stt import StreamingSTT
from src.backend.tts_engine import TTSEngine
from src.backend.llm_engine import LLMEngine
from src.backend.function_handler import FunctionHandler
from src.backend.file_controller import FileController
from src.backend.app_controller import AppController
from src.backend.input_controller import InputController
from src.backend.context_manager import ContextManager
from src.backend.conversation_state import ConversationState
from src.backend.web_search import search_web
from src.backend.system_info import (
    get_system_info, get_cpu_info, get_memory_info, 
    get_disk_usage, get_network_info
)
from src.plugins.plugin_manager import PluginManager
from src.plugins.plugin_base import PluginHook
from src.backend.wake_word_detector import WakeWordDetector
from src.config import load_config, get_config, AssistantConfig
from src.utils.logger import get_logger, log_performance, log_timing
from src.utils.error_handler import handle_error
from src.utils.sentence_splitter import SentenceSplitter
from src.utils.memory_manager import get_memory_manager
from typing import Dict, List, Optional
import json
import time
import os
import threading
from typing import Optional


class AssistantCore:
    """
    Unified AI Assistant Core.
    
    Integrates all components for end-to-end voice interaction.
    """
    
    def __init__(
        self,
        config: Optional[AssistantConfig] = None,
        llm_model_path: Optional[str] = None,
        stt_model_size: Optional[str] = None,
        tts_model_name: Optional[str] = None,
        # Dependency injection parameters
        stt: Optional[StreamingSTT] = None,
        tts: Optional[TTSEngine] = None,
        llm: Optional[LLMEngine] = None,
        file_ctrl: Optional[FileController] = None,
        app_ctrl: Optional[AppController] = None,
        input_ctrl: Optional[InputController] = None,
        function_handler: Optional[FunctionHandler] = None,
        context_manager: Optional[ContextManager] = None,
        conversation_state: Optional[ConversationState] = None
    ):
        """
        Initialize the assistant core.
        
        Args:
            config: AssistantConfig object (takes precedence over individual params)
            llm_model_path: Path to LLM GGUF model (required if config not provided)
            stt_model_size: Whisper model size
            tts_model_name: TTS model name
            
            # Dependency injection parameters (optional)
            stt: STT engine instance (created if not provided)
            tts: TTS engine instance (created if not provided)
            llm: LLM engine instance (created if not provided)
            file_ctrl: File controller instance (created if not provided)
            app_ctrl: App controller instance (created if not provided)
            input_ctrl: Input controller instance (created if not provided)
            function_handler: Function handler instance (created if not provided)
            context_manager: Context manager instance (created if not provided)
            conversation_state: Conversation state instance (created if not provided)
        """
        # Load config if not provided
        if config is None:
            config = get_config()
            # Override with individual params if provided (for backward compatibility)
            if llm_model_path:
                config.llm.model_path = llm_model_path
            if stt_model_size:
                config.stt.model_size = stt_model_size
            if tts_model_name:
                config.tts.model_name = tts_model_name
        
        self.config = config
        self.logger = get_logger(__name__)
        
        self.logger.info("=" * 60)
        self.logger.info("Initializing AI Assistant Core...")
        self.logger.info("=" * 60)
        
        # Core engines (dependency injection with defaults)
        if stt is not None:
            self.logger.info("1. Using injected STT engine...")
            self.stt = stt
        else:
            self.logger.info("1. Initializing STT engine...")
            self.stt = StreamingSTT(config=config.stt)
        
        if tts is not None:
            self.logger.info("2. Using injected TTS engine...")
            self.tts = tts
        else:
            self.logger.info("2. Initializing TTS engine...")
            self.tts = TTSEngine(config=config.tts)
        
        if llm is not None:
            self.logger.info("3. Using injected LLM engine...")
            self.llm = llm
        else:
            self.logger.info("3. Initializing LLM engine...")
            self.llm = LLMEngine(config=config.llm)
        
        # Controllers (dependency injection with defaults)
        if file_ctrl is not None:
            self.logger.info("4a. Using injected file controller...")
            self.file_ctrl = file_ctrl
        else:
            self.logger.info("4a. Initializing file controller...")
            self.file_ctrl = FileController(config=config.file_controller)
        
        if app_ctrl is not None:
            self.logger.info("4b. Using injected app controller...")
            self.app_ctrl = app_ctrl
        else:
            self.logger.info("4b. Initializing app controller...")
            self.app_ctrl = AppController(config=config.app_controller)
        
        if input_ctrl is not None:
            self.logger.info("4c. Using injected input controller...")
            self.input_ctrl = input_ctrl
        else:
            self.logger.info("4c. Initializing input controller...")
            self.input_ctrl = InputController(config=config.input_controller)
        
        # Function handler (dependency injection with default)
        if function_handler is not None:
            self.logger.info("5. Using injected function handler...")
            self.function_handler = function_handler
        else:
            self.logger.info("5. Setting up function handler...")
            self.function_handler = FunctionHandler()
        
        # Register functions (only if we created the handler)
        if function_handler is None:
            self._register_functions()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": """You are Jane, a helpful AI assistant with the ability to control the computer.
You can:
- Answer questions and provide information
- Read, write, and search files
- Launch and control applications
- Control keyboard and mouse
- Take screenshots

Always confirm before taking potentially destructive actions.
Be concise and helpful. When asked to perform actions, use the available functions."""
            }
        ]
        
        # Store max conversation history from config
        self.max_conversation_history = config.max_conversation_history
        
        # Conversation state (dependency injection with default)
        if conversation_state is not None:
            self.logger.info("6a. Using injected conversation state...")
            self.conversation_state = conversation_state
        else:
            self.logger.info("6a. Initializing conversation state...")
            self.conversation_state = ConversationState()
            self.conversation_state.start_session()
        
        # Context manager (dependency injection with default)
        if context_manager is not None:
            self.logger.info("6b. Using injected context manager...")
            self.context_manager = context_manager
        else:
            self.logger.info("6b. Initializing context manager...")
            # Create summarization callback using LLM
            def summarize_messages(messages: List[Dict[str, str]]) -> str:
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
                    result = self.llm.generate(
                        summary_prompt,
                        max_tokens=100,
                        temperature=0.3
                    )
                    
                    return result.get("text", "").strip()
                except Exception as e:
                    self.logger.warning(f"Summarization failed: {e}")
                    return "Previous conversation context (summarization unavailable)"
            
            self.context_manager = ContextManager(
                max_messages=config.max_conversation_history,
                summarize_threshold=int(config.max_conversation_history * 1.5),  # Summarize at 1.5x threshold
                summarize_callback=summarize_messages,
                conversation_state=self.conversation_state
            )
        
        # Memory manager for cleanup
        self.memory_manager = get_memory_manager()
        
        # Log initial memory usage
        self.memory_manager.log_memory_usage("(initialization)")
        
        self.logger.info("=" * 60)
        self.logger.info("✅ Assistant Core initialized successfully!")
        self.logger.info("=" * 60)
    
    def _register_functions(self):
        """Register all control functions with the function handler."""
        
        # File operations
        self.function_handler.register(
            "read_file",
            self.file_ctrl.read_file,
            "Read the contents of a text file",
            {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        )
        
        self.function_handler.register(
            "write_file",
            self.file_ctrl.write_file,
            "Write content to a file (creates file if it doesn't exist)",
            {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        )
        
        self.function_handler.register(
            "list_directory",
            self.file_ctrl.list_directory,
            "List files and directories in a directory",
            {
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    }
                },
                "required": ["dir_path"]
            }
        )
        
        self.function_handler.register(
            "search_files",
            self.file_ctrl.search_files,
            "Search for files matching a pattern (e.g., *.txt)",
            {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File pattern to search for (e.g., *.txt)"
                    }
                },
                "required": ["directory", "pattern"]
            }
        )
        
        # App control
        self.function_handler.register(
            "launch_app",
            self.app_ctrl.launch_app,
            "Launch an application",
            {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application (e.g., 'calculator', 'notepad')"
                    }
                },
                "required": ["app_name"]
            }
        )
        
        self.function_handler.register(
            "close_app",
            self.app_ctrl.close_app,
            "Close an application by name",
            {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to close"
                    }
                },
                "required": ["app_name"]
            }
        )
        
        self.function_handler.register(
            "get_running_apps",
            self.app_ctrl.get_running_apps,
            "Get a list of currently running applications",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        # Input control
        self.function_handler.register(
            "take_screenshot",
            lambda filename="screenshot.png": self.input_ctrl.screenshot(filename),
            "Take a screenshot of the screen",
            {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename to save the screenshot"
                    }
                },
                "required": []
            }
        )
        
        self.function_handler.register(
            "type_text",
            self.input_ctrl.type_text,
            "Type text at the current keyboard focus",
            {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["text"]
            }
        )
        
        # Web search
        self.function_handler.register(
            "search_web",
            search_web,
            "Search the web for information using DuckDuckGo",
            {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        
        # System information
        self.function_handler.register(
            "get_system_info",
            get_system_info,
            "Get system information (OS, platform, processor, Python version)",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.function_handler.register(
            "get_cpu_info",
            get_cpu_info,
            "Get CPU information and current usage",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.function_handler.register(
            "get_memory_info",
            get_memory_info,
            "Get memory (RAM) information and usage",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.function_handler.register(
            "get_disk_usage",
            get_disk_usage,
            "Get disk usage information for a path (default: root/C: drive)",
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check disk usage (default: '/' or 'C:\\')",
                        "default": "/"
                    }
                },
                "required": []
            }
        )
        
        self.function_handler.register(
            "get_network_info",
            get_network_info,
            "Get network interface information",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        self.logger.info(f"✅ Registered {len(self.function_handler.list_functions())} functions")
        
        # Initialize plugin system
        self.logger.info("6. Initializing plugin system...")
        self.plugin_manager = PluginManager()
        
        # Load plugins
        loaded_plugins = self.plugin_manager.load_all_plugins(self)
        self.logger.info(f"✅ Loaded {len(loaded_plugins)} plugins")
        
        # Register plugin functions
        plugin_functions = self.plugin_manager.get_all_functions()
        for func_name, func_def in plugin_functions.items():
            self.function_handler.register(
                func_name,
                func_def["function"],
                func_def["description"],
                func_def["parameters"]
            )
            self.logger.debug(f"Registered plugin function: {func_name} (from {func_def.get('plugin', 'unknown')})")
        
        if plugin_functions:
            self.logger.info(f"✅ Registered {len(plugin_functions)} plugin functions")
    
    def listen(self, duration: float = 5.0) -> str:
        """
        Listen for voice input and return transcription.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        self.logger.info("🎤 Listening...")
        result = self.stt.listen_and_transcribe(duration=duration)
        text = result.get('text', '').strip()
        if text:
            self.logger.info(f"Transcribed: '{text}'")
        return text
    
    def speak(self, text: str):
        """
        Speak the given text.
        
        Args:
            text: Text to speak
        """
        if not text.strip():
            return
        
        self.tts.speak(text, wait=True)
    
    def process_command(
        self,
        user_input: str,
        max_tokens: int = 512,
        use_functions: bool = True,
        stream: bool = True
    ) -> str:
        """
        Process user input and generate response with function calling support.
        
        Args:
            user_input: User's input text
            max_tokens: Maximum tokens to generate
            use_functions: Whether to allow function calling
            stream: Whether to stream the response (default: True)
            
        Returns:
            Assistant's response text
        """
        # Add user message to conversation history
        user_message = {
            "role": "user",
            "content": user_input
        }
        self.conversation_history.append(user_message)
        
        # Execute ON_MESSAGE hook
        self.plugin_manager.execute_hook(PluginHook.ON_MESSAGE, user_message)
        
        # Get LLM response
        self.logger.info("🤔 Thinking...")
        
        # Manage context before getting LLM response
        managed_history = self.context_manager.manage_context(
            self.conversation_history,
            add_summary=True
        )
        
        # Update conversation history (context manager may have modified it)
        if managed_history != self.conversation_history:
            self.logger.debug(f"Context managed: {len(self.conversation_history)} -> {len(managed_history)} messages")
            self.conversation_history = managed_history
        
        # Prepare function calling if enabled
        tools = None
        if use_functions:
            tools = self.function_handler.format_functions_for_llm()
            if tools:
                self.logger.debug(f"Function calling enabled with {len(tools)} functions")
        
        # Get LLM response with function calling support
        max_iterations = 5  # Limit function call chains
        iteration = 0
        final_response = None
        result = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # Execute BEFORE_LLM hook (plugins can modify messages)
            modified_history = self.plugin_manager.execute_hook(PluginHook.BEFORE_LLM, managed_history)
            if modified_history and len(modified_history) > 0:
                # Use the last result if it's a list, otherwise use original
                if isinstance(modified_history[-1], list):
                    managed_history = modified_history[-1]
                elif isinstance(modified_history[-1], dict):
                    # Single message modification - replace last message
                    managed_history = managed_history[:-1] + [modified_history[-1]]
            
            # Get LLM response (streaming or non-streaming)
            if stream and iteration == 1 and not tools:  # Only stream if no function calling
                response = self._process_streaming_response(
                    managed_history,
                    max_tokens or self.config.llm.max_tokens,
                    tools=None  # No tools for streaming
                )
                # Streaming doesn't support function calling, so we're done
                final_response = response
                # Execute AFTER_LLM hook
                self.plugin_manager.execute_hook(PluginHook.AFTER_LLM, response)
                break
            else:
                result = self.llm.chat(
                    managed_history,
                    max_tokens=max_tokens or self.config.llm.max_tokens,
                    temperature=self.config.llm.temperature,
                    tools=tools if iteration == 1 else None  # Only provide tools on first call
                )
                response = result.get('response', '')
                function_calls = result.get('function_calls', [])
                
                # Execute AFTER_LLM hook
                self.plugin_manager.execute_hook(PluginHook.AFTER_LLM, result)
            
            # Check for function calls
            if use_functions and result and 'function_calls' in result and result['function_calls']:
                # Execute function calls
                for fc in result['function_calls']:
                    func_name = fc['function']['name']
                    func_args_str = fc['function'].get('arguments', '{}')
                    
                    try:
                        func_args = json.loads(func_args_str) if isinstance(func_args_str, str) else func_args_str
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON in function arguments: {func_args_str}")
                        func_args = {}
                    
                    self.logger.info(f"🔧 Calling function: {func_name} with args: {func_args}")
                    
                    # Execute BEFORE_FUNCTION_CALL hook
                    self.plugin_manager.execute_hook(PluginHook.BEFORE_FUNCTION_CALL, func_name, func_args)
                    
                    # Execute function
                    func_result = self.function_handler.execute(func_name, func_args)
                    
                    # Execute AFTER_FUNCTION_CALL hook
                    self.plugin_manager.execute_hook(PluginHook.AFTER_FUNCTION_CALL, func_name, func_args, func_result)
                    
                    if func_result['success']:
                        result_str = str(func_result['result'])
                        # Add function result to conversation
                        managed_history.append({
                            "role": "tool",
                            "content": result_str,
                            "tool_call_id": fc.get('id'),
                            "name": func_name
                        })
                        self.logger.debug(f"Function result: {result_str[:100]}...")
                    else:
                        error_msg = func_result.get('error', 'Unknown error')
                        managed_history.append({
                            "role": "tool",
                            "content": f"Error: {error_msg}",
                            "tool_call_id": fc.get('id'),
                            "name": func_name
                        })
                        self.logger.warning(f"Function {func_name} failed: {error_msg}")
                
                # Continue loop to get LLM response with function results
                continue
            else:
                # No function calls, we're done
                final_response = response
                break
        
        if final_response is None:
            # Max iterations reached, use last response
            final_response = response
            self.logger.warning(f"Function call chain reached max iterations ({max_iterations})")
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        # Save conversation state periodically
        if len(self.conversation_history) % 10 == 0:
            self.conversation_state.save()
        
        return final_response
    
    def _process_streaming_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """
        Process streaming LLM response with early TTS synthesis.
        
        Args:
            messages: Conversation history
            max_tokens: Maximum tokens to generate
        
        Returns:
            Complete response text
        """
        sentence_splitter = SentenceSplitter()
        full_response = ""
        sentences_spoken = []
        
        self.logger.debug("Starting streaming response...")
        
        try:
            # Stream response from LLM
            # Note: Function calling with streaming is complex, so we disable it for now
            # If tools are provided, we'll fall back to non-streaming
            if tools:
                self.logger.debug("Function calling enabled, disabling streaming")
                raise ValueError("Streaming not supported with function calling")
            
            stream = self.llm.stream_chat(
                messages,
                max_tokens=max_tokens,
                temperature=self.config.llm.temperature
            )
            
            # Process stream
            for chunk in stream:
                if chunk.get('done'):
                    break
                
                delta = chunk.get('delta', '')
                if not delta:
                    continue
                
                full_response += delta
                
                # Print delta for visual feedback (optional)
                print(delta, end='', flush=True)
                
                # Check for complete sentences
                sentences = sentence_splitter.add_text(delta)
                
                # Speak complete sentences as they arrive
                for sentence in sentences:
                    if sentence and sentence not in sentences_spoken:
                        sentences_spoken.append(sentence)
                        self.logger.debug(f"Speaking sentence: '{sentence[:50]}...'")
                        # Speak in background thread to not block streaming
                        threading.Thread(
                            target=self.tts.speak,
                            args=(sentence,),
                            kwargs={"wait": True},
                            daemon=True
                        ).start()
            
            # Print newline after streaming
            print()  # Newline after streaming output
            
            # Speak any remaining text
            remaining = sentence_splitter.flush()
            if remaining and len(remaining.strip()) > 10:
                self.logger.debug(f"Speaking remaining text: '{remaining[:50]}...'")
                threading.Thread(
                    target=self.tts.speak,
                    args=(remaining.strip(),),
                    kwargs={"wait": True},
                    daemon=True
                ).start()
            
            self.logger.info(f"Streaming complete: {len(full_response)} characters")
            return full_response.strip()
            
        except Exception as e:
            error_info = handle_error(e, context={"operation": "streaming_response"}, logger=self.logger)
            self.logger.error(f"Error during streaming: {error_info['message']}", exc_info=True)
            
            # Fallback to non-streaming
            self.logger.warning("Falling back to non-streaming response")
            result = self.llm.chat(
                messages,
                max_tokens=max_tokens,
                temperature=self.config.llm.temperature
            )
            return result['response']
    
    def _try_function_call(self, user_input: str) -> Optional[str]:
        """
        DEPRECATED: Try to detect and execute a function call based on user input.
        
        This method is kept for backward compatibility but is no longer used.
        Function calling is now handled by the LLM directly.
        
        Args:
            user_input: User's input text
            
        Returns:
            Function result string if function was called, None otherwise
        """
        # This method is deprecated - function calling is now handled by LLM
        return None
        
        # File listing queries
        if any(phrase in user_lower for phrase in ["list files", "show files", "what files", "files in"]):
            # Try to extract directory from query
            import os
            if "desktop" in user_lower:
                dir_path = os.path.join(os.path.expanduser("~"), "Desktop")
            elif "documents" in user_lower:
                dir_path = os.path.join(os.path.expanduser("~"), "Documents")
            elif "downloads" in user_lower:
                dir_path = os.path.join(os.path.expanduser("~"), "Downloads")
            else:
                dir_path = os.path.join(os.path.expanduser("~"), "Documents")
            
            result = self.file_ctrl.list_directory(dir_path)
            if result["success"]:
                file_count = len(result["files"])
                file_list = ", ".join([f["name"] for f in result["files"][:10]])
                if file_count > 10:
                    file_list += f", and {file_count - 10} more"
                return f"Found {file_count} items: {file_list}"
        
        # Running apps queries
        if any(phrase in user_lower for phrase in ["running apps", "what apps", "open apps", "running applications"]):
            result = self.app_ctrl.get_running_apps()
            if result["success"]:
                app_count = result["count"]
                app_list = ", ".join([app["name"] for app in result["apps"][:10]])
                if app_count > 10:
                    app_list += f", and {app_count - 10} more"
                return f"Found {app_count} running applications: {app_list}"
        
        return None
    
    def run_voice_loop(self, use_wake_word: Optional[bool] = None):
        """
        Main voice interaction loop.
        
        Continuously listens for voice input, processes it, and responds.
        
        Args:
            use_wake_word: Override wake word setting (None = use config)
        """
        self.logger.info("=" * 60)
        self.logger.info("AI Assistant Ready!")
        self.logger.info("=" * 60)
        
        # Determine if wake word should be used
        use_wake_word = use_wake_word if use_wake_word is not None else (
            self.wake_word_detector is not None and self.config.wake_word.enabled
        )
        
        if use_wake_word:
            self.logger.info("Wake word mode enabled")
            self.logger.info(f"Wake words: {self.config.wake_word.wake_words}")
            self.logger.info("Say a wake word to activate, or 'goodbye'/'exit' to stop.")
            self.speak("Hello! I'm Jane. Say my name to activate me.")
            
            # Start continuous wake word listening
            def on_wake_word_detected(command: str):
                """Handle wake word detection."""
                self.logger.info(f"🔔 Wake word detected! Command: '{command}'")
                
                if not command.strip():
                    # Just wake word, no command - prompt for input
                    self.speak("Yes? How can I help you?")
                    # Listen for actual command
                    user_input = self.listen(duration=5)
                    if user_input.strip():
                        self._process_user_input(user_input)
                else:
                    # Command included with wake word
                    self._process_user_input(command)
            
            self.wake_word_detector.start_continuous_listening(
                callback=on_wake_word_detected,
                check_interval=self.config.wake_word.check_interval
            )
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
                    # Check for exit (could be done via a command)
            except KeyboardInterrupt:
                self.logger.info("Exiting (KeyboardInterrupt)...")
                if self.wake_word_detector:
                    self.wake_word_detector.stop_continuous_listening()
                self.speak("Goodbye!")
        else:
            # Standard mode (no wake word)
            self.logger.info("Voice interaction loop starting...")
            self.logger.info("Say 'goodbye' or 'exit' to stop.")
            self.speak("Hello! I'm Jane, your AI assistant. I'm ready to help you.")
            
            while True:
                try:
                    # Listen for voice input
                    user_input = self.listen(duration=5)
                    
                    if not user_input.strip():
                        continue
                    
                    self._process_user_input(user_input)
                    
                except KeyboardInterrupt:
                    self.logger.info("Exiting (KeyboardInterrupt)...")
                    self.speak("Goodbye!")
                    break
                except Exception as e:
                    error_info = handle_error(e, context={"user_input": user_input if 'user_input' in locals() else None}, logger=self.logger)
                    self.logger.error(f"❌ Error in voice loop: {error_info['message']}", exc_info=True)
    
    def _process_user_input(self, user_input: str):
        """
        Process user input and generate response.
        
        Args:
            user_input: User's input text
        """
        self.logger.info(f"👤 You: {user_input}")
        
        # Check for exit commands
        if any(word in user_input.lower() for word in ["goodbye", "exit", "quit", "stop"]):
            self.speak("Goodbye! Have a great day!")
            self.logger.info("User requested exit")
            return
        
        # Process command (with streaming enabled)
        response = self.process_command(user_input, stream=True)
        self.logger.info(f"🤖 Jane: {response}")
        
        # Note: Response may already be spoken via streaming
        # Only speak if streaming didn't work or was disabled
        # (This is handled in _process_streaming_response)
        
        # Periodic memory cleanup
        if len(self.conversation_history) % 10 == 0:
            self.memory_manager.clear_gpu_cache()
            self.memory_manager.log_memory_usage("(periodic cleanup)")
                
                # Try to provide user feedback
                try:
                    self.speak("I encountered an error. Please try again.")
                except:
                    pass  # Don't fail if TTS also fails
                
                continue
    
    def get_status(self) -> Dict:
        """Get status of all components."""
        return {
            "stt": "ready",
            "tts": "ready",
            "llm": "ready",
            "functions": len(self.function_handler.list_functions()),
            "conversation_turns": len([m for m in self.conversation_history if m["role"] == "user"])
        }


if __name__ == "__main__":
    # Test the assistant core
    print("=" * 60)
    print("Testing Assistant Core")
    print("=" * 60)
    
    # Check if model exists
    from pathlib import Path
    model_path = "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    if not Path(model_path).exists():
        print(f"\n❌ Model not found: {model_path}")
        print("Please download a model first:")
        print("  python download_llm_model.py")
        exit(1)
    
    print(f"\nInitializing assistant with model: {model_path}")
    print("This may take a few minutes to load all components...\n")
    
    assistant = AssistantCore(llm_model_path=model_path)
    
    # Show status
    print("\n" + "=" * 60)
    print("Assistant Status")
    print("=" * 60)
    status = assistant.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test voice loop
    print("\n" + "=" * 60)
    print("Starting Voice Interaction Loop")
    print("=" * 60)
    print("\nYou can now speak to the assistant!")
    print("Say 'goodbye' to exit.\n")
    
    assistant.run_voice_loop()

