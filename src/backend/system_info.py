"""
System Information Module

Provides system information functions for the assistant.
"""

import platform
import psutil
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger, log_performance
from src.utils.error_handler import handle_error


class SystemInfo:
    """
    System information provider.
    """
    
    def __init__(self):
        """Initialize the system info module."""
        self.logger = get_logger(__name__)
        self.logger.info("SystemInfo initialized")
    
    @log_performance()
    def get_system_info(self) -> Dict:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary with system information:
            {
                "success": bool,
                "system": str,  # OS name
                "platform": str,  # Platform details
                "processor": str,  # CPU info
                "python_version": str,
                "error": str  # Error message if success is False
            }
        """
        try:
            info = {
                "success": True,
                "system": platform.system(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
                "hostname": platform.node()
            }
            
            self.logger.debug("Retrieved system information")
            return info
        
        except Exception as e:
            error_info = handle_error(e, logger=self.logger)
            return {
                "success": False,
                "error": error_info["message"]
            }
    
    @log_performance()
    def get_cpu_info(self) -> Dict:
        """
        Get CPU information and usage.
        
        Returns:
            Dictionary with CPU information:
            {
                "success": bool,
                "cpu_count": int,  # Physical cores
                "cpu_count_logical": int,  # Logical cores
                "cpu_percent": float,  # Current CPU usage %
                "cpu_freq": Dict,  # CPU frequency info
                "error": str  # Error message if success is False
            }
        """
        try:
            cpu_freq = psutil.cpu_freq()
            info = {
                "success": True,
                "cpu_count": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "cpu_freq": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                }
            }
            
            self.logger.debug("Retrieved CPU information")
            return info
        
        except Exception as e:
            error_info = handle_error(e, logger=self.logger)
            return {
                "success": False,
                "error": error_info["message"]
            }
    
    @log_performance()
    def get_memory_info(self) -> Dict:
        """
        Get memory (RAM) information.
        
        Returns:
            Dictionary with memory information:
            {
                "success": bool,
                "total": int,  # Total RAM in bytes
                "available": int,  # Available RAM in bytes
                "used": int,  # Used RAM in bytes
                "percent": float,  # Memory usage %
                "error": str  # Error message if success is False
            }
        """
        try:
            mem = psutil.virtual_memory()
            info = {
                "success": True,
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent
            }
            
            self.logger.debug("Retrieved memory information")
            return info
        
        except Exception as e:
            error_info = handle_error(e, logger=self.logger)
            return {
                "success": False,
                "error": error_info["message"]
            }
    
    @log_performance()
    def get_disk_info(self, path: str = "/") -> Dict:
        """
        Get disk usage information.
        
        Args:
            path: Path to check (default: "/" for root)
            
        Returns:
            Dictionary with disk information:
            {
                "success": bool,
                "total": int,  # Total disk space in bytes
                "used": int,  # Used disk space in bytes
                "free": int,  # Free disk space in bytes
                "percent": float,  # Disk usage %
                "path": str,  # Path checked
                "error": str  # Error message if success is False
            }
        """
        try:
            # On Windows, use "C:\\" as default
            if platform.system() == "Windows" and path == "/":
                path = "C:\\"
            
            disk = psutil.disk_usage(path)
            info = {
                "success": True,
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100,
                "path": path
            }
            
            self.logger.debug(f"Retrieved disk information for {path}")
            return info
        
        except Exception as e:
            error_info = handle_error(e, context={"path": path}, logger=self.logger)
            return {
                "success": False,
                "path": path,
                "error": error_info["message"]
            }
    
    @log_performance()
    def get_network_info(self) -> Dict:
        """
        Get network interface information.
        
        Returns:
            Dictionary with network information:
            {
                "success": bool,
                "interfaces": List[Dict],  # List of network interfaces
                "error": str  # Error message if success is False
            }
        """
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addresses in net_if_addrs.items():
                interface_info = {
                    "name": interface_name,
                    "addresses": [],
                    "isup": net_if_stats.get(interface_name, {}).isup if interface_name in net_if_stats else None
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                interfaces.append(interface_info)
            
            info = {
                "success": True,
                "interfaces": interfaces
            }
            
            self.logger.debug(f"Retrieved network information for {len(interfaces)} interfaces")
            return info
        
        except Exception as e:
            error_info = handle_error(e, logger=self.logger)
            return {
                "success": False,
                "error": error_info["message"]
            }
    
    @log_performance()
    def get_running_processes(self, limit: int = 10) -> Dict:
        """
        Get information about running processes.
        
        Args:
            limit: Maximum number of processes to return (default: 10)
            
        Returns:
            Dictionary with process information:
            {
                "success": bool,
                "processes": List[Dict],  # List of process info
                "error": str  # Error message if success is False
            }
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            info = {
                "success": True,
                "processes": processes[:limit]
            }
            
            self.logger.debug(f"Retrieved information for {len(info['processes'])} processes")
            return info
        
        except Exception as e:
            error_info = handle_error(e, logger=self.logger)
            return {
                "success": False,
                "error": error_info["message"]
            }


# Convenience functions for function handler
def get_system_info() -> str:
    """Get system information as formatted string."""
    sys_info = SystemInfo()
    info = sys_info.get_system_info()
    
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"
    
    lines = [
        "System Information:",
        f"  OS: {info['system']}",
        f"  Platform: {info['platform']}",
        f"  Processor: {info['processor']}",
        f"  Architecture: {info['architecture']}",
        f"  Python Version: {info['python_version']}",
        f"  Hostname: {info['hostname']}"
    ]
    return "\n".join(lines)


def get_cpu_info() -> str:
    """Get CPU information as formatted string."""
    sys_info = SystemInfo()
    info = sys_info.get_cpu_info()
    
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"
    
    lines = [
        "CPU Information:",
        f"  Physical Cores: {info['cpu_count']}",
        f"  Logical Cores: {info['cpu_count_logical']}",
        f"  CPU Usage: {info['cpu_percent']:.1f}%"
    ]
    
    if info['cpu_freq'].get('current'):
        lines.append(f"  Current Frequency: {info['cpu_freq']['current']:.0f} MHz")
    
    return "\n".join(lines)


def get_memory_info() -> str:
    """Get memory information as formatted string."""
    sys_info = SystemInfo()
    info = sys_info.get_memory_info()
    
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"
    
    def format_bytes(bytes_val):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    lines = [
        "Memory Information:",
        f"  Total: {format_bytes(info['total'])}",
        f"  Used: {format_bytes(info['used'])} ({info['percent']:.1f}%)",
        f"  Available: {format_bytes(info['available'])}"
    ]
    return "\n".join(lines)


def get_disk_usage(path: str = "/") -> str:
    """Get disk usage information as formatted string."""
    sys_info = SystemInfo()
    info = sys_info.get_disk_info(path)
    
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"
    
    def format_bytes(bytes_val):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    lines = [
        f"Disk Usage ({info['path']}):",
        f"  Total: {format_bytes(info['total'])}",
        f"  Used: {format_bytes(info['used'])} ({info['percent']:.1f}%)",
        f"  Free: {format_bytes(info['free'])}"
    ]
    return "\n".join(lines)


def get_network_info() -> str:
    """Get network information as formatted string."""
    sys_info = SystemInfo()
    info = sys_info.get_network_info()
    
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"
    
    lines = ["Network Interfaces:"]
    for interface in info['interfaces'][:5]:  # Limit to first 5 interfaces
        lines.append(f"  {interface['name']}:")
        for addr in interface['addresses'][:2]:  # Limit to first 2 addresses
            if addr['address'] and not addr['address'].startswith('::'):
                lines.append(f"    {addr['address']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test the system info module
    print("=" * 60)
    print("Testing System Info")
    print("=" * 60)
    
    sys_info = SystemInfo()
    
    # Test system info
    print("\n1. Testing get_system_info:")
    result = sys_info.get_system_info()
    if result.get("success"):
        print(f"   ✅ System: {result['system']}")
        print(f"   ✅ Platform: {result['platform']}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test CPU info
    print("\n2. Testing get_cpu_info:")
    result = sys_info.get_cpu_info()
    if result.get("success"):
        print(f"   ✅ CPU Cores: {result['cpu_count']} physical, {result['cpu_count_logical']} logical")
        print(f"   ✅ CPU Usage: {result['cpu_percent']:.1f}%")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test memory info
    print("\n3. Testing get_memory_info:")
    result = sys_info.get_memory_info()
    if result.get("success"):
        print(f"   ✅ Memory Usage: {result['percent']:.1f}%")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test disk info
    print("\n4. Testing get_disk_info:")
    result = sys_info.get_disk_info()
    if result.get("success"):
        print(f"   ✅ Disk Usage: {result['percent']:.1f}%")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test network info
    print("\n5. Testing get_network_info:")
    result = sys_info.get_network_info()
    if result.get("success"):
        print(f"   ✅ Found {len(result['interfaces'])} network interfaces")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test convenience functions
    print("\n6. Testing convenience functions:")
    print("\n" + get_system_info())
    print("\n" + get_cpu_info())
    print("\n" + get_memory_info())
    print("\n" + get_disk_usage())
    print("\n" + get_network_info())
    
    print("\n" + "=" * 60)
    print("✅ System Info test complete!")
    print("=" * 60)

