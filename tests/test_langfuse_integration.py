"""Integration tests for Langfuse service with LLM providers."""

import pytest
import uuid
from unittest.mock import MagicMock, patch
from typing import Generator

from src.config.settings import Settings
from src.services.langfuse_service import LangfuseService, get_langfuse_service
from src.models.azure_llm import AzureLLMProvider
from src.models.ollama_llm import OllamaLLMProvider

@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing test settings with mock credentials."""
    settings = Settings()
    return settings

@pytest.fixture
def langfuse_service(test_settings) -> LangfuseService:
    """Fixture providing a LangfuseService instance with test settings."""
    return LangfuseService(settings=test_settings)

@pytest.fixture
def mock_tool() -> Generator:
    """Fixture providing a mock tool."""
    tool = MagicMock()
    tool.name = "test-tool"
    tool.description = "A test tool for integration testing"
    yield tool

@pytest.mark.integration
@patch('src.models.azure_llm.AzureChatOpenAI')
@patch('src.models.ollama_llm.ChatOllama')
def test_full_integration_flow(mock_ollama, mock_azure, langfuse_service, test_settings, mock_tool):
    """Test the complete integration flow from service to providers."""
    
    # Setup mocks
    mock_azure_instance = MagicMock()
    mock_azure_instance.bind_tools.return_value = mock_azure_instance
    mock_azure.return_value = mock_azure_instance
    
    mock_ollama_instance = MagicMock()
    mock_ollama_instance.bind_tools.return_value = mock_ollama_instance
    mock_ollama.return_value = mock_ollama_instance
    
    # Test data
    user_id = "test-user"
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    # 1. Test service health and configuration
    health_status = langfuse_service.get_health_status()
    assert health_status["configured"] is True
    assert health_status["has_secret_key"] is True
    assert health_status["has_public_key"] is True
    
    # 2. Test Azure provider integration
    azure_provider = AzureLLMProvider(langfuse_service=langfuse_service)
    assert azure_provider.validate_config() is True
    
    # Create Azure LLM (now mocked)
    azure_llm = azure_provider.create_llm(
        model_name="gpt-4o",  # Using the model name from AZURE_MODEL in .env
        tools=[mock_tool],
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        message_id=message_id,
        metadata={"test_integration": True}
    )
    assert azure_llm is not None
    
    # Verify Azure LLM was created with correct parameters
    mock_azure.assert_called_once()
    call_kwargs = mock_azure.call_args[1]
    assert call_kwargs["azure_endpoint"] == test_settings.AZURE_OPENAI_ENDPOINT
    assert call_kwargs["api_key"] == test_settings.AZURE_OPENAI_API_KEY
    assert call_kwargs["deployment_name"] == "gpt-4o"  # Matches AZURE_MODEL in .env
    assert call_kwargs["model"] == "gpt-4o"  # Matches AZURE_MODEL in .env
    assert len(call_kwargs["callbacks"]) == 1  # Langfuse callback
    
    # 3. Test Ollama provider integration
    ollama_provider = OllamaLLMProvider(langfuse_service=langfuse_service)
    assert ollama_provider.validate_config() is True
    
    # Create Ollama LLM (now mocked)
    ollama_llm = ollama_provider.create_llm(
        model_name="llama3.2",  # Matches OLLAMA_MODEL in .env
        tools=[mock_tool],
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        message_id=message_id,
        metadata={"test_integration": True}
    )
    assert ollama_llm is not None
    
    # Verify Ollama LLM was created with correct parameters
    mock_ollama.assert_called_once()
    ollama_call_kwargs = mock_ollama.call_args[1]
    assert ollama_call_kwargs["base_url"] == test_settings.OLLAMA_ENDPOINT
    assert ollama_call_kwargs["model"] == "llama3.2"
    assert len(ollama_call_kwargs["callbacks"]) == 1  # Langfuse callback
    
    # 4. Test trace management
    with langfuse_service.trace_manager.trace_context(
        name="test-trace",
        user_id=user_id,
        session_id=session_id
    ) as new_trace_id:
        assert new_trace_id is not None
        trace_url = langfuse_service.trace_manager.get_trace_url(new_trace_id)
        assert trace_url.startswith(test_settings.LANGFUSE_HOST)
        assert new_trace_id in trace_url
    
    # 5. Test session management
    new_session_id = langfuse_service.session_manager.create_session_context(
        user_id=user_id,
        metadata={"test_session": True}
    )
    assert new_session_id is not None
    
    # 6. Verify singleton pattern
    service2 = get_langfuse_service()
    assert isinstance(service2, LangfuseService)
    assert id(langfuse_service) != id(service2)  # Different because we used a custom settings

@pytest.mark.unit
def test_service_error_handling(langfuse_service):
    """Test error handling in the Langfuse service."""
    
    # Test with missing user_id
    with pytest.raises(ValueError, match="Empty user_id not allowed"):
        langfuse_service.create_callback_handler(
            provider="test",
            model_name="test-model",
            user_id="",  # Empty user_id
            session_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            message_id=str(uuid.uuid4())
        )
    
    # Test with invalid provider
    handler = langfuse_service.create_callback_handler(
        provider="invalid-provider",  # Should still work, just logs metadata
        model_name="test-model",
        user_id="test-user",
        session_id=str(uuid.uuid4()),
        trace_id=str(uuid.uuid4()),
        message_id=str(uuid.uuid4())
    )
    assert handler is not None
    assert handler.metadata["provider"] == "invalid-provider"