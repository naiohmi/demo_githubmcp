#!/usr/bin/env python3
"""
Tests for service modules
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from typing import Dict, Any, List

from src.services.github_service import GitHubService


class TestGitHubService:
    """Test GitHub service functionality"""
    
    @pytest.mark.unit
    def test_github_service_initialization(self):
        """Test GitHub service initialization"""
        service = GitHubService()
        assert service is not None
        assert service.agent is None  # Agent is lazily initialized
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_github_service_agent_creation(self):
        """Test GitHub service agent creation"""
        service = GitHubService()
        
        # Mock dependencies
        with patch('src.services.github_service.get_session_context') as mock_context:
            with patch('src.services.github_service.create_github_agent') as mock_create:
                mock_session = MagicMock()
                mock_session.get_session_parameters.return_value = ("user", "session", "trace", "gpt-4o")
                mock_context.return_value = mock_session
                
                mock_agent = MagicMock()
                mock_create.return_value = mock_agent
                
                agent = await service._get_agent()
                
                assert agent is not None
                assert agent == mock_agent
                mock_create.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_github_search_repositories(self):
        """Test GitHub repository search through service"""
        service = GitHubService()
        
        with patch.object(service, '_get_agent') as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.return_value = "Found repositories: test-repo"
            mock_get_agent.return_value = mock_agent
            
            result = await service.search_repositories("test query")
            
            assert result is not None
            assert "test-repo" in str(result)
            mock_agent.ainvoke.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_github_get_user_info(self):
        """Test GitHub user info retrieval"""
        service = GitHubService()
        
        with patch.object(service, '_get_agent') as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.return_value = "User: test_user"
            mock_get_agent.return_value = mock_agent
            
            result = await service.get_user_info()
            
            assert result is not None
            assert "test_user" in str(result)
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_github_list_repositories(self):
        """Test GitHub repository listing"""
        service = GitHubService()
        
        with patch.object(service, '_get_agent') as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.return_value = "Repositories: repo1, repo2"
            mock_get_agent.return_value = mock_agent
            
            result = await service.list_repositories("test_user")
            
            assert result is not None
            assert "repo1" in str(result)
    
    @pytest.mark.unit
    def test_github_service_error_handling(self):
        """Test GitHub service error handling"""
        service = GitHubService()
        
        # Test that service can be created even with potential configuration issues
        assert service is not None
        assert hasattr(service, '_get_agent')


class TestServiceIntegration:
    """Test service integration patterns"""
    
    @pytest.mark.integration
    def test_service_initialization_pattern(self):
        """Test that all services follow consistent initialization pattern"""
        from src.services.langfuse_service import LangfuseService
        from src.services.github_service import GitHubService
        from src.config.settings import Settings
        
        settings = Settings()
        
        # Test that services can be initialized
        langfuse_service = LangfuseService(settings=settings)
        github_service = GitHubService()
        
        assert langfuse_service.settings == settings
        assert github_service is not None
    
    @pytest.mark.integration
    def test_service_configuration_validation(self):
        """Test that services properly validate configuration"""
        from src.services.langfuse_service import LangfuseService
        from src.services.github_service import GitHubService
        from src.config.settings import Settings
        
        settings = Settings()
        
        # Test Langfuse service configuration
        langfuse_service = LangfuseService(settings=settings)
        langfuse_health = langfuse_service.get_health_status()
        assert 'configured' in langfuse_health
        
        # Test GitHub service configuration
        github_service = GitHubService()
        assert github_service is not None
    
    @pytest.mark.unit
    def test_service_error_isolation(self):
        """Test that service errors are properly isolated"""
        from src.services.langfuse_service import LangfuseService
        from src.services.github_service import GitHubService
        from src.config.settings import Settings
        
        # Test that one service failure doesn't affect others
        settings = Settings()
        
        # Even with invalid settings, services should initialize without throwing
        try:
            langfuse_service = LangfuseService(settings=settings)
            github_service = GitHubService()
            
            # Services should exist even if not configured
            assert langfuse_service is not None
            assert github_service is not None
            
        except Exception as e:
            pytest.fail(f"Service initialization should not throw: {e}")


class TestServiceHealthChecks:
    """Test service health check functionality"""
    
    @pytest.mark.unit
    def test_langfuse_service_health_check(self):
        """Test that Langfuse service implements health check methods"""
        from src.services.langfuse_service import LangfuseService
        from src.config.settings import Settings
        
        settings = Settings()
        
        # Test Langfuse service
        langfuse_service = LangfuseService(settings=settings)
        assert hasattr(langfuse_service, 'get_health_status')
        assert callable(langfuse_service.get_health_status)
    
    @pytest.mark.unit
    def test_health_check_return_format(self):
        """Test that health checks return consistent format"""
        from src.services.langfuse_service import LangfuseService
        from src.config.settings import Settings
        
        settings = Settings()
        langfuse_service = LangfuseService(settings=settings)
        
        health_status = langfuse_service.get_health_status()
        
        # Health status should be a dict with specific keys
        assert isinstance(health_status, dict)
        assert 'configured' in health_status
        assert isinstance(health_status['configured'], bool)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
