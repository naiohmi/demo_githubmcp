"""
LangGraph tools for GitHub MCP integration
"""
import asyncio
from typing import Any, Dict, List, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.tools.mcp_client.github_client import GitHubMCPClient, GitHubMCPClientManager


class GitHubSpecificTool(BaseTool):
    """Base class for specific GitHub tools"""
    
    def __init__(self, tool_name: str, description: str, args_schema: Type[BaseModel]):
        super().__init__(
            name=f"github_{tool_name}",
            description=description,
            args_schema=args_schema
        )
        self._tool_name = tool_name
        self._client: Optional[GitHubMCPClient] = None
        
    async def _get_client(self) -> GitHubMCPClient:
        """Get or create MCP client"""
        from src.tools.mcp_client.github_client import create_github_client
        return await create_github_client()
        
    def _run(self, **kwargs) -> str:
        """Synchronous wrapper"""
        return asyncio.run(self._arun(**kwargs))
        
    async def _arun(self, *args, **kwargs) -> str:
        """Execute the tool"""
        try:
            # If args is passed, merge it with kwargs based on the schema
            if args and hasattr(self, 'args_schema') and self.args_schema:
                # Get field names from the schema
                field_names = list(self.args_schema.model_fields.keys())
                # Map positional args to field names
                for i, arg in enumerate(args):
                    if i < len(field_names):
                        kwargs[field_names[i]] = arg
            
            client = await self._get_client()
            result = await client.call_tool(self._tool_name, kwargs)
            
            if isinstance(result, dict):
                import json
                return json.dumps(result, indent=2)
            return str(result)
            
        except Exception as e:
            return f"Error calling GitHub tool '{self._tool_name}': {str(e)}"


# Specific tool schemas
class ListBranchesInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")


class GetPullRequestInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    pullNumber: int = Field(description="Pull request number")


class ListPullRequestsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    state: Optional[str] = Field(default="open", description="PR state: open, closed, all")
    sort: Optional[str] = Field(default=None, description="Sort field")
    direction: Optional[str] = Field(default=None, description="Sort direction")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")


class GetRepositoryInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")


# Comprehensive tool schemas based on GitHub MCP server capabilities
class GetFileContentsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    path: str = Field(description="File path")
    ref: Optional[str] = Field(default=None, description="Git reference (branch, tag, or commit SHA)")

class SearchRepositoriesInput(BaseModel):
    query: str = Field(description="Search query")
    sort: Optional[str] = Field(default=None, description="Sort field")
    order: Optional[str] = Field(default=None, description="Sort order")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class ListCommitsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    sha: Optional[str] = Field(default=None, description="Branch name, tag, or commit SHA")
    path: Optional[str] = Field(default=None, description="Only commits containing this file path")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetCommitInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    sha: str = Field(description="Commit SHA, branch name, or tag name")

class GetPullRequestFilesInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    pullNumber: int = Field(description="Pull request number")

class SearchIssuesInput(BaseModel):
    query: str = Field(description="Search query")
    sort: Optional[str] = Field(default=None, description="Sort field")
    order: Optional[str] = Field(default=None, description="Sort order")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetMeInput(BaseModel):
    pass  # No parameters required

class ListIssuesInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    state: Optional[str] = Field(default="open", description="Issue state: open, closed, all")
    labels: Optional[str] = Field(default=None, description="Comma-separated list of label names")
    sort: Optional[str] = Field(default=None, description="Sort field")
    direction: Optional[str] = Field(default=None, description="Sort direction")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetIssueInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    issueNumber: int = Field(description="Issue number")

class CreateIssueInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    title: str = Field(description="Issue title")
    body: Optional[str] = Field(default=None, description="Issue body")
    labels: Optional[List[str]] = Field(default=None, description="List of label names")
    assignees: Optional[List[str]] = Field(default=None, description="List of assignee usernames")

class UpdateIssueInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    issueNumber: int = Field(description="Issue number")
    title: Optional[str] = Field(default=None, description="Issue title")
    body: Optional[str] = Field(default=None, description="Issue body")
    state: Optional[str] = Field(default=None, description="Issue state: open, closed")
    labels: Optional[List[str]] = Field(default=None, description="List of label names")
    assignees: Optional[List[str]] = Field(default=None, description="List of assignee usernames")

class SearchCodeInput(BaseModel):
    query: str = Field(description="Code search query")
    sort: Optional[str] = Field(default=None, description="Sort field")
    order: Optional[str] = Field(default=None, description="Sort order")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetUserInput(BaseModel):
    username: str = Field(description="GitHub username")

class GetReleaseInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    releaseId: int = Field(description="Release ID")

class ListReleasesInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class CreateReleaseInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    tagName: str = Field(description="Tag name for the release")
    name: Optional[str] = Field(default=None, description="Release name")
    body: Optional[str] = Field(default=None, description="Release notes")
    draft: Optional[bool] = Field(default=False, description="True to create a draft release")
    prerelease: Optional[bool] = Field(default=False, description="True to identify as prerelease")

class GetDirectoryContentsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    path: str = Field(description="Directory path")
    ref: Optional[str] = Field(default=None, description="Git reference (branch, tag, or commit SHA)")

class GetReadmeInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    ref: Optional[str] = Field(default=None, description="Git reference (branch, tag, or commit SHA)")

class GetLanguagesInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")

class GetContributorsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    anon: Optional[bool] = Field(default=False, description="Include anonymous contributors")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetStatsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")

