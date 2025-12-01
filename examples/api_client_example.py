"""
Example API Client for Jane AI Voice Assistant

Demonstrates how to interact with the API using HTTP requests and WebSocket.
"""

import requests
import json
import websockets
import asyncio
from typing import Optional


class JaneAPIClient:
    """
    Client for interacting with Jane AI Voice Assistant API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def chat(self, text: str, stream: bool = False) -> dict:
        """
        Send a text message and get response.
        
        Args:
            text: Text message to send
            stream: Whether to stream the response
            
        Returns:
            Response dictionary
        """
        response = requests.post(
            f"{self.base_url}/api/v1/chat",
            json={"text": text, "stream": stream},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def transcribe(self, audio_file_path: str) -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Response dictionary with transcribed text
        """
        import base64
        
        # Read and encode audio file
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        response = requests.post(
            f"{self.base_url}/api/v1/transcribe",
            json={"audio_data": audio_b64, "sample_rate": 16000},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        import base64
        
        response = requests.post(
            f"{self.base_url}/api/v1/synthesize",
            params={"text": text},
            headers=self.headers
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            audio_b64 = result.get("audio", "")
            return base64.b64decode(audio_b64)
        else:
            raise Exception(result.get("error", "Synthesis failed"))
    
    def call_function(self, function_name: str, arguments: dict = None) -> dict:
        """
        Call a function directly.
        
        Args:
            function_name: Name of function to call
            arguments: Function arguments
            
        Returns:
            Function call result
        """
        response = requests.post(
            f"{self.base_url}/api/v1/functions/call",
            json={"function_name": function_name, "arguments": arguments or {}},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_functions(self) -> list:
        """
        List all available functions.
        
        Returns:
            List of function definitions
        """
        response = requests.get(
            f"{self.base_url}/api/v1/functions",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> dict:
        """
        Get assistant status.
        
        Returns:
            Status dictionary
        """
        response = requests.get(
            f"{self.base_url}/api/v1/status",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    async def websocket_chat(self, text: str) -> dict:
        """
        Send a message via WebSocket and get response.
        
        Args:
            text: Text message to send
            
        Returns:
            Response dictionary
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        
        async with websockets.connect(f"{ws_url}/ws") as websocket:
            # Send text message
            message = {
                "type": "text",
                "text": text
            }
            await websocket.send(json.dumps(message))
            
            # Receive response
            response = await websocket.recv()
            return json.loads(response)


def example_rest_api():
    """Example of using REST API."""
    print("=" * 60)
    print("REST API Example")
    print("=" * 60)
    
    client = JaneAPIClient()
    
    try:
        # Check status
        print("\n1. Checking status:")
        status = client.get_status()
        print(f"   Status: {status}")
        
        # List functions
        print("\n2. Listing functions:")
        functions = client.list_functions()
        print(f"   Found {len(functions)} functions")
        
        # Send a chat message
        print("\n3. Sending chat message:")
        response = client.chat("Hello, what time is it?")
        print(f"   Response: {response.get('response', 'No response')}")
        
        # Call a function
        print("\n4. Calling function directly:")
        result = client.call_function("get_current_time")
        print(f"   Result: {result}")
        
    except requests.exceptions.ConnectionError:
        print("\n   ⚠️  Could not connect to API server")
        print("   Make sure the server is running: python -m src.api.server")
    except Exception as e:
        print(f"\n   ❌ Error: {e}")


async def example_websocket():
    """Example of using WebSocket."""
    print("\n" + "=" * 60)
    print("WebSocket Example")
    print("=" * 60)
    
    client = JaneAPIClient()
    
    try:
        response = await client.websocket_chat("Hello, Jane!")
        print(f"\n   Response: {response}")
    except Exception as e:
        print(f"\n   ⚠️  Error: {e}")
        print("   Make sure the server is running: python -m src.api.server")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Jane AI Voice Assistant - API Client Example")
    print("=" * 60)
    
    example_rest_api()
    
    # Run WebSocket example
    try:
        asyncio.run(example_websocket())
    except Exception as e:
        print(f"\n   ⚠️  WebSocket example failed: {e}")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
    print("\nTo use the API:")
    print("1. Start the server: python -m src.api.server")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Use this client to interact with the API")

