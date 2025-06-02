"""
High-level GitHub service using the agent for operations
"""
import uuid
from typing import Optional
from src.agents.github_agent import GitHubAgent, create_github_agent
from src.utils.session_context import get_session_context
from src.config.parameters import (
    DEFAULT_PR_LIMIT,
    DEFAULT_COMMIT_LIMIT,
    DEFAULT_BRANCH
)
from src.utils.prompt_loader import get_prompt_loader


class GitHubService:
    """High-level service for GitHub operations"""
    
    def __init__(self):
        self.agent: Optional[GitHubAgent] = None
        
    async def _get_agent(self) -> GitHubAgent:
        """Get or create the GitHub agent"""
        if self.agent is None:
            # Use shared session parameters from main.py for consistent tracing
            session_context = get_session_context()
            user_id, session_id, trace_id, llm_model_name = session_context.get_session_parameters()
            
            # Use service-specific user_id but keep same session/trace for consistency
            service_user_id = "service_user"
            self.agent = await create_github_agent(service_user_id, session_id, trace_id, llm_model_name)
        return self.agent
    
    async def ask_question(self, question: str) -> str:
        """Ask a question about GitHub repositories"""
        agent = await self._get_agent()
        message_id = str(uuid.uuid4())
        return await agent.ainvoke(question, message_id)
    
    async def get_repository_branches(self, owner: str, repo: str) -> str:
        """Get branches for a specific repository"""
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("branches").format(owner=owner, repo=repo)
        return await self.ask_question(question)
    
    async def get_repository_info(self, owner: str, repo: str) -> str:
        """Get information about a repository"""
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("repository_info").format(owner=owner, repo=repo)
        return await self.ask_question(question)
    
    async def get_latest_pull_requests(self, owner: str, repo: str, limit: int = 5) -> str:
        """Get latest pull requests for a repository"""
        limit = limit or DEFAULT_PR_LIMIT
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("pull_requests").format(owner=owner, repo=repo, limit=limit)
        return await self.ask_question(question)
    
    async def summarize_pull_request(self, owner: str, repo: str, pr_number: int) -> str:
        """Get detailed summary of a specific pull request"""
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("pull_request_summary").format(owner=owner, repo=repo, pr_number=pr_number)
        return await self.ask_question(question)
    
    async def get_recent_commits(self, owner: str, repo: str, limit: int = 10) -> str:
        """Get recent commits for a repository"""
        limit = limit or DEFAULT_COMMIT_LIMIT
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("commits").format(owner=owner, repo=repo, limit=limit)
        return await self.ask_question(question)
    
    async def get_latest_commits(self, owner: str, repo: str, limit: int = 10) -> str:
        """Get latest commits for a repository (alias for get_recent_commits)"""
        return await self.get_recent_commits(owner, repo, limit)
    
    async def search_repositories(self, query: str, limit: int = 10) -> str:
        """Search for repositories"""
        limit = limit or DEFAULT_PR_LIMIT
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("search_repos").format(query=query, limit=limit)
        return await self.ask_question(question)
    
    async def get_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> str:
        """Get content of a specific file"""
        ref = ref or DEFAULT_BRANCH
        prompt_loader = get_prompt_loader()
        question = prompt_loader.get_query_template("file_content").format(owner=owner, repo=repo, file_path=file_path, ref=ref)
        return await self.ask_question(question)
    
    async def get_user_info(self) -> str:
        """Get information about the authenticated user"""
        return await self.ask_question("Who am I on GitHub?")
    
    async def list_repositories(self, username: str) -> str:
        """List repositories for a specific user"""
        return await self.ask_question(f"What repositories does {username} have?")


# Singleton instance
_github_service: Optional[GitHubService] = None


async def get_github_service() -> GitHubService:
    """Get the GitHub service singleton"""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService()
    return _github_service