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
from typing import Dict, List, Optional
import json
import time


class AssistantCore:
    """
    Unified AI Assistant Core.
    
    Integrates all components for end-to-end voice interaction.
    """
    
    def __init__(
        self,
        llm_model_path: str,
        stt_model_size: str = "medium",
        tts_model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    ):
        """
        Initialize the assistant core.
        
        Args:
            llm_model_path: Path to LLM GGUF model
            stt_model_size: Whisper model size
            tts_model_name: TTS model name
        """
        print("=" * 60)
        print("Initializing AI Assistant Core...")
        print("=" * 60)
        
        # Core engines
        print("\n1. Initializing STT engine...")
        self.stt = StreamingSTT(model_size=stt_model_size)
        
        print("\n2. Initializing TTS engine...")
        self.tts = TTSEngine(model_name=tts_model_name)
        
        print("\n3. Initializing LLM engine...")
        self.llm = LLMEngine(llm_model_path)
        
        # Controllers
        print("\n4. Initializing controllers...")
        self.file_ctrl = FileController(safe_mode=True)
        self.app_ctrl = AppController()
        self.input_ctrl = InputController(safe_mode=True)
        
        # Function handler
        print("\n5. Setting up function handler...")
        self.function_handler = FunctionHandler()
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
        
        print("\n" + "=" * 60)
        print("✅ Assistant Core initialized successfully!")
        print("=" * 60)
    
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
        
        print(f"   ✅ Registered {len(self.function_handler.list_functions())} functions")
    
    def listen(self, duration: float = 5.0) -> str:
        """
        Listen for voice input and return transcription.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        print("🎤 Listening...")
        result = self.stt.listen_and_transcribe(duration=duration)
        return result.get('text', '').strip()
    
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
        use_functions: bool = True
    ) -> str:
        """
        Process user input and generate response.
        
        Args:
            user_input: User's input text
            max_tokens: Maximum tokens to generate
            use_functions: Whether to allow function calling
            
        Returns:
            Assistant's response text
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get LLM response
        print("🤔 Thinking...")
        
        # For now, use simple chat completion
        # TODO: Implement function calling integration with LLM
        result = self.llm.chat(
            self.conversation_history[-10:],  # Last 10 messages for context
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        response = result['response']
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def run_voice_loop(self):
        """
        Main voice interaction loop.
        
        Continuously listens for voice input, processes it, and responds.
        """
        print("\n" + "=" * 60)
        print("AI Assistant Ready!")
        print("=" * 60)
        print("\nVoice interaction loop starting...")
        print("Say 'goodbye' or 'exit' to stop.\n")
        
        self.speak("Hello! I'm Jane, your AI assistant. I'm ready to help you.")
        
        while True:
            try:
                # Listen for voice input
                user_input = self.listen(duration=5)
                
                if not user_input.strip():
                    continue
                
                print(f"\n👤 You: {user_input}")
                
                # Check for exit commands
                if any(word in user_input.lower() for word in ["goodbye", "exit", "quit", "stop"]):
                    self.speak("Goodbye! Have a great day!")
                    break
                
                # Process command
                response = self.process_command(user_input)
                print(f"🤖 Jane: {response}")
                
                # Speak response
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
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

