# Monster Service - ENHANCED WITH ADVANCED PAGINATION
# Handles monster generation with automatic abilities and card art
# Now includes server-side filtering, sorting, and enhanced statistics

from typing import Dict, Any, Optional, List
from sqlalchemy import and_, func, distinct
from backend.models.monster import Monster
from backend.ai.llm.prompt_engine import get_template_config, build_prompt
from . import generation_service
from . import ability_service

def generate_monster(prompt_name: str = "detailed_monster", 
                    wait_for_completion: bool = True,
                    generate_card_art: bool = True) -> Dict[str, Any]:
    """
    Generate a new monster with automatic abilities and card art
    
    Args:
        prompt_name (str): Template name to use
        wait_for_completion (bool): Whether to wait for generation
        generate_card_art (bool): Whether to generate card art image
        
    Returns:
        dict: Complete monster generation results
    """
    
    try:
        # Get template and build prompt
        template_config = get_template_config(prompt_name)
        if not template_config:
            return {'success': False, 'error': f'Template not found: {prompt_name}', 'monster': None}
        
        prompt_text = build_prompt(prompt_name)
        if not prompt_text:
            return {'success': False, 'error': f'Failed to build prompt: {prompt_name}', 'monster': None}
        
        # Generate monster via LLM
        llm_result = generation_service.text_generation_request(
            prompt=prompt_text,
            prompt_type='monster_generation',
            prompt_name=prompt_name,
            parser_config=template_config['parser'],
            max_tokens=template_config['max_tokens'],
            temperature=template_config['temperature'],
            wait_for_completion=wait_for_completion
        )
        
        if not llm_result['success']:
            return {
                'success': False,
                'error': llm_result['error'],
                'monster': None,
                'generation_id': llm_result.get('generation_id')
            }
        
        if not wait_for_completion:
            return {
                'success': True,
                'message': 'Monster generation started',
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        # Check parsing success
        if not llm_result.get('parsing_success'):
            return {
                'success': False,
                'error': "Parsing failed",
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        # Create and save monster
        monster = Monster.create_from_llm_data(llm_result['parsed_data'])
        if not monster or not monster.save():
            return {
                'success': False,
                'error': 'Failed to save monster',
                'monster': None,
                'generation_id': llm_result['generation_id']
            }
        
        print(f"🐉 Monster '{monster.name}' created with ID: {monster.id}")
        
        # Generate starting abilities
        abilities_result = ability_service.generate_initial_abilities(
            monster_data=monster.get_context_for_ability_generation(),
            monster_id=monster.id
        )
        
        # Generate card art if requested
        card_art_result = {'success': False}
        if generate_card_art:
            card_art_result = _generate_and_connect_card_art(monster)
        
        # Reload monster with abilities and card art
        monster = Monster.get_monster_by_id(monster.id)
        
        return {
            'success': True,
            'monster': monster.to_dict(),
            'generation_id': llm_result['generation_id'],
            'generation_stats': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0),
                'abilities_generated': abilities_result.get('abilities_created', 0),
                'card_art_generated': card_art_result['success']
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'monster': None}

def get_all_monsters_enhanced(limit: int = 50, 
                            offset: int = 0,
                            filter_type: str = 'all',
                            sort_by: str = 'newest') -> Dict[str, Any]:
    """
    Get all monsters with enhanced server-side filtering, sorting, and pagination
    
    Args:
        limit (int): Number of monsters to return (max 1000)
        offset (int): Number of monsters to skip
        filter_type (str): 'all', 'with_art', 'without_art'
        sort_by (str): 'newest', 'oldest', 'name', 'species'
        
    Returns:
        dict: Monsters with pagination info and filtering applied
    """
    
    try:
        from backend.config.database import db
        
        # Start with base query
        query = Monster.query
        
        # Apply filtering
        if filter_type == 'with_art':
            query = query.filter(Monster.card_art_path.isnot(None))
        elif filter_type == 'without_art':
            query = query.filter(Monster.card_art_path.is_(None))
        # 'all' requires no additional filtering
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(Monster.created_at.desc())
        elif sort_by == 'oldest':
            query = query.order_by(Monster.created_at.asc())
        elif sort_by == 'name':
            query = query.order_by(Monster.name.asc())
        elif sort_by == 'species':
            query = query.order_by(Monster.species.asc(), Monster.name.asc())  # Secondary sort by name
        
        # Get total count with same filters (before pagination)
        total_count = query.count()
        
        # Apply pagination and load abilities in one query (performance optimization)
        monsters = query.options(db.joinedload(Monster.abilities)).offset(offset).limit(limit).all()
        
        # Calculate pagination info
        has_more = offset + len(monsters) < total_count
        
        return {
            'success': True,
            'monsters': [monster.to_dict() for monster in monsters],
            'total': total_count,
            'count': len(monsters),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': has_more,
                'next_offset': offset + limit if has_more else None,
                'prev_offset': max(0, offset - limit) if offset > 0 else None
            },
            'filters_applied': {
                'filter_type': filter_type,
                'sort_by': sort_by
            }
        }
        
    except Exception as e:
        return {
            'success': False, 
            'error': str(e), 
            'monsters': [], 
            'total': 0, 
            'count': 0,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': False,
                'next_offset': None,
                'prev_offset': None
            },
            'filters_applied': {
                'filter_type': filter_type,
                'sort_by': sort_by
            }
        }

def get_enhanced_monster_stats(filter_type: str = 'all') -> Dict[str, Any]:
    """
    Get comprehensive monster statistics with optional filtering
    
    Args:
        filter_type (str): 'all', 'with_art', 'without_art'
        
    Returns:
        dict: Enhanced statistics about monsters and abilities
    """
    
    try:
        from backend.config.database import db
        from backend.models.ability import Ability
        
        # Base query for monsters
        monster_query = Monster.query
        
        # Apply filtering
        if filter_type == 'with_art':
            monster_query = monster_query.filter(Monster.card_art_path.isnot(None))
        elif filter_type == 'without_art':
            monster_query = monster_query.filter(Monster.card_art_path.is_(None))
        
        # Get filtered monster statistics
        total_monsters = monster_query.count()
        
        if total_monsters == 0:
            return {
                'success': True,
                'filter_applied': filter_type,
                'stats': {
                    'total_monsters': 0,
                    'total_abilities': 0,
                    'avg_abilities_per_monster': 0,
                    'with_card_art': 0,
                    'without_card_art': 0,
                    'card_art_percentage': 0,
                    'unique_species': 0,
                    'species_breakdown': {},
                    'newest_monster': None,
                    'oldest_monster': None
                }
            }
        
        # Get monster IDs for filtered results (for ability counting)
        monster_ids = [monster.id for monster in monster_query.with_entities(Monster.id).all()]
        
        # Count abilities for filtered monsters only
        total_abilities = Ability.query.filter(Ability.monster_id.in_(monster_ids)).count() if monster_ids else 0
        avg_abilities_per_monster = total_abilities / total_monsters if total_monsters > 0 else 0
        
        # Card art statistics (always calculate from all monsters for context)
        all_monsters_count = Monster.query.count()
        with_card_art = Monster.query.filter(Monster.card_art_path.isnot(None)).count()
        without_card_art = all_monsters_count - with_card_art
        card_art_percentage = (with_card_art / all_monsters_count * 100) if all_monsters_count > 0 else 0
        
        # If filtering by art status, adjust the card art stats to reflect only filtered results
        if filter_type == 'with_art':
            filtered_with_art = total_monsters
            filtered_without_art = 0
            filtered_card_art_percentage = 100
        elif filter_type == 'without_art':
            filtered_with_art = 0
            filtered_without_art = total_monsters
            filtered_card_art_percentage = 0
        else:
            filtered_with_art = with_card_art
            filtered_without_art = without_card_art
            filtered_card_art_percentage = card_art_percentage
        
        # Species analysis on filtered results
        species_data = db.session.query(
            Monster.species, 
            func.count(Monster.id).label('count')
        ).filter(Monster.id.in_(monster_ids) if monster_ids else Monster.id.isnot(None)).group_by(Monster.species).all()
        
        unique_species = len(species_data)
        species_breakdown = {species: count for species, count in species_data}
        
        # Get newest and oldest from filtered results
        newest_monster = monster_query.order_by(Monster.created_at.desc()).first()
        oldest_monster = monster_query.order_by(Monster.created_at.asc()).first()
        
        return {
            'success': True,
            'filter_applied': filter_type,
            'stats': {
                'total_monsters': total_monsters,
                'total_abilities': total_abilities,
                'avg_abilities_per_monster': round(avg_abilities_per_monster, 1),
                'with_card_art': filtered_with_art,
                'without_card_art': filtered_without_art,
                'card_art_percentage': round(filtered_card_art_percentage, 1),
                'unique_species': unique_species,
                'species_breakdown': species_breakdown,
                'newest_monster': newest_monster.to_dict() if newest_monster else None,
                'oldest_monster': oldest_monster.to_dict() if oldest_monster else None
            },
            'context': {
                'all_monsters_count': all_monsters_count,
                'all_monsters_with_art': with_card_art,
                'overall_card_art_percentage': round(card_art_percentage, 1)
            } if filter_type != 'all' else None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filter_applied': filter_type,
            'stats': {
                'total_monsters': 0,
                'total_abilities': 0,
                'with_card_art': 0,
                'unique_species': 0
            }
        }

# LEGACY COMPATIBILITY: Keep existing methods for backward compatibility
def get_all_monsters(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    LEGACY: Get all monsters with basic pagination
    Maintained for backward compatibility - new code should use get_all_monsters_enhanced
    """
    return get_all_monsters_enhanced(limit=limit, offset=offset, filter_type='all', sort_by='newest')

def get_monster_stats() -> Dict[str, Any]:
    """
    LEGACY: Get basic monster statistics
    Maintained for backward compatibility - new code should use get_enhanced_monster_stats
    """
    enhanced_stats = get_enhanced_monster_stats(filter_type='all')
    if not enhanced_stats['success']:
        return enhanced_stats
    
    # Convert to legacy format
    stats = enhanced_stats['stats']
    return {
        'success': True,
        'total_monsters': stats['total_monsters'],
        'total_abilities': stats['total_abilities'],
        'avg_abilities_per_monster': stats['avg_abilities_per_monster'],
        'monsters_with_card_art': stats['with_card_art'],
        'card_art_percentage': stats['card_art_percentage'],
        'newest_monster': stats['newest_monster'],
        'available_templates': list(get_available_templates().keys())
    }

def _generate_and_connect_card_art(monster: Monster) -> Dict[str, Any]:
    """Generate and connect card art to monster"""
    
    try:
        prompt_text = monster.get_context_for_image_generation()
        
        image_result = generation_service.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name="monster_generation",
            wait_for_completion=True
        )
        
        if not image_result['success']:
            return {'success': False, 'error': image_result.get('error', 'Image generation failed')}
        
        relative_path = image_result.get('image_path')
        if not relative_path or not monster.set_card_art(relative_path):
            return {'success': False, 'error': 'Failed to save card art path'}
        
        return {
            'success': True,
            'image_path': relative_path,
            'generation_id': image_result.get('generation_id')
        }
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_card_art_for_existing_monster(monster_id: int, wait_for_completion: bool = True) -> Dict[str, Any]:
    """Generate card art for an existing monster"""
    
    try:
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return {'success': False, 'error': f'Monster {monster_id} not found'}
        
        return _generate_and_connect_card_art(monster)
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_monster_by_id(monster_id: int) -> Dict[str, Any]:
    """Get specific monster by ID"""
    try:
        monster = Monster.query.get(monster_id)
        
        if not monster:
            return {'success': False, 'error': 'Monster not found', 'monster': None}
        
        return {'success': True, 'monster': monster.to_dict()}
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'monster': None}

def get_available_templates() -> Dict[str, str]:
    """Get available monster generation templates"""
    try:
        from backend.ai.llm.prompt_engine import get_prompt_engine
        
        engine = get_prompt_engine()
        templates = {}
        
        for name in engine.list_templates():
            template = engine.get_template(name)
            if template and template.category == 'monster_generation':
                templates[name] = template.description
        
        return templates
        
    except Exception as e:
        return {}