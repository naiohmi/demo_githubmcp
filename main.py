"""
GitHub MCP Agent with LangGraph, Azure GPT-4o, and Langfuse

Interactive GitHub assistant that can help you with:
- Repository information and management
- Code search and file operations
- Issue and pull request operations
- User and organization queries
- Commit history and branch information

Usage: python main.py
"""
import asyncio
import os
from src.config.settings import get_settings
from src.services.github_service import get_github_service
from src.agents.github_agent import create_github_agent


async def check_environment():
    """Check if required environment variables are set"""
    settings = get_settings()
    
    missing_vars = []
    
    if not settings.AZURE_OPENAI_API_KEY:
        missing_vars.append("AZURE_OPENAI_API_KEY")
    if not settings.AZURE_OPENAI_ENDPOINT:
        missing_vars.append("AZURE_OPENAI_ENDPOINT")
    if not settings.GITHUB_PERSONAL_ACCESS_TOKEN:
        missing_vars.append("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not settings.LANGFUSE_SECRET_KEY:
        missing_vars.append("LANGFUSE_SECRET_KEY")
    if not settings.LANGFUSE_PUBLIC_KEY:
        missing_vars.append("LANGFUSE_PUBLIC_KEY")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set!")
    return True


async def demo_agent_capabilities():
    """Demo the agent's capabilities with example questions"""
    print("\n🤖 GitHub MCP Agent Capabilities Demo")
    print("=" * 50)
    print("This agent can help you with various GitHub operations:")
    print("• Search repositories, code, issues, and users")
    print("• Get repository information, branches, and files")
    print("• Retrieve commits, pull requests, and issues")
    print("• Create and update issues")
    print("• Access both public and private repositories (with proper permissions)")
    print("\nAgent is ready! ✅")
    print("=" * 50)


async def demo_service_capabilities():
    """Demo the service layer capabilities"""
    print("\n🔧 Service Layer Available")
    print("=" * 50)
    print("The GitHub service provides direct access to:")
    print("• Repository operations (branches, info, search)")
    print("• File operations (get contents, search code)")
    print("• Commit operations (list, get specific commits)")
    print("• Issue operations (list, get, create, update)")
    print("• Pull request operations (list, get, files, comments)")
    print("• User operations (search, get profile)")
    print("\nService layer is ready! ✅")
    print("=" * 50)


async def interactive_mode():
    """Interactive mode for asking GitHub questions"""
    print("\n💬 Interactive GitHub Assistant")
    print("=" * 50)
    print("Ask me anything about GitHub repositories!")
    print("\nExample questions:")
    print("• 'What branches are available in [owner/repo]?'")
    print("• 'What repositories does [username] have?'")
    print("• 'Show me the README file from [owner/repo]'")
    print("• 'What is the latest commit in [owner/repo]?'")
    print("• 'Search for repositories about [topic]'")
    print("• 'Find issues in [owner/repo] with label [label]'")
    print("\nReplace [owner/repo] with actual repository names")
    print("Type 'quit' to exit\n")
    
    agent = await create_github_agent()
    
    while True:
        try:
            question = input("🔍 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            if not question:
                continue
                
            print("\n🤔 Thinking...")
            response = await agent.ainvoke(question)
            print(f"\n🤖 Answer: {response}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    print("Goodbye! 👋")


def main():
    """Main entry point"""
    print("🚀 GitHub MCP Agent with LangGraph + Azure GPT-4o + Langfuse")
    print("=" * 70)
    
    async def run_application():
        # Check environment
        if not await check_environment():
            return
        
        # Show capabilities
        await demo_agent_capabilities()
        await demo_service_capabilities()
        
        # Start interactive mode
        print("\n🎯 Starting Interactive Mode...")
        await interactive_mode()
    
    try:
        asyncio.run(run_application())
    except KeyboardInterrupt:
        print("\nApplication interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"❌ Error running application: {str(e)}")


if __name__ == "__main__":
    main()
