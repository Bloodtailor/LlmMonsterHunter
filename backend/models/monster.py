# Monster Database Model - CLEANED UP
# Removed generation_prompt and abilities fields for simplicity
# Focuses only on data storage and retrieval - NO game logic

from backend.models.base import BaseModel
from backend.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON
import json

class Monster(BaseModel):
    """
    Monster model for storing AI-generated creatures
    
    Stores all monster data including:
    - Basic info (name, species, description)
    - Stats for future battle system
    - Personality traits as flexible JSON
    - Backstory for roleplay
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
    
    def to_dict(self):
        """
        Convert monster to dictionary for JSON API responses
        Includes all monster data in a clean format
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
            'personality_traits': self.personality_traits or []
        })
        
        return result
    
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
        Get all monsters from database
        
        Returns:
            list: List of all Monster instances
        """
        try:
            return cls.query.all()
        except Exception as e:
            print(f"❌ Error fetching monsters: {e}")
            return []
    
    @classmethod
    def get_monster_by_id(cls, monster_id):
        """
        Get specific monster by ID
        
        Args:
            monster_id (int): Monster ID
            
        Returns:
            Monster: Monster instance or None if not found
        """
        try:
            return cls.query.get(monster_id)
        except Exception as e:
            print(f"❌ Error fetching monster {monster_id}: {e}")
            return None
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Monster(id={self.id}, name='{self.name}', species='{self.species}')>"