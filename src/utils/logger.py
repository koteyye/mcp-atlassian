"""
Logging utilities with decorator pattern for request validation and logging.
"""
import logging
import functools
from typing import Any, Callable, Dict
from src.config import config


class Logger:
    """Logger singleton for the MCP server."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        logging_config = config.get_logging_config()
        level = getattr(logging, logging_config.get('level', 'WARNING'))
        
        self._logger = logging.getLogger('mcp_atlassian')
        self._logger.setLevel(level)
        
        # Console handler only - no file logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Simple formatter
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        if not self._logger.handlers:
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Get the logger instance."""
        return self._logger


# Global logger instance
logger = Logger().get_logger()


def log_method_call(func: Callable) -> Callable:
    """Decorator to log method calls with arguments and return values."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args={args[1:]} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper


def validate_required_fields(required_fields: list):
    """Decorator to validate required fields in method arguments."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the data argument (usually the first non-self argument)
            data = args[1] if len(args) > 1 else kwargs.get('data', {})
            
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