class SearchUsersInput(BaseModel):
    query: str = Field(description="User search query")
    sort: Optional[str] = Field(default=None, description="Sort field")
    order: Optional[str] = Field(default=None, description="Sort order")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")


# Additional schemas for tools that exist in MCP server
class GetPullRequestCommentsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    pullNumber: int = Field(description="Pull request number")

class GetPullRequestDiffInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    pullNumber: int = Field(description="Pull request number")

class ListTagsInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    page: Optional[int] = Field(default=None, description="Page number")
    perPage: Optional[int] = Field(default=None, description="Results per page")

class GetTagInput(BaseModel):
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    tag: str = Field(description="Tag name")


# Create specific tools
class ListBranchesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_branches",
            description="List branches in a GitHub repository",
            args_schema=ListBranchesInput
        )


class GetPullRequestTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_pull_request",
            description="Get details of a specific pull request",
            args_schema=GetPullRequestInput
        )


class ListPullRequestsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_pull_requests", 
            description="List pull requests in a repository",
            args_schema=ListPullRequestsInput
        )


# Comprehensive tool classes based on GitHub MCP server capabilities
class GetFileContentsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_file_contents",
            description="Get contents of a file or directory from a GitHub repository",
            args_schema=GetFileContentsInput
        )

class SearchRepositoriesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="search_repositories",
            description="Search for GitHub repositories",
            args_schema=SearchRepositoriesInput
        )

class ListCommitsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_commits",
            description="Get a list of commits from a repository branch",
            args_schema=ListCommitsInput
        )

class GetCommitTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_commit",
            description="Get details for a specific commit from a repository",
            args_schema=GetCommitInput
        )

class GetPullRequestFilesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_pull_request_files",
            description="Get the list of files changed in a pull request",
            args_schema=GetPullRequestFilesInput
        )

class SearchIssuesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="search_issues",
            description="Search for issues and pull requests",
            args_schema=SearchIssuesInput
        )

class GetMeTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_me",
            description="Get details of the authenticated user",
            args_schema=GetMeInput
        )

class ListIssuesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_issues",
            description="List issues in a repository",
            args_schema=ListIssuesInput
        )

class GetIssueTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_issue",
            description="Get details of a specific issue",
            args_schema=GetIssueInput
        )

class CreateIssueTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="create_issue",
            description="Create a new issue in a repository",
            args_schema=CreateIssueInput
        )

class UpdateIssueTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="update_issue",
            description="Update an existing issue",
            args_schema=UpdateIssueInput
        )

class SearchCodeTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="search_code",
            description="Search for code in GitHub repositories",
            args_schema=SearchCodeInput
        )

class GetUserTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_user",
            description="Get information about a GitHub user",
            args_schema=GetUserInput
        )

class GetReleaseTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_release",
            description="Get details of a specific release",
            args_schema=GetReleaseInput
        )

class ListReleasesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_releases",
            description="List releases for a repository",
            args_schema=ListReleasesInput
        )

class CreateReleaseTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="create_release",
            description="Create a new release for a repository",
            args_schema=CreateReleaseInput
        )

class GetDirectoryContentsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_directory_contents",
            description="Get the contents of a directory in a repository",
            args_schema=GetDirectoryContentsInput
        )

class GetReadmeTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_readme",
            description="Get the README file of a repository",
            args_schema=GetReadmeInput
        )

class GetLanguagesTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_languages",
            description="Get the programming languages used in a repository",
            args_schema=GetLanguagesInput
        )

class GetContributorsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_contributors",
            description="Get the contributors to a repository",
            args_schema=GetContributorsInput
        )

class GetStatsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_stats",
            description="Get repository statistics",
            args_schema=GetStatsInput
        )

class SearchUsersTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="search_users",
            description="Search for GitHub users",
            args_schema=SearchUsersInput
        )

class GetRepositoryTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_repository",
            description="Get details of a specific repository",
            args_schema=GetRepositoryInput
        )


class GetPullRequestCommentsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_pull_request_comments",
            description="Get comments for a specific pull request",
            args_schema=GetPullRequestCommentsInput
        )

class GetPullRequestDiffTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_pull_request_diff",
            description="Get the diff of a pull request",
            args_schema=GetPullRequestDiffInput
        )

class ListTagsTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="list_tags",
            description="List git tags in a GitHub repository",
            args_schema=ListTagsInput
        )

class GetTagTool(GitHubSpecificTool):
    def __init__(self):
        super().__init__(
            tool_name="get_tag",
            description="Get details about a specific git tag",
            args_schema=GetTagInput
        )


def get_github_tools() -> List[BaseTool]:
    """Get all GitHub tools for LangGraph - only tools that exist in MCP server"""
    return [
        # User and authentication
        GetMeTool(),
        
        # Repository browsing
        ListBranchesTool(),
        GetFileContentsTool(),
        
        # Search tools
        SearchRepositoriesTool(),
        SearchCodeTool(),
        SearchIssuesTool(),
        SearchUsersTool(),
        
        # Commit and history tools
        ListCommitsTool(),
        GetCommitTool(),
        
        # Pull request tools
        ListPullRequestsTool(),
        GetPullRequestTool(),
        GetPullRequestFilesTool(),
        
        # Issue tools
        ListIssuesTool(),
        GetIssueTool(),
        CreateIssueTool(),
        UpdateIssueTool(),
        
        # Additional working tools
        GetPullRequestCommentsTool(),
        GetPullRequestDiffTool(),
        ListTagsTool(),
        GetTagTool(),
    ]


async def cleanup_github_tools():
    """Cleanup function to stop any running MCP clients"""
    # This would be called at the end of the application
    pass
