#!/usr/bin/env python3
"""
GitHub Tools tests
"""
import asyncio
import sys
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.tools.github_tools import get_github_tools


class TestGitHubTools:
    """Test GitHub tool implementations"""
    
    def test_tools_loading(self):
        """Test that GitHub tools can be loaded"""
        tools = get_github_tools()
        assert len(tools) > 0, "No GitHub tools loaded"
        assert len(tools) == 20, f"Expected 20 tools, got {len(tools)}"
        
    def test_tool_names(self):
        """Test that all expected tools are present"""
        tools = get_github_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "github_get_me", "github_list_branches", "github_get_file_contents",
            "github_search_repositories", "github_search_code", "github_search_issues", "github_search_users",
            "github_list_commits", "github_get_commit",
            "github_list_pull_requests", "github_get_pull_request", "github_get_pull_request_files",
            "github_get_pull_request_comments", "github_get_pull_request_diff",
            "github_list_issues", "github_get_issue", "github_create_issue", "github_update_issue",
            "github_list_tags", "github_get_tag"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Expected tool '{expected_tool}' not found"
    
    @pytest.mark.asyncio
    async def test_get_me_tool(self):
        """Test get_me tool functionality"""
        tools = get_github_tools()
        get_me_tool = next((tool for tool in tools if tool.name == "github_get_me"), None)
        assert get_me_tool is not None, "github_get_me tool not found"
        
        try:
            result = await get_me_tool.arun("")
            assert result is not None, "get_me tool returned None"
            assert "login" in str(result).lower(), "get_me result doesn't contain login info"
        except Exception as e:
            pytest.fail(f"get_me tool failed: {e}")
    
    @pytest.mark.asyncio
    async def test_search_repositories_tool(self):
        """Test search_repositories tool functionality"""
        tools = get_github_tools()
        search_tool = next((tool for tool in tools if tool.name == "github_search_repositories"), None)
        assert search_tool is not None, "github_search_repositories tool not found"
        
        try:
            # Search for a popular repository
            result = await search_tool.arun("microsoft/vscode")
            assert result is not None, "search_repositories tool returned None"
            assert "vscode" in str(result).lower(), "Search result doesn't contain vscode"
        except Exception as e:
            pytest.fail(f"search_repositories tool failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
