"""
MCP Atlassian Server - Main application using stdio protocol.
"""
import json
import sys
import traceback
from typing import Dict, Any, Optional

from src.config import config
from src.utils import logger
from src.jira import JiraAPI
from src.confluence import ConfluenceAPI
from src.commands import (
    CreateJiraIssueCommand, UpdateJiraIssueCommand, DeleteJiraIssueCommand,
    CreateJiraSubtaskCommand, SearchJiraIssuesCommand, GetJiraDebugInfoCommand,
    CreateConfluencePageCommand, UpdateConfluencePageCommand, DeleteConfluencePageCommand,
    SearchConfluencePagesCommand, SearchConfluencePagesByParentCommand, GetConfluenceDebugInfoCommand,
    JiraCommandHandler, ConfluenceCommandHandler, SystemCommandHandler
)


class MCPAtlassianServer:
    """Main MCP server class."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.jira_api = None
        self.confluence_api = None
        self.command_handler = None
        # Initialize system commands first
        self._initialize_system_commands()
        # Try to initialize APIs from environment variables
        self._try_initialize_from_env()
    
    def _initialize_apis(self):
        """Initialize Jira and Confluence APIs after configuration is set."""
        if not config.is_configured():
            logger.warning("Configuration not set, APIs cannot be initialized")
            return
        
        logger.info("Starting API initialization...")
        logger.info(f"Configuration status: {config.get_configuration_status()}")
        
        validation = config.validate_configuration()
        logger.debug(f"Configuration validation: {validation}")
        
        try:
            # Initialize Jira API
            if validation['jira']:
                jira_config = config.get_jira_config()
                self.jira_api = JiraAPI(
                    jira_config['url'],
                    jira_config['username'],
                    jira_config['api_token']
                )
                logger.info(f"Jira API initialized successfully for {jira_config.get('url')}")
            else:
                logger.warning("Jira configuration incomplete, Jira commands will be unavailable")
            
            # Initialize Confluence API
            if validation['confluence']:
                confluence_config = config.get_confluence_config()
                self.confluence_api = ConfluenceAPI(
                    confluence_config['url'],
                    confluence_config['username'],
                    confluence_config['api_token']
                )
                logger.info(f"Confluence API initialized successfully for {confluence_config.get('url')}")
            else:
                logger.warning("Confluence configuration incomplete, Confluence commands will be unavailable")
        
        except Exception as e:
            logger.error(f"Failed to initialize APIs: {str(e)}")
            raise
        
        # After APIs are initialized, initialize commands
        self._initialize_commands()
    
    def _initialize_system_commands(self):
        """Initialize system command handler only."""
        system_handler = SystemCommandHandler()
        self.command_handler = system_handler
        logger.info("System command handler initialized")
    
    def _try_initialize_from_env(self):
        """Try to initialize APIs from environment variables."""
        try:
            # Check if we have environment variables
            jira_config = config.get_jira_config()
            confluence_config = config.get_confluence_config()
            
            has_jira = all([jira_config.get('url'), jira_config.get('username'), jira_config.get('api_token')])
            has_confluence = all([confluence_config.get('url'), confluence_config.get('username'), confluence_config.get('api_token')])
            
            if has_jira or has_confluence:
                logger.info("Found configuration in environment variables, initializing APIs...")
                # Set a dummy config to mark as configured
                config.set_config({'initialized_from_env': True})
                self._initialize_apis()
            else:
                logger.info("No complete configuration found in environment variables")
        except Exception as e:
            logger.error(f"Failed to initialize from environment: {str(e)}")
    
    def _initialize_commands(self):
        """Initialize command handlers using Chain of Responsibility pattern."""
        # Initialize Jira commands
        jira_commands = {}
        if self.jira_api:
            jira_commands = {
                'create_jira_issue': CreateJiraIssueCommand(self.jira_api),
                'update_jira_issue': UpdateJiraIssueCommand(self.jira_api),
                'delete_jira_issue': DeleteJiraIssueCommand(self.jira_api),
                'create_jira_subtask': CreateJiraSubtaskCommand(self.jira_api),
                'search_jira_issues': SearchJiraIssuesCommand(self.jira_api),
                'get_jira_debug_info': GetJiraDebugInfoCommand(self.jira_api)
            }
        
        # Initialize Confluence commands
        confluence_commands = {}
        if self.confluence_api:
            confluence_commands = {
                'create_confluence_page': CreateConfluencePageCommand(self.confluence_api),
                'update_confluence_page': UpdateConfluencePageCommand(self.confluence_api),
                'delete_confluence_page': DeleteConfluencePageCommand(self.confluence_api),
                'search_confluence_pages': SearchConfluencePagesCommand(self.confluence_api),
                'search_confluence_pages_by_parent': SearchConfluencePagesByParentCommand(self.confluence_api),
                'get_confluence_debug_info': GetConfluenceDebugInfoCommand(self.confluence_api)
            }
        
        # Build command handler chain
        system_handler = SystemCommandHandler()
        jira_handler = JiraCommandHandler(jira_commands)
        confluence_handler = ConfluenceCommandHandler(confluence_commands)
        
        # Chain: System -> Jira -> Confluence
        system_handler.set_successor(jira_handler).set_successor(confluence_handler)
        
        self.command_handler = system_handler
        logger.info("Command handlers initialized successfully")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming MCP message."""
        try:
            # Extract command and arguments
            if 'method' not in message:
                return {
                    'error': 'Missing method in message',
                    'success': False
                }
            
            method = message['method']
            params = message.get('params', {})
            
            logger.info(f"Processing command: {method}")
            
            # Handle MCP protocol messages
            if method == 'initialize':
                return self._handle_initialize(params)
            elif method == 'tools/list':
                return self._handle_tools_list()
            elif method == 'tools/call':
                return self._handle_tool_call(params)
            elif method == 'set_config':
                return self._handle_set_config(params)
            else:
                # Direct command execution
                return self.command_handler.handle(method, params)
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request and setup configuration."""
        logger.info("Handling MCP initialize request")
        logger.debug(f"Initialize params keys: {list(params.keys())}")
        
        # Check if configuration is provided in params
        if 'config' in params:
            logger.info("Received configuration from MCP client")
            logger.debug(f"Config structure: {params['config'].keys() if isinstance(params['config'], dict) else type(params['config'])}")
            config.set_config(params['config'])
            
            # Initialize APIs after configuration is set
            try:
                self._initialize_apis()
                logger.info("Server initialization completed with configuration")
            except Exception as e:
                logger.error(f"Failed to initialize APIs with provided config: {str(e)}")
                logger.debug(f"Full error: {traceback.format_exc()}")
        else:
            logger.info("No configuration provided in initialize request")
        
        return {
            'protocolVersion': '2024-11-05',
            'capabilities': {
                'tools': {}
            },
            'serverInfo': {
                'name': 'mcp-atlassian-server',
                'version': '1.0.0'
            }
        }
    
    def _handle_tools_list(self) -> Dict[str, Any]:
        """Handle MCP tools list request."""
        tools = []
        
        # System tools
        tools.extend([
            {
                'name': 'ping',
                'description': 'Check server connectivity',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'health',
                'description': 'Check server health status',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'config_status',
                'description': 'Check configuration status for Jira and Confluence',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            }
        ])
        
        # Jira tools
        if self.jira_api:
            tools.extend([
                {
                    'name': 'create_jira_issue',
                    'description': 'Create a new Jira issue',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'project': {'type': 'string', 'description': 'Project key'},
                            'summary': {'type': 'string', 'description': 'Issue summary'},
                            'issuetype': {'type': 'string', 'description': 'Issue type'},
                            'description': {'type': 'string', 'description': 'Issue description'},
                            'assignee': {'type': 'string', 'description': 'Assignee username'},
                            'labels': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Labels'},
                            'epic': {'type': 'string', 'description': 'Epic key'}
                        },
                        'required': ['project', 'summary', 'issuetype']
                    }
                },
                {
                    'name': 'search_jira_issues',
                    'description': 'Search for Jira issues',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'project': {'type': 'string', 'description': 'Project key'},
                            'epic': {'type': 'string', 'description': 'Epic key'},
                            'assignee': {'type': 'string', 'description': 'Assignee username'},
                            'status': {'type': 'string', 'description': 'Issue status'},
                            'maxResults': {'type': 'number', 'description': 'Maximum results'}
                        }
                    }
                },
                {
                    'name': 'get_jira_debug_info',
                    'description': 'Get Jira debug information',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {}
                    }
                }
            ])
        
        # Confluence tools
        if self.confluence_api:
            tools.extend([
                {
                    'name': 'create_confluence_page',
                    'description': 'Create a new Confluence page',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'space': {'type': 'string', 'description': 'Space key'},
                            'title': {'type': 'string', 'description': 'Page title'},
                            'content': {'type': 'string', 'description': 'Page content'},
                            'parent': {'type': 'string', 'description': 'Parent page ID'}
                        },
                        'required': ['space', 'title', 'content']
                    }
                },
                {
                    'name': 'search_confluence_pages',
                    'description': 'Search for Confluence pages',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'space': {'type': 'string', 'description': 'Space key'},
                            'title': {'type': 'string', 'description': 'Page title'},
                            'limit': {'type': 'number', 'description': 'Maximum results'}
                        }
                    }
                },
                {
                    'name': 'get_confluence_debug_info',
                    'description': 'Get Confluence debug information',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {}
                    }
                }
            ])
        
        return {'tools': tools}
    
    def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool call request."""
        if 'name' not in params:
            return {
                'error': 'Missing tool name',
                'success': False
            }
        
        tool_name = params['name']
        arguments = params.get('arguments', {})
        
        result = self.command_handler.handle(tool_name, arguments)
        
        return {
            'content': [
                {
                    'type': 'text',
                    'text': json.dumps(result, indent=2)
                }
            ]
        }
    
    def _handle_set_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration setting request."""
        try:
            if 'config' not in params:
                return {
                    'success': False,
                    'error': 'Missing config in parameters'
                }
            
            logger.info("Setting configuration from MCP client")
            config.set_config(params['config'])
            
            # Re-initialize APIs with new configuration
            self._initialize_apis()
            
            return {
                'success': True,
                'message': 'Configuration set and APIs initialized successfully'
            }
        except Exception as e:
            logger.error(f"Failed to set configuration: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run(self):
        """Run the MCP server on stdio."""
        logger.info("Starting MCP Atlassian server on stdio")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    message = json.loads(line)
                    result = self.process_message(message)
                    
                    # Send response
                    response = {
                        'jsonrpc': '2.0',
                        'id': message.get('id'),
                        'result': result
                    }
                    
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {line}")
                    error_response = {
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {
                            'code': -32700,
                            'message': 'Parse error'
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
