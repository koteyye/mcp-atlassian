#!/usr/bin/env python3
"""
Main entry point for MCP Atlassian Server.
Configuration is received dynamically via stdio from Roo Code/Cline.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server import MCPAtlassianServer


def main():
    """Main entry point."""
    try:
        server = MCPAtlassianServer()
        server.run()
    except Exception as e:
        print(f"Failed to start server: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
