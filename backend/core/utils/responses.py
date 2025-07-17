# Response Utilities - Standardized Error/Success Patterns
# Universal response helpers for entire backend project
print(f"🔍 Loading {__file__}")
from typing import Any, Dict, Optional
from .console import print_error, print_warning

def success_response(data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """
    Create standardized success response
    
    Args:
        data (dict): Main data payload
        **kwargs: Additional fields to include
    
    Returns:
        dict: Success response with consistent format
    """
    response = {'success': True}
    
    if data:
        response.update(data)
    
    if kwargs:
        response.update(kwargs)
    
    return response

def error_response(error: str, **kwargs) -> Dict[str, Any]:
    """
    Create standardized error response with logging
    
    Args:
        error (str): Error message
        **kwargs: Additional fields (like setting defaults to None)
    
    Returns:
        dict: Error response with consistent format
    """
    # Log the error using console utilities
    print_error(error)
    
    response = {
        'success': False,
        'error': error
    }
    
    if kwargs:
        response.update(kwargs)
    
    return response

def check_and_return(condition: bool, 
                    error_msg: str, 
                    success_data: Dict[str, Any] = None,
                    error_defaults: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Check condition and return error response if failed, None if success
    Perfect for early returns in validation chains
    
    Args:
        condition (bool): Condition to check
        error_msg (str): Error message if condition fails
        success_data (dict): Data to return on success (None means continue)
        error_defaults (dict): Default values to set on error
    
    Returns:
        dict: Error response if condition fails, None if success
    """
    if not condition:
        print_warning(f"Validation failed: {error_msg}")
        return error_response(error_msg, **(error_defaults or {}))
    
    if success_data:
        return success_response(success_data)
    
    return None

def validate_and_continue(validation_result: Dict[str, Any], 
                         error_defaults: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Check validation result and return error if invalid, None if valid
    
    Args:
        validation_result (dict): Result from validation function
        error_defaults (dict): Default values on error
    
    Returns:
        dict: Error response if invalid, None if valid
    """
    if not validation_result.get('valid', False):
        error_msg = validation_result.get('error', 'Validation failed')
        print_warning(f"Validation check failed: {error_msg}")
        return error_response(error_msg, **(error_defaults or {}))
    
    return None