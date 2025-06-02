"""Tests for LLM providers with proper mocking to avoid import issues."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from langchain_core.tools import BaseTool

# Test constants
TEST_USER_ID = "test-user"
TEST_SESSION_ID = "test-session"
TEST_TRACE_ID = "test-trace"
TEST_MESSAGE_ID = "test-message"


@pytest.fixture
def mock_settings():
    """Fixture providing test settings."""
    with patch('src.config.settings.Settings') as MockSettings:
        settings = MockSettings.return_value
        settings.AZURE_OPENAI_API_KEY = "test-key"
        settings.AZURE_OPENAI_ENDPOINT = "test-endpoint"
        settings.AZURE_OPENAI_API_VERSION = "2025-01-01"
        settings.OLLAMA_ENDPOINT = "http://test-ollama:11434"
        yield settings


@pytest.fixture
def mock_langfuse_service():
    """Fixture providing a mock LangfuseService."""
    service = MagicMock()
    mock_handler = MagicMock()
    service.create_callback_handler.return_value = mock_handler
    return service


@pytest.fixture
def mock_tool():
    """Fixture providing a mock tool."""
    tool = MagicMock(spec=BaseTool)
    tool.name = "test-tool"
    tool.description = "A test tool"
    tool.__name__ = "test_tool"  # Add __name__ attribute
    return tool


class TestAzureLLMProvider:
    """Tests for the Azure LLM provider."""
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_initialization_with_service(self, mock_langfuse_service):
        """Test provider initialization with LangfuseService."""
        with patch('src.services.langfuse_service.CallbackHandler'):
            with patch('langfuse.callback.CallbackHandler'):
                from src.models.azure_llm import AzureLLMProvider
                
                provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
                assert provider.langfuse_service == mock_langfuse_service
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_create_llm(self, mock_langfuse_service, mock_tool, mock_settings):
        """Test LLM creation with Langfuse integration."""
        with patch('src.services.langfuse_service.CallbackHandler'):
            with patch('langfuse.callback.CallbackHandler'):
                with patch('src.models.azure_llm.AzureChatOpenAI') as mock_azure_class:
                    from src.models.azure_llm import AzureLLMProvider
                    
                    # Setup the mock
                    mock_llm = MagicMock()
                    mock_azure_class.return_value = mock_llm
                    mock_llm.bind_tools.return_value = mock_llm
                    
                    provider = AzureLLMProvider(langfuse_service=mock_langfuse_service)
                    
                    llm = provider.create_llm(
                        model_name="gpt-4o",
                        tools=[mock_tool],
                        user_id=TEST_USER_ID,
                        session_id=TEST_SESSION_ID,
                        trace_id=TEST_TRACE_ID,
                        message_id=TEST_MESSAGE_ID
                    )
                    
                    # Verify service was used to create handler
                    mock_langfuse_service.create_callback_handler.assert_called_once_with(
                        provider="azure",
                        model_name="gpt-4o",
                        user_id=TEST_USER_ID,
                        session_id=TEST_SESSION_ID,
                        trace_id=TEST_TRACE_ID,
                        message_id=TEST_MESSAGE_ID,
                        metadata=None
                    )
                    
                    # Verify Azure LLM was configured correctly
                    mock_azure_class.assert_called_once()
                    assert llm == mock_llm
                    mock_llm.bind_tools.assert_called_once_with(tools=[mock_tool])


class TestOllamaLLMProvider:
    """Tests for the Ollama LLM provider."""
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_initialization_with_service(self, mock_langfuse_service):
        """Test provider initialization with LangfuseService."""
        with patch('src.services.langfuse_service.CallbackHandler'):
            with patch('langfuse.callback.CallbackHandler'):
                from src.models.ollama_llm import OllamaLLMProvider
                
                provider = OllamaLLMProvider(langfuse_service=mock_langfuse_service)
                assert provider.langfuse_service == mock_langfuse_service
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_create_llm(self, mock_langfuse_service, mock_tool, mock_settings):
        """Test LLM creation with Langfuse integration."""
        with patch('src.services.langfuse_service.CallbackHandler'):
            with patch('langfuse.callback.CallbackHandler'):
                with patch('src.models.ollama_llm.ChatOllama') as mock_ollama_class:
                    from src.models.ollama_llm import OllamaLLMProvider
                    
                    # Setup the mock
                    mock_llm = MagicMock()
                    mock_ollama_class.return_value = mock_llm
                    mock_llm.bind_tools.return_value = mock_llm
                    
                    provider = OllamaLLMProvider(langfuse_service=mock_langfuse_service)
                    
                    llm = provider.create_llm(
                        model_name="llama3.2",
                        tools=[mock_tool],
                        user_id=TEST_USER_ID,
                        session_id=TEST_SESSION_ID,
                        trace_id=TEST_TRACE_ID,
                        message_id=TEST_MESSAGE_ID
                    )
                    
                    # Verify service was used to create handler
                    mock_langfuse_service.create_callback_handler.assert_called_once_with(
                        provider="ollama",
                        model_name="llama3.2",
                        user_id=TEST_USER_ID,
                        session_id=TEST_SESSION_ID,
                        trace_id=TEST_TRACE_ID,
                        message_id=TEST_MESSAGE_ID,
                        metadata=None
                    )
                    
                    # Verify Ollama LLM was configured correctly
                    mock_ollama_class.assert_called_once()
                    assert llm == mock_llm
                    mock_llm.bind_tools.assert_called_once_with(tools=[mock_tool])
    
    @pytest.mark.unit
    @pytest.mark.provider
    def test_validate_config(self, mock_settings):
        """Test Ollama configuration validation."""
        with patch('src.services.langfuse_service.CallbackHandler'):
            with patch('langfuse.callback.CallbackHandler'):
                from src.models.ollama_llm import OllamaLLMProvider
                
                provider = OllamaLLMProvider()
                
                # Test with valid config
                with patch.object(provider.settings, 'OLLAMA_ENDPOINT', 'http://test-ollama:11434'):
                    assert provider.validate_config() is True
                
                # Test with invalid config
                with patch.object(provider.settings, 'OLLAMA_ENDPOINT', None):
                    assert provider.validate_config() is False