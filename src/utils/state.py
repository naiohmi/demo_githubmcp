"""State definitions for the GitHub Agent application."""

from typing import List
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State type for the GitHub agent workflow.
    
    This defines the structure of the state that flows through the LangGraph workflow.
    The messages list contains the conversation history with automatic message addition.
    """
    messages: Annotated[List[AIMessage | HumanMessage | SystemMessage], add_messages]