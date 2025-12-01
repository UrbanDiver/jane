"""
Controller Interfaces

Abstract base classes for file, app, and input controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path


class FileControllerInterface(ABC):
    """
    Interface for file system operations.
    
    All file controllers must implement these methods.
    """
    
    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """
        Read contents of a text file.
        
        Args:
            file_path: Path to file to read
            
        Returns:
            File contents as string
        """
        pass
    
    @abstractmethod
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file to write
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_directory(self, dir_path: str) -> List[str]:
        """
        List files and directories in a directory.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            List of file and directory names
        """
        pass
    
    @abstractmethod
    def search_files(self, directory: str, pattern: str) -> List[str]:
        """
        Search for files matching a pattern.
        
        Args:
            directory: Directory to search in
            pattern: File pattern (e.g., "*.txt")
            
        Returns:
            List of matching file paths
        """
        pass


class AppControllerInterface(ABC):
    """
    Interface for application control.
    
    All app controllers must implement these methods.
    """
    
    @abstractmethod
    def launch_app(self, app_name: str) -> bool:
        """
        Launch an application.
        
        Args:
            app_name: Name of application to launch
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def close_app(self, app_name: str) -> bool:
        """
        Close an application by name.
        
        Args:
            app_name: Name of application to close
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_running_apps(self) -> List[str]:
        """
        Get list of currently running applications.
        
        Returns:
            List of application names
        """
        pass


class InputControllerInterface(ABC):
    """
    Interface for input control (keyboard, mouse, screenshots).
    
    All input controllers must implement these methods.
    """
    
    @abstractmethod
    def screenshot(self, filename: str = "screenshot.png") -> str:
        """
        Take a screenshot of the screen.
        
        Args:
            filename: Filename to save screenshot
            
        Returns:
            Path to saved screenshot
        """
        pass
    
    @abstractmethod
    def type_text(self, text: str) -> bool:
        """
        Type text at the current keyboard focus.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        pass

