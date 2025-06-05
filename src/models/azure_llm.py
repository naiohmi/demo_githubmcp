"""Azure OpenAI LLM provider implementation."""

from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_openai import AzureChatOpenAI

from src.config.settings import get_settings
from src.config.parameters import AGENT_TEMPERATURE, AGENT_STREAMING
from src.services.langfuse_service import LangfuseService, get_langfuse_service
from .base_provider import BaseLLMProvider


class AzureLLMProvider(BaseLLMProvider):
    """Azure OpenAI LLM provider implementation."""
    
    provider_name = "azure"
    
    def __init__(self, langfuse_service: Optional[LangfuseService] = None):
        """Initialize Azure LLM provider.
        
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
    ) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM with tools and Langfuse integration.
        
        Args:
            model_name: The Azure deployment/model name (e.g., "gpt-4o")
            tools: List of tools to bind to the LLM for function calling
            user_id: User identifier for Langfuse tracking
            session_id: Session identifier for Langfuse tracking
            trace_id: Trace identifier for Langfuse tracking
            message_id: Message identifier for Langfuse tracking
            **kwargs: Additional Azure-specific arguments
            
        Returns:
            Configured AzureChatOpenAI instance with bound tools
            
        Raises:
            Exception: If Azure configuration is invalid or connection fails
        """
        
        # Get Langfuse callback handler from service
        langfuse_handler = self.langfuse_service.create_callback_handler(
            provider="azure",
            model_name=model_name,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            message_id=message_id,
            metadata=kwargs.get("metadata")
        )
        
        # Create Azure OpenAI LLM instance
        llm = AzureChatOpenAI(
            azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
            api_key=self.settings.AZURE_OPENAI_API_KEY,
            api_version=self.settings.AZURE_OPENAI_API_VERSION,
            deployment_name=model_name,
            model=model_name,
            temperature=AGENT_TEMPERATURE,
            streaming=AGENT_STREAMING,
            callbacks=[langfuse_handler]
        )
        
        # Bind tools to enable function calling
        llm_with_tools = llm.bind_tools(tools=tools)
        return llm_with_tools