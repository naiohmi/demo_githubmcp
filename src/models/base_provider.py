"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def create_llm(
        self,
        model_name: str,
        tools: List[BaseTool],
        user_id: str,
        session_id: str,
        trace_id: str,
        message_id: str,
        **kwargs
    ) -> BaseChatModel:
        """Create and configure LLM instance with tools.
        
        Args:
            model_name: The specific model name (without provider prefix)
            tools: List of tools to bind to the LLM for function calling
            user_id: User identifier for Langfuse tracking
            session_id: Session identifier for Langfuse tracking
            trace_id: Trace identifier for Langfuse tracking
            message_id: Message identifier for Langfuse tracking
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Configured LLM instance with bound tools
            
        Raises:
            Exception: If configuration is invalid or connection fails
        """
        pass