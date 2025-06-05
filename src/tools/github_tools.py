"""
Simplified GitHub tools using langchain-mcp-adapters with GitHub-specific MCP client
"""
import logging
from typing import List, Optional
from langchain_core.tools import BaseTool
from src.tools.mcp_client.github_client import GitHubMCPClient

# Setup logging configuration for MCP adapters
logging.getLogger("langchain_mcp_adapters").setLevel(logging.WARNING)


async def get_github_tools() -> List[BaseTool]:
    """
    Get all GitHub tools automatically from the MCP server.
    
    This replaces all the individual tool classes with a single function
    that dynamically discovers and converts all available tools from the
    GitHub MCP server using langchain-mcp-adapters.
    
    Returns:
        List[BaseTool]: All available GitHub tools as LangChain tools
    """
    client = GitHubMCPClient()
    return await client.get_tools()


# Backward compatibility function if needed
async def get_all_github_tools() -> List[BaseTool]:
    """Alias for get_github_tools() for backward compatibility"""
    return await get_github_tools()


# If you need to get tools by category or filter them, you can do so like this:
async def get_github_tools_by_prefix(prefix: str) -> List[BaseTool]:
    """
    Get GitHub tools that start with a specific prefix.
    
    Args:
        prefix: The prefix to filter tools by (e.g., "list_", "get_", "search_")
    
    Returns:
        List[BaseTool]: Filtered GitHub tools
    """
    all_tools = await get_github_tools()
    return [tool for tool in all_tools if tool.name.startswith(prefix)]


async def get_available_tool_names() -> List[str]:
    """
    Get names of all available GitHub tools.
    
    Returns:
        List[str]: Names of all available tools
    """
    tools = await get_github_tools()
    return [tool.name for tool in tools]