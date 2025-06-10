# LLM Response Parser Module
# Handles parsing different types of LLM responses
# Supports JSON parsing, validation, and error recovery

import json
import re
from typing import Dict, Any, List, Optional, Tuple

class ParseResult:
    """Container for parsing results"""
    def __init__(self, success: bool, data: Any = None, error: str = None, parser_used: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.parser_used = parser_used

def clean_json_response(text: str) -> str:
    """
    Clean LLM response text to extract JSON
    Removes common LLM artifacts and formatting issues
    
    Args:
        text (str): Raw LLM response
        
    Returns:
        str: Cleaned JSON text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove common LLM prefixes
    prefixes_to_remove = [
        "Here's the JSON:",
        "Here is the JSON:",
        "```json",
        "```",
        "JSON:",
        "Response:",
    ]
    
    for prefix in prefixes_to_remove:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Remove common LLM suffixes
    suffixes_to_remove = [
        "```",
        "Is this helpful?",
        "Let me know if you need any changes.",
    ]
    
    for suffix in suffixes_to_remove:
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()
    
    # Find JSON block using regex
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        text = match.group(0)
    
    return text

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
    """
    Validate that required fields are present in parsed data
    
    Args:
        data (dict): Parsed data to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""

def basic_monster_parser(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Parse basic monster generation response
    Expected format: {"name": "...", "description": "..."}
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration from prompts
        
    Returns:
        ParseResult: Parsing results
    """
    try:
        # Clean the response
        cleaned = clean_json_response(response_text)
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate it's a dictionary
        if not isinstance(data, dict):
            return ParseResult(
                success=False,
                error="Response is not a JSON object",
                parser_used="basic_monster_parser"
            )
        
        # Validate required fields
        required_fields = parser_config.get('required_fields', ['name', 'description'])
        is_valid, error_msg = validate_required_fields(data, required_fields)
        
        if not is_valid:
            return ParseResult(
                success=False,
                error=error_msg,
                parser_used="basic_monster_parser"
            )
        
        # Clean up the data
        cleaned_data = {
            'name': str(data['name']).strip(),
            'description': str(data['description']).strip()
        }
        
        return ParseResult(
            success=True,
            data=cleaned_data,
            parser_used="basic_monster_parser"
        )
        
    except json.JSONDecodeError as e:
        return ParseResult(
            success=False,
            error=f"Invalid JSON: {str(e)}",
            parser_used="basic_monster_parser"
        )
    except Exception as e:
        return ParseResult(
            success=False,
            error=f"Parsing error: {str(e)}",
            parser_used="basic_monster_parser"
        )

def detailed_monster_parser(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Parse detailed monster generation response
    Expected format includes stats, abilities, personality, etc.
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration from prompts
        
    Returns:
        ParseResult: Parsing results
    """
    try:
        # Clean the response
        cleaned = clean_json_response(response_text)
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate it's a dictionary
        if not isinstance(data, dict):
            return ParseResult(
                success=False,
                error="Response is not a JSON object",
                parser_used="detailed_monster_parser"
            )
        
        # Validate required fields
        required_fields = parser_config.get('required_fields', ['name', 'description'])
        is_valid, error_msg = validate_required_fields(data, required_fields)
        
        if not is_valid:
            return ParseResult(
                success=False,
                error=error_msg,
                parser_used="detailed_monster_parser"
            )
        
        # Process and validate the detailed structure
        cleaned_data = {
            'basic_info': {
                'name': str(data.get('name', '')).strip(),
                'species': str(data.get('species', 'Unknown')).strip(),
                'description': str(data.get('description', '')).strip(),
                'backstory': str(data.get('backstory', '')).strip()
            },
            'stats': data.get('stats', {}),
            'personality': data.get('personality', {}),
            'abilities': data.get('abilities', [])
        }
        
        # Validate stats structure
        if isinstance(cleaned_data['stats'], dict):
            # Ensure numeric values for stats
            for stat_name in ['health', 'attack', 'defense', 'speed']:
                if stat_name in cleaned_data['stats']:
                    try:
                        cleaned_data['stats'][stat_name] = int(cleaned_data['stats'][stat_name])
                    except (ValueError, TypeError):
                        cleaned_data['stats'][stat_name] = 100  # Default value
        
        # Validate abilities structure
        if not isinstance(cleaned_data['abilities'], list):
            cleaned_data['abilities'] = []
        
        return ParseResult(
            success=True,
            data=cleaned_data,
            parser_used="detailed_monster_parser"
        )
        
    except json.JSONDecodeError as e:
        return ParseResult(
            success=False,
            error=f"Invalid JSON: {str(e)}",
            parser_used="detailed_monster_parser"
        )
    except Exception as e:
        return ParseResult(
            success=False,
            error=f"Parsing error: {str(e)}",
            parser_used="detailed_monster_parser"
        )

def story_monster_parser(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Parse story-driven monster generation response
    Expected format includes wish, motivation, detailed backstory
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration from prompts
        
    Returns:
        ParseResult: Parsing results
    """
    try:
        # Clean the response
        cleaned = clean_json_response(response_text)
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate it's a dictionary
        if not isinstance(data, dict):
            return ParseResult(
                success=False,
                error="Response is not a JSON object",
                parser_used="story_monster_parser"
            )
        
        # Validate required fields
        required_fields = parser_config.get('required_fields', ['name', 'description', 'wish'])
        is_valid, error_msg = validate_required_fields(data, required_fields)
        
        if not is_valid:
            return ParseResult(
                success=False,
                error=error_msg,
                parser_used="story_monster_parser"
            )
        
        # Process the story-focused structure
        cleaned_data = {
            'basic_info': {
                'name': str(data.get('name', '')).strip(),
                'species': str(data.get('species', 'Unknown')).strip(),
                'description': str(data.get('description', '')).strip(),
                'backstory': str(data.get('backstory', '')).strip()
            },
            'story': {
                'wish': str(data.get('wish', '')).strip(),
                'motivation': str(data.get('personality', {}).get('motivation', '')).strip()
            },
            'stats': data.get('stats', {}),
            'personality': data.get('personality', {}),
            'abilities': data.get('abilities', [])
        }
        
        return ParseResult(
            success=True,
            data=cleaned_data,
            parser_used="story_monster_parser"
        )
        
    except json.JSONDecodeError as e:
        return ParseResult(
            success=False,
            error=f"Invalid JSON: {str(e)}",
            parser_used="story_monster_parser"
        )
    except Exception as e:
        return ParseResult(
            success=False,
            error=f"Parsing error: {str(e)}",
            parser_used="story_monster_parser"
        )

# Parser registry - maps parser names to functions
PARSER_REGISTRY = {
    'basic_monster_parser': basic_monster_parser,
    'detailed_monster_parser': detailed_monster_parser,
    'story_monster_parser': story_monster_parser
}

def parse_response(response_text: str, parser_config: Dict[str, Any]) -> ParseResult:
    """
    Parse LLM response using the specified parser
    
    Args:
        response_text (str): Raw LLM response
        parser_config (dict): Parser configuration including parser name
        
    Returns:
        ParseResult: Parsing results
    """
    parser_name = parser_config.get('parser_name', 'basic_monster_parser')
    
    if parser_name not in PARSER_REGISTRY:
        return ParseResult(
            success=False,
            error=f"Unknown parser: {parser_name}",
            parser_used=parser_name
        )
    
    parser_function = PARSER_REGISTRY[parser_name]
    return parser_function(response_text, parser_config)

def get_available_parsers() -> List[str]:
    """Get list of available parser names"""
    return list(PARSER_REGISTRY.keys())