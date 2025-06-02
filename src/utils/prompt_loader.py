"""
Utility for loading and validating prompts from YAML files
"""
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import yaml


class SystemPrompts(BaseModel):
    """System prompts configuration"""
    base: str


class QueryPrompts(BaseModel):
    """Query templates for GitHub operations"""
    branches: str
    repository_info: str
    pull_requests: str
    pull_request_summary: str
    commits: str
    file_content: str
    search_repos: str


class TestPrompts(BaseModel):
    """Test prompts and example queries"""
    example_queries: List[str]


class Prompts(BaseModel):
    """Root prompt configuration"""
    system: SystemPrompts
    queries: QueryPrompts
    test: TestPrompts


class PromptLoader:
    """Loader for YAML prompt files with validation"""
    
    def __init__(self, prompts_dir: str = "src/prompts"):
        """Initialize the prompt loader"""
        self.prompts_dir = prompts_dir
        self._prompts: Optional[Prompts] = None
    
    def load_prompts(self, filename: str = "github_agent_prompts.yaml") -> Prompts:
        """Load and validate prompts from YAML file"""
        if self._prompts is not None:
            return self._prompts
        
        path = os.path.join(self.prompts_dir, filename)
        
        try:
            with open(path, 'r') as file:
                data = yaml.safe_load(file)
                self._prompts = Prompts(**data)
                return self._prompts
        except FileNotFoundError:
            raise  # Re-raise FileNotFoundError as is
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading prompts: {e}")
    
    def get_system_message(self) -> str:
        """Get the system message prompt"""
        prompts = self.load_prompts()
        return prompts.system.base.strip()
    
    def get_query_template(self, query_type: str) -> str:
        """Get a specific query template"""
        prompts = self.load_prompts()
        if not hasattr(prompts.queries, query_type):
            raise ValueError(f"Unknown query type: {query_type}")
        return getattr(prompts.queries, query_type)
    
    def get_test_queries(self) -> List[str]:
        """Get example test queries"""
        prompts = self.load_prompts()
        return prompts.test.example_queries


# Global instance
_prompt_loader: Optional[PromptLoader] = None


def get_prompt_loader() -> PromptLoader:
    """Get or create the global prompt loader instance"""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader