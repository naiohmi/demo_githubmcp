#!/usr/bin/env python3
"""
GitHub Tools tests
"""
import asyncio
import pytest

from src.tools.github_tools import get_github_tools


class TestGitHubTools:
    """Test GitHub tool implementations"""
    
    @pytest.mark.unit
    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_tools_loading(self):
        """Test that GitHub tools can be loaded"""
        tools = await get_github_tools()
        assert len(tools) > 0, "No GitHub tools loaded"
        # Note: The exact number may vary as tools are dynamically discovered from MCP server
        
    @pytest.mark.unit
    @pytest.mark.mcp
    @pytest.mark.asyncio
    async def test_tool_names(self):
        """Test that all expected tools are present"""
        tools = await get_github_tools()
        tool_names = [tool.name for tool in tools]
        
        # Check that we have common GitHub tools (using actual tool names from MCP server)
        common_tools = ["list_branches", "get_me", "search_repositories", "get_file_contents"]
        for tool_name in common_tools:
            assert any(tool_name in name for name in tool_names), f"Tool containing '{tool_name}' not found in {tool_names}"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.mcp
    async def test_get_me_tool(self):
        """Test get_me tool functionality"""
        tools = await get_github_tools()
        get_me_tool = next((tool for tool in tools if "get_me" in tool.name), None)
        assert get_me_tool is not None, "get_me tool not found"
        
        try:
            # get_me tool typically doesn't require parameters
            result = await get_me_tool.ainvoke({})
            assert result is not None, "get_me tool returned None"
            assert "login" in str(result).lower(), "get_me result doesn't contain login info"
        except Exception as e:
            pytest.fail(f"get_me tool failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.mcp
    async def test_search_repositories_tool(self):
        """Test search_repositories tool functionality"""
        tools = await get_github_tools()
        search_tool = next((tool for tool in tools if "search_repositories" in tool.name), None)
        assert search_tool is not None, "search_repositories tool not found"
        
        try:
            # Search for a popular repository with proper parameters
            result = await search_tool.ainvoke({"query": "microsoft/vscode"})
            assert result is not None, "search_repositories tool returned None"
            assert "vscode" in str(result).lower(), "Search result doesn't contain vscode"
        except Exception as e:
            pytest.fail(f"search_repositories tool failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
