"""
Command pattern implementation for MCP commands.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.utils import logger, log_method_call


class Command(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the command with given arguments."""
        pass
    
    def validate_args(self, args: Dict[str, Any], required_fields: list) -> None:
        """Validate required arguments."""
        missing_fields = []
        for field in required_fields:
            if field not in args or args[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


class JiraCommand(Command):
    """Base class for Jira commands."""
    
    def __init__(self, name: str, description: str, jira_api):
        super().__init__(name, description)
        self.jira_api = jira_api


class ConfluenceCommand(Command):
    """Base class for Confluence commands."""
    
    def __init__(self, name: str, description: str, confluence_api):
        super().__init__(name, description)
        self.confluence_api = confluence_api
