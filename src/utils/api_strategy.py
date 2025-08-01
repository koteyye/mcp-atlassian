"""
Strategy pattern for different API integrations.
"""
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.utils import logger, log_method_call
from src.config import config


class APIStrategy(ABC):
    """Abstract base class for API strategies."""
    
    def __init__(self, base_url: str, username: str, api_token: str, auth_type: str = 'basic'):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.auth_type = auth_type.lower()
        self.session = requests.Session()
        
        # Configure authentication based on auth_type
        self._setup_authentication()
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Always disable SSL verification for corporate self-signed certificates
        # This is common for internal corporate Atlassian instances
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.info("SSL verification disabled for corporate self-signed certificates")
    
    def _setup_authentication(self):
        """Setup authentication method based on auth_type."""
        if self.auth_type == 'bearer':
            # Use Bearer token authentication
            self.session.headers['Authorization'] = f'Bearer {self.api_token}'
            logger.info("Bearer token authentication configured")
        else:
            # Use Basic authentication (default)
            if self.username and self.api_token:
                self.session.auth = (self.username, self.api_token)
                logger.info("Basic authentication configured")
            else:
                logger.warning("No valid authentication credentials found")
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        pass
    
    @abstractmethod
    def get(self, resource_id: str) -> Dict[str, Any]:
        """Get a resource by ID."""
        pass
    
    @abstractmethod
    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a resource."""
        pass
    
    @abstractmethod
    def delete(self, resource_id: str) -> bool:
        """Delete a resource."""
        pass
    
    @abstractmethod
    def search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for resources with filters."""
        pass
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        # Detailed request logging
        logger.info(f"=== API REQUEST DETAILS ===")
        logger.info(f"Method: {method}")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {dict(self.session.headers)}")
        if self.session.auth:
            logger.info(f"Auth: {self.session.auth[0]}:***")  # Hide password/token
        else:
            logger.info("Auth: Bearer token (in headers)")
        logger.info(f"SSL Verify: {self.session.verify}")
        if data:
            logger.info(f"Request Data: {data}")
        
        try:
            response = self.session.request(method, url, json=data)
            
            # Detailed response logging
            logger.info(f"=== API RESPONSE DETAILS ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Text (first 500 chars): {response.text[:500]}")
            
            response.raise_for_status()
            
            # Check if response is empty
            if not response.text.strip():
                logger.warning("Response body is empty")
                
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"=== API REQUEST FAILED ===")
            logger.error(f"Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Headers: {dict(e.response.headers)}")
                logger.error(f"Response Text: {e.response.text}")
            raise
