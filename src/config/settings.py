"""
Configuration settings for AI Agent Application
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Azure OpenAI Configuration (optional)
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        self.AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
        self.MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o')
        
        # Ollama Configuration (optional)
        self.OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
                
        # Langfuse Observability
        self.LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
        self.LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.LANGFUSE_HOST = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        
        # GitHub Configuration
        self.GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        self.GITHUB_HOST = os.getenv('GITHUB_HOST', 'https://api.github.com')

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

async def check_environment():
    """Check if required environment variables are set based on usage."""
    settings = get_settings()
    
    # Import here to avoid circular imports
    from src.services.langfuse_service import get_langfuse_service
    
    missing_vars = []
    
    # Always required
    if not settings.GITHUB_PERSONAL_ACCESS_TOKEN:
        missing_vars.append("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    # Check Langfuse configuration using service
    langfuse_service = get_langfuse_service()
    is_valid_langfuse, missing_langfuse = langfuse_service.validate_configuration()
    if not is_valid_langfuse:
        missing_vars.extend(missing_langfuse)
    
    # Check if at least one provider is configured
    azure_configured = all([
        settings.AZURE_OPENAI_API_KEY,
        settings.AZURE_OPENAI_ENDPOINT
    ])
    
    ollama_configured = bool(settings.OLLAMA_ENDPOINT)
    
    if not azure_configured and not ollama_configured:
        missing_vars.extend([
            "Either Azure OpenAI (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT)",
            "Or Ollama (OLLAMA_ENDPOINT) must be configured"
        ])
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    # Show which providers are configured
    configured_providers = []
    if azure_configured:
        configured_providers.append("Azure OpenAI")
    if ollama_configured:
        configured_providers.append(f"Ollama ({settings.OLLAMA_ENDPOINT})")
    
    print("✅ Environment configuration is valid!")
    print(f"📊 Configured providers: {', '.join(configured_providers)}")
    
    # Show Langfuse status
    langfuse_status = langfuse_service.get_health_status()
    print("\n📈 Langfuse Configuration:")
    print(f"  Host: {langfuse_status['host']}")
    print(f"  Status: {'✅ Configured' if langfuse_status['configured'] else '❌ Invalid'}")
    
    return True