"""
Application Controller

This module provides functionality to launch, manage, and control applications.
"""

import subprocess
import psutil
from typing import List, Optional, Dict
import time


class AppController:
    """
    Controller for application management.
    
    Provides functionality to launch, list, and close applications.
    """
    
    def __init__(self):
        """Initialize application controller."""
        # Common applications with their executable paths
        self.common_apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        }
        
        print("AppController initialized")
        print(f"  Common apps registered: {len(self.common_apps)}")
    
    def launch_app(
        self,
        app_name: str,
        args: Optional[List[str]] = None
    ) -> Dict:
        """
        Launch an application.
        
        Args:
            app_name: Name of application (common name or full path)
            args: Optional list of command-line arguments
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "pid": int,          # Process ID (if success)
                "message": str,       # Status message
                "error": str          # Error message (if failure)
            }
        """
        try:
            # Check if it's a known app
            app_name_lower = app_name.lower()
            if app_name_lower in self.common_apps:
                exe_path = self.common_apps[app_name_lower]
            else:
                # Assume it's a full path or executable name
                exe_path = app_name
            
            # Build command
            cmd = [exe_path] + (args or [])
            
            # Launch process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a moment to start
            time.sleep(0.5)
            
            # Check if process is still running
            if process.poll() is None:
                return {
                    "success": True,
                    "pid": process.pid,
                    "message": f"Launched {app_name} (PID: {process.pid})"
                }
            else:
                # Process exited immediately (error)
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') or "Process exited immediately"
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Application not found: {app_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_running_apps(self) -> Dict:
        """
        Get list of running applications.
        
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "apps": list,        # List of app info dicts (if success)
                "count": int,        # Number of apps (if success)
                "error": str         # Error message (if failure)
            }
        """
        try:
            apps = []
            seen_names = set()
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info']):
                try:
                    info = proc.info
                    name = info['name']
                    
                    # Filter to .exe files and avoid duplicates
                    if name and name.lower().endswith('.exe') and name not in seen_names:
                        seen_names.add(name)
                        apps.append({
                            "name": name,
                            "pid": info['pid'],
                            "exe": info.get('exe', 'N/A'),
                            "memory_mb": info.get('memory_info', {}).rss / (1024 * 1024) if info.get('memory_info') else None
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Skip processes we can't access
                    continue
            
            # Sort by name
            apps.sort(key=lambda x: x['name'].lower())
            
            return {
                "success": True,
                "apps": apps,
                "count": len(apps)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def close_app(
        self,
        app_name: str,
        force: bool = False
    ) -> Dict:
        """
        Close an application by name.
        
        Args:
            app_name: Name of application to close (e.g., "notepad.exe")
            force: Force kill if graceful termination fails
            
        Returns:
            Dictionary with results:
            {
                "success": bool,
                "closed": int,       # Number of processes closed (if success)
                "message": str,      # Status message
                "error": str         # Error message (if failure)
            }
        """
        try:
            closed = 0
            app_name_lower = app_name.lower()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and app_name_lower in proc_name.lower():
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        closed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed > 0:
                # Wait a moment for processes to close
                time.sleep(0.5)
                return {
                    "success": True,
                    "closed": closed,
                    "message": f"Closed {closed} instance(s) of {app_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"No running instances found: {app_name}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_app_running(self, app_name: str) -> bool:
        """
        Check if an application is currently running.
        
        Args:
            app_name: Name of application to check
            
        Returns:
            True if app is running, False otherwise
        """
        app_name_lower = app_name.lower()
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name and app_name_lower in proc_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def get_app_info(self, app_name: str) -> Dict:
        """
        Get information about a running application.
        
        Args:
            app_name: Name of application
            
        Returns:
            Dictionary with app information
        """
        app_name_lower = app_name.lower()
        apps_found = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'cpu_percent']):
            try:
                proc_name = proc.info['name']
                if proc_name and app_name_lower in proc_name.lower():
                    apps_found.append({
                        "pid": proc.info['pid'],
                        "name": proc_name,
                        "exe": proc.info.get('exe', 'N/A'),
                        "memory_mb": proc.info.get('memory_info', {}).rss / (1024 * 1024) if proc.info.get('memory_info') else None,
                        "cpu_percent": proc.info.get('cpu_percent', 0)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "success": len(apps_found) > 0,
            "apps": apps_found,
            "count": len(apps_found)
        }


if __name__ == "__main__":
    # Test the app controller
    print("=" * 60)
    print("Testing App Controller")
    print("=" * 60)
    
    ac = AppController()
    
    # Test 1: Get running apps
    print("\n1. Testing get_running_apps:")
    result = ac.get_running_apps()
    if result["success"]:
        print(f"   ✅ Found {result['count']} running applications")
        print("   Sample apps:")
        for app in result['apps'][:5]:
            print(f"      - {app['name']} (PID: {app['pid']})")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 2: Launch Calculator
    print("\n2. Testing launch_app (Calculator):")
    result = ac.launch_app("calculator")
    if result["success"]:
        print(f"   ✅ {result['message']}")
        print("   Calculator should be open now.")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 3: Check if calculator is running
    print("\n3. Testing is_app_running (Calculator):")
    is_running = ac.is_app_running("calculator")
    print(f"   Calculator running: {is_running}")
    
    # Test 4: Get calculator info
    print("\n4. Testing get_app_info (Calculator):")
    result = ac.get_app_info("calculator")
    if result["success"]:
        print(f"   ✅ Found {result['count']} instance(s)")
        for app in result['apps']:
            print(f"      PID: {app['pid']}, Memory: {app.get('memory_mb', 0):.1f} MB")
    
    # Test 5: Close Calculator
    print("\n5. Testing close_app (Calculator):")
    input("   Press Enter to close calculator...")
    result = ac.close_app("calculator")
    if result["success"]:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ App Controller test complete!")
    print("=" * 60)

