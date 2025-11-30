"""
Helper script to download LLM models for Jane AI Assistant.

This script downloads GGUF models from Hugging Face for use with llama.cpp.
"""

import sys
from pathlib import Path

def download_model(
    repo_id: str = "bartowski/Qwen2.5-32B-Instruct-GGUF",
    filename: str = "Qwen2.5-32B-Instruct-Q4_K_M.gguf",
    local_dir: str = "models"
):
    """
    Download a GGUF model from Hugging Face.
    
    Args:
        repo_id: Hugging Face repository ID
        filename: Model filename to download
        local_dir: Local directory to save the model
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("❌ huggingface-hub not installed!")
        print("Install it with: pip install huggingface-hub[cli]")
        sys.exit(1)
    
    # Create models directory
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    output_path = Path(local_dir) / filename
    
    if output_path.exists():
        print(f"✅ Model already exists: {output_path}")
        print(f"   Size: {output_path.stat().st_size / (1024**3):.2f} GB")
        response = input("Download again? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping download.")
            return str(output_path)
    
    print(f"Downloading model from: {repo_id}")
    print(f"  Filename: {filename}")
    print(f"  Destination: {output_path}")
    print("\n⚠️  This may take a while (model is ~20GB)...")
    print("   Press Ctrl+C to cancel\n")
    
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"\n✅ Model downloaded successfully!")
        print(f"   Path: {downloaded_path}")
        print(f"   Size: {Path(downloaded_path).stat().st_size / (1024**3):.2f} GB")
        
        return downloaded_path
        
    except KeyboardInterrupt:
        print("\n\nDownload cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        sys.exit(1)

def list_recommended_models():
    """List recommended models for different use cases."""
    models = {
        "Large (32B) - Best Quality": {
            "repo": "bartowski/Qwen2.5-32B-Instruct-GGUF",
            "file": "Qwen2.5-32B-Instruct-Q4_K_M.gguf",
            "size": "~20GB",
            "description": "High quality, requires 24GB+ VRAM"
        },
        "Medium (7B) - Balanced": {
            "repo": "bartowski/Qwen2.5-7B-Instruct-GGUF",
            "file": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            "size": "~4.5GB",
            "description": "Good balance of quality and speed"
        },
        "Small (1.5B) - Fast": {
            "repo": "bartowski/Qwen2.5-1.5B-Instruct-GGUF",
            "file": "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
            "size": "~1GB",
            "description": "Fast inference, lower quality"
        }
    }
    
    print("Recommended Models:")
    print("=" * 60)
    for name, info in models.items():
        print(f"\n{name}:")
        print(f"  Repository: {info['repo']}")
        print(f"  File: {info['file']}")
        print(f"  Size: {info['size']}")
        print(f"  Description: {info['description']}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LLM models for Jane AI Assistant")
    parser.add_argument("--list", action="store_true", help="List recommended models")
    parser.add_argument("--repo", default="bartowski/Qwen2.5-32B-Instruct-GGUF", help="Hugging Face repository ID")
    parser.add_argument("--file", default="Qwen2.5-32B-Instruct-Q4_K_M.gguf", help="Model filename")
    parser.add_argument("--dir", default="models", help="Local directory to save model")
    
    args = parser.parse_args()
    
    if args.list:
        list_recommended_models()
    else:
        print("=" * 60)
        print("Jane AI Assistant - LLM Model Downloader")
        print("=" * 60)
        print()
        list_recommended_models()
        print("\n" + "=" * 60)
        print(f"Downloading: {args.repo}/{args.file}")
        print("=" * 60)
        
        download_model(args.repo, args.file, args.dir)

