# Ability Database Model
# Stores AI-generated abilities for monsters
# Each ability belongs to one monster, monsters can have unlimited abilities
print(f"🔍 Loading {__file__}")
from backend.models.base import BaseModel
from backend.core.config.database import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey

class Ability(BaseModel):
    """
    Ability model for storing monster abilities
    
    Each ability is unique to a specific monster and contains:
    - Basic info (name, description, type)
    - Connection to parent monster via foreign key
    - AI generation metadata
    """
    
    # Table name in database
    __tablename__ = 'abilities'
    
    # Foreign key to monsters table
    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    
    # Ability Information
    name = Column(String(100), nullable=False)           # e.g., "Lightning Strike"
    description = Column(Text, nullable=False)           # Detailed description of what it does
    ability_type = Column(String(50), nullable=True)     # e.g., "attack", "defense", "support"
    
    def to_dict(self):
        """
        Convert ability to dictionary for JSON API responses
        Includes all ability data in a clean format
        """
        # Get base fields from BaseModel
        result = super().to_dict()
        
        # Add ability-specific fields
        result.update({
            'monster_id': self.monster_id,
            'name': self.name,
            'description': self.description,
            'ability_type': self.ability_type
        })
        
        return result
    
    @classmethod
    def create_from_llm_data(cls, monster_id, llm_response_data):
        """
        Create a new Ability from LLM-generated data
        
        Args:
            monster_id (int): ID of the monster this ability belongs to
            llm_response_data (dict): Parsed JSON from LLM containing ability data
            
        Returns:
            Ability: New ability instance (not yet saved to database)
        """
        
        # Extract data with safe defaults
        ability = cls(
            monster_id=monster_id,
            name=llm_response_data.get('name', 'Unnamed Ability'),
            description=llm_response_data.get('description', 'A mysterious power.'),
            ability_type=llm_response_data.get('type', 'unknown')
        )
        
        return ability
    
    @classmethod
    def get_abilities_for_monster(cls, monster_id):
        """
        Get all abilities for a specific monster
        
        Args:
            monster_id (int): Monster ID
            
        Returns:
            list: List of Ability instances
        """
        try:
            return cls.query.filter_by(monster_id=monster_id).order_by(cls.created_at.asc()).all()
        except Exception as e:
            print(f"❌ Error fetching abilities for monster {monster_id}: {e}")
            return []
    
    @classmethod
    def get_ability_by_id(cls, ability_id):
        """
        Get specific ability by ID
        
        Args:
            ability_id (int): Ability ID
            
        Returns:
            Ability: Ability instance or None if not found
        """
        try:
            return cls.query.get(ability_id)
        except Exception as e:
            print(f"❌ Error fetching ability {ability_id}: {e}")
            return None
    
    @classmethod
    def count_abilities_for_monster(cls, monster_id):
        """
        Count how many abilities a monster has
        
        Args:
            monster_id (int): Monster ID
            
        Returns:
            int: Number of abilities
        """
        try:
            return cls.query.filter_by(monster_id=monster_id).count()
        except Exception as e:
            print(f"❌ Error counting abilities for monster {monster_id}: {e}")
            return 0
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Ability(id={self.id}, name='{self.name}', monster_id={self.monster_id})>"