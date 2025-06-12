# LLM Response Parser - ULTRA-SIMPLE
# Just extracts JSON between first { and last }

import json
from typing import Dict, Any, List, Optional, Tuple

class ParseResult:
    """Container for parsing results"""
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

def extract_json(text: str) -> str:
    """
    Extract JSON from response - just find first { to last }
    
    Args:
        text (str): Raw LLM response
        
    Returns:
        str: Extracted JSON text
    """
    if not text:
        return ""
    
    # Find first { and last }
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or start >= end:
        return ""
    
    return text[start:end+1]

def basic_parser(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Simple JSON parser
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration
        
    Returns:
        ParseResult: Parsing results
    """
    try:
        if not response_text:
            return ParseResult(success=False, error="Empty response")
        
        # Extract JSON
        json_text = extract_json(response_text)
        if not json_text:
            return ParseResult(success=False, error="No JSON found")
        
        # Parse JSON
        data = json.loads(json_text)
        
        if not isinstance(data, dict):
            return ParseResult(success=False, error="Response is not a JSON object")
        
        # Check required fields if specified
        required_fields = parser_config.get('required_fields', [])
        for field in required_fields:
            if field not in data or not data[field]:
                return ParseResult(success=False, error=f"Missing required field: {field}")
        
        return ParseResult(success=True, data=data)
        
    except json.JSONDecodeError as e:
        return ParseResult(success=False, error=f"Invalid JSON: {str(e)}")
    except Exception as e:
        return ParseResult(success=False, error=f"Parse error: {str(e)}")

def parse_response(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Main entry point for parsing - just uses basic_parser
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration
        
    Returns:
        ParseResult: Parsing results
    """
    return basic_parser(response_text, parser_config)