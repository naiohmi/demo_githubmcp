"""
GitHub Agent using LangGraph with Azure GPT-4o and Langfuse
"""
import asyncio
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict
from langfuse.callback import CallbackHandler

from src.config.settings import get_settings
from src.tools.github_tools import get_github_tools


class AgentState(TypedDict):
    """State for the agent"""
    messages: Annotated[List[AIMessage | HumanMessage | SystemMessage], add_messages]


class GitHubAgent:
    """GitHub Agent using LangGraph, Azure GPT-4o, and Langfuse"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tools = get_github_tools()
        self.llm = self._create_llm()
        self.tool_node = ToolNode(self.tools)
        self.graph = self._create_graph()
        
    def _create_llm(self) -> AzureChatOpenAI:
        """Create Azure GPT-4o LLM with Langfuse callback"""
        langfuse_handler = CallbackHandler(
            secret_key=self.settings.LANGFUSE_SECRET_KEY,
            public_key=self.settings.LANGFUSE_PUBLIC_KEY,
            host=self.settings.LANGFUSE_HOST
        )
        
        llm = AzureChatOpenAI(
            azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
            api_key=self.settings.AZURE_OPENAI_API_KEY,
            api_version=self.settings.AZURE_OPENAI_API_VERSION,
            deployment_name=self.settings.MODEL_NAME,
            model=self.settings.MODEL_NAME,
            temperature=0.1,
            streaming=False,
            callbacks=[langfuse_handler]
        )
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(tools=self.tools)
        return llm_with_tools
        
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        def should_continue(state: AgentState) -> str:
            """Decide whether to continue or end the conversation"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If the last message has tool calls, go to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # Otherwise, end the conversation
            return END
        
        def call_model(state: AgentState) -> Dict[str, Any]:
            """Call the LLM"""
            messages = state["messages"]
            
            # Add system message if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                system_message = SystemMessage(content="""
You are a helpful GitHub assistant that can interact with GitHub repositories using various tools.

You have access to GitHub MCP tools that allow you to:
- List and explore repository branches
- Get repository information and metadata  
- List and analyze pull requests
- Get detailed pull request information including files changed
- List repository commits and get commit details
- Get file contents from repositories
- Search for repositories and issues
- Get issue details and comments
- And many other GitHub operations

When a user asks about GitHub repositories, branches, pull requests, issues, or any GitHub-related information:
1. Use the appropriate GitHub tools to gather the information
2. Provide clear, helpful responses based on the data retrieved
3. If you need specific repository information (owner/repo), ask the user for clarification
4. Format your responses in a readable way, highlighting key information

Always be helpful and provide actionable insights when possible.
                """)
                messages = [system_message] + messages
            
            response = self.llm.invoke(messages)
            return {"messages": [response]}
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", self.tool_node)
        
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
    
    async def ainvoke(self, message: str, **kwargs) -> str:
        """Invoke the agent asynchronously"""
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
    
    def invoke(self, message: str, **kwargs) -> str:
        """Invoke the agent synchronously"""
        return asyncio.run(self.ainvoke(message, **kwargs))


async def create_github_agent() -> GitHubAgent:
    """Factory function to create a GitHub agent"""
    return GitHubAgent()


# Example usage functions
async def example_queries():
    """Example queries to test the agent"""
    agent = await create_github_agent()
    
    # Example queries
    queries = [
        "what branches are available in the repository microsoft/vscode?",
        "what is the current version of the repository openai/openai-python?",
        "can you summarize and show me the latest PR changes in the repository microsoft/TypeScript?"
    ]
    
    for query in queries:
        print(f"\n🤖 Query: {query}")
        print("─" * 50)
        response = await agent.ainvoke(query)
        print(f"📝 Response: {response}")
        print("═" * 80)


if __name__ == "__main__":
    # Run example queries
    asyncio.run(example_queries())
