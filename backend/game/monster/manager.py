# Monster Manager - Clean Monster Management Logic

from typing import Dict, Any
from sqlalchemy import func
from backend.models.monster import Monster
from backend.models.ability import Ability
from backend.config.database import db
from backend.game.utils import error_response, success_response

class MonsterManager:
    """Clean monster management - handles retrieval, pagination, filtering, statistics"""
    
    def get_all_monsters_enhanced(self, limit: int = 50, 
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
            
            return success_response({
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
            })
            
        except Exception as e:
            return error_response(str(e), 
                monsters=[], 
                total=0, 
                count=0,
                pagination={
                    'limit': limit,
                    'offset': offset,
                    'has_more': False,
                    'next_offset': None,
                    'prev_offset': None
                },
                filters_applied={
                    'filter_type': filter_type,
                    'sort_by': sort_by
                }
            )
    
    def get_enhanced_monster_stats(self, filter_type: str = 'all') -> Dict[str, Any]:
        """
        Get comprehensive monster statistics with optional filtering
        
        Args:
            filter_type (str): 'all', 'with_art', 'without_art'
            
        Returns:
            dict: Enhanced statistics about monsters and abilities
        """
        
        try:
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
            
            response_data = {
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
                }
            }
            
            # Add context if filtering (to show overall stats)
            if filter_type != 'all':
                response_data['context'] = {
                    'all_monsters_count': all_monsters_count,
                    'all_monsters_with_art': with_card_art,
                    'overall_card_art_percentage': round(card_art_percentage, 1)
                }
            
            return success_response(response_data)
            
        except Exception as e:
            return error_response(str(e),
                filter_applied=filter_type,
                stats={
                    'total_monsters': 0,
                    'total_abilities': 0,
                    'with_card_art': 0,
                    'unique_species': 0
                }
            )
    
    def get_monster_by_id(self, monster_id: int) -> Dict[str, Any]:
        """Get specific monster by ID"""
        
        try:
            monster = Monster.query.get(monster_id)
            
            if not monster:
                return error_response('Monster not found', monster=None)
            
            return success_response({'monster': monster.to_dict()})
            
        except Exception as e:
            return error_response(str(e), monster=None)
    
    # LEGACY COMPATIBILITY: Keep existing methods for backward compatibility
    def get_all_monsters(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        LEGACY: Get all monsters with basic pagination
        Maintained for backward compatibility - new code should use get_all_monsters_enhanced
        """
        return self.get_all_monsters_enhanced(limit=limit, offset=offset, filter_type='all', sort_by='newest')
    
    def get_monster_stats(self) -> Dict[str, Any]:
        """
        LEGACY: Get basic monster statistics
        Maintained for backward compatibility - new code should use get_enhanced_monster_stats
        """
        enhanced_stats = self.get_enhanced_monster_stats(filter_type='all')
        if not enhanced_stats['success']:
            return enhanced_stats
        
        # Convert to legacy format
        stats = enhanced_stats['stats']
        return success_response({
            'total_monsters': stats['total_monsters'],
            'total_abilities': stats['total_abilities'],
            'avg_abilities_per_monster': stats['avg_abilities_per_monster'],
            'monsters_with_card_art': stats['with_card_art'],
            'card_art_percentage': stats['card_art_percentage'],
            'newest_monster': stats['newest_monster'],
            'available_templates': list(self._get_generator().get_available_templates().keys())
        })
    
    def _get_generator(self):
        """Get generator instance for template access"""
        from .generator import MonsterGenerator
        return MonsterGenerator()