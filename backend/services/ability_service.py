# Ability Service - CLEANED UP
# Handles generating unique abilities for monsters using LLM pipeline
# Uses generation_service for text generation

from typing import Dict, Any, List
from backend.models.monster import Monster
from backend.models.ability import Ability
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
from . import generation_service

def generate_ability(monster_id: int, wait_for_completion: bool = True) -> Dict[str, Any]:
    """
    Generate a single new ability for an existing monster
    
    Args:
        monster_id (int): ID of monster to generate ability for
        wait_for_completion (bool): Whether to wait for generation
        
    Returns:
        dict: Complete ability generation results
    """
    
    try:
        # Get monster with existing abilities
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return {
                'success': False,
                'error': f'Monster {monster_id} not found',
                'ability': None
            }
        
        print(f"⚡ Ability Service: Single ability request for {monster.name} (ID: {monster_id})")
        
        # Get monster context and build prompt
        monster_context = monster.get_context_for_ability_generation()
        prompt_variables = _build_prompt_variables(monster_context)
        prompt_text = build_prompt('generate_ability', prompt_variables)
        
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build ability generation prompt',
                'ability': None
            }
        
        # Get template configuration
        template_config = get_template_config('generate_ability')
        if not template_config:
            return {
                'success': False,
                'error': 'Ability generation template not found',
                'ability': None
            }
        
        # Generate via LLM
        llm_result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='ability_generation',
            prompt_name='generate_ability',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=wait_for_completion
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'ability': None,
                'generation_id': llm_result.get('generation_id'),
                'monster_id': monster_id
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Ability generation started',
                'ability': None,
                'generation_id': llm_result['generation_id'],
                'monster_id': monster_id
            }
        
        # Check parsing success
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': f"Automatic parsing failed after {llm_result.get('attempt', 1)} attempts",
                'ability': None,
                'generation_id': llm_result['generation_id'],
                'monster_id': monster_id
            }
        
        # Create and save ability
        ability = Ability.create_from_llm_data(monster_id, llm_result['parsed_data'])
        
        if not ability or not ability.save():
            return {
                'success': False,
                'error': 'Failed to save ability to database',
                'ability': None,
                'generation_id': llm_result['generation_id'],
                'monster_id': monster_id
            }
        
        print(f"✅ Ability '{ability.name}' saved for {monster.name}")
        
        return {
            'success': True,
            'ability': ability.to_dict(),
            'monster_id': monster_id,
            'generation_id': llm_result['generation_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'attempts_needed': llm_result.get('attempt', 1)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Service error: {str(e)}',
            'ability': None,
            'monster_id': monster_id
        }

def generate_initial_abilities(monster_data: Dict[str, Any], monster_id: int) -> Dict[str, Any]:
    """
    Generate 2 starting abilities for a newly created monster
    Called automatically during monster creation
    
    Args:
        monster_data (dict): Monster data for context
        monster_id (int): ID of the newly created monster
        
    Returns:
        dict: Results of generating both abilities
    """
    
    try:
        monster_name = monster_data.get('name', f'Monster {monster_id}')
        print(f"⚡ Ability Service: Initial abilities request for {monster_name} (ID: {monster_id})")
        
        # Build prompt
        prompt_variables = _build_prompt_variables(monster_data)
        prompt_text = build_prompt('generate_initial_abilities', prompt_variables)
        
        if not prompt_text:
            return {
                'success': False,
                'error': 'Failed to build initial abilities prompt',
                'abilities': []
            }
        
        # Get template configuration
        template_config = get_template_config('generate_initial_abilities')
        if not template_config:
            return {
                'success': False,
                'error': 'Initial abilities template not found',
                'abilities': []
            }
        
        # Generate via LLM
        llm_result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='ability_generation',
            prompt_name='generate_initial_abilities',
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=True  # Always wait for initial abilities
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'abilities': [],
                'generation_id': llm_result.get('generation_id')
            }
        
        # Check parsing success
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': f"Initial abilities parsing failed after {llm_result.get('attempt', 1)} attempts",
                'abilities': [],
                'generation_id': llm_result['generation_id']
            }
        
        parsed_data = llm_result['parsed_data']
        
        # Create and save both abilities
        abilities = []
        
        for ability_key in ['ability1', 'ability2']:
            if ability_key in parsed_data:
                ability = Ability.create_from_llm_data(monster_id, parsed_data[ability_key])
                
                if ability and ability.save():
                    abilities.append(ability.to_dict())
                    print(f"✅ Initial ability '{ability.name}' saved")
        
        return {
            'success': True,
            'abilities': abilities,
            'abilities_created': len(abilities),
            'generation_id': llm_result['generation_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'attempts_needed': llm_result.get('attempt', 1)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Initial abilities error: {str(e)}',
            'abilities': []
        }

def _build_prompt_variables(monster_context: Dict[str, Any]) -> Dict[str, Any]:
    """Build variables for ability generation prompts"""
    
    # Format existing abilities for prompt
    existing_abilities = monster_context.get('existing_abilities', [])
    if existing_abilities:
        abilities_text = "\n".join([
            f"- {ability['name']} ({ability.get('type', 'unknown')}): {ability['description']}"
            for ability in existing_abilities
        ])
    else:
        abilities_text = "None (this will be their first ability)"
    
    # Format personality traits
    traits = monster_context.get('personality_traits', [])
    personality_text = ', '.join(traits) if traits else 'Mysterious'
    
    # Build complete variable set
    return {
        'monster_name': monster_context.get('name', 'Unknown'),
        'monster_species': monster_context.get('species', 'Unknown Species'),
        'monster_description': monster_context.get('description', 'A mysterious creature'),
        'monster_backstory': monster_context.get('backstory', 'Unknown origins'),
        'monster_health': monster_context.get('stats', {}).get('health', 100),
        'monster_attack': monster_context.get('stats', {}).get('attack', 20),
        'monster_defense': monster_context.get('stats', {}).get('defense', 15),
        'monster_speed': monster_context.get('stats', {}).get('speed', 10),
        'monster_personality': personality_text,
        'existing_abilities_text': abilities_text,
        'ability_count': monster_context.get('ability_count', 0)
    }

def get_abilities_for_monster(monster_id: int) -> Dict[str, Any]:
    """Get all abilities for a specific monster"""
    
    try:
        abilities = Ability.get_abilities_for_monster(monster_id)
        
        return {
            'success': True,
            'monster_id': monster_id,
            'abilities': [ability.to_dict() for ability in abilities],
            'count': len(abilities)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'monster_id': monster_id,
            'abilities': [],
            'count': 0
        }