"""LLM model factory for dynamic provider switching."""

from typing import List, Dict
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel

from src.models.azure_llm import AzureLLMProvider
from src.models.ollama_llm import OllamaLLMProvider
from src.config.settings import get_settings
from src.services.langfuse_service import get_langfuse_service


# Provider registry
_PROVIDERS = {
    "azure": AzureLLMProvider(),
    "ollama": OllamaLLMProvider()
}


def _parse_model_name(llm_model_name: str) -> tuple[str, str]:
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


def _get_services():
    """Get required services."""
    settings = get_settings()
    langfuse_service = get_langfuse_service()
    return langfuse_service, None, settings  # Redis service placeholder


def validate_provider_config(provider_name: str) -> bool:
    """Validate provider configuration."""
    settings = get_settings()
    
    if provider_name == "azure":
        return bool(settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT)
    elif provider_name == "ollama":
        return bool(settings.OLLAMA_ENDPOINT)
    else:
        return False


def create_llm_with_tools(
    llm_model_name: str,
    tools: List[BaseTool],
    user_id: str,
    session_id: str,
    trace_id: str,
    message_id: str,
    **kwargs
) -> BaseChatModel:
    """Create LLM instance based on provider:model format.
    
    Main entry point for creating LLM instances with tool binding.
    Handles langfuse integration at this layer.
    
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
    provider_name, model_name = _parse_model_name(llm_model_name)
    
    if provider_name not in _PROVIDERS:
        raise ValueError(
            f"Unsupported provider: {provider_name}. "
            f"Available: {list(_PROVIDERS.keys())}"
        )
    
    provider = _PROVIDERS[provider_name]
    
    # Get services
    langfuse_service, redis_service, settings = _get_services()
    
    # Validate provider configuration
    if not validate_provider_config(provider_name):
        if provider_name == "azure":
            raise RuntimeError(
                f"Invalid Azure configuration. Please check AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables."
            )
        elif provider_name == "ollama":
            raise RuntimeError(
                f"Invalid Ollama configuration. Please check OLLAMA_ENDPOINT environment variable."
            )
        else:
            raise RuntimeError(
                f"Invalid configuration for provider: {provider_name}."
            )
    
    # Create LLM instance
    return provider.create_llm(
        model_name=model_name,
        tools=tools,
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        message_id=message_id,
        **kwargs
    )