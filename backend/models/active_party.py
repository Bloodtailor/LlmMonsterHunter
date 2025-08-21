# Active Party Database Model - SIMPLIFIED DESIGN
# No game_state_id FK - true singleton behavior for single-player game
# Stores which monsters are in the active adventuring party with position ordering

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class ActiveParty(BaseModel):
    """
    Active party model - stores monsters currently in the adventuring party
    
    Simplified design without game_state_id foreign key since there's only
    ever one game state in a single-player game.
    
    Features:
    - Direct reference to monsters via monster_id
    - Party position for ordering (1-4)
    - Unique constraints to prevent duplicates
    """
    
    __tablename__ = 'active_party'
    
    # === Core Fields ===
    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    party_position = Column(Integer, nullable=False)  # 1, 2, 3, 4 for ordering
    
    # === Relationships ===
    monster = relationship('Monster', foreign_keys=[monster_id])
    
    # === Constraints ===
    __table_args__ = (
        UniqueConstraint('monster_id', name='unique_party_monster'),
        UniqueConstraint('party_position', name='unique_party_position'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'monster_id': self.monster_id,
            'party_position': self.party_position
        })
        
        # Include monster details if loaded
        if self.monster:
            result['monster'] = self.monster.to_dict()
        
        return result
    
    @classmethod
    def get_all_party_members(cls):
        """Get all party members ordered by position"""
        return cls.query.order_by(cls.party_position).all()
    
    @classmethod
    def get_party_monster_ids(cls):
        """Get list of monster IDs in party order"""
        party_members = cls.get_all_party_members()
        return [member.monster_id for member in party_members]
    
    @classmethod
    def clear_party(cls):
        """Remove all monsters from party"""
        cls.query.delete()
        db.session.commit()
    
    @classmethod
    def set_party(cls, monster_ids: list):
        """
        Set the active party (replaces existing party)
        
        Args:
            monster_ids (list): List of monster IDs in desired order
        """
        # Clear existing party
        cls.clear_party()
        
        # Add new party members with positions
        for position, monster_id in enumerate(monster_ids, 1):
            party_member = cls(
                monster_id=monster_id,
                party_position=position
            )
            party_member.save()
    
    @classmethod
    def add_to_party(cls, monster_id: int):
        """
        Add a monster to the next available party position
        
        Args:
            monster_id (int): Monster to add
            
        Returns:
            bool: True if added successfully, False if party full or monster already in party
        """
        # Check if monster already in party
        if cls.query.filter_by(monster_id=monster_id).first():
            return False
        
        # Check party size (max 4)
        current_count = cls.query.count()
        if current_count >= 4:
            return False
        
        # Find next position
        next_position = current_count + 1
        
        party_member = cls(
            monster_id=monster_id,
            party_position=next_position
        )
        return party_member.save()
    
    @classmethod
    def remove_from_party(cls, monster_id: int):
        """
        Remove a monster from party and reorder positions
        
        Args:
            monster_id (int): Monster to remove
            
        Returns:
            bool: True if removed successfully
        """
        party_member = cls.query.filter_by(monster_id=monster_id).first()
        if not party_member:
            return False
        
        removed_position = party_member.party_position
        party_member.delete()
        
        # Reorder remaining party members
        remaining_members = cls.query.filter(cls.party_position > removed_position).all()
        for member in remaining_members:
            member.party_position -= 1
            member.save()
        
        return True
    
    @classmethod
    def get_party_count(cls):
        """Get number of monsters in party"""
        return cls.query.count()
    
    @classmethod
    def is_party_ready(cls):
        """Check if party has at least one monster"""
        return cls.get_party_count() > 0
    
    @classmethod
    def is_in_active_party(cls, monster_id: int):
        """Check if monster is in active party"""
        return cls.query.filter_by(monster_id=monster_id).first() is not None
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<ActiveParty(id={self.id}, monster_id={self.monster_id}, position={self.party_position})>"