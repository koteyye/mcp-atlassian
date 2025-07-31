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
    
    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (username, api_token)
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
        logger.info(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
