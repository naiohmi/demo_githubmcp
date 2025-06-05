#!/usr/bin/env python3
"""
Tests for utility modules
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import uuid
from typing import Dict, Any

from src.utils.prompt_loader import PromptLoader
from src.utils.session_context import SessionContext
from src.utils.state import AgentState
from src.utils.graph import create_agent_graph, should_continue, call_model
from src.utils.nodes import create_llm_with_tools, validate_provider_config


class TestPromptLoader:
    """Test prompt loading functionality"""
    
    @pytest.mark.unit
    def test_prompt_loader_initialization(self):
        """Test PromptLoader initialization"""
        loader = PromptLoader()
        assert loader is not None
        assert hasattr(loader, 'load_prompts')
    
    @pytest.mark.unit
    def test_load_prompts_with_valid_file(self):
        """Test loading prompts from valid YAML file"""
        mock_yaml_content = """
        system:
          base: "You are a helpful assistant"
        queries:
          branches: "List branches"
          repository_info: "Get repo info"
          pull_requests: "List PRs"
          pull_request_summary: "PR summary"
          commits: "List commits"
          file_content: "Get file"
          search_repos: "Search repos"
        test:
          example_queries:
            - "Example query 1"
            - "Example query 2"
        """
        
        with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
            with patch("yaml.safe_load") as mock_yaml_load:
                mock_yaml_load.return_value = {
                    "system": {
                        "base": "You are a helpful assistant"
                    },
                    "queries": {
                        "branches": "List branches",
                        "repository_info": "Get repo info",
                        "pull_requests": "List PRs",
                        "pull_request_summary": "PR summary",
                        "commits": "List commits",
                        "file_content": "Get file",
                        "search_repos": "Search repos"
                    },
                    "test": {
                        "example_queries": [
                            "Example query 1",
                            "Example query 2"
                        ]
                    }
                }
                
                loader = PromptLoader()
                prompts = loader.load_prompts("test_prompts.yaml")
                
                assert prompts.system.base == "You are a helpful assistant"
                assert prompts.queries.branches == "List branches"
                assert prompts.test.example_queries == ["Example query 1", "Example query 2"]
    
    @pytest.mark.unit
    def test_load_prompts_file_not_found(self):
        """Test handling of missing prompt files"""
        loader = PromptLoader()
        
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                loader.load_prompts("nonexistent.yaml")


class TestSessionContext:
    """Test session context management"""
    
    @pytest.mark.unit
    def test_session_context_creation(self):
        """Test session context creation"""
        context = SessionContext()
        assert context is not None
        
        # Default parameters should be generated
        user_id, session_id, trace_id, llm_model_name = context.get_session_parameters()
        assert user_id is not None
        assert session_id is not None
        assert trace_id is not None
        assert llm_model_name is not None
    
    @pytest.mark.unit
    def test_session_context_set_parameters(self):
        """Test setting session parameters"""
        context = SessionContext()
        
        user_id = "test_user"
        session_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        llm_model_name = "azure:gpt-4o"
        
        context.set_session_parameters(user_id, session_id, trace_id, llm_model_name)
        
        # Retrieve and verify parameters
        retrieved_params = context.get_session_parameters()
        assert retrieved_params[0] == user_id
        assert retrieved_params[1] == session_id
        assert retrieved_params[2] == trace_id
        assert retrieved_params[3] == llm_model_name


class TestAgentState:
    """Test agent state management"""
    
    @pytest.mark.unit
    def test_agent_state_initialization(self):
        """Test AgentState initialization"""
        from langchain_core.messages import HumanMessage, AIMessage
        
        state = AgentState(messages=[])
        assert state["messages"] == []
    
    @pytest.mark.unit
    def test_agent_state_with_messages(self):
        """Test AgentState with initial messages"""
        from langchain_core.messages import HumanMessage, AIMessage
        
        messages = [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]
        state = AgentState(messages=messages)
        
        assert len(state["messages"]) == 2
        assert state["messages"][0].content == "Hello"
        assert state["messages"][1].content == "Hi there!"


class TestGraphUtilities:
    """Test graph creation and utilities"""
    
    @pytest.mark.unit
    def test_create_agent_graph_exists(self):
        """Test that create_agent_graph function exists and can be imported"""
        from src.utils.graph import create_agent_graph
        assert callable(create_agent_graph)
    
    @pytest.mark.unit
    def test_should_continue_exists(self):
        """Test that should_continue function exists"""
        from src.utils.graph import should_continue
        assert callable(should_continue)
    
    @pytest.mark.unit
    def test_call_model_exists(self):
        """Test that call_model function exists"""
        from src.utils.graph import call_model
        assert callable(call_model)


class TestLLMUtilities:
    """Test LLM utility functions"""
    
    @pytest.mark.unit
    def test_validate_provider_config(self):
        """Test provider configuration validation"""
        assert validate_provider_config("azure") is not None
        assert validate_provider_config("ollama") is not None
    
    @pytest.mark.unit
    def test_create_llm_with_tools_exists(self):
        """Test that create_llm_with_tools function exists"""
        assert callable(create_llm_with_tools)


class TestCommonUtilities:
    """Test common utility functions"""
    
    @pytest.mark.unit
    def test_common_utilities_exist(self):
        """Test that common utilities module can be imported"""
        try:
            import src.utils.common
            assert True  # If import succeeds, test passes
        except ImportError:
            # If common.py doesn't have functions yet, just check it exists
            from pathlib import Path
            common_path = Path(__file__).parent.parent / "src" / "utils" / "common.py"
            assert common_path.exists(), "common.py utility file should exist"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
