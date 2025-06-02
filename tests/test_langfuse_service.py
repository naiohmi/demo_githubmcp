"""Tests for the Langfuse service implementation."""

import pytest
from unittest.mock import MagicMock, patch
from langfuse.callback import CallbackHandler

from src.config.settings import Settings
from src.services.langfuse_service import (
    LangfuseService,
    CallbackFactory,
    CallbackConfig,
    get_langfuse_service
)

# Test data
TEST_CONFIG = CallbackConfig(
    provider="test-provider",
    model_name="test-model",
    user_id="test-user",
    session_id="test-session",
    trace_id="test-trace",
    message_id="test-message"
)

@pytest.fixture
def mock_settings():
    """Fixture providing test settings."""
    return Settings()

@pytest.fixture
def mock_callback_handler():
    """Fixture providing a mock callback handler."""
    return MagicMock(spec=CallbackHandler)

@pytest.fixture
def langfuse_service(mock_settings):
    """Fixture providing a LangfuseService instance with test settings."""
    return LangfuseService(settings=mock_settings)

class TestCallbackFactory:
    """Tests for the CallbackFactory class."""
    
    @pytest.mark.unit
    def test_create_handler_basic(self, mock_settings):
        """Test basic callback handler creation."""
        factory = CallbackFactory(mock_settings)
        handler = factory.create_handler(TEST_CONFIG)
        
        assert isinstance(handler, CallbackHandler)
        assert handler.user_id == TEST_CONFIG.user_id
        assert handler.session_id == TEST_CONFIG.session_id
        
    def test_create_handler_with_metadata(self, mock_settings):
        """Test callback handler creation with custom metadata."""
        factory = CallbackFactory(mock_settings)
        config = TEST_CONFIG
        config.metadata = {"custom": "value"}
        
        handler = factory.create_handler(config)
        assert isinstance(handler, CallbackHandler)
        assert handler.metadata.get("custom") == "value"
        assert handler.metadata.get("provider") == TEST_CONFIG.provider

class TestLangfuseService:
    """Tests for the LangfuseService class."""
    
    def test_create_callback_handler(self, langfuse_service):
        """Test callback handler creation through service."""
        handler = langfuse_service.create_callback_handler(
            provider=TEST_CONFIG.provider,
            model_name=TEST_CONFIG.model_name,
            user_id=TEST_CONFIG.user_id,
            session_id=TEST_CONFIG.session_id,
            trace_id=TEST_CONFIG.trace_id,
            message_id=TEST_CONFIG.message_id
        )
        
        assert isinstance(handler, CallbackHandler)
        assert handler.user_id == TEST_CONFIG.user_id
        assert handler.session_id == TEST_CONFIG.session_id
    
    def test_create_callback_handler_with_metadata(self, langfuse_service):
        """Test callback handler creation with custom metadata."""
        custom_metadata = {"custom_field": "test_value"}
        
        handler = langfuse_service.create_callback_handler(
            provider=TEST_CONFIG.provider,
            model_name=TEST_CONFIG.model_name,
            user_id=TEST_CONFIG.user_id,
            session_id=TEST_CONFIG.session_id,
            trace_id=TEST_CONFIG.trace_id,
            message_id=TEST_CONFIG.message_id,
            metadata=custom_metadata
        )
        
        assert isinstance(handler, CallbackHandler)
        assert handler.metadata.get("custom_field") == "test_value"
    
    def test_validate_configuration_valid(self, langfuse_service):
        """Test configuration validation with valid settings."""
        with patch.object(langfuse_service.settings, 'LANGFUSE_SECRET_KEY', 'test-key'), \
             patch.object(langfuse_service.settings, 'LANGFUSE_PUBLIC_KEY', 'test-key'):
            
            is_valid, missing = langfuse_service.validate_configuration()
            assert is_valid
            assert not missing
    
    def test_validate_configuration_invalid(self, langfuse_service):
        """Test configuration validation with missing settings."""
        with patch.object(langfuse_service.settings, 'LANGFUSE_SECRET_KEY', None), \
             patch.object(langfuse_service.settings, 'LANGFUSE_PUBLIC_KEY', None):
            
            is_valid, missing = langfuse_service.validate_configuration()
            assert not is_valid
            assert "LANGFUSE_SECRET_KEY" in missing
            assert "LANGFUSE_PUBLIC_KEY" in missing
    
    def test_get_health_status(self, langfuse_service):
        """Test health status reporting."""
        with patch.object(langfuse_service.settings, 'LANGFUSE_SECRET_KEY', 'test-key'), \
             patch.object(langfuse_service.settings, 'LANGFUSE_PUBLIC_KEY', 'test-key'), \
             patch.object(langfuse_service.settings, 'LANGFUSE_HOST', 'test-host'):
            
            status = langfuse_service.get_health_status()
            assert status["configured"] is True
            assert status["host"] == "test-host"
            assert status["has_secret_key"] is True
            assert status["has_public_key"] is True

def test_get_langfuse_service_singleton():
    """Test the global service singleton pattern."""
    service1 = get_langfuse_service()
    service2 = get_langfuse_service()
    
    assert service1 is service2
    assert isinstance(service1, LangfuseService)