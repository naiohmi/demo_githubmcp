from src.agents.github_agent import create_github_agent
import uuid

async def interactive_mode(user_id: str, session_id: str, trace_id: str, llm_model_name: str):
    """Interactive mode for asking GitHub questions.
    
    Provides a command-line interface for interacting with the GitHub agent.
    Users can ask questions about repositories, issues, users, and more.
    
    Args:
        user_id: User identifier for Langfuse tracking
        session_id: Session identifier for Langfuse tracking
        trace_id: Trace identifier for Langfuse tracking
        llm_model_name: LLM model name in format "provider:model" (e.g., "azure:gpt-4o", "ollama:llama2")
    """
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
    
    agent = await create_github_agent(user_id, session_id, trace_id, llm_model_name)
    
    while True:
        try:
            question = input("🔍 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            if not question:
                continue
                
            # Generate unique message ID for this interaction
            message_id = str(uuid.uuid4())
            print(f"\n🤔 Thinking... (Message ID: {message_id[:8]}...)")
            response = await agent.ainvoke(question, message_id)
            print(f"\n🤖 Answer: {response}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    print("Goodbye! 👋")