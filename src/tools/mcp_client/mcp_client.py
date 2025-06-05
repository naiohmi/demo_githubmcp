"""
Generic MCP Client using langchain-mcp-adapters with registry-based configuration
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config.settings import get_settings


class ToolInfo:
    """Simple tool info class for backward compatibility"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class MCPClient:
    """Generic MCP Client that reads configuration from JSON registry"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = get_settings()
        self._client: Optional[MultiServerMCPClient] = None
        self._tools: Optional[Dict[str, List[BaseTool]]] = None
        self._started = False
        
        # Load configuration from registry
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "registry" / "mcp_client_config.json"
        
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load MCP configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"MCP configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logging(self):
        """Setup logging based on configuration"""
        global_config = self.config.get("global_config", {})
        
        if global_config.get("suppress_mcp_logging", False):
            # Suppress langchain-mcp-adapters logging
            logging.getLogger("langchain_mcp_adapters").setLevel(logging.WARNING)
        
        log_level = global_config.get("log_level", "INFO")
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.getLogger(__name__).setLevel(numeric_level)
    
    @property
    def process(self):
        """Compatibility property - returns mock process when started"""
        return self if self._started else None
    
    def _get_client(self) -> MultiServerMCPClient:
        """Get or create MCP client from registry configuration"""
        if self._client is None:
            servers_config = {}
            
            # Get the base path for relative command paths
            base_path = Path(__file__).parent.parent.parent.parent
            
            for server_name, server_config in self.config["servers"].items():
                if not server_config.get("enabled", True):
                    continue
                
                # Resolve command path
                command = server_config["command"]
                if not os.path.isabs(command):
                    command = str(base_path / command)
                
                # Prepare environment variables
                env = os.environ.copy()
                for env_var in server_config.get("environment_variables", []):
                    if hasattr(self.settings, env_var):
                        value = getattr(self.settings, env_var)
                        if value:
                            env[env_var] = value
                
                # Add global log level environment variables
                global_config = self.config.get("global_config", {})
                log_level = global_config.get("log_level", "ERROR")
                env.update({
                    'MCP_LOG_LEVEL': log_level,
                    'LOG_LEVEL': log_level
                })
                
                servers_config[server_name] = {
                    "command": command,
                    "args": server_config.get("args", []),
                    "transport": server_config.get("transport", "stdio"),
                    "env": env
                }
            
            if not servers_config:
                raise ValueError("No enabled servers found in configuration")
            
            self._client = MultiServerMCPClient(servers_config)
        
        return self._client
    
    async def get_tools(self, server_name: Optional[str] = None) -> List[BaseTool]:
        """Get tools from specific server or all servers"""
        if self._tools is None:
            self._tools = {}
        
        client = self._get_client()
        
        if server_name:
            # Get tools from specific server
            if server_name not in self._tools:
                self._tools[server_name] = await client.get_tools(server_name=server_name)
            return self._tools[server_name]
        else:
            # Get tools from all enabled servers
            all_tools = []
            for server_name in self.config["servers"].keys():
                if self.config["servers"][server_name].get("enabled", True):
                    if server_name not in self._tools:
                        self._tools[server_name] = await client.get_tools(server_name=server_name)
                    all_tools.extend(self._tools[server_name])
            return all_tools
    
    async def get_tools_by_prefix(self, prefix: str) -> List[BaseTool]:
        """Get tools that start with a specific prefix"""
        all_tools = await self.get_tools()
        return [tool for tool in all_tools if tool.name.startswith(prefix)]
    
    async def get_available_tool_names(self, server_name: Optional[str] = None) -> List[str]:
        """Get list of available tool names"""
        tools = await self.get_tools(server_name)
        return [tool.name for tool in tools]
    
    async def call_tool(self, tool_name: str, arguments: dict, server_name: Optional[str] = None) -> dict:
        """Call a specific tool by name"""
        tools = await self.get_tools(server_name)
        
        # Find the tool by name
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            available_tools = [t.name for t in tools]
            raise RuntimeError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        
        # Call the tool and return the result
        result = await tool.ainvoke(arguments)
        
        # Convert result to dictionary format for compatibility
        if hasattr(result, 'content'):
            return {"content": [{"type": "text", "text": str(result.content)}]}
        else:
            return {"content": [{"type": "text", "text": str(result)}]}
    
    async def list_tools(self, server_name: Optional[str] = None) -> List[ToolInfo]:
        """List available tools (for compatibility)"""
        tools = await self.get_tools(server_name)
        return [ToolInfo(tool.name, tool.description) for tool in tools]
    
    async def start(self):
        """Start method for compatibility"""
        self._started = True
    
    async def stop(self):
        """Stop method for compatibility"""
        self._started = False
        if self._client:
            # Clean up client resources if needed
            self._client = None
            self._tools = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


async def create_mcp_client(config_path: Optional[str] = None) -> MCPClient:
    """Factory function to create and start an MCP client"""
    client = MCPClient(config_path)
    await client.start()
    return client


# Context managers
class MCPClientManager:
    """Context manager for MCP client"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.client: Optional[MCPClient] = None
    
    async def __aenter__(self) -> MCPClient:
        self.client = await create_mcp_client(self.config_path)
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.stop()


class SimpleMCPClientManager:
    """Simple MCP client manager without global state"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
    
    async def __aenter__(self) -> MCPClient:
        """Create a new client for each operation"""
        client = MCPClient(self.config_path)
        await client.start()
        return client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed as each client manages its own lifecycle
        pass