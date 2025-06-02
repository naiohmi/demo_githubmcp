"""
GitHub MCP Agent with LangGraph, Multi-Provider LLM Support, and Langfuse

Interactive GitHub assistant that can help you with:
- Repository information and management
- Code search and file operations
- Issue and pull request operations
- User and organization queries
- Commit history and branch information

Supports multiple LLM providers:
- Azure OpenAI: azure:gpt-4o, azure:gpt-4, azure:gpt-35-turbo
- Ollama: ollama:llama2, ollama:llama3, ollama:mistral

Usage: python main.py
"""
import asyncio
import uuid
from src.config.settings import check_environment
from src.utils.common import interactive_mode
from src.utils.session_context import set_global_session_parameters

def main():
    """Main entry point"""
    print("🚀 GitHub MCP Agent with LangGraph + Multi-Provider LLM + Langfuse")
    print("=" * 75)
    
    async def run_application():
        # Check environment
        if not await check_environment():
            return
        
        # Generate session-level parameters for Langfuse tracking
        user_id = "demo_user"
        session_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        llm_model_name = "azure:gpt-4o"  # Use provider:model format, {e.g., "azure:gpt-4o", "ollama:llama3.2"}
        
        # Set global session parameters for use across the application
        set_global_session_parameters(user_id, session_id, trace_id, llm_model_name)
        
        print(f"\n🎯 Available LLM Models:")
        print(f"  Selected: {llm_model_name}")
        
        print(f"\n📊 Session Info:")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   Trace ID: {trace_id}")
        print(f"   LLM Model: {llm_model_name}")
        
        # Start interactive mode with parameters
        print("\n🎯 Starting Interactive Mode...")
        await interactive_mode(user_id, session_id, trace_id, llm_model_name)
    
    try:
        asyncio.run(run_application())
    except KeyboardInterrupt:
        print("\nApplication interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"❌ Error running application: {str(e)}")


if __name__ == "__main__":
    main()
