#!/usr/bin/env python3
"""
Environment and setup validation tests
"""
import os
import sys
import subprocess
from pathlib import Path
import pytest

from src.config.settings import get_settings


class TestEnvironmentSetup:
    """Test environment configuration and setup"""
    
    @pytest.mark.unit
    def test_python_version(self):
        """Test Python version is 3.11+"""
        version = sys.version_info
        assert version.major == 3 and version.minor >= 11, f"Python 3.11+ required, found: {version.major}.{version.minor}"
    
    @pytest.mark.unit
    def test_mcp_server_binary_exists(self):
        """Test GitHub MCP server binary exists"""
        mcp_server_path = Path(__file__).parent.parent / "mcp_server" / "github-mcp-server"
        assert mcp_server_path.exists(), "GitHub MCP server binary not found"
        assert mcp_server_path.is_file(), "MCP server path is not a file"
    
    @pytest.mark.unit
    def test_env_file_exists(self):
        """Test .env file exists"""
        env_path = Path(__file__).parent.parent / ".env"
        assert env_path.exists(), ".env file not found"
    
    @pytest.mark.unit
    def test_required_environment_variables(self):
        """Test required environment variables are set"""
        settings = get_settings()
        
        # Check Azure OpenAI settings
        assert settings.AZURE_OPENAI_API_KEY, "AZURE_OPENAI_API_KEY not set"
        assert not settings.AZURE_OPENAI_API_KEY.startswith("your_"), "AZURE_OPENAI_API_KEY still has template value"
        
        assert settings.AZURE_OPENAI_ENDPOINT, "AZURE_OPENAI_ENDPOINT not set"
        assert not settings.AZURE_OPENAI_ENDPOINT.startswith("https://your-"), "AZURE_OPENAI_ENDPOINT still has template value"
        
        # Check GitHub settings
        assert settings.GITHUB_PERSONAL_ACCESS_TOKEN, "GITHUB_PERSONAL_ACCESS_TOKEN not set"
        assert not settings.GITHUB_PERSONAL_ACCESS_TOKEN.startswith("your_"), "GITHUB_PERSONAL_ACCESS_TOKEN still has template value"
    
    @pytest.mark.unit
    def test_optional_langfuse_variables(self):
        """Test Langfuse variables (optional but warn if not set)"""
        settings = get_settings()
        
        if not settings.LANGFUSE_SECRET_KEY or settings.LANGFUSE_SECRET_KEY.startswith("your_"):
            print("⚠️  Warning: LANGFUSE_SECRET_KEY not configured (observability disabled)")
        
        if not settings.LANGFUSE_PUBLIC_KEY or settings.LANGFUSE_PUBLIC_KEY.startswith("your_"):
            print("⚠️  Warning: LANGFUSE_PUBLIC_KEY not configured (observability disabled)")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
