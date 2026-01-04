"""
Response helpers for creating standardized success and error responses.

This module provides utility functions for creating consistent response
structures across different services in the Chat-Toner backend.
"""

from typing import Dict, Any


def create_error_response(error_message: str, **kwargs) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error_message: The error message to include in the response
        **kwargs: Additional fields to include in the response
        
    Returns:
        Dict containing success=False, error message, and any additional fields
        
    Example:
        >>> create_error_response("Invalid input", original_text="hello", code=400)
        {'success': False, 'error': 'Invalid input', 'original_text': 'hello', 'code': 400}
    """
    if 'success' in kwargs or 'error' in kwargs:
        raise ValueError("Reserved keys 'success' and 'error' cannot be provided in kwargs")

    return {
        "success": False,
        "error": error_message,
        **kwargs
    }


def create_success_response(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: The primary data to include in the response
        **kwargs: Additional fields to include in the response
        
    Returns:
        Dict containing success=True and the provided data
        
    Example:
        >>> create_success_response({"result": "ok"}, timestamp="2024-01-01")
        {'success': True, 'result': 'ok', 'timestamp': '2024-01-01'}
    """
    if 'success' in data or 'success' in kwargs:
        raise ValueError("Reserved key 'success' cannot be provided in data or kwargs")

    return {
        "success": True,
        **data,
        **kwargs
    }
