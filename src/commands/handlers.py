"""
Chain of Responsibility pattern for command processing.
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from src.utils import logger


class CommandHandler(ABC):
    """Abstract base class for command handlers."""
    
    def __init__(self, successor: Optional['CommandHandler'] = None):
        self._successor = successor
    
    def set_successor(self, successor: 'CommandHandler'):
        """Set the next handler in the chain."""
        self._successor = successor
        return successor
    
    def handle(self, command_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the command or pass to next handler."""
        result = self._handle(command_name, args)
        
        if result is None and self._successor:
            return self._successor.handle(command_name, args)
        
        if result is None:
            return {
                'success': False,
                'error': f"Unknown command: {command_name}"
            }
        
        return result
    
    @abstractmethod
    def _handle(self, command_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle specific commands. Return None if cannot handle."""
        pass


class JiraCommandHandler(CommandHandler):
    """Handler for Jira commands."""
    
    def __init__(self, jira_commands: Dict[str, Any], successor: Optional[CommandHandler] = None):
        super().__init__(successor)
        self.jira_commands = jira_commands
    
    def _handle(self, command_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle Jira commands."""
        if command_name in self.jira_commands:
            command = self.jira_commands[command_name]
            return command.execute(args)
        return None


class ConfluenceCommandHandler(CommandHandler):
    """Handler for Confluence commands."""
    
    def __init__(self, confluence_commands: Dict[str, Any], successor: Optional[CommandHandler] = None):
        super().__init__(successor)
        self.confluence_commands = confluence_commands
    
    def _handle(self, command_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle Confluence commands."""
        if command_name in self.confluence_commands:
            command = self.confluence_commands[command_name]
            return command.execute(args)
        return None


class SystemCommandHandler(CommandHandler):
    """Handler for system commands."""
    
    def __init__(self, successor: Optional[CommandHandler] = None):
        super().__init__(successor)
    
    def _handle(self, command_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle system commands."""
        if command_name == "ping":
            return {
                'success': True,
                'message': 'pong'
            }
        
        if command_name == "health":
            return {
                'success': True,
                'status': 'healthy',
                'message': 'MCP Atlassian server is running'
            }
        
        if command_name == "config_status":
            from src.config import config
            return {
                'success': True,
                'configured': config.is_configured(),
                'status': config.get_configuration_status(),
                'validation': config.validate_configuration(),
                'message': 'Configuration status retrieved'
            }
        
        if command_name == "list_commands":
            return {
                'success': True,
                'commands': self._get_available_commands(),
                'message': 'Available commands listed'
            }
        
        return None
    
    def _get_available_commands(self) -> Dict[str, str]:
        """Get list of all available commands."""
        commands = {
            # System commands
            'ping': 'Check server connectivity',
            'health': 'Check server health status',
            'config_status': 'Check configuration status',
            'list_commands': 'List all available commands',
            
            # Jira commands
            'create_jira_issue': 'Create a new Jira issue',
            'update_jira_issue': 'Update an existing Jira issue',
            'delete_jira_issue': 'Delete a Jira issue',
            'create_jira_subtask': 'Create a subtask for a parent issue',
            'search_jira_issues': 'Search for Jira issues with filters',
            'get_jira_debug_info': 'Get Jira debug information',
            
            # Confluence commands
            'create_confluence_page': 'Create a new Confluence page',
            'update_confluence_page': 'Update an existing Confluence page',
            'delete_confluence_page': 'Delete a Confluence page',
            'search_confluence_pages': 'Search for Confluence pages with filters',
            'search_confluence_pages_by_parent': 'Search for child pages of a parent page',
            'get_confluence_debug_info': 'Get Confluence debug information'
        }
        return commands
