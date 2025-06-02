"""Graph creation utilities for the GitHub Agent workflow."""

from typing import Dict, Any
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.utils.state import AgentState
from src.utils.prompt_loader import get_prompt_loader


def should_continue(state: AgentState) -> str:
    """Decide whether to continue or end the conversation."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise, end the conversation
    return END


def call_model(llm, state: AgentState) -> Dict[str, Any]:
    """Call the LLM with the current state."""
    messages = state["messages"]
    
    # Add system message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        prompt_loader = get_prompt_loader()
        system_message = SystemMessage(content=prompt_loader.get_system_message())
        messages = [system_message] + messages
    
    response = llm.invoke(messages)
    return {"messages": [response]}


def create_agent_graph(llm, tools) -> StateGraph:
    """Create the agent workflow graph.
    
    Args:
        llm: Configured LLM instance
        tools: List of tools for the agent
        
    Returns:
        Compiled StateGraph for the agent workflow
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Create tool node
    tool_node = ToolNode(tools)
    
    # Add nodes
    workflow.add_node("agent", lambda state: call_model(llm, state))
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Tools always go back to agent
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()