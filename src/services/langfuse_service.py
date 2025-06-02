"""Comprehensive Langfuse observability service.

This service centralizes all Langfuse functionality, including:
- Callback handler creation
- Trace management
- Custom metrics collection
- Session management
- Configuration validation
"""

import uuid
import logging
import contextlib
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from langfuse.callback import CallbackHandler

from src.config.settings import Settings, get_settings

logger = logging.getLogger("langfuse")

@dataclass
class CallbackConfig:
    """Configuration for callback handler creation."""
    provider: str
    model_name: str
    user_id: str
    session_id: str
    trace_id: str
    message_id: str
    metadata: Optional[Dict[str, Any]] = None

class CallbackFactory:
    """Factory for creating configured Langfuse callback handlers."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def create_handler(self, config: CallbackConfig) -> CallbackHandler:
        """Create a configured Langfuse callback handler.
        
        Args:
            config: Callback configuration parameters
            
        Returns:
            Configured CallbackHandler instance
            
        Raises:
            ValueError: If required configuration is missing
        """
        # Prepare metadata with standard fields
        metadata = {
            "llm_model_name": f"{config.provider}:{config.model_name}",
            "message_id": config.message_id,
            "session_id": config.session_id,
            "trace_id": config.trace_id,
            "provider": config.provider
        }
        
        # Add any custom metadata
        if config.metadata:
            metadata.update(config.metadata)
            
        try:
            return CallbackHandler(
                secret_key=self.settings.LANGFUSE_SECRET_KEY,
                public_key=self.settings.LANGFUSE_PUBLIC_KEY,
                host=self.settings.LANGFUSE_HOST,
                session_id=config.session_id,
                user_id=config.user_id,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to create Langfuse callback handler: {str(e)}")
            raise

class TraceManager:
    """Manages Langfuse trace operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    @contextlib.contextmanager
    def trace_context(self, name: str, user_id: str, session_id: str):
        """Context manager for automatic trace management.
        
        Args:
            name: Name of the trace
            user_id: User identifier
            session_id: Session identifier
            
        Yields:
            str: Trace ID for the created trace
        """
        try:
            trace_id = str(uuid.uuid4())
            yield trace_id
        finally:
            # In the future, we can add trace cleanup or finalization here
            pass
            
    def get_trace_url(self, trace_id: str) -> str:
        """Get the Langfuse UI URL for a trace.
        
        Args:
            trace_id: The trace identifier
            
        Returns:
            str: URL to view the trace in Langfuse UI
        """
        return f"{self.settings.LANGFUSE_HOST}/trace/{trace_id}"

class MetricsCollector:
    """Collects and manages custom metrics."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def track_llm_performance(self, provider: str, model: str, duration: float,
                            tokens: Dict[str, int]) -> None:
        """Track LLM performance metrics.
        
        Args:
            provider: LLM provider name
            model: Model name
            duration: Request duration in seconds
            tokens: Token usage statistics
        """
        # TODO: Implement performance tracking using Langfuse SDK
        pass

class SessionManager:
    """Manages Langfuse session operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def create_session_context(self, user_id: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session context.
        
        Args:
            user_id: User identifier
            metadata: Optional session metadata
            
        Returns:
            str: Created session ID
        """
        return str(uuid.uuid4())

class LangfuseService:
    """Main Langfuse service that provides centralized access to all functionality."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the Langfuse service.
        
        Args:
            settings: Application settings (uses global settings if not provided)
        """
        self.settings = settings or get_settings()
        self.callback_factory = CallbackFactory(self.settings)
        self.trace_manager = TraceManager(self.settings)
        self.metrics_collector = MetricsCollector(self.settings)
        self.session_manager = SessionManager(self.settings)
        
    def create_callback_handler(
        self,
        provider: str,
        model_name: str,
        user_id: str,
        session_id: str,
        trace_id: str,
        message_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CallbackHandler:
        """Create a configured Langfuse callback handler.
        
        Args:
            provider: LLM provider name (e.g., "azure", "ollama")
            model_name: Model name without provider prefix
            user_id: User identifier for tracking
            session_id: Session identifier for tracking
            trace_id: Trace identifier for tracking
            message_id: Message identifier for tracking
            metadata: Optional additional metadata
            
        Returns:
            Configured CallbackHandler instance
            
        Raises:
            ValueError: If user_id is empty
        """
        if not user_id:
            raise ValueError("Empty user_id not allowed")
        config = CallbackConfig(
            provider=provider,
            model_name=model_name,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            message_id=message_id,
            metadata=metadata
        )
        return self.callback_factory.create_handler(config)
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate Langfuse configuration.
        
        Returns:
            Tuple of (is_valid, list of missing variables)
        """
        missing_vars = []
        
        if not self.settings.LANGFUSE_SECRET_KEY:
            missing_vars.append("LANGFUSE_SECRET_KEY")
        if not self.settings.LANGFUSE_PUBLIC_KEY:
            missing_vars.append("LANGFUSE_PUBLIC_KEY")
            
        return (len(missing_vars) == 0, missing_vars)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Langfuse service health status.
        
        Returns:
            Dict containing service health information
        """
        is_valid, missing = self.validate_configuration()
        return {
            "configured": is_valid,
            "missing_variables": missing,
            "host": self.settings.LANGFUSE_HOST,
            "has_secret_key": bool(self.settings.LANGFUSE_SECRET_KEY),
            "has_public_key": bool(self.settings.LANGFUSE_PUBLIC_KEY)
        }

# Global service instance
_langfuse_service = None

def get_langfuse_service() -> LangfuseService:
    """Get or create the global LangfuseService instance.
    
    Returns:
        Global LangfuseService singleton
    """
    global _langfuse_service
    if _langfuse_service is None:
        _langfuse_service = LangfuseService()
    return _langfuse_service