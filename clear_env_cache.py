#!/usr/bin/env python3
"""
Utility script to clear environment variable cache and reload .env file
"""

import os
import sys
from dotenv import load_dotenv


def clear_env_cache():
    """Clear environment variables cache and reload .env file"""
    
    print("🧹 Clearing environment cache...")
    
    # Step 1: Clear environment variables from current session
    env_prefixes = ['AZURE_', 'OLLAMA_', 'LANGFUSE_', 'GITHUB_', 'REDIS_', 'MODEL_']
    cleared_vars = []
    
    for key in list(os.environ.keys()):
        if any(key.startswith(prefix) for prefix in env_prefixes):
            del os.environ[key]
            cleared_vars.append(key)
    
    print(f"   ✅ Cleared {len(cleared_vars)} environment variables")
    
    # Step 2: Clear Python module cache for config modules
    modules_to_clear = []
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('src.config') or module_name.startswith('src.services'):
            del sys.modules[module_name]
            modules_to_clear.append(module_name)
    
    print(f"   ✅ Cleared {len(modules_to_clear)} cached modules")
    
    # Step 3: Force reload .env file
    print("🔄 Reloading .env file...")
    load_dotenv(override=True)
    
    # Step 4: Verify reload by checking a few key variables
    print("🔍 Verifying environment variables:")
    test_vars = ['AZURE_OPENAI_API_KEY', 'OLLAMA_ENDPOINT', 'GITHUB_PERSONAL_ACCESS_TOKEN']
    
    for var in test_vars:
        value = os.getenv(var)
        if value:
            # Show first and last few characters for security
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    print("\n✅ Environment cache cleared and .env reloaded successfully!")
    print("💡 Note: Restart your application to ensure all components use the new values.")


def reset_settings_singleton():
    """Reset the settings singleton to force reload"""
    try:
        # Import after clearing cache
        from src.config.settings import _settings
        
        # Reset global singleton
        import src.config.settings as settings_module
        settings_module._settings = None
        
        print("   ✅ Settings singleton reset")
        
        # Test reload
        from src.config.settings import get_settings
        settings = get_settings()
        print("   ✅ Settings reloaded successfully")
        
    except ImportError as e:
        print(f"   ⚠️  Could not reset settings singleton: {e}")


if __name__ == "__main__":
    clear_env_cache()
    reset_settings_singleton()
    
    print("\n🎉 Cache clearing complete!")
    print("🔧 You can also run this programmatically:")
    print("   from clear_env_cache import clear_env_cache")
    print("   clear_env_cache()")
