"""
GitHub service for handling high-level GitHub operations
"""
import asyncio
from typing import Dict, List, Any, Optional
from src.agents.github_agent import GitHubAgent, create_github_agent
from src.tools.mcp_client.github_client import GitHubMCPClientManager


class GitHubService:
    """High-level service for GitHub operations"""
    
    def __init__(self):
        self.agent: Optional[GitHubAgent] = None
        
    async def _get_agent(self) -> GitHubAgent:
        """Get or create the GitHub agent"""
        if self.agent is None:
            self.agent = await create_github_agent()
        return self.agent
    
    async def ask_question(self, question: str) -> str:
        """Ask a question about GitHub repositories"""
        agent = await self._get_agent()
        return await agent.ainvoke(question)
    
    async def get_repository_branches(self, owner: str, repo: str) -> str:
        """Get branches for a specific repository"""
        question = f"What branches are available in the repository {owner}/{repo}?"
        return await self.ask_question(question)
    
    async def get_repository_info(self, owner: str, repo: str) -> str:
        """Get information about a repository"""
        question = f"Can you tell me about the repository {owner}/{repo}? Include version, description, and recent activity."
        return await self.ask_question(question)
    
    async def get_latest_pull_requests(self, owner: str, repo: str, limit: int = 5) -> str:
        """Get latest pull requests for a repository"""
        question = f"Can you show me the latest {limit} pull requests in {owner}/{repo}? Include titles, authors, and status."
        return await self.ask_question(question)
    
    async def summarize_pull_request(self, owner: str, repo: str, pr_number: int) -> str:
        """Get detailed summary of a specific pull request"""
        question = f"Can you summarize pull request #{pr_number} in {owner}/{repo}? Include what files were changed, the description, and review status."
        return await self.ask_question(question)
    
    async def get_recent_commits(self, owner: str, repo: str, limit: int = 10) -> str:
        """Get recent commits for a repository"""
        question = f"Can you show me the latest {limit} commits in {owner}/{repo}? Include commit messages and authors."
        return await self.ask_question(question)
    
    async def get_latest_commits(self, owner: str, repo: str, limit: int = 10) -> str:
        """Get latest commits for a repository (alias for get_recent_commits)"""
        return await self.get_recent_commits(owner, repo, limit)
    
    async def search_repositories(self, query: str, limit: int = 10) -> str:
        """Search for repositories"""
        question = f"Can you search for repositories related to '{query}' and show me the top {limit} results?"
        return await self.ask_question(question)
    
    async def get_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> str:
        """Get content of a specific file"""
        question = f"Can you get the content of the file '{file_path}' from {owner}/{repo} on the {ref} branch?"
        return await self.ask_question(question)


# Singleton instance
_github_service: Optional[GitHubService] = None


async def get_github_service() -> GitHubService:
    """Get the GitHub service singleton"""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService()
    return _github_service


# Example usage
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


if __name__ == "__main__":
    asyncio.run(demo_github_operations())
