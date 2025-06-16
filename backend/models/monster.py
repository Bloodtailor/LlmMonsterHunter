# Monster Database Model - UPDATED WITH ABILITIES
# Enhanced with abilities relationship and methods
# Focuses only on data storage and retrieval - NO game logic

from backend.models.base import BaseModel
from backend.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
import json

class Monster(BaseModel):
    """
    Monster model for storing AI-generated creatures
    
    Stores all monster data including:
    - Basic info (name, species, description)
    - Stats for future battle system
    - Personality traits as flexible JSON
    - Backstory for roleplay
    - Relationship to abilities (one-to-many)
    """
    
    # Table name in database
    __tablename__ = 'monsters'
    
    # Basic Monster Information
    name = Column(String(100), nullable=False)
    species = Column(String(100), nullable=False) 
    description = Column(Text, nullable=False)  # Short description
    backstory = Column(Text, nullable=True)     # Longer backstory from AI
    
    # Basic Stats (for future battle system)
    max_health = Column(Integer, default=100)
    current_health = Column(Integer, default=100)
    attack = Column(Integer, default=20)
    defense = Column(Integer, default=15)
    speed = Column(Integer, default=10)
    
    # Personality traits (JSON for flexibility)
    personality_traits = Column(JSON, nullable=True)  # List of personality traits
    
    # Relationship to abilities (one monster -> many abilities)
    abilities = relationship('Ability', backref='monster', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        Convert monster to dictionary for JSON API responses
        Includes all monster data including abilities in a clean format
        """
        # Get base fields from BaseModel
        result = super().to_dict()
        
        # Add monster-specific formatting
        result.update({
            'name': self.name,
            'species': self.species,
            'description': self.description,
            'backstory': self.backstory,
            'stats': {
                'max_health': self.max_health,
                'current_health': self.current_health,
                'attack': self.attack,
                'defense': self.defense,
                'speed': self.speed
            },
            'personality_traits': self.personality_traits or [],
            'abilities': [ability.to_dict() for ability in self.abilities],
            'ability_count': len(self.abilities)
        })
        
        return result
    
    def get_abilities_summary(self):
        """
        Get a summary of abilities for UI display
        
        Returns:
            dict: Summary with count and preview of ability names
        """
        ability_names = [ability.name for ability in self.abilities]
        return {
            'count': len(self.abilities),
            'names': ability_names,
            'preview': ', '.join(ability_names[:2]) + ('...' if len(ability_names) > 2 else '')
        }
    
    def get_context_for_ability_generation(self):
        """
        Get monster context for ability generation prompts
        Includes all relevant information for the LLM to create appropriate abilities
        
        Returns:
            dict: Complete monster context for LLM prompts
        """
        existing_abilities = [
            {
                'name': ability.name,
                'description': ability.description,
                'type': ability.ability_type
            }
            for ability in self.abilities
        ]
        
        return {
            'name': self.name,
            'species': self.species,
            'description': self.description,
            'backstory': self.backstory,
            'stats': {
                'health': self.max_health,
                'attack': self.attack,
                'defense': self.defense,
                'speed': self.speed
            },
            'personality_traits': self.personality_traits or [],
            'existing_abilities': existing_abilities,
            'ability_count': len(existing_abilities)
        }
    
    @classmethod
    def create_from_llm_data(cls, llm_response_data):
        """
        Create a new Monster from LLM-generated data
        Handles both basic and detailed monster formats
        
        Args:
            llm_response_data (dict): Parsed JSON from LLM containing monster data
            
        Returns:
            Monster: New monster instance (not yet saved to database)
        """
        
        # Extract data with safe defaults
        basic_info = llm_response_data.get('basic_info', {})
        stats = llm_response_data.get('stats', {})
        personality = llm_response_data.get('personality', {})
        
        # Create new monster instance
        monster = cls(
            name=basic_info.get('name', 'Unnamed Monster'),
            species=basic_info.get('species', 'Unknown Species'),
            description=basic_info.get('description', 'A mysterious creature.'),
            backstory=basic_info.get('backstory', ''),
            
            # Stats with defaults
            max_health=stats.get('health', 100),
            current_health=stats.get('health', 100),  # Start at full health
            attack=stats.get('attack', 20),
            defense=stats.get('defense', 15),
            speed=stats.get('speed', 10),
            
            # JSON fields
            personality_traits=personality.get('traits', [])
        )
        
        return monster
    
    @classmethod
    def get_all_monsters(cls):
        """
        Get all monsters from database with their abilities loaded
        
        Returns:
            list: List of all Monster instances with abilities
        """
        try:
            return cls.query.options(db.joinedload(cls.abilities)).all()
        except Exception as e:
            print(f"❌ Error fetching monsters: {e}")
            return []
    
    @classmethod
    def get_monster_by_id(cls, monster_id):
        """
        Get specific monster by ID with abilities loaded
        
        Args:
            monster_id (int): Monster ID
            
        Returns:
            Monster: Monster instance or None if not found
        """
        try:
            return cls.query.options(db.joinedload(cls.abilities)).get(monster_id)
        except Exception as e:
            print(f"❌ Error fetching monster {monster_id}: {e}")
            return None
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Monster(id={self.id}, name='{self.name}', species='{self.species}', abilities={len(self.abilities)})>"