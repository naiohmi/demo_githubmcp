"""LLM model registry and factory for dynamic provider switching."""

import warnings
from typing import List, Dict, Type
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel

from src.models.base_provider import BaseLLMProvider
from src.models.azure_llm import AzureLLMProvider
from src.models.ollama_llm import OllamaLLMProvider


class LLMModelRegistry:
    """Registry for managing LLM providers and model creation."""
    
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {
            "azure": AzureLLMProvider(),
            "ollama": OllamaLLMProvider()
        }
    
    def create_llm_with_tools(
        self,
        llm_model_name: str,
        tools: List[BaseTool],
        user_id: str,
        session_id: str,
        trace_id: str,
        message_id: str,
        **kwargs
    ) -> BaseChatModel:
        """Create LLM instance based on provider:model format.
        
        Args:
            llm_model_name: Format "provider:model" (e.g., "azure:gpt-4o", "ollama:llama2")
            tools: List of tools to bind to the LLM for function calling
            user_id: User identifier for Langfuse tracking
            session_id: Session identifier for Langfuse tracking
            trace_id: Trace identifier for Langfuse tracking
            message_id: Message identifier for Langfuse tracking
            **kwargs: Additional arguments for provider
            
        Returns:
            Configured LLM instance with bound tools
            
        Raises:
            ValueError: If provider or model format is invalid
            RuntimeError: If provider configuration is invalid
        """
        provider_name, model_name = self._parse_model_name(llm_model_name)
        
        if provider_name not in self._providers:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Available: {list(self._providers.keys())}"
            )
        
        provider = self._providers[provider_name]
        
        if not provider.validate_config():
            raise RuntimeError(
                f"Invalid configuration for provider: {provider_name}. "
                f"Please check your environment variables."
            )
        
        return provider.create_llm(
            model_name=model_name,
            tools=tools,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            message_id=message_id,
            **kwargs
        )
    
    def _parse_model_name(self, llm_model_name: str) -> tuple[str, str]:
        """Parse provider:model format.
        
        Args:
            llm_model_name: Format "provider:model"
            
        Returns:
            Tuple of (provider_name, model_name)
            
        Raises:
            ValueError: If format is invalid
        """
        if ":" not in llm_model_name:
            raise ValueError(
                f"Invalid model name format: {llm_model_name}. "
                "Expected format: 'provider:model' (e.g., 'azure:gpt-4o', 'ollama:llama2')"
            )
        
        parts = llm_model_name.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid model name format: {llm_model_name}")
        
        provider_name, model_name = parts
        if not provider_name or not model_name:
            raise ValueError(f"Provider and model name cannot be empty: {llm_model_name}")
        
        return provider_name, model_name
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self._providers.keys())
    
    def get_supported_models(self, provider_name: str) -> List[str]:
        """Get supported models for a provider."""
        if provider_name not in self._providers:
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        return self._providers[provider_name].get_supported_models()
    
    def list_all_models(self) -> Dict[str, List[str]]:
        """Get all supported models grouped by provider."""
        return {
            provider: self.get_supported_models(provider)
            for provider in self.get_available_providers()
        }


# Global registry instance
_registry = None

def get_llm_registry() -> LLMModelRegistry:
    """Get global LLM registry instance."""
    global _registry
    if _registry is None:
        _registry = LLMModelRegistry()
    return _registry


def create_llm_with_tools(
    llm_model_name: str,
    tools: List[BaseTool],
    user_id: str,
    session_id: str,
    trace_id: str,
    message_id: str,
    **kwargs
) -> BaseChatModel:
    """Create LLM with tools using the global registry.
    
    This is the main entry point for creating LLM instances.
    
    Args:
        llm_model_name: Format "provider:model" (e.g., "azure:gpt-4o", "ollama:llama2")
        tools: List of tools to bind to the LLM for function calling
        user_id: User identifier for Langfuse tracking
        session_id: Session identifier for Langfuse tracking
        trace_id: Trace identifier for Langfuse tracking
        message_id: Message identifier for Langfuse tracking
        **kwargs: Additional provider-specific arguments
        
    Returns:
        Configured LLM instance with bound tools
        
    Raises:
        ValueError: If provider or model format is invalid
        RuntimeError: If provider configuration is invalid
    """
    registry = get_llm_registry()
    return registry.create_llm_with_tools(
        llm_model_name=llm_model_name,
        tools=tools,
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        message_id=message_id,
        **kwargs
    )