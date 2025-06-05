"""
MCP Client module for generic and GitHub-specific MCP server integration
"""
from .mcp_client import (
    MCPClient,
    ToolInfo,
    create_mcp_client,
    MCPClientManager,
    SimpleMCPClientManager
)

from .github_client import (
    GitHubMCPClient,
    create_github_client,
    GitHubMCPClientManager,
    PersistentGitHubMCPClient,
    get_global_github_client,
    cleanup_global_client
)

__all__ = [
    # Generic MCP Client
    "MCPClient",
    "ToolInfo",
    "create_mcp_client",
    "MCPClientManager",
    "SimpleMCPClientManager",
    
    # GitHub-specific Client (backward compatibility)
    "GitHubMCPClient", 
    "create_github_client",
    "GitHubMCPClientManager",
    "PersistentGitHubMCPClient",
    "get_global_github_client",
    "cleanup_global_client"
]