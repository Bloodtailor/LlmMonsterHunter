# Monster Generation Module - CLEANED UP VERSION
# 🔧 SIMPLIFIED: Only queue path, no legacy dual paths
# All generation goes through queue system with proper logging

import json
from pathlib import Path
from typing import Dict, Any, Optional

from backend.llm.queue import get_llm_queue
from backend.models.llm_log import LLMLog
from backend.models.monster import Monster
from backend.llm.parser import parse_response

def load_prompts() -> Dict[str, Any]:
    """Load monster generation prompts from JSON file"""
    try:
        prompts_file = Path(__file__).parent.parent / 'prompts' / 'monster_generation.json'
        
        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")
        return {}

def generate_monster(prompt_name: str = "basic_monster") -> Dict[str, Any]:
    """
    🔧 SIMPLIFIED: Generate monster using ONLY queue system
    Creates log, queues request, waits for completion, creates monster
    
    Args:
        prompt_name (str): Name of prompt to use
        
    Returns:
        dict: Generation results
    """

    
    # Load prompts
    prompts = load_prompts()
    if prompt_name not in prompts:
        return {
            'success': False,
            'error': f'Unknown prompt: {prompt_name}',
            'monster': None,
            'log_id': None
        }
    
    prompt_config = prompts[prompt_name]
    
    try:
        # 1. Create LLM log entry FIRST
        log = LLMLog.create_log(
            prompt_type='monster_generation',
            prompt_name=prompt_name,
            prompt_text=prompt_config['prompt_template'],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature']
        )
        
        if not log.save():
            return {
                'success': False,
                'error': 'Could not create log entry',
                'monster': None,
                'log_id': None
            }
        
        print(f"📋 Created log entry: {log.id}")
        
        # 2. Add to queue with log reference
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=prompt_config['prompt_template'],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
            prompt_type=f'monster_generation_{prompt_name}',
            priority=3,  # High priority for monster generation
            log_id=log.id
        )
        
        print(f"🎲 Queued with request ID: {request_id}")
        
        # 3. Wait for completion (queue system handles the generation)
        from backend.llm.core import wait_for_generation
        result = wait_for_generation(request_id, timeout=600)  # 10 minutes max
        
        if not result or result['status'] != 'completed':
            error_msg = result.get('error', 'Generation failed or timed out') if result else 'Generation timed out'
            return {
                'success': False,
                'error': error_msg,
                'monster': None,
                'request_id': request_id,
                'log_id': log.id
            }
        
        # 4. Get generation result
        generation_result = result['result']
        
        if not generation_result['success']:
            return {
                'success': False,
                'error': f"Generation failed: {generation_result['error']}",
                'monster': None,
                'request_id': request_id,
                'log_id': log.id
            }
        
        # 5. Parse the response
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
                'log_id': log.id,
                'raw_response': generation_result['text']
            }
        
        # 6. Create monster from parsed data
        monster = create_monster_from_parsed_data(parse_result.data, prompt_name)
        
        if monster and monster.save():
            # Associate monster with log
            log.entity_type = 'monster'
            log.entity_id = monster.id
            log.save()
            
            print(f"✅ Monster created: {monster.name} (ID: {monster.id})")
            
            return {
                'success': True,
                'error': None,
                'monster': monster.to_dict(),
                'request_id': request_id,
                'log_id': log.id,
                'generation_stats': {
                    'tokens': generation_result['tokens'],
                    'duration': generation_result['duration'],
                    'tokens_per_second': generation_result.get('tokens_per_second', 0)
                }
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save monster to database',
                'monster': None,
                'request_id': request_id,
                'log_id': log.id
            }
            
    except Exception as e:
        print(f"❌ Monster generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'monster': None,
            'log_id': getattr(log, 'id', None) if 'log' in locals() else None
        }

def create_monster_from_parsed_data(parsed_data: Dict[str, Any], prompt_type: str) -> Optional['Monster']:
    """Create a Monster instance from parsed LLM data"""
    
    try:
        # Handle different data structures based on prompt type
        if prompt_type == "basic_monster":
            # Simple structure: {name, description}
            monster_data = {
                'basic_info': {
                    'name': parsed_data['name'],
                    'species': 'Unknown Species',
                    'description': parsed_data['description'],
                    'backstory': f"{parsed_data['name']} is a mysterious creature with unique characteristics."
                },
                'stats': {
                    'health': 100,
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
    """Get available monster generation prompts"""
    prompts = load_prompts()
    return {
        name: config.get('description', 'No description available')
        for name, config in prompts.items()
    }