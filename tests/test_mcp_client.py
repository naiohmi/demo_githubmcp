#!/usr/bin/env python3
"""
GitHub MCP Client tests
"""
import asyncio
import pytest

from src.tools.mcp_client.github_client import GitHubMCPClient


class TestMCPClient:
    """Test MCP client functionality"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_client_connection(self):
        """Test MCP client can connect to server"""
        client = GitHubMCPClient()
        try:
            await client.start()
            assert client.process is not None, "MCP server process not started"
            await client.stop()
        except Exception as e:
            pytest.fail(f"Failed to connect to MCP client: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_client_tools_discovery(self):
        """Test client can discover available tools"""
        client = GitHubMCPClient()
        try:
            await client.start()
            tools = await client.list_tools()
            assert len(tools) > 0, "No tools discovered from MCP server"
            # Check for at least one known tool from the MCP server
            tool_names = [tool.name for tool in tools]
            assert any("get_me" in tool_name for tool_name in tool_names), f"get_me tool not found in {tool_names}"
            await client.stop()
        except Exception as e:
            pytest.fail(f"Failed to discover tools: {e}")
    
    @pytest.mark.asyncio
    async def test_basic_tool_call(self):
        """Test basic tool call functionality"""
        client = GitHubMCPClient()
        try:
            await client.start()
            
            # Test get_me tool (should work with any valid GitHub token)
            result = await client.call_tool("get_me", {})
            assert result is not None, "get_me tool returned None"
            assert "login" in str(result), "get_me result doesn't contain login info"
            
            await client.stop()
        except Exception as e:
            pytest.fail(f"Failed to call basic tool: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
