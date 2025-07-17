# Monster Database Model - UPDATED WITH CARD ART PATH
# Enhanced with abilities relationship, methods, and card art storage
# Focuses only on data storage and retrieval - NO game logic
print(f"🔍 Loading {__file__}")
from backend.models.base import BaseModel
from backend.core.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
import json
from pathlib import Path

class Monster(BaseModel):
    """
    Monster model for storing AI-generated creatures
    
    Stores all monster data including:
    - Basic info (name, species, description)
    - Stats for future battle system
    - Personality traits as flexible JSON
    - Backstory for roleplay
    - Card art path (relative to outputs folder)
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
    
    # NEW: Card art path (relative to outputs folder, e.g., "monster_card_art/00000001.png")
    card_art_path = Column(String(500), nullable=True)
    
    # Relationship to abilities (one monster -> many abilities)
    abilities = relationship('Ability', backref='monster', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        Convert monster to dictionary for JSON API responses
        Includes all monster data including abilities and card art info
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
            'ability_count': len(self.abilities),
            'card_art': self.get_card_art_info()  # NEW: Card art information
        })
        
        return result
    
    def get_card_art_info(self):
        """
        Get card art information including path and existence check
        
        Returns:
            dict: Card art information for frontend
        """
        if not self.card_art_path:
            return {
                'has_card_art': False,
                'relative_path': None,
                'full_path': None,
                'exists': False
            }
        
        # Build full path for existence check
        try:
            from pathlib import Path
            # Assume images are in backend/ai/comfyui/outputs/
            full_path = Path(__file__).parent.parent / 'ai' / 'comfyui' / 'outputs' / self.card_art_path
            exists = full_path.exists()
        except Exception:
            exists = False
        
        return {
            'has_card_art': True,
            'relative_path': self.card_art_path,
            'full_path': str(full_path) if exists else None,
            'exists': exists,
            'url': f'/api/images/{self.card_art_path}' if exists else None  # For future API endpoint
        }
    
    def set_card_art(self, relative_path: str) -> bool:
        """
        Set the card art path for this monster
        
        Args:
            relative_path (str): Relative path from outputs folder (e.g., "monster_card_art/00000001.png")
            
        Returns:
            bool: True if set successfully
        """
        try:
            self.card_art_path = relative_path
            return self.save()
        except Exception as e:
            print(f"❌ Error setting card art for monster {self.id}: {e}")
            return False
    
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
    
    def get_context_for_image_generation(self):
        """
        Get monster context for image generation prompts
        Builds a descriptive prompt text from monster data
        
        Returns:
            str: Prompt text for image generation
        """
        prompt_parts = []
        
        # Add name and species
        if self.name:
            prompt_parts.append(self.name)
        if self.species:
            prompt_parts.append(self.species)
        
        # Add description
        if self.description:
            prompt_parts.append(self.description)
        
        # Add personality traits if available
        if self.personality_traits:
            traits_text = ", ".join(self.personality_traits[:3])  # Limit to 3 traits
            prompt_parts.append(f"personality: {traits_text}")
        
        return ", ".join(prompt_parts)
    
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
            personality_traits=personality.get('traits', []),
            
            # NEW: Card art starts as None (will be set when image is generated)
            card_art_path=None
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
    
    @classmethod
    def find_monster_by_image_generation_id(cls, generation_id: int):
        """
        Find monster that was being generated when this image generation was created
        Uses timing to match monster creation with image generation
        
        Args:
            generation_id (int): Generation ID of the image
            
        Returns:
            Monster: Most recently created monster or None
        """
        try:
            # Get the most recently created monster
            # This assumes monster creation and image generation happen in sequence
            return cls.query.order_by(cls.created_at.desc()).first()
        except Exception as e:
            print(f"❌ Error finding monster for image generation {generation_id}: {e}")
            return None
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Monster(id={self.id}, name='{self.name}', species='{self.species}', abilities={len(self.abilities)}, has_art={bool(self.card_art_path)})>"