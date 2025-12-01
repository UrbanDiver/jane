"""
File System Controller

This module provides safe file system operations for the AI assistant.
Includes safety checks to prevent access to sensitive system directories.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import json
from src.config.config_schema import FileControllerConfig
from src.utils.logger import get_logger


class FileController:
    """
    Controller for file system operations.
    
    Provides safe file operations with directory restrictions.
    """
    
    def __init__(
        self,
        config: Optional[FileControllerConfig] = None,
        safe_mode: Optional[bool] = None
    ):
        """
        Initialize file controller.
        
        Args:
            config: FileControllerConfig object (takes precedence over individual params)
            safe_mode: Enable safety checks (restrict to user directories)
        """
        # Use config if provided, otherwise use individual params or defaults
        if config:
            safe_mode = config.safe_mode
            allowed_dirs = [Path(d).expanduser() for d in config.allowed_directories]
        else:
            safe_mode = safe_mode if safe_mode is not None else True
            allowed_dirs = [
                Path.home() / "Documents",
                Path.home() / "Desktop",
                Path.home() / "Downloads",
                Path.home() / "Pictures",
                Path.home() / "Videos",
                Path.home() / "Music"
            ]
        
        self.safe_mode = safe_mode
        self.allowed_dirs = allowed_dirs
        self.logger = get_logger(__name__)
        
        self.logger.info(f"FileController initialized (safe_mode={safe_mode})")
        if safe_mode:
            self.logger.debug(f"  Allowed directories: {len(self.allowed_dirs)}")
    
    def _check_path_safety(self, path: Path) -> bool:
        """
        Ensure path is in allowed directories (if safe_mode enabled).
        
        Args:
            path: Path to check
            
        Returns:
            True if path is safe, False otherwise
        """
        if not self.safe_mode:
            return True
        
        try:
            resolved_path = Path(path).resolve()
            
            # Check if path is within any allowed directory
            for allowed_dir in self.allowed_dirs:
                try:
                    allowed_resolved = allowed_dir.resolve()
                    # Check if resolved_path is a subpath of allowed_resolved
                    if str(resolved_path).startswith(str(allowed_resolved)):
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def read_file(self, file_path: str) -> Dict:
        """
        Read a file's contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "content": str,      # File contents (if success)
                "error": str         # Error message (if failure)
            }
        """
        path = Path(file_path)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {file_path}"
            }
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        try:
            # Try to read as text first
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "path": str(path)
            }
            
        except UnicodeDecodeError:
            # File is binary
            return {
                "success": False,
                "error": f"File is binary, cannot read as text: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def write_file(
        self,
        file_path: str,
        content: str,
        mode: str = "w"
    ) -> Dict:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
            mode: Write mode ("w" for overwrite, "a" for append)
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "path": str,         # File path (if success)
                "error": str         # Error message (if failure)
            }
        """
        path = Path(file_path)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {file_path}"
            }
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(path),
                "size": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_directory(self, dir_path: str) -> Dict:
        """
        List files in a directory.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "files": list,       # List of file info dicts (if success)
                "count": int,        # Number of files (if success)
                "error": str         # Error message (if failure)
            }
        """
        path = Path(dir_path)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {dir_path}"
            }
        
        if not path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {dir_path}"
            }
        
        if not path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {dir_path}"
            }
        
        try:
            files = []
            for item in path.iterdir():
                try:
                    file_info = {
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "path": str(item)
                    }
                    
                    if item.is_file():
                        file_info["size"] = item.stat().st_size
                        file_info["size_mb"] = file_info["size"] / (1024 * 1024)
                    else:
                        file_info["size"] = None
                        file_info["size_mb"] = None
                    
                    files.append(file_info)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "path": str(path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(
        self,
        directory: str,
        pattern: str,
        recursive: bool = True
    ) -> Dict:
        """
        Search for files matching a pattern.
        
        Args:
            directory: Directory to search in
            pattern: File pattern (e.g., "*.txt", "*.py")
            recursive: Search recursively in subdirectories
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "matches": list,     # List of matching file paths (if success)
                "count": int,        # Number of matches (if success)
                "error": str         # Error message (if failure)
            }
        """
        path = Path(directory)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {directory}"
            }
        
        if not path.exists() or not path.is_dir():
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        try:
            if recursive:
                matches = list(path.rglob(pattern))
            else:
                matches = list(path.glob(pattern))
            
            # Filter to only include files (not directories)
            matches = [m for m in matches if m.is_file()]
            
            # Check safety for each match
            safe_matches = []
            for match in matches:
                if self._check_path_safety(match):
                    safe_matches.append(str(match.relative_to(path)))
            
            return {
                "success": True,
                "matches": safe_matches,
                "count": len(safe_matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            Dictionary with results
        """
        path = Path(file_path)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {file_path}"
            }
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                return {
                    "success": False,
                    "error": "Path is a directory, use delete_directory instead"
                }
            else:
                return {
                    "success": False,
                    "error": "Path does not exist"
                }
            
            return {
                "success": True,
                "path": str(path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_directory(self, dir_path: str) -> Dict:
        """
        Create a directory.
        
        Args:
            dir_path: Path to directory to create
            
        Returns:
            Dictionary with results
        """
        path = Path(dir_path)
        
        if not self._check_path_safety(path):
            return {
                "success": False,
                "error": f"Path not allowed: {dir_path}"
            }
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "path": str(path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the file controller
    print("=" * 60)
    print("Testing File Controller")
    print("=" * 60)
    
    fc = FileController(safe_mode=True)
    
    # Test 1: List Desktop
    print("\n1. Testing list_directory (Desktop):")
    desktop = Path.home() / "Desktop"
    result = fc.list_directory(str(desktop))
    if result["success"]:
        print(f"   ✅ Found {result['count']} items")
        for item in result['files'][:5]:
            print(f"      - {item['name']} ({item['type']})")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 2: Create test file
    print("\n2. Testing write_file:")
    test_file = Path.home() / "Documents" / "assistant_test.txt"
    result = fc.write_file(str(test_file), "Hello from AI Assistant!\nThis is a test file.")
    if result["success"]:
        print(f"   ✅ File created: {result['path']}")
        print(f"   Size: {result['size']} bytes")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 3: Read test file
    print("\n3. Testing read_file:")
    result = fc.read_file(str(test_file))
    if result["success"]:
        print(f"   ✅ File read successfully")
        print(f"   Content: {result['content'][:50]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 4: Search for .txt files
    print("\n4. Testing search_files (.txt files in Documents):")
    docs = Path.home() / "Documents"
    result = fc.search_files(str(docs), "*.txt")
    if result["success"]:
        print(f"   ✅ Found {result['count']} .txt files")
        for match in result['matches'][:3]:
            print(f"      - {match}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 5: Cleanup
    print("\n5. Cleaning up test file:")
    result = fc.delete_file(str(test_file))
    if result["success"]:
        print(f"   ✅ Test file deleted")
    else:
        print(f"   ⚠️  Could not delete: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ File Controller test complete!")
    print("=" * 60)

