"""
GitHub-specific MCP Client wrapper for backward compatibility
"""
from typing import List, Optional
from langchain_core.tools import BaseTool
from .mcp_client import MCPClient, ToolInfo


class GitHubMCPClient(MCPClient):
    """GitHub-specific MCP client for backward compatibility"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        # Add GitHub-specific environment variables
        self._add_github_env_vars()
    
    def _add_github_env_vars(self):
        """Add GitHub-specific environment variables to the configuration"""
        # This method can be used to add GitHub-specific environment variables
        # that are not in the base configuration
        pass
    
    async def get_tools(self, server_name: Optional[str] = None) -> List[BaseTool]:
        """Get GitHub tools specifically"""
        return await super().get_tools(server_name="github")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call GitHub tool specifically"""
        return await super().call_tool(tool_name, arguments, server_name="github")
    
    async def list_tools(self) -> List[ToolInfo]:
        """List GitHub tools specifically"""
        return await super().list_tools(server_name="github")


async def create_github_client(config_path: Optional[str] = None) -> GitHubMCPClient:
    """Factory function to create and start a GitHub MCP client"""
    client = GitHubMCPClient(config_path)
    await client.start()
    return client


# Context managers for GitHub-specific usage
class GitHubMCPClientManager:
    """Context manager for GitHub MCP client"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.client: Optional[GitHubMCPClient] = None
    
    async def __aenter__(self) -> GitHubMCPClient:
        self.client = await create_github_client(self.config_path)
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.stop()


class PersistentGitHubMCPClient:
    """Simplified GitHub client that creates new connections per use"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
    
    async def __aenter__(self) -> GitHubMCPClient:
        return await create_github_client(self.config_path)
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Each client manages its own cleanup
        pass


# Backwards compatibility functions
async def get_global_github_client(config_path: Optional[str] = None) -> GitHubMCPClient:
    """Create a new GitHub MCP client (no longer global)"""
    return await create_github_client(config_path)


async def cleanup_global_client():
    """No-op for backwards compatibility"""
    pass
