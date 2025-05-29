"""
Configuration settings for AI Agent Application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Azure OpenAI Configuration
        self.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        self.AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
        self.MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o')
               
        # Langfuse Observability
        self.LANGFUSE_SECRET_KEY = os.getenv('LANGFUSE_SECRET_KEY')
        self.LANGFUSE_PUBLIC_KEY = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.LANGFUSE_HOST = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        
        # GitHub Configuration
        self.GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        self.GITHUB_HOST = os.getenv('GITHUB_HOST', 'https://api.github.com')

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings