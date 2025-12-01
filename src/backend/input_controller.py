"""
Input Controller for Keyboard and Mouse

This module provides functionality to control keyboard and mouse input.
Includes safety features to prevent accidental actions.
"""

import pyautogui
import time
from typing import Tuple, Optional, Dict
import platform
from src.config.config_schema import InputControllerConfig
from src.utils.logger import get_logger
from src.interfaces.controllers import InputControllerInterface


class InputController(InputControllerInterface):
    """
    Controller for keyboard and mouse input.
    
    Provides safe input control with failsafe mechanisms.
    """
    
    def __init__(
        self,
        config: Optional[InputControllerConfig] = None,
        safe_mode: Optional[bool] = None,
        pause: Optional[float] = None
    ):
        """
        Initialize input controller.
        
        Args:
            config: InputControllerConfig object (takes precedence over individual params)
            safe_mode: Enable safety features (failsafe, pauses)
            pause: Pause between actions in seconds
        """
        # Use config if provided, otherwise use individual params or defaults
        if config:
            safe_mode = config.safe_mode
            pause = config.pause
        else:
            safe_mode = safe_mode if safe_mode is not None else True
            pause = pause if pause is not None else 0.1
        
        self.safe_mode = safe_mode
        self.logger = get_logger(__name__)
        
        # Configure pyautogui
        pyautogui.PAUSE = pause
        pyautogui.FAILSAFE = safe_mode  # Move mouse to corner to abort
        
        if safe_mode:
            self.logger.info("InputController initialized (safe_mode=True)")
            self.logger.debug("  Failsafe enabled: Move mouse to corner to abort")
        else:
            self.logger.warning("InputController initialized (safe_mode=False)")
            self.logger.warning("  ⚠️  WARNING: Failsafe disabled!")
    
    def type_text(
        self,
        text: str,
        interval: float = 0.0
    ) -> Dict:
        """
        Type text at the current keyboard focus.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes in seconds
            
        Returns:
            Dictionary with results
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            return {
                "success": True,
                "typed": text,
                "length": len(text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def press_key(self, key: str) -> Dict:
        """
        Press a single key.
        
        Args:
            key: Key to press (e.g., 'enter', 'space', 'tab')
            
        Returns:
            Dictionary with results
        """
        try:
            pyautogui.press(key)
            return {
                "success": True,
                "key": key
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def hotkey(self, *keys) -> Dict:
        """
        Press a hotkey combination (e.g., ctrl+c, alt+tab).
        
        Args:
            *keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
            
        Returns:
            Dictionary with results
        """
        try:
            pyautogui.hotkey(*keys)
            return {
                "success": True,
                "keys": keys
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def move_mouse(
        self,
        x: int,
        y: int,
        duration: float = 0.5
    ) -> Dict:
        """
        Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            Dictionary with results
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return {
                "success": True,
                "position": (x, y)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = 'left',
        clicks: int = 1,
        interval: float = 0.0
    ) -> Dict:
        """
        Click at current position or specified coordinates.
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Delay between clicks in seconds
            
        Returns:
            Dictionary with results
        """
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button, interval=interval)
            else:
                pyautogui.click(clicks=clicks, button=button, interval=interval)
            
            return {
                "success": True,
                "clicks": clicks,
                "button": button,
                "position": (x, y) if x is not None and y is not None else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 1.0,
        button: str = 'left'
    ) -> Dict:
        """
        Drag mouse from one position to another.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Drag duration in seconds
            button: Mouse button to hold
            
        Returns:
            Dictionary with results
        """
        try:
            pyautogui.drag(start_x, start_y, end_x - start_x, end_y - start_y, duration=duration, button=button)
            return {
                "success": True,
                "start": (start_x, start_y),
                "end": (end_x, end_y)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def scroll(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        clicks: int = 3
    ) -> Dict:
        """
        Scroll mouse wheel.
        
        Args:
            x: X coordinate (None for current position)
            y: Y coordinate (None for current position)
            clicks: Number of scroll clicks (positive = up, negative = down)
            
        Returns:
            Dictionary with results
        """
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            return {
                "success": True,
                "clicks": clicks,
                "position": (x, y) if x is not None and y is not None else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_mouse_position(self) -> Dict:
        """
        Get current mouse position.
        
        Returns:
            Dictionary with mouse position:
            {
                "success": bool,
                "x": int,
                "y": int
            }
        """
        try:
            x, y = pyautogui.position()
            return {
                "success": True,
                "x": x,
                "y": y
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def screenshot(
        self,
        filename: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict:
        """
        Take a screenshot.
        
        Args:
            filename: Output filename (None to return image object)
            region: Optional region (x, y, width, height) to capture
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "saved": str,        # Filename if saved
                "error": str         # Error message if failure
            }
        """
        try:
            if region:
                img = pyautogui.screenshot(region=region)
            else:
                img = pyautogui.screenshot()
            
            if filename:
                img.save(filename)
                return {
                    "success": True,
                    "saved": filename
                }
            else:
                # Return image object (PIL Image)
                return {
                    "success": True,
                    "image": img
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_screen_size(self) -> Dict:
        """
        Get screen size.
        
        Returns:
            Dictionary with screen dimensions
        """
        try:
            width, height = pyautogui.size()
            return {
                "success": True,
                "width": width,
                "height": height
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the input controller
    print("=" * 60)
    print("Testing Input Controller")
    print("=" * 60)
    
    ic = InputController(safe_mode=True)
    
    # Test 1: Get screen size
    print("\n1. Testing get_screen_size:")
    result = ic.get_screen_size()
    if result["success"]:
        print(f"   ✅ Screen size: {result['width']}x{result['height']}")
    
    # Test 2: Get mouse position
    print("\n2. Testing get_mouse_position:")
    print("   Move your mouse around...")
    for i in range(3):
        time.sleep(1)
        result = ic.get_mouse_position()
        if result["success"]:
            print(f"   Position {i+1}: ({result['x']}, {result['y']})")
    
    # Test 3: Screenshot
    print("\n3. Testing screenshot:")
    result = ic.screenshot("test_screenshot.png")
    if result["success"]:
        print(f"   ✅ Screenshot saved: {result['saved']}")
    
    # Test 4: Move mouse
    print("\n4. Testing move_mouse:")
    screen = ic.get_screen_size()
    if screen["success"]:
        center_x = screen["width"] // 2
        center_y = screen["height"] // 2
        result = ic.move_mouse(center_x, center_y, duration=0.5)
        if result["success"]:
            print(f"   ✅ Moved mouse to center: ({center_x}, {center_y})")
    
    # Test 5: Type text (with warning)
    print("\n5. Testing type_text:")
    print("   ⚠️  This will type text at the current keyboard focus!")
    response = input("   Test typing? (y/n): ").strip().lower()
    if response == 'y':
        print("   Typing 'Hello from AI Assistant!' in 2 seconds...")
        time.sleep(2)
        result = ic.type_text("Hello from AI Assistant!", interval=0.05)
        if result["success"]:
            print(f"   ✅ Typed {result['length']} characters")
    
    print("\n" + "=" * 60)
    print("✅ Input Controller test complete!")
    print("=" * 60)
    print("\nNote: Failsafe is enabled - move mouse to corner to abort any action")

