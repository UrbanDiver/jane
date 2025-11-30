"""
Jane - AI Voice Assistant

Main entry point for the Jane AI assistant.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.backend.assistant_core import AssistantCore


def main():
    """Main entry point for Jane assistant."""
    print("=" * 60)
    print("Jane - AI Voice Assistant")
    print("=" * 60)
    
    # Check for model
    model_path = "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    if not Path(model_path).exists():
        print(f"\n❌ Model not found: {model_path}")
        print("\nPlease download a model first:")
        print("  python download_llm_model.py")
        print("\nOr specify a different model path:")
        print("  python jane.py --model path/to/model.gguf")
        return 1
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("\nUsage:")
            print("  python jane.py                    # Use default model")
            print("  python jane.py --model <path>      # Use custom model")
            print("  python jane.py --help              # Show this help")
            return 0
        elif sys.argv[1] == "--model" and len(sys.argv) > 2:
            model_path = sys.argv[2]
            if not Path(model_path).exists():
                print(f"\n❌ Model not found: {model_path}")
                return 1
    
    print(f"\nUsing model: {model_path}")
    print("\nInitializing assistant...")
    print("(This may take a few minutes to load all components)\n")
    
    try:
        # Initialize assistant
        assistant = AssistantCore(llm_model_path=model_path)
        
        # Show status
        print("\n" + "=" * 60)
        print("Assistant Status")
        print("=" * 60)
        status = assistant.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Start voice loop
        print("\n" + "=" * 60)
        assistant.run_voice_loop()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

