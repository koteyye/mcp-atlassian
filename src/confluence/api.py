"""
Confluence API implementation using Strategy pattern.
"""
from typing import Dict, Any, List, Optional
from src.utils.api_strategy import APIStrategy
from src.utils import logger, log_method_call, validate_required_fields, ConfluencePageBuilder


class ConfluenceAPI(APIStrategy):
    """Confluence API implementation."""
    
    def __init__(self, base_url: str, username: str, api_token: str, auth_type: str = 'basic'):
        super().__init__(base_url, username, api_token, auth_type)
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
        try:
            logger.info(f"Getting page with ID: {page_id}")
            response = self._make_request(
                'GET',
                f'{self.api_base}/content/{page_id}?expand=body.storage,space,ancestors'
            )
            
            logger.info(f"Response received, status: {response.status_code}")
            logger.info(f"Response text length: {len(response.text) if response.text else 0}")
            
            # Safe JSON parsing
            try:
                if not response.text or not response.text.strip():
                    logger.error("Response text is empty or None")
                    return {}
                    
                logger.info("Attempting to parse JSON...")
                result = response.json()
                logger.info(f"JSON parsed successfully, type: {type(result)}")
                
                if result is None:
                    logger.error("JSON result is None")
                    return {}
                    
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response.text[:500]}")
                return {}
            except Exception as e:
                logger.error(f"Unexpected error parsing JSON: {str(e)}")
                logger.error(f"Response text: {response.text[:500]}")
                return {}
            
            # Safe result validation
            if not isinstance(result, dict):
                logger.warning(f"Expected dict response, got {type(result)}: {result}")
                return {}
                
            logger.info(f"Successfully parsed page data: {result.get('title', 'No title')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in get() method: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
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
        
        # Safe JSON parsing
        try:
            result = response.json() if response.text.strip() else {}
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response.text}")
            return []
        
        # Safe result extraction
        if not isinstance(result, dict):
            logger.warning(f"Expected dict response, got {type(result)}")
            return []
            
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
        
        # Safe JSON parsing
        try:
            result = response.json() if response.text.strip() else {}
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response.text}")
            return []
        
        # Safe result extraction
        if not isinstance(result, dict):
            logger.warning(f"Expected dict response, got {type(result)}")
            return []
            
        return result.get('results', [])
    
    @log_method_call
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information - spaces, content types, etc."""
        debug_info = {}
        
        try:
            # Get spaces
            spaces_response = self._make_request('GET', f'{self.api_base}/space?limit=100')
            try:
                spaces_data = spaces_response.json() if spaces_response.text.strip() else {}
                if isinstance(spaces_data, dict) and 'results' in spaces_data:
                    debug_info['spaces'] = [
                        {'key': s.get('key', ''), 'name': s.get('name', ''), 'type': s.get('type', '')}
                        for s in spaces_data['results'] if isinstance(s, dict)
                    ]
                else:
                    debug_info['spaces'] = []
            except ValueError as e:
                debug_info['spaces_error'] = f"JSON parse error: {str(e)}"
        except Exception as e:
            debug_info['spaces_error'] = str(e)
        
        try:
            # Get current user info
            user_response = self._make_request('GET', f'{self.api_base}/user/current')
            try:
                user_data = user_response.json() if user_response.text.strip() else {}
                debug_info['current_user'] = user_data if isinstance(user_data, dict) else {}
            except ValueError as e:
                debug_info['user_error'] = f"JSON parse error: {str(e)}"
        except Exception as e:
            debug_info['user_error'] = str(e)
        
        return debug_info
