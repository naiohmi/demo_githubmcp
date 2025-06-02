from src.agents.github_agent import create_github_agent
from src.utils.prompt_loader import get_prompt_loader
import asyncio
import uuid

# Example usage functions
async def example_queries():
    """Example queries to test the agent"""
    # Create agent with demo parameters
    user_id = "demo_user"
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    llm_model_name = "gpt-4o"
    agent = await create_github_agent(user_id, session_id, trace_id, llm_model_name)
    
    print(f"📊 Demo Session Info:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Trace ID: {trace_id}")
    print(f"   LLM Model: {llm_model_name}")
    print("═" * 80)
    
    # Example queries
    prompt_loader = get_prompt_loader()
    queries = prompt_loader.get_test_queries()
    
    for query in queries:
        message_id = str(uuid.uuid4())
        print(f"\n🤖 Query: {query}")
        print(f"   Message ID: {message_id[:8]}...")
        print("─" * 50)
        response = await agent.ainvoke(query, message_id)
        print(f"📝 Response: {response}")
        print("═" * 80)


if __name__ == "__main__":
    # Run example queries
    asyncio.run(example_queries())
