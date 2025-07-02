"""
Confluence API implementation using Strategy pattern.
"""
from typing import Dict, Any, List, Optional
from src.utils.api_strategy import APIStrategy
from src.utils import logger, log_method_call, validate_required_fields, ConfluencePageBuilder


class ConfluenceAPI(APIStrategy):
    """Confluence API implementation."""
    
    def __init__(self, base_url: str, username: str, api_token: str):
        super().__init__(base_url, username, api_token)
        self.api_base = "/rest/api"
    
    @log_method_call
    @validate_required_fields(['space', 'title', 'content'])
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Confluence page."""
        builder = ConfluencePageBuilder()
        
        # Required fields
        builder.set_space(data['space'])
        builder.set_title(data['title'])
        builder.set_content(data['content'])
        builder.set_type('page')
        
        # Optional fields
        if 'parent' in data:
            builder.set_parent(data['parent'])
        
        request_data = builder.build()
        response = self._make_request('POST', f'{self.api_base}/content', request_data)
        return response.json()
    
    @log_method_call
    def get(self, page_id: str) -> Dict[str, Any]:
        """Get a Confluence page by ID."""
        response = self._make_request(
            'GET', 
            f'{self.api_base}/content/{page_id}?expand=body.storage,space,ancestors'
        )
        return response.json()
    
    @log_method_call
    def update(self, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Confluence page."""
        # First get current page to get version
        current_page = self.get(page_id)
        current_version = current_page['version']['number']
        
        builder = ConfluencePageBuilder()
        builder.set_type('page')
        
        # Set version for update
        builder._request['version'] = {'number': current_version + 1}
        
        # Update fields
        if 'title' in data:
            builder.set_title(data['title'])
        else:
            builder.set_title(current_page['title'])
        
        if 'content' in data:
            builder.set_content(data['content'])
        
        if 'space' in data:
            builder.set_space(data['space'])
        else:
            builder.set_space(current_page['space']['key'])
        
        request_data = builder.build()
        response = self._make_request('PUT', f'{self.api_base}/content/{page_id}', request_data)
        return response.json()
    
    @log_method_call
    def delete(self, page_id: str) -> bool:
        """Delete a Confluence page."""
        response = self._make_request('DELETE', f'{self.api_base}/content/{page_id}')
        return response.status_code == 204
    
    @log_method_call
    def search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for Confluence pages with filters."""
        params = {}
        
        if 'space' in filters:
            params['spaceKey'] = filters['space']
        
        if 'title' in filters:
            params['title'] = filters['title']
        
        if 'type' in filters:
            params['type'] = filters['type']
        else:
            params['type'] = 'page'
        
        if 'expand' not in params:
            params['expand'] = 'space,ancestors'
        
        # Limit results
        if 'limit' in filters:
            params['limit'] = filters['limit']
        else:
            params['limit'] = 50
        
        if 'start' in filters:
            params['start'] = filters['start']
        
        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        endpoint = f'{self.api_base}/content?{query_string}'
        
        response = self._make_request('GET', endpoint)
        result = response.json()
        
        return result.get('results', [])
    
    @log_method_call
    def search_by_parent(self, parent_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for child pages of a parent page."""
        if filters is None:
            filters = {}
        
        params = {
            'expand': 'space,ancestors',
            'type': 'page'
        }
        
        if 'limit' in filters:
            params['limit'] = filters['limit']
        else:
            params['limit'] = 50
        
        if 'start' in filters:
            params['start'] = filters['start']
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        endpoint = f'{self.api_base}/content/{parent_id}/child/page?{query_string}'
        
        response = self._make_request('GET', endpoint)
        result = response.json()
        
        return result.get('results', [])
    
    @log_method_call
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information - spaces, content types, etc."""
        debug_info = {}
        
        try:
            # Get spaces
            spaces_response = self._make_request('GET', f'{self.api_base}/space?limit=100')
            debug_info['spaces'] = [
                {'key': s['key'], 'name': s['name'], 'type': s['type']} 
                for s in spaces_response.json().get('results', [])
            ]
        except Exception as e:
            debug_info['spaces_error'] = str(e)
        
        try:
            # Get current user info
            user_response = self._make_request('GET', f'{self.api_base}/user/current')
            debug_info['current_user'] = user_response.json()
        except Exception as e:
            debug_info['user_error'] = str(e)
        
        return debug_info
