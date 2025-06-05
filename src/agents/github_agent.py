"""
GitHub Agent using LangGraph with Dynamic LLM Provider Support and Langfuse
"""
import asyncio
import uuid
from langchain_core.messages import HumanMessage, AIMessage

from src.tools.github_tools import get_github_tools
from src.utils.nodes import create_llm_with_tools
from src.utils.graph import create_agent_graph


class GitHubAgent:
    """GitHub Agent using LangGraph with Dynamic LLM Provider Support and Langfuse.
    
    This class provides a simplified interface for the GitHub agent,
    using the modular components for LLM creation and graph workflow.
    Supports multiple LLM providers (Azure OpenAI, Ollama) via provider:model format.
    """
    
    def __init__(self, user_id: str, session_id: str, trace_id: str, llm_model_name: str):
        """Initialize the GitHub agent with LLM and workflow graph.
        
        Args:
            user_id: User identifier for Langfuse tracking
            session_id: Session identifier for Langfuse tracking
            trace_id: Trace identifier for Langfuse tracking
            llm_model_name: LLM model name in format "provider:model" (e.g., "azure:gpt-4o", "ollama:llama2")
        """
        self.user_id = user_id
        self.session_id = session_id
        self.trace_id = trace_id
        self.llm_model_name = llm_model_name
        self.tools = None  # Will be loaded asynchronously
    
    async def ainvoke(self, message: str, message_id: str, **kwargs) -> str:
        """Invoke the agent asynchronously.
        
        Args:
            message: User message to process
            message_id: Unique identifier for this message
            **kwargs: Additional arguments for graph invocation
            
        Returns:
            Agent response as string
        """
        # Load tools if not already loaded
        if self.tools is None:
            self.tools = await get_github_tools()
        
        # Create LLM with current message context using registry
        self.llm = create_llm_with_tools(
            llm_model_name=self.llm_model_name,
            tools=self.tools,
            user_id=self.user_id,
            session_id=self.session_id,
            trace_id=self.trace_id,
            message_id=message_id
        )
        self.graph = create_agent_graph(self.llm, self.tools)
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=message)]
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state, **kwargs)
            
            # Extract the final response
            messages = result["messages"]
            final_message = messages[-1]
            
            if isinstance(final_message, AIMessage):
                return final_message.content
            else:
                return str(final_message)
                
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def invoke(self, message: str, message_id: str, **kwargs) -> str:
        """Invoke the agent synchronously.
        
        Args:
            message: User message to process
            message_id: Unique identifier for this message
            **kwargs: Additional arguments for graph invocation
            
        Returns:
            Agent response as string
        """
        return asyncio.run(self.ainvoke(message, message_id, **kwargs))


async def create_github_agent(user_id: str, session_id: str, trace_id: str, llm_model_name: str) -> GitHubAgent:
    """Factory function to create a GitHub agent.
    
    Args:
        user_id: User identifier for Langfuse tracking
        session_id: Session identifier for Langfuse tracking
        trace_id: Trace identifier for Langfuse tracking
        llm_model_name: LLM model name in format "provider:model" (e.g., "azure:gpt-4o", "ollama:llama2")
        
    Returns:
        Configured GitHubAgent instance
    """
    return GitHubAgent(user_id, session_id, trace_id, llm_model_name)