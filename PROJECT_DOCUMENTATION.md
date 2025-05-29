# GitHub MCP Agent: Intelligent GitHub Assistant

## 🎯 Project Overview

This project demonstrates how to build an intelligent GitHub assistant using the **Model Context Protocol (MCP)**, combining GitHub's official MCP server with advanced AI agent workflows. The system enables natural language interactions with GitHub repositories, powered by Azure GPT-4o and enhanced with comprehensive observability.

### Key Achievements

- **✅ Complete Integration**: Seamlessly connects GitHub's MCP server with LangGraph agents
- **✅ Natural Language Interface**: Ask questions like "What branches are in microsoft/vscode?" in plain English
- **✅20+ GitHub Operations**: Comprehensive tool coverage from repository management to issue tracking
- **✅ Production Ready**: Robust error handling, configuration management, and testing framework
- **✅ Cross-Platform**: Works on macOS and Windows with detailed setup instructions

## 🏗️ Architecture & Design

### High-Level Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Human Query   │───▶│   LangGraph     │───▶│   Azure GPT-4o  │
│ "What branches  │    │     Agent       │    │   (Langfuse)    │
│ are in repo X?" │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  GitHub Tools   │───▶│  GitHub MCP     │
                       │   (LangChain)   │    │    Server       │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   GitHub API    │
                                               └─────────────────┘
```

### Core Components

#### 1. **GitHub MCP Server** (`mcp_server/github-mcp-server`)
- Official GitHub implementation built from Go source
- Provides 51 GitHub operations via standardized MCP protocol
- Handles authentication, rate limiting, and API communication

#### 2. **MCP Client** (`src/tools/mcp_client/github_client.py`)
- Python wrapper for MCP communication
- Manages server lifecycle and connection pooling
- Handles tool discovery and invocation

#### 3. **LangChain Tools** (`src/tools/github_tools.py`)
- 20 implemented GitHub tools mapped to MCP server capabilities
- LangChain-compatible interfaces for agent integration
- Comprehensive coverage: repositories, issues, PRs, commits, users

#### 4. **LangGraph Agent** (`src/agents/github_agent.py`)
- Intelligent workflow orchestration
- Azure GPT-4o integration with tool calling
- Multi-step reasoning and error recovery

#### 5. **Service Layer** (`src/services/github_service.py`)
- High-level abstraction for common operations
- Clean async interfaces for direct API usage
- Simplified access for programmatic integration

## 🛠️ Available GitHub Operations

### Repository Operations
- **Search repositories** - Find repositories by name, topic, language
- **List branches** - Get all branches in a repository  
- **Get file contents** - Retrieve any file from a repository
- **List commits** - Get commit history with filtering
- **Get commit details** - Detailed information about specific commits

### Pull Request Operations
- **List pull requests** - Get PRs with status and label filtering
- **Get PR details** - Comprehensive PR information
- **Get PR files** - See what files changed in a PR
- **Get PR comments** - Read all comments and reviews
- **Get PR diff** - View actual code changes

### Issue Management
- **List issues** - Get repository issues with advanced filtering
- **Get issue details** - Complete issue information
- **Create issues** - Programmatically create new issues
- **Update issues** - Modify existing issues
- **Search issues** - Find issues across repositories

### User & Organization
- **Get authenticated user** - Your GitHub profile information
- **Search users** - Find GitHub users and organizations

### Tags & Releases
- **List tags** - Get repository tags and releases
- **Get tag details** - Information about specific tags

## 🔧 Technical Implementation

### Technology Stack

**Core Technologies:**
- **Python 3.11+** - Modern async/await support
- **Go 1.19+** - For building GitHub MCP server
- **Model Context Protocol** - Standardized AI-tool integration

**AI & Agent Framework:**
- **Azure OpenAI GPT-4o** - Primary language model
- **LangGraph** - Agent workflow orchestration
- **LangChain** - Tool integration and abstractions

**GitHub Integration:**
- **GitHub MCP Server** - Official GitHub MCP implementation
- **GitHub Personal Access Token** - API authentication
- **GitHub REST API** - Underlying repository operations

**Observability & Development:**
- **Langfuse** - LLM observability and tracing
- **UV Package Manager** - Fast Python dependency management
- **Pydantic** - Data validation and settings management

### Project Structure

```text
demo_githubmcp/
├── 📄 README.md                   # Comprehensive setup guide
├── 🚀 main.py                     # Interactive GitHub assistant
├── ⚙️  pyproject.toml              # UV project configuration
├── 🧪 tests/                      # Organized test suite
│   ├── test_environment.py        # Environment validation
│   ├── test_mcp_client.py         # MCP client functionality
│   ├── test_github_tools.py       # GitHub tools testing
│   └── test_agent.py              # Agent integration tests
├── 🔧 mcp_server/
│   └── github-mcp-server          # GitHub MCP server binary
└── 📦 src/
    ├── 🤖 agents/
    │   └── github_agent.py        # LangGraph agent implementation
    ├── ⚙️  config/
    │   └── settings.py            # Configuration management
    ├── 🏗️  services/
    │   └── github_service.py      # High-level service operations
    └── 🛠️  tools/
        ├── github_tools.py        # 20 GitHub tool implementations
        └── mcp_client/
            └── github_client.py   # MCP client wrapper
```

## 💡 Key Design Decisions

### 1. **MCP Protocol Adoption**
**Why:** Standardized protocol ensures compatibility and future-proofing
**Benefit:** Easy integration with other MCP-compatible tools and models

### 2. **LangGraph for Agent Orchestration** 
**Why:** Provides structured workflow management and state handling
**Benefit:** Enables complex multi-step reasoning and error recovery

### 3. **Service Layer Architecture**
**Why:** Separates high-level operations from low-level tool calls
**Benefit:** Clean API for both agent and programmatic usage

### 4. **Comprehensive Tool Coverage**
**Why:** Maps essential GitHub operations to standardized tools
**Benefit:** Handles 80% of common GitHub workflows through natural language

### 5. **Azure OpenAI Integration**
**Why:** Enterprise-grade AI with reliable performance and compliance
**Benefit:** Production-ready with proper security and monitoring

## 🔬 Engineering Challenges Solved

### 1. **MCP Connection Management**
**Challenge:** MCP client connections hanging during initialization
**Solution:** Implemented connection pooling with proper lifecycle management and timeout handling

### 2. **Tool Schema Validation**
**Challenge:** Ensuring LangChain tools properly interface with MCP server
**Solution:** Comprehensive schema validation and error handling in tool wrappers

### 3. **Async Operation Coordination**
**Challenge:** Managing concurrent GitHub API calls and agent operations
**Solution:** Proper async/await patterns with connection pooling and resource management

### 4. **Cross-Platform Compatibility**
**Challenge:** Supporting both macOS and Windows development environments
**Solution:** UV package manager with comprehensive setup documentation

### 5. **Error Recovery and Debugging**
**Challenge:** Providing meaningful error messages for complex agent workflows
**Solution:** Layered error handling with Langfuse observability integration

## 🎯 Use Cases & Applications

### 1. **Repository Analysis**
- Analyze repository structure and activity
- Compare branches and review commit history
- Understand project evolution and contributor patterns

### 2. **Code Review Assistance**
- Summarize pull request changes
- Identify potential issues in code changes
- Track review progress and comment threads

### 3. **Issue Management**
- Intelligent issue triage and categorization
- Automated issue creation from natural language descriptions
- Cross-repository issue tracking and analysis

### 4. **Project Planning**
- Analyze repository activity and trends
- Generate project status reports
- Identify bottlenecks and areas for improvement

### 5. **Developer Productivity**
- Natural language interface for GitHub operations
- Automated routine tasks and reporting
- Integration with existing development workflows

## 🚀 Getting Started

### Quick Start
1. **Install UV package manager**: `brew install uv` (macOS) or follow Windows instructions
2. **Setup project**: `uv sync` to install dependencies
3. **Build MCP server**: Follow Go build instructions for GitHub MCP server
4. **Configure environment**: Set up Azure OpenAI, GitHub token, and Langfuse (optional)
5. **Run application**: `python main.py` for interactive GitHub assistant

### Example Usage
```text
🔍 Your question: What branches are available in microsoft/vscode?
🤖 Answer: The microsoft/vscode repository has 3 main branches: main, release/1.85, and insiders...

🔍 Your question: Show me the latest commits in openai/openai-python
🤖 Answer: Here are the latest commits in openai/openai-python: [detailed commit information]

🔍 Your question: Find issues in facebook/react with label "bug"
🤖 Answer: I found 23 open issues with the "bug" label in facebook/react...
```

## 📊 Project Metrics

- **✅ 51 MCP Tools Available** - Complete GitHub MCP server integration
- **✅ 20 Implemented Tools** - Essential GitHub operations covered
- **✅ 4 Test Suites** - Comprehensive testing framework
- **✅ Cross-Platform Support** - macOS and Windows compatibility
- **✅ Production Ready** - Error handling, configuration, and observability

## 🔮 Future Enhancements

### Planned Features
- **Advanced Code Analysis** - Syntax highlighting and code quality metrics
- **Multi-Repository Operations** - Cross-repository analysis and comparison
- **Workflow Automation** - Custom GitHub Actions integration
- **Team Collaboration** - Multi-user agent coordination
- **Enhanced Observability** - Advanced analytics and performance monitoring

### Integration Opportunities
- **IDE Plugins** - VS Code and other editor integrations
- **CI/CD Pipelines** - Automated code review and analysis
- **Project Management** - Integration with Jira, Linear, and other tools
- **Slack/Teams Bots** - Conversational GitHub operations
- **Custom Dashboards** - Real-time repository monitoring and reporting

---

**This project demonstrates the power of combining Model Context Protocol with modern AI agents to create intelligent, natural language interfaces for complex technical operations. The result is a production-ready system that makes GitHub operations accessible through conversation while maintaining the full power and flexibility of the underlying APIs.**
