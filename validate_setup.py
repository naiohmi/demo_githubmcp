#!/usr/bin/env python3
"""
Setup validation script for GitHub MCP Agent
Run this to verify your environment is properly configured.
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.11+ required, found:", f"{version.major}.{version.minor}.{version.micro}")
        return False

def check_uv_installed():
    """Check if UV is installed"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UV installed:", result.stdout.strip())
            return True
        else:
            print("❌ UV not working properly")
            return False
    except FileNotFoundError:
        print("❌ UV not found. Install with: brew install uv (macOS) or pip install uv")
        return False

def check_go_installed():
    """Check if Go is installed"""
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Go installed:", result.stdout.strip())
            return True
        else:
            print("❌ Go not working properly")
            return False
    except FileNotFoundError:
        print("❌ Go not found. Install from: https://golang.org/dl/")
        return False

def check_mcp_server():
    """Check if GitHub MCP server binary exists"""
    server_path = Path("mcp_server/github-mcp-server")
    if server_path.exists():
        print("✅ GitHub MCP server binary found")
        return True
    else:
        print("❌ GitHub MCP server binary not found. Run the build commands from README.md")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found. Copy .env.example to .env and configure")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    from src.config.settings import get_settings
    
    try:
        settings = get_settings()
        missing_vars = []
        
        if not settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_API_KEY.startswith("your_"):
            missing_vars.append("AZURE_OPENAI_API_KEY")
        if not settings.AZURE_OPENAI_ENDPOINT or settings.AZURE_OPENAI_ENDPOINT.startswith("https://your-"):
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not settings.GITHUB_PERSONAL_ACCESS_TOKEN or settings.GITHUB_PERSONAL_ACCESS_TOKEN.startswith("your_"):
            missing_vars.append("GITHUB_PERSONAL_ACCESS_TOKEN")
        
        if missing_vars:
            print("❌ Missing or template environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        else:
            print("✅ Required environment variables configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking environment variables: {e}")
        return False

def main():
    """Run all checks"""
    print("🔍 GitHub MCP Agent Setup Validation")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_uv_installed,
        check_go_installed,
        check_mcp_server,
        check_env_file,
        check_environment_variables,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"❌ Error in {check.__name__}: {e}")
            results.append(False)
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All checks passed! You're ready to run: python main.py")
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        print("\nFor detailed setup instructions, see README.md")

if __name__ == "__main__":
    main()
