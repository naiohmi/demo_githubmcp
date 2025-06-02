"""
Session context management for sharing session parameters across the application
"""
from typing import Optional
import uuid


class SessionContext:
    """Global session context to share session parameters across the application"""
    
    def __init__(self):
        self._user_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._trace_id: Optional[str] = None
        self._llm_model_name: Optional[str] = None
    
    def set_session_parameters(
        self, 
        user_id: str, 
        session_id: str, 
        trace_id: str, 
        llm_model_name: str
    ):
        """Set the session parameters from main.py"""
        self._user_id = user_id
        self._session_id = session_id
        self._trace_id = trace_id
        self._llm_model_name = llm_model_name
    
    def get_session_parameters(self) -> tuple[str, str, str, str]:
        """Get the session parameters, with defaults if not set"""
        return (
            self._user_id or "service_user",
            self._session_id or str(uuid.uuid4()),
            self._trace_id or str(uuid.uuid4()),
            self._llm_model_name or "gpt-4o"
        )
    
    @property
    def user_id(self) -> str:
        return self._user_id or "service_user"
    
    @property
    def session_id(self) -> str:
        return self._session_id or str(uuid.uuid4())
    
    @property
    def trace_id(self) -> str:
        return self._trace_id or str(uuid.uuid4())
    
    @property
    def llm_model_name(self) -> str:
        return self._llm_model_name or "gpt-4o"


# Global session context instance
_session_context: Optional[SessionContext] = None


def get_session_context() -> SessionContext:
    """Get the global session context"""
    global _session_context
    if _session_context is None:
        _session_context = SessionContext()
    return _session_context


def set_global_session_parameters(
    user_id: str, 
    session_id: str, 
    trace_id: str, 
    llm_model_name: str
):
    """Set global session parameters from main.py"""
    context = get_session_context()
    context.set_session_parameters(user_id, session_id, trace_id, llm_model_name)