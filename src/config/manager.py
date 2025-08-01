"""
Configuration management using Singleton pattern.
Configuration is received dynamically from Roo Code/Cline via stdio protocol.
"""
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Singleton configuration manager for MCP server settings."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Dict[str, Any]] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Configuration is set externally via set_config() method
        # No automatic loading from files
        pass
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set configuration received from external source (Roo Code/Cline)."""
        self._config = config.copy() if config else {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        if self._config is None:
            return default
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_jira_config(self) -> Dict[str, str]:
        """Get Jira configuration with fallback to environment variables."""
        jira_config = self.get('jira', {})
        
        # Fallback to environment variables if config is not complete
        # Support both uppercase and lowercase env vars for RooCode compatibility
        if not jira_config.get('url'):
            jira_config['url'] = os.getenv('jira_url', os.getenv('JIRA_URL', jira_config.get('url', '')))
        if not jira_config.get('username'):
            jira_config['username'] = os.getenv('jira_username', os.getenv('JIRA_USERNAME', jira_config.get('username', '')))
        if not jira_config.get('api_token'):
            jira_config['api_token'] = os.getenv('jira_api_token', os.getenv('JIRA_API_TOKEN', jira_config.get('api_token', '')))
        if not jira_config.get('auth_type'):
            jira_config['auth_type'] = os.getenv('jira_auth_type', os.getenv('JIRA_AUTH_TYPE', jira_config.get('auth_type', 'basic')))
        
        return jira_config
    
    def get_confluence_config(self) -> Dict[str, str]:
        """Get Confluence configuration with fallback to environment variables."""
        confluence_config = self.get('confluence', {})
        
        # Fallback to environment variables if config is not complete
        # Support both uppercase and lowercase env vars for RooCode compatibility
        if not confluence_config.get('url'):
            confluence_config['url'] = os.getenv('confluence_url', os.getenv('CONFLUENCE_URL', confluence_config.get('url', '')))
        if not confluence_config.get('username'):
            confluence_config['username'] = os.getenv('confluence_username', os.getenv('CONFLUENCE_USERNAME', confluence_config.get('username', '')))
        if not confluence_config.get('api_token'):
            confluence_config['api_token'] = os.getenv('confluence_api_token', os.getenv('CONFLUENCE_API_TOKEN', confluence_config.get('api_token', '')))
        if not confluence_config.get('auth_type'):
            confluence_config['auth_type'] = os.getenv('confluence_auth_type', os.getenv('CONFLUENCE_AUTH_TYPE', confluence_config.get('auth_type', 'basic')))
        
        return confluence_config
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration."""
        return self.get('logging', {'level': 'INFO', 'file': 'mcp_server.log'})
    
    def is_ssl_disabled(self) -> bool:
        """Check if SSL verification should be disabled."""
        # Check environment variable first (for RooCode compatibility)
        ssl_disable_env = os.getenv('ssl_disable', os.getenv('SSL_DISABLE', ''))
        if ssl_disable_env:
            return ssl_disable_env.lower() in ('true', '1', 'yes', 'on')
        
        # Check config
        return self.get('ssl_disable', False)
    
    def is_configured(self) -> bool:
        """Check if configuration has been set."""
        return self._config is not None
    
    def reload(self) -> None:
        """Reload configuration - stub method for compatibility."""
        # Configuration comes from external source, nothing to reload
        pass
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration for debugging (without sensitive data)."""
        if self._config is None:
            return {}
        
        # Create safe copy without API tokens
        safe_config = {}
        for service, service_config in self._config.items():
            if isinstance(service_config, dict):
                safe_config[service] = {}
                for key, value in service_config.items():
                    if key in ['api_token', 'token', 'password']:
                        safe_config[service][key] = "***" if value else "not set"
                    else:
                        safe_config[service][key] = value
            else:
                safe_config[service] = service_config
        
        return safe_config
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate current configuration and return status for each service."""
        validation_results = {
            'jira': False,
            'confluence': False,
            'overall': False
        }
        
        # Validate Jira configuration
        jira_config = self.get_jira_config()
        if (jira_config.get('url') and 
            jira_config.get('username') and 
            jira_config.get('api_token')):
            validation_results['jira'] = True
        
        # Validate Confluence configuration
        confluence_config = self.get_confluence_config()
        if (confluence_config.get('url') and 
            confluence_config.get('username') and 
            confluence_config.get('api_token')):
            validation_results['confluence'] = True
        
        # Overall validation - at least one service should be configured
        validation_results['overall'] = validation_results['jira'] or validation_results['confluence']
        
        return validation_results
    
    def get_configuration_status(self) -> str:
        """Get human-readable configuration status."""
        if not self.is_configured():
            return "Not configured"
        
        validation = self.validate_configuration()
        
        status_parts = []
        if validation['jira']:
            status_parts.append("Jira: ✓")
        else:
            status_parts.append("Jira: ✗")
        
        if validation['confluence']:
            status_parts.append("Confluence: ✓")
        else:
            status_parts.append("Confluence: ✗")
        
        return f"Configuration status - {', '.join(status_parts)}"


# Global instance
config = ConfigManager()
