# Monster Manager - TRULY SIMPLIFIED: No Validation
# Pure business logic - assumes all inputs are valid
# Eliminates defensive programming completely
print(f"🔍 Loading {__file__}")
from typing import Dict, Any
from sqlalchemy import func
from backend.models.monster import Monster
from backend.models.ability import Ability
from backend.core.config.database import db
from backend.core.utils import success_response, error_response

class MonsterManager:
    """Pure business logic - no validation"""
    
    def get_all_monsters(self, limit: int, offset: int, filter_type: str, sort_by: str) -> Dict[str, Any]:
        """Get monsters - assumes valid parameters"""
        
        # Start with base query
        query = Monster.query
        
        # Apply filtering
        if filter_type == 'with_art':
            query = query.filter(Monster.card_art_path.isnot(None))
        elif filter_type == 'without_art':
            query = query.filter(Monster.card_art_path.is_(None))
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(Monster.created_at.desc())
        elif sort_by == 'oldest':
            query = query.order_by(Monster.created_at.asc())
        elif sort_by == 'name':
            query = query.order_by(Monster.name.asc())
        elif sort_by == 'species':
            query = query.order_by(Monster.species.asc(), Monster.name.asc())
        
        # Get results
        total_count = query.count()
        monsters = query.options(db.joinedload(Monster.abilities)).offset(offset).limit(limit).all()
        
        return success_response({
            'monsters': [monster.to_dict() for monster in monsters],
            'total': total_count,
            'count': len(monsters),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(monsters) < total_count,
                'next_offset': offset + limit if offset + len(monsters) < total_count else None,
                'prev_offset': max(0, offset - limit) if offset > 0 else None
            },
            'filters_applied': {'filter_type': filter_type, 'sort_by': sort_by}
        })
    
    def get_monster_stats(self, filter_type: str) -> Dict[str, Any]:
        """Get stats - assumes valid filter_type"""
        
        # Base query
        monster_query = Monster.query
        
        # Apply filtering
        if filter_type == 'with_art':
            monster_query = monster_query.filter(Monster.card_art_path.isnot(None))
        elif filter_type == 'without_art':
            monster_query = monster_query.filter(Monster.card_art_path.is_(None))
        
        # Get counts
        total_monsters = monster_query.count()
        
        if total_monsters == 0:
            return success_response({
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
            })
        
        # Get stats
        monster_ids = [monster.id for monster in monster_query.with_entities(Monster.id).all()]
        total_abilities = Ability.query.filter(Ability.monster_id.in_(monster_ids)).count()
        
        # Card art stats
        all_monsters_count = Monster.query.count()
        with_card_art = Monster.query.filter(Monster.card_art_path.isnot(None)).count()
        
        # Species breakdown
        species_data = db.session.query(
            Monster.species, func.count(Monster.id).label('count')
        ).filter(Monster.id.in_(monster_ids)).group_by(Monster.species).all()
        
        # Get newest/oldest
        newest_monster = monster_query.order_by(Monster.created_at.desc()).first()
        oldest_monster = monster_query.order_by(Monster.created_at.asc()).first()
        
        return success_response({
            'filter_applied': filter_type,
            'stats': {
                'total_monsters': total_monsters,
                'total_abilities': total_abilities,
                'avg_abilities_per_monster': round(total_abilities / total_monsters, 1),
                'with_card_art': with_card_art if filter_type == 'all' else (total_monsters if filter_type == 'with_art' else 0),
                'without_card_art': (all_monsters_count - with_card_art) if filter_type == 'all' else (0 if filter_type == 'with_art' else total_monsters),
                'card_art_percentage': round((with_card_art / all_monsters_count * 100) if all_monsters_count > 0 else 0, 1),
                'unique_species': len(species_data),
                'species_breakdown': {species: count for species, count in species_data},
                'newest_monster': newest_monster.to_dict() if newest_monster else None,
                'oldest_monster': oldest_monster.to_dict() if oldest_monster else None
            }
        })
    
    def get_monster_by_id(self, monster_id: int) -> Dict[str, Any]:
        """Get monster by ID - assumes valid ID"""
        
        monster = Monster.query.get(monster_id)
        
        if not monster:
            return error_response('Monster not found', monster=None)
        
        return success_response({'monster': monster.to_dict()})