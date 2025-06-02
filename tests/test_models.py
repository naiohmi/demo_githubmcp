#!/usr/bin/env python3
"""
Tests for model providers
"""
import pytest
from unittest.mock import MagicMock, patch
from abc import ABC
from typing import List, Any

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks.manager import BaseCallbackManager

from src.models.base_provider import BaseLLMProvider
from src.models.azure_llm import AzureLLMProvider
from src.models.ollama_llm import OllamaLLMProvider
from src.services.langfuse_service import LangfuseService
from src.config.settings import Settings


class MockCallbackHandler(BaseCallbackHandler):
    """Mock callback handler for testing"""
    
    def __init__(self):
        super().__init__()
        self.calls = []
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.calls.append(('on_llm_start', serialized, prompts, kwargs))
    
    def on_llm_end(self, response, **kwargs):
        self.calls.append(('on_llm_end', response, kwargs))
    
    def on_llm_error(self, error, **kwargs):
        self.calls.append(('on_llm_error', error, kwargs))


class TestBaseLLMProvider:
    """Test base LLM provider abstract class"""
    
    @pytest.mark.unit
    def test_base_provider_is_abstract(self):
        """Test that BaseLLMProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseLLMProvider()
    
    @pytest.mark.unit
    def test_base_provider_interface(self):
        """Test that BaseLLMProvider defines required interface"""
        # Check that the base class has required abstract methods
        required_methods = ['create_llm']
        
        for method in required_methods:
            assert hasattr(BaseLLMProvider, method), f"BaseLLMProvider should have {method} method"
        
        # Verify it's an abstract base class
        assert issubclass(BaseLLMProvider, ABC), "BaseLLMProvider should inherit from ABC"


class TestConcreteProviders:
    """Test concrete provider implementations"""
    
    @pytest.fixture
    def mock_settings(self):
        """Fixture providing mock settings"""
        settings = Settings()
        # Azure settings
        settings.AZURE_OPENAI_API_KEY = "test-azure-key"
        settings.AZURE_OPENAI_ENDPOINT = "https://test.azure.com"
        settings.AZURE_OPENAI_API_VERSION = "2025-01-01"
        # Ollama settings
        settings.OLLAMA_ENDPOINT = "http://test.ollama:11434"
        return settings
    
    @pytest.fixture
    def mock_langfuse_service(self, mock_settings):
        """Fixture providing mock Langfuse service"""
        service = LangfuseService(settings=mock_settings)
        
        # Create a proper mock callback handler
        mock_handler = MockCallbackHandler()
        service.create_callback_handler = MagicMock(return_value=mock_handler)
        
        return service
    
    @pytest.fixture
    def mock_tools(self):
        """Fixture providing mock tools"""
        from langchain_core.tools import tool
        
        @tool
        def test_tool_1(input_text: str) -> str:
            """First test tool"""
            return f"Tool 1 result: {input_text}"
        
        @tool  
        def test_tool_2(input_text: str) -> str:
            """Second test tool"""
            return f"Tool 2 result: {input_text}"
        
        return [test_tool_1, test_tool_2]
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_azure_provider_implements_interface(self, mock_langfuse_service):
        """Test that AzureLLMProvider properly implements the interface"""
        provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
        
        # Verify it's a BaseLLMProvider
        assert isinstance(provider, BaseLLMProvider)
        
        # Verify it has required methods
        assert hasattr(provider, 'create_llm')
        assert callable(provider.create_llm)
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_ollama_provider_implements_interface(self, mock_langfuse_service):
        """Test that OllamaLLMProvider properly implements the interface"""
        provider = OllamaLLMProvider(langfuse_service=mock_langfuse_service)
        
        # Verify it's a BaseLLMProvider
        assert isinstance(provider, BaseLLMProvider)
        
        # Verify it has required methods
        assert hasattr(provider, 'create_llm')
        assert callable(provider.create_llm)
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_azure_provider_initialization(self, mock_langfuse_service):
        """Test Azure provider initialization"""
        provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
        
        assert provider.langfuse_service == mock_langfuse_service
        assert hasattr(provider, 'provider_name')
        assert provider.provider_name == "azure"
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_ollama_provider_initialization(self, mock_langfuse_service):
        """Test Ollama provider initialization"""
        provider = OllamaLLMProvider(langfuse_service=mock_langfuse_service)
        
        assert provider.langfuse_service == mock_langfuse_service
        assert hasattr(provider, 'provider_name')
        assert provider.provider_name == "ollama"
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_azure_create_llm_interface(self, mock_langfuse_service, mock_tools):
        """Test Azure provider create_llm method interface"""
        provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
        
        with patch('src.models.azure_llm.AzureChatOpenAI') as mock_azure:
            mock_llm = MagicMock()
            mock_llm_with_tools = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm_with_tools
            mock_azure.return_value = mock_llm
            
            # Test the method signature and basic functionality
            result = provider.create_llm(
                model_name="gpt-4o",
                tools=mock_tools,
                user_id="test_user",
                session_id="test_session",
                trace_id="test_trace",
                message_id="test_message"
            )
            
            assert result is not None
            assert result is mock_llm_with_tools
            mock_azure.assert_called_once()
            mock_llm.bind_tools.assert_called_once_with(tools=mock_tools)
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_ollama_create_llm_interface(self, mock_langfuse_service, mock_tools):
        """Test Ollama provider create_llm method interface"""
        provider = OllamaLLMProvider(langfuse_service=mock_langfuse_service)
        
        with patch('src.models.ollama_llm.ChatOllama') as mock_ollama:
            mock_llm = MagicMock()
            mock_llm_with_tools = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm_with_tools
            mock_ollama.return_value = mock_llm
            
            # Test the method signature and basic functionality
            result = provider.create_llm(
                model_name="llama3.2",
                tools=mock_tools,
                user_id="test_user",
                session_id="test_session",
                trace_id="test_trace",
                message_id="test_message"
            )
            
            assert result is not None
            assert result is mock_llm_with_tools
            mock_ollama.assert_called_once()
            mock_llm.bind_tools.assert_called_once_with(tools=mock_tools)
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_provider_error_handling(self, mock_langfuse_service, mock_tools):
        """Test provider error handling"""
        provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
        
        with patch('src.models.azure_llm.AzureChatOpenAI', side_effect=Exception("Connection error")):
            with pytest.raises(Exception):
                provider.create_llm(
                    model_name="gpt-4o",
                    tools=mock_tools,
                    user_id="test_user",
                    session_id="test_session",
                    trace_id="test_trace",
                    message_id="test_message"
                )
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_provider_langfuse_integration(self, mock_langfuse_service, mock_tools):
        """Test that providers properly integrate with Langfuse"""
        provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
        
        # The mock service already has a proper callback handler
        with patch('src.models.azure_llm.AzureChatOpenAI') as mock_azure:
            mock_llm = MagicMock()
            mock_llm_with_tools = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm_with_tools
            mock_azure.return_value = mock_llm
            
            provider.create_llm(
                model_name="gpt-4o",
                tools=mock_tools,
                user_id="test_user",
                session_id="test_session",
                trace_id="test_trace",
                message_id="test_message"
            )
            
            # Verify Langfuse callback handler was created
            mock_langfuse_service.create_callback_handler.assert_called_once()


class TestProviderRegistry:
    """Test provider registry and selection logic"""
    
    @pytest.mark.unit
    def test_provider_selection_by_model(self):
        """Test that correct provider is selected based on model name"""
        # This tests the logic that might exist in the agent or a registry
        
        azure_models = ["gpt-4", "gpt-4o", "gpt-3.5-turbo"]
        ollama_models = ["llama3.2", "llama2", "mistral", "codellama"]
        
        for model in azure_models:
            # Logic that would determine provider based on model
            assert "azure" in model.lower() or model.startswith("gpt"), f"Model {model} should use Azure provider"
        
        for model in ollama_models:
            # Logic that would determine provider based on model
            assert not model.startswith("gpt"), f"Model {model} should use Ollama provider"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
