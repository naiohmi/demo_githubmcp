"""
GitHub operations demo script showing various capabilities of the GitHub service
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from src.services.github_service import get_github_service


async def demo_github_operations():
    """Demonstrate various GitHub operations"""
    service = await get_github_service()
    
    print("🚀 GitHub Service Demo")
    print("=" * 50)
    
    # Example 1: Get repository branches
    print("\n1. Getting repository branches...")
    branches_result = await service.get_repository_branches("microsoft", "vscode")
    print(f"Branches: {branches_result}")
    
    # Example 2: Get repository info
    print("\n2. Getting repository information...")
    repo_info = await service.get_repository_info("openai", "openai-python")
    print(f"Repository Info: {repo_info}")
    
    # Example 3: Get latest pull requests
    print("\n3. Getting latest pull requests...")
    prs_result = await service.get_latest_pull_requests("microsoft", "TypeScript", 3)
    print(f"Pull Requests: {prs_result}")
    
    # Example 4: Search repositories
    print("\n4. Searching repositories...")
    search_result = await service.search_repositories("machine learning python", 5)
    print(f"Search Results: {search_result}")

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


if __name__ == "__main__":
    async def run_all_demos():
        await demo_github_operations()
        await demo_agent_capabilities()
        await demo_service_capabilities()
    
    asyncio.run(run_all_demos())