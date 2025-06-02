#!/usr/bin/env python3
"""
Agent integration tests
"""
import asyncio
import uuid
import pytest

from src.agents.github_agent import create_github_agent


class TestGitHubAgent:
    """Test GitHub agent functionality"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_creation(self):
        """Test that agent can be created"""
        try:
            # Create agent with test parameters
            user_id = "test_user"
            session_id = str(uuid.uuid4())
            trace_id = str(uuid.uuid4())
            llm_model_name = "gpt-4o"
            agent = await create_github_agent(user_id, session_id, trace_id, llm_model_name)
            assert agent is not None, "Failed to create GitHub agent"
        except Exception as e:
            pytest.fail(f"Failed to create agent: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simple_query(self):
        """Test agent can handle simple queries"""
        try:
            # Create agent with test parameters
            user_id = "test_user"
            session_id = str(uuid.uuid4())
            trace_id = str(uuid.uuid4())
            llm_model_name = "azure:gpt-4o"
            agent = await create_github_agent(user_id, session_id, trace_id, llm_model_name)
            
            # Test with a simple query
            message_id = str(uuid.uuid4())
            response = await agent.ainvoke("Who am I on GitHub?", message_id)
            assert response is not None, "Agent returned None response"
            assert len(str(response)) > 0, "Agent returned empty response"
            
        except Exception as e:
            pytest.fail(f"Agent query failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_repository_query(self):
        """Test agent can handle repository queries"""
        try:
            # Create agent with test parameters
            user_id = "test_user"
            session_id = str(uuid.uuid4())
            trace_id = str(uuid.uuid4())
            llm_model_name = "azure:gpt-4o"
            agent = await create_github_agent(user_id, session_id, trace_id, llm_model_name)
            
            # Test repository search
            message_id = str(uuid.uuid4())
            response = await agent.ainvoke("Find repositories about python", message_id)
            assert response is not None, "Agent returned None for repository query"
            assert "python" in str(response).lower(), "Response doesn't mention python"
            
        except Exception as e:
            pytest.fail(f"Repository query failed: {e}")


if __name__ == "__main__":
    # Run tests directly  
    pytest.main([__file__, "-v"])
