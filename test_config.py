#!/usr/bin/env python3
"""
Simple test for MCP Atlassian Server configuration.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server import MCPAtlassianServer
from src.config import config

def test_configuration():
    """Test configuration setting functionality."""
    print("🧪 Testing MCP Atlassian Server Configuration...")
    
    # Initialize server
    server = MCPAtlassianServer()
    print("✅ Server initialized without configuration")
    
    # Test initial state
    assert not config.is_configured(), "Config should not be set initially"
    print("✅ Initial state: configuration not set")
    
    # Test configuration setting
    test_config = {
        "jira": {
            "url": "https://test.atlassian.net",
            "username": "test@example.com",
            "api_token": "test-token"
        },
        "confluence": {
            "url": "https://test.atlassian.net/wiki",
            "username": "test@example.com",
            "api_token": "test-token"
        },
        "logging": {
            "level": "INFO",
            "file": "test.log"
        }
    }
    
    config.set_config(test_config)
    print("✅ Configuration set successfully")
    
    # Test configuration retrieval
    assert config.is_configured(), "Config should be set now"
    assert config.get("jira.url") == "https://test.atlassian.net"
    assert config.get("confluence.username") == "test@example.com"
    assert config.get("logging.level") == "INFO"
    assert config.get("nonexistent.key", "default") == "default"
    print("✅ Configuration retrieval works correctly")
    
    # Test MCP initialize message
    init_params = {
        "protocolVersion": "2024-11-05",
        "config": test_config
    }
    
    result = server._handle_initialize(init_params)
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"]["name"] == "mcp-atlassian-server"
    print("✅ MCP initialize with config works")
    
    # Test set_config message
    new_config = {
        "jira": {
            "url": "https://updated.atlassian.net",
            "username": "updated@example.com",
            "api_token": "updated-token"
        }
    }
    
    set_config_result = server._handle_set_config({"config": new_config})
    assert set_config_result["success"] == True
    assert config.get("jira.url") == "https://updated.atlassian.net"
    print("✅ Set config message works")
    
    print("🎉 All configuration tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_configuration()
        print("✅ Configuration system is working correctly!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
