# GitHub MCP Integration Project Manual

## 📑 Quick Navigation

- [👋 Getting Started](#getting-started-for-new-developers) - Start here if you're new
- [🔍 What is MCP?](#what-is-mcp) - Basic concepts
- [🏗️ Architecture](#system-architecture-explained) - System design
- [📚 Core Components](#core-components) - Key parts
- [⚡ Common Tasks](#common-tasks-with-examples) - Example workflows
- [🔧 Best Practices](#best-practices) - Guidelines and tips
- [🆘 Troubleshooting](#troubleshooting-tips) - Common issues

## Getting Started for New Developers

### What is MCP?
Model Context Protocol (MCP) is a standardized way for different parts of a system to communicate. In our case, it helps us talk to GitHub's API in a consistent and reliable way. Think of it like a translator that helps our code communicate with GitHub.

### System Architecture Explained
Let's break down how our system works in simple terms:

```mermaid
graph TB
    subgraph "How It Works"
        A[Your Code] --> B[Service Layer<br/>(The Manager)]
        B --> C[Tools Layer<br/>(Dynamic Discovery)]
        C --> D[GitHub Client Layer<br/>(Specific Wrapper)]
        D --> E[Generic MCP Client<br/>(Extensible Base)]
        E --> F[MCP Server<br/>(The Translator)]
        F --> G[GitHub API]
    end

    style A fill:#d4f1f4
    style B fill:#89c4f4
    style C fill:#89f4a3
    style D fill:#f4cf89
    style E fill:#cf89f4
    style F fill:#f49189
    style G fill:#ddd
```

**Key Benefits of the New Architecture:**
- **Generic Base**: The MCP client can now work with any MCP server, not just GitHub
- **Dynamic Discovery**: Tools are automatically discovered from the server at runtime
- **Backward Compatibility**: All existing code continues to work unchanged
- **Extensibility**: Easy to add new MCP servers through JSON configuration
    style B fill:#89c4f4
    style C fill:#89f4a3
    style D fill:#f4cf89
    style E fill:#f49189
    style F fill:#ddd
```

1. **MCP Server (The Translator)**
   - This is like a translator that understands both our code and GitHub
   - Handles all direct communication with GitHub
   - Makes sure we don't exceed GitHub's limits

2. **Client Layer (The Messenger)**
   - This is how our code talks to the translator (MCP Server)
   - Manages connections and handles basic errors
   - Like sending and receiving messages through a mailbox

3. **Tools Layer (The Toolkit)**
   - A collection of specific tools for GitHub tasks
   - Each tool does one specific job (like getting repository info)
   - Makes complex GitHub operations simple to use

4. **Service Layer (The Manager)**
   - Coordinates different tools to accomplish tasks
   - Handles high-level operations
   - Makes everything work together smoothly

### Your First Steps

1. **Setting Up**
   ```bash
   # Clone the repository
   git clone <repository-url>
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up your GitHub token
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token
   ```

2. **Basic Example: Getting Repository Info**
   ```python
   # This is the simplest way to use our system
   from src.services.github_service import get_github_service
   
   async def my_first_github_operation():
       # Get the service (it handles all the complex setup)
       service = await get_github_service()
       
       # Get info about a repository (it's that simple!)
       repo_info = await service.get_repository_info(
           owner="microsoft",
           repo="vscode"
       )
       print(repo_info)
   ```

### Common Tasks with Examples

1. **Working with Repositories**
   ```python
   async def repository_examples():
       service = await get_github_service()
       
       # Get repository details
       repo_info = await service.get_repository_info(
           owner="username",
           repo="repository"
       )
       
       # Get repository branches
       branches = await service.get_repository_branches(
           owner="username",
           repo="repository"
       )
   ```

2. **Working with Pull Requests**
   ```python
   async def pr_examples():
       service = await get_github_service()
       
       # List recent PRs
       prs = await service.get_latest_pull_requests(
           owner="username",
           repo="repository",
           limit=5  # Get 5 most recent PRs
       )
   ```

### Troubleshooting Tips

1. **Common Issues and Solutions**
   - `Token not found`: Make sure you've set your GitHub token
   - `Connection failed`: Check your internet connection
   - `Rate limit exceeded`: You're making too many requests too quickly

2. **Debug Checklist**
   - Is your GitHub token set correctly?
   - Are you using `async/await` correctly?
   - Are the repository owner and name correct?
   - Do you have the right permissions?

### Best Practices for Beginners

1. **Code Organization**
   - Always use context managers (`async with`)
   - Handle errors appropriately
   - Clean up resources properly

2. **Performance**
   - Reuse service instances when possible
   - Don't make unnecessary API calls
   - Use batch operations when available

## Core Components

### New Architecture Components

#### 1. Generic MCP Client (`src/tools/mcp_client/mcp_client.py`)
- **Purpose**: Handles communication with any MCP server
- **Key Features**: 
  - Multi-server support via JSON configuration
  - Dynamic tool discovery
  - Environment variable mapping
  - Server-specific operations

#### 2. GitHub Client Wrapper (`src/tools/mcp_client/github_client.py`)
- **Purpose**: Provides GitHub-specific convenience methods
- **Key Features**:
  - Backward compatibility with existing code
  - GitHub-specific defaults and configurations
  - Context managers for easy resource management

#### 3. Configuration Registry (`src/registry/mcp_client_config.json`)
- **Purpose**: Centralized configuration for all MCP servers
- **Benefits**:
  - Easy to add new servers without code changes
  - Environment variable management
  - Server-specific timeouts and settings

#### 4. Dynamic Tool Discovery (`src/tools/github_tools.py`)
- **Purpose**: Automatically discovers and converts MCP tools to LangChain tools
- **Benefits**:
  - Reduced code maintenance (90% reduction in lines)
  - Always up-to-date with server capabilities
  - No manual tool definitions needed

1. **MCP Server**
   - Handles GitHub API communication
   - Manages authentication and rate limiting
   - Provides standardized tool interfaces

2. **Client Layer**
   - Manages server communication
   - Handles process lifecycle
   - Implements error handling

3. **Tools Layer**
   - Provides specific GitHub operations
   - Implements input validation
   - Standardizes tool interfaces

4. **Service Layer**
   - High-level operation coordination
   - Session and context management
   - Agent-based interactions

## Documentation and Resources

- [GitHub MCP Manual](docs/github_mcp_manual.md) - Detailed technical documentation
- [Configuration Guide](config/settings.py) - Environment setup
- [Example Code](examples/) - Code samples and demos
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Issue Tracker](https://github.com/your-org/project/issues)

## Contributing

1. **Code Style**
   - Follow PEP 8 guidelines
   - Implement proper type hints
   - Document all public interfaces

2. **Testing**
   - Write unit tests for new features
   - Update integration tests
   - Maintain test coverage

## Version History

- Current Version: 1.0.0
- Release Notes: See [CHANGELOG.md](CHANGELOG.md)