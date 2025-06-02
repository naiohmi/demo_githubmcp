"""
GitHub MCP Client for interacting with GitHub MCP Server
"""
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.config.settings import get_settings


class GitHubTool(BaseModel):
    """GitHub tool representation"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class GitHubMCPClient:
    """Client for GitHub MCP Server using direct subprocess communication"""
    
    def __init__(self):
        self.settings = get_settings()
        self.process: Optional[subprocess.Popen] = None
        self.tools: List[GitHubTool] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
        
    async def start(self):
        """Start the GitHub MCP server process"""
        # Get the path to the GitHub MCP server binary
        mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "github-mcp-server"
        
        if not mcp_server_path.exists():
            raise FileNotFoundError(f"GitHub MCP server binary not found at {mcp_server_path}")
        
        # Set environment variables
        env = os.environ.copy()
        env['GITHUB_PERSONAL_ACCESS_TOKEN'] = self.settings.GITHUB_PERSONAL_ACCESS_TOKEN
        if self.settings.GITHUB_HOST:
            env['GITHUB_HOST'] = self.settings.GITHUB_HOST
        
        # Start the process directly
        self.process = subprocess.Popen(
            [str(mcp_server_path), "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "simple-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_request(init_request)
        response = await self._read_response()
        
        if "error" in response:
            raise RuntimeError(f"Initialize failed: {response['error']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self._send_request(initialized_notification)
        
        # Load available tools
        await self._load_tools()
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send a JSON-RPC request"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process not started")
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message)
        self.process.stdin.flush()
    
    async def _read_response(self) -> Dict[str, Any]:
        """Read a JSON-RPC response"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Process not started")
        
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("No response from server")
        
        line = line.strip()
        if not line:
            raise RuntimeError("Empty response from server")
        
        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {line[:100]}...") from e
        
    async def _load_tools(self):
        """Load available tools from the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        await self._send_request(request)
        response = await self._read_response()
        
        if "error" in response:
            raise RuntimeError(f"List tools failed: {response['error']}")
        
        tools_data = response.get("result", {}).get("tools", [])
        self.tools = []
        for tool in tools_data:
            github_tool = GitHubTool(
                name=tool.get("name", ""),
                description=tool.get("description", ""),
                input_schema=tool.get("inputSchema", {})
            )
            self.tools.append(github_tool)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.process:
            raise RuntimeError("Process not started. Call start() first.")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self._send_request(request)
        response = await self._read_response()
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
    
    def get_available_tools(self) -> List[GitHubTool]:
        """Get list of available tools"""
        return self.tools
    
    async def list_tools(self) -> List[GitHubTool]:
        """Async method to get list of available tools (alias for get_available_tools)"""
        return self.get_available_tools()
    
    def get_tool_by_name(self, name: str) -> Optional[GitHubTool]:
        """Get a specific tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None


async def create_github_client() -> GitHubMCPClient:
    """Factory function to create and start a GitHub MCP client"""
    client = GitHubMCPClient()
    await client.start()
    return client


# Context manager for automatic cleanup
class GitHubMCPClientManager:
    """Context manager for GitHub MCP client"""
    
    def __init__(self):
        self.client: Optional[GitHubMCPClient] = None
    
    async def __aenter__(self) -> GitHubMCPClient:
        self.client = await create_github_client()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.stop()


# Simplified client management - no global singleton
class SimpleMCPClientManager:
    """Simple MCP client manager without global state"""
    
    async def __aenter__(self) -> GitHubMCPClient:
        """Create a new client for each operation"""
        client = GitHubMCPClient()
        await client.start()
        return client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed as each client manages its own lifecycle
        pass


# Backwards compatibility aliases
async def get_global_github_client() -> GitHubMCPClient:
    """Create a new GitHub MCP client (no longer global)"""
    return await create_github_client()


async def cleanup_global_client():
    """No-op for backwards compatibility"""
    pass


class PersistentGitHubMCPClient:
    """Simplified client that creates new connections per use"""
    
    async def __aenter__(self) -> GitHubMCPClient:
        return await create_github_client()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Each client manages its own cleanup
        pass
