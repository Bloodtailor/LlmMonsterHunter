# Monster Generation Module
# High-level interface for generating monsters using LLM
# Coordinates prompts, generation, parsing, and database logging

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.llm.core import generate_text, ensure_model_loaded, wait_for_generation
from backend.llm.parser import parse_response
from backend.models.llm_log import LLMLog
from backend.models.monster import Monster

def load_prompts() -> Dict[str, Any]:
    """
    Load monster generation prompts from JSON file
    
    Returns:
        dict: Loaded prompts configuration
    """
    try:
        prompts_file = Path(__file__).parent.parent / 'prompts' / 'monster_generation.json'
        
        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        return prompts
        
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")
        return {}

def generate_monster(prompt_name: str = "basic_monster", use_queue: bool = True) -> Dict[str, Any]:
    """
    Generate a monster using the specified prompt
    
    Args:
        prompt_name (str): Name of prompt to use from monster_generation.json
        use_queue (bool): Whether to use the queue system (recommended)
        
    Returns:
        dict: Generation results with monster data, logs, and status
    """
    
    # Load prompts configuration
    prompts = load_prompts()
    if not prompts:
        return {
            'success': False,
            'error': 'Could not load prompts configuration',
            'monster': None,
            'log_id': None
        }
    
    # Get specific prompt configuration
    if prompt_name not in prompts:
        return {
            'success': False,
            'error': f'Unknown prompt: {prompt_name}',
            'monster': None,
            'log_id': None
        }
    
    prompt_config = prompts[prompt_name]
    
    # Use queue system for better management
    if use_queue:
        return generate_monster_with_queue(prompt_config, prompt_name)
    else:
        # Legacy direct generation
        return generate_monster_direct(prompt_config, prompt_name)

def generate_monster_with_queue(prompt_config: Dict[str, Any], prompt_name: str) -> Dict[str, Any]:
    """
    Generate monster using the queue system (recommended approach)
    
    Args:
        prompt_config (dict): Prompt configuration
        prompt_name (str): Name of the prompt
        
    Returns:
        dict: Generation results
    """
    from backend.llm.queue import get_llm_queue
    
    # Add to queue with high priority for monster generation
    queue = get_llm_queue()
    request_id = queue.add_request(
        prompt=prompt_config['prompt_template'],
        max_tokens=prompt_config['max_tokens'],
        temperature=prompt_config['temperature'],
        prompt_type=f'monster_generation_{prompt_name}',
        priority=3  # High priority for monster generation
    )
    
    print(f"🎲 Monster generation queued with ID: {request_id}")
    
    # Wait for completion (with longer timeout for monster generation)
    result = wait_for_generation(request_id, timeout=600)  # 10 minutes max
    
    if not result:
        return {
            'success': False,
            'error': 'Generation timed out or failed',
            'monster': None,
            'request_id': request_id
        }
    
    if result['status'] != 'completed':
        return {
            'success': False,
            'error': result.get('error', 'Generation failed'),
            'monster': None,
            'request_id': request_id
        }
    
    # Get the generation result
    generation_result = result['result']
    
    if not generation_result['success']:
        return {
            'success': False,
            'error': f"Generation failed: {generation_result['error']}",
            'monster': None,
            'request_id': request_id
        }
    
    # Parse the response
    print("🔍 Parsing response...")
    
    parse_result = parse_response(
        response_text=generation_result['text'],
        parser_config=prompt_config['parser']
    )
    
    if not parse_result.success:
        return {
            'success': False,
            'error': f"Parsing failed: {parse_result.error}",
            'monster': None,
            'request_id': request_id,
            'raw_response': generation_result['text']
        }
    
    print(f"✅ Parsing successful using {parse_result.parser_used}")
    
    # Create monster from parsed data
    print("🐉 Creating monster...")
    
    monster = create_monster_from_parsed_data(parse_result.data, prompt_name)
    
    if monster and monster.save():
        print(f"✅ Monster created: {monster.name}")
        
        return {
            'success': True,
            'error': None,
            'monster': monster.to_dict(),
            'request_id': request_id,
            'generation_stats': {
                'tokens': generation_result['tokens'],
                'duration': generation_result['duration'],
                'tokens_per_second': generation_result['tokens_per_second']
            }
        }
    else:
        return {
            'success': False,
            'error': 'Failed to save monster to database',
            'monster': None,
            'request_id': request_id
        }

def generate_monster_direct(prompt_config: Dict[str, Any], prompt_name: str) -> Dict[str, Any]:
    """
    Generate monster using direct LLM calls (legacy approach)
    
    Args:
        prompt_config (dict): Prompt configuration  
        prompt_name (str): Name of the prompt
        
    Returns:
        dict: Generation results
    """
    
    # Ensure model is loaded
    if not ensure_model_loaded():
        return {
            'success': False,
            'error': 'Could not load LLM model',
            'monster': None,
            'log_id': None
        }
    
    # Create log entry
    log = LLMLog.create_log(
        prompt_type='monster_generation',
        prompt_name=prompt_name,
        prompt_text=prompt_config['prompt_template'],
        max_tokens=prompt_config['max_tokens'],
        temperature=prompt_config['temperature']
    )
    
    try:
        # Save initial log
        if not log.save():
            print("⚠️  Could not save initial log entry")
        
        # Mark generation as started
        log.mark_started()
        log.save()
        
        print(f"🎲 Generating monster using '{prompt_name}' prompt...")
        
        # Generate with LLM
        generation_result = generate_text(
            prompt=prompt_config['prompt_template'],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
            prompt_type=f'monster_generation_{prompt_name}',
            stop_sequences=None  # 🔧 FIX: Let model use default stop sequences
        )
        
        if not generation_result['success']:
            log.mark_failed(generation_result['error'])
            log.save()
            
            return {
                'success': False,
                'error': f"Generation failed: {generation_result['error']}",
                'monster': None,
                'log_id': log.id
            }
        
        # Mark generation as completed
        log.mark_completed(
            response_text=generation_result['text'],
            response_tokens=generation_result['tokens']
        )
        log.save()
        
        print(f"✅ Generation completed ({generation_result['tokens']} tokens in {generation_result['duration']:.1f}s)")
        
        # Parse the response
        print("🔍 Parsing response...")
        
        parse_result = parse_response(
            response_text=generation_result['text'],
            parser_config=prompt_config['parser']
        )
        
        if not parse_result.success:
            log.mark_parse_failed(parse_result.error, parse_result.parser_used)
            log.save()
            
            return {
                'success': False,
                'error': f"Parsing failed: {parse_result.error}",
                'monster': None,
                'log_id': log.id,
                'raw_response': generation_result['text']
            }
        
        # Mark parsing as successful
        log.mark_parsed(parse_result.data, parse_result.parser_used)
        log.save()
        
        print(f"✅ Parsing successful using {parse_result.parser_used}")
        
        # Create monster from parsed data
        print("🐉 Creating monster...")
        
        monster = create_monster_from_parsed_data(parse_result.data, prompt_name)
        
        if monster and monster.save():
            # Associate monster with log
            log.entity_type = 'monster'
            log.entity_id = monster.id
            log.save()
            
            print(f"✅ Monster created: {monster.name}")
            
            return {
                'success': True,
                'error': None,
                'monster': monster.to_dict(),
                'log_id': log.id,
                'generation_stats': {
                    'tokens': generation_result['tokens'],
                    'duration': generation_result['duration'],
                    'tokens_per_second': generation_result['tokens_per_second']
                }
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save monster to database',
                'monster': None,
                'log_id': log.id
            }
            
    except Exception as e:
        # Mark log as failed if not already done
        if log.status != 'failed':
            log.mark_failed(str(e))
            log.save()
        
        print(f"❌ Monster generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'monster': None,
            'log_id': log.id
        }

def create_monster_from_parsed_data(parsed_data: Dict[str, Any], prompt_type: str) -> Optional[Monster]:
    """
    Create a Monster instance from parsed LLM data
    Handles different data structures based on prompt type
    
    Args:
        parsed_data (dict): Parsed data from LLM response
        prompt_type (str): Type of prompt used for generation
        
    Returns:
        Monster: Created monster instance or None if failed
    """
    try:
        # Handle different data structures based on prompt type
        if prompt_type == "basic_monster":
            # Simple structure: {name, description}
            monster_data = {
                'basic_info': {
                    'name': parsed_data['name'],
                    'species': 'Unknown Species',  # Default for basic monsters
                    'description': parsed_data['description'],
                    'backstory': f"{parsed_data['name']} is a mysterious creature with unique characteristics."
                },
                'stats': {
                    'health': 100,  # Default stats for basic monsters
                    'attack': 20,
                    'defense': 15,
                    'speed': 10
                },
                'personality': {
                    'traits': ['mysterious', 'unique']
                },
                'abilities': [
                    {'name': 'Basic Attack', 'description': 'A simple attack'}
                ]
            }
        else:
            # Detailed structure: already processed by parser
            monster_data = parsed_data
        
        # Create monster using the Monster model's method
        monster = Monster.create_from_llm_data(monster_data)
        
        return monster
        
    except Exception as e:
        print(f"❌ Error creating monster from parsed data: {e}")
        return None

def get_available_prompts() -> Dict[str, str]:
    """
    Get available monster generation prompts
    
    Returns:
        dict: Map of prompt names to descriptions
    """
    prompts = load_prompts()
    
    return {
        name: config.get('description', 'No description available')
        for name, config in prompts.items()
    }

def test_monster_generation(prompt_name: str = "basic_monster"):
    """
    Test monster generation with a specific prompt
    Useful for debugging and development
    
    Args:
        prompt_name (str): Name of prompt to test
    """
    print(f"🧪 Testing monster generation with '{prompt_name}' prompt...")
    
    result = generate_monster(prompt_name)
    
    if result['success']:
        print("✅ Test successful!")
        print(f"   Monster: {result['monster']['name']}")
        print(f"   Species: {result['monster']['species']}")
        print(f"   Description: {result['monster']['description']}")
        print(f"   Log ID: {result['log_id']}")
        
        if 'generation_stats' in result:
            stats = result['generation_stats']
            print(f"   Generation: {stats['tokens']} tokens in {stats['duration']:.1f}s ({stats['tokens_per_second']} tok/s)")
    else:
        print(f"❌ Test failed: {result['error']}")
        print(f"   Log ID: {result['log_id']}")
        if 'raw_response' in result:
            print(f"   Raw response: {result['raw_response'][:200]}...")

if __name__ == "__main__":
    # Test basic monster generation
    test_monster_generation("basic_monster")