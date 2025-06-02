"""Demo script showing dynamic provider switching."""

import asyncio
import uuid
from src.agents.github_agent import create_github_agent
from src.config.settings import check_environment


async def demo_provider_switching():
    """Demonstrate switching between providers."""
    
    print("🧪 LLM Provider Switching Demo")
    print("=" * 40)
    
    # Check environment first
    if not await check_environment():
        print("❌ Environment not properly configured. Please check your .env file.")
        return
    
    # Session parameters
    user_id = "demo_user"
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    # Test different providers
    models_to_test = [
        "azure:gpt-4o",
        "ollama:llama2"
    ]
    
    test_message = "List public repositories for microsoft"
    
    for model_name in models_to_test:
        print(f"\n🔧 Testing {model_name}")
        print("-" * 30)
        
        try:
            # Create agent with specific provider
            agent = await create_github_agent(user_id, session_id, trace_id, model_name)
            message_id = str(uuid.uuid4())
            
            print(f"📤 Query: {test_message}")
            print(f"🤔 Processing... (Message ID: {message_id[:8]}...)")
            
            # Test the agent
            response = await agent.ainvoke(test_message, message_id)
            
            print(f"✅ {model_name}: Success!")
            print(f"📝 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"❌ {model_name}: Failed - {str(e)}")
        
        print()
    
    print("🎉 Provider switching demo completed!")


async def interactive_provider_selection():
    """Allow user to interactively select a provider."""
    
    print("🎛️  Interactive Provider Selection")
    print("=" * 40)
    
    # Check environment first
    if not await check_environment():
        return
    
    # Available models
    available_models = {
        "1": "azure:gpt-4o",
        "2": "azure:gpt-4",
        "3": "azure:gpt-35-turbo",
        "4": "ollama:llama2",
        "5": "ollama:llama3",
        "6": "ollama:mistral"
    }
    
    print("\n📋 Available Models:")
    for key, model in available_models.items():
        print(f"  {key}. {model}")
    
    # Get user selection
    while True:
        try:
            choice = input("\n🔢 Select a model (1-6): ").strip()
            if choice in available_models:
                selected_model = available_models[choice]
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return
    
    print(f"\n✅ Selected: {selected_model}")
    
    # Session parameters
    user_id = "demo_user"
    session_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    
    try:
        # Create agent with selected provider
        agent = await create_github_agent(user_id, session_id, trace_id, selected_model)
        
        # Test query
        test_message = "What repositories does github have?"
        message_id = str(uuid.uuid4())
        
        print(f"\n📤 Test Query: {test_message}")
        print(f"🤔 Processing with {selected_model}...")
        
        response = await agent.ainvoke(test_message, message_id)
        
        print(f"\n🤖 Response from {selected_model}:")
        print(f"📝 {response}")
        
    except Exception as e:
        print(f"❌ Error with {selected_model}: {str(e)}")


def main():
    """Main entry point for demo."""
    
    print("🚀 LLM Provider Demo")
    print("=" * 30)
    print("1. Automatic provider switching test")
    print("2. Interactive provider selection")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\n🔢 Choose an option (1-3): ").strip()
            
            if choice == "1":
                asyncio.run(demo_provider_switching())
                break
            elif choice == "2":
                asyncio.run(interactive_provider_selection())
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()