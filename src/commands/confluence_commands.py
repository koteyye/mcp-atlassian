"""
Confluence command implementations.
"""
from typing import Dict, Any
from .base import ConfluenceCommand
from src.utils import logger, log_method_call


class CreateConfluencePageCommand(ConfluenceCommand):
    """Command to create a Confluence page."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "create_confluence_page",
            "Create a new Confluence page",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create page command."""
        self.validate_args(args, ['space', 'title', 'content'])
        
        try:
            result = self.confluence_api.create(args)
            return {
                'success': True,
                'page_id': result.get('id'),
                'page_title': result.get('title'),
                'space': result.get('space', {}).get('key'),
                'message': f"Page '{result.get('title')}' created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create Confluence page: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class UpdateConfluencePageCommand(ConfluenceCommand):
    """Command to update a Confluence page."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "update_confluence_page",
            "Update an existing Confluence page",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update page command."""
        self.validate_args(args, ['page_id'])
        
        page_id = args.pop('page_id')
        
        try:
            result = self.confluence_api.update(page_id, args)
            return {
                'success': True,
                'page_id': result.get('id'),
                'page_title': result.get('title'),
                'message': f"Page {page_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to update Confluence page: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class DeleteConfluencePageCommand(ConfluenceCommand):
    """Command to delete a Confluence page."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "delete_confluence_page",
            "Delete a Confluence page",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delete page command."""
        self.validate_args(args, ['page_id'])
        
        try:
            success = self.confluence_api.delete(args['page_id'])
            if success:
                return {
                    'success': True,
                    'message': f"Page {args['page_id']} deleted successfully"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete page'
                }
        except Exception as e:
            logger.error(f"Failed to delete Confluence page: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SearchConfluencePagesCommand(ConfluenceCommand):
    """Command to search Confluence pages."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "search_confluence_pages",
            "Search for Confluence pages with filters",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search pages command."""
        try:
            pages = self.confluence_api.search(args)
            return {
                'success': True,
                'pages': pages,
                'count': len(pages),
                'message': f"Found {len(pages)} pages"
            }
        except Exception as e:
            logger.error(f"Failed to search Confluence pages: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SearchConfluencePagesByParentCommand(ConfluenceCommand):
    """Command to search Confluence pages by parent."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "search_confluence_pages_by_parent",
            "Search for child pages of a parent page",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search pages by parent command."""
        self.validate_args(args, ['parent_id'])
        
        parent_id = args.pop('parent_id')
        
        try:
            pages = self.confluence_api.search_by_parent(parent_id, args)
            return {
                'success': True,
                'pages': pages,
                'count': len(pages),
                'parent_id': parent_id,
                'message': f"Found {len(pages)} child pages"
            }
        except Exception as e:
            logger.error(f"Failed to search Confluence pages by parent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GetConfluenceDebugInfoCommand(ConfluenceCommand):
    """Command to get Confluence debug information."""
    
    def __init__(self, confluence_api):
        super().__init__(
            "get_confluence_debug_info",
            "Get Confluence debug information (spaces, etc.)",
            confluence_api
        )
    
    @log_method_call
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get debug info command."""
        try:
            debug_info = self.confluence_api.get_debug_info()
            return {
                'success': True,
                'debug_info': debug_info,
                'message': "Debug information retrieved successfully"
            }
        except Exception as e:
            logger.error(f"Failed to get Confluence debug info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
