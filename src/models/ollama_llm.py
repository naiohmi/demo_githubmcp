"""Ollama LLM provider implementation."""

from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama

from src.config.settings import get_settings
from src.config.parameters import AGENT_TEMPERATURE
from src.services.langfuse_service import LangfuseService, get_langfuse_service
from .base_provider import BaseLLMProvider


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    provider_name = "ollama"
    
    def __init__(self, langfuse_service: Optional[LangfuseService] = None):
        """Initialize Ollama LLM provider.
        
        Args:
            langfuse_service: Optional LangfuseService instance (uses global if not provided)
        """
        self.settings = get_settings()
        self.langfuse_service = langfuse_service or get_langfuse_service()
    
    def create_llm(
        self,
        model_name: str,
        tools: List[BaseTool],
        user_id: str,
        session_id: str,
        trace_id: str,
        message_id: str,
        **kwargs
    ) -> ChatOllama:
        """Create Ollama LLM with tools and Langfuse integration.
        
        Args:
            model_name: The Ollama model name (e.g., "llama2", "mistral")
            tools: List of tools to bind to the LLM for function calling
            user_id: User identifier for Langfuse tracking
            session_id: Session identifier for Langfuse tracking
            trace_id: Trace identifier for Langfuse tracking
            message_id: Message identifier for Langfuse tracking
            **kwargs: Additional Ollama-specific arguments
            
        Returns:
            Configured ChatOllama instance with bound tools
            
        Raises:
            Exception: If Ollama configuration is invalid or connection fails
        """
        
        # Get Langfuse callback handler from service
        langfuse_handler = self.langfuse_service.create_callback_handler(
            provider="ollama",
            model_name=model_name,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            message_id=message_id,
            metadata=kwargs.get("metadata")
        )
        
        # Create Ollama LLM instance
        llm = ChatOllama(
            base_url=self.settings.OLLAMA_ENDPOINT,
            model=model_name,
            temperature=AGENT_TEMPERATURE,
            callbacks=[langfuse_handler]
        )
        
        # Bind tools to enable function calling
        llm_with_tools = llm.bind_tools(tools=tools)
        return llm_with_tools
    
    def validate_config(self) -> bool:
        """Validate Ollama configuration.
        
        Returns:
            True if Ollama endpoint is configured
        """
        return bool(self.settings.OLLAMA_ENDPOINT)
    
    def get_supported_models(self) -> List[str]:
        """Get supported Ollama models.
        
        Returns:
            List of commonly supported Ollama model names
        """
        return [
            "llama3.2",
        ]