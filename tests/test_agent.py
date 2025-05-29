#!/usr/bin/env python3
"""
Agent integration tests
"""
import asyncio
import sys
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.github_agent import create_github_agent


class TestGitHubAgent:
    """Test GitHub agent functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """Test that agent can be created"""
        try:
            agent = await create_github_agent()
            assert agent is not None, "Failed to create GitHub agent"
        except Exception as e:
            pytest.fail(f"Failed to create agent: {e}")
    
    @pytest.mark.asyncio
    async def test_simple_query(self):
        """Test agent can handle simple queries"""
        try:
            agent = await create_github_agent()
            
            # Test with a simple query
            response = await agent.ainvoke("Who am I on GitHub?")
            assert response is not None, "Agent returned None response"
            assert len(str(response)) > 0, "Agent returned empty response"
            
        except Exception as e:
            pytest.fail(f"Agent query failed: {e}")
    
    @pytest.mark.asyncio
    async def test_repository_query(self):
        """Test agent can handle repository queries"""
        try:
            agent = await create_github_agent()
            
            # Test repository search
            response = await agent.ainvoke("Find repositories about python")
            assert response is not None, "Agent returned None for repository query"
            assert "python" in str(response).lower(), "Response doesn't mention python"
            
        except Exception as e:
            pytest.fail(f"Repository query failed: {e}")


if __name__ == "__main__":
    # Run tests directly  
    pytest.main([__file__, "-v"])
