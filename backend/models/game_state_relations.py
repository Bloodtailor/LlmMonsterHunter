# Game State Relationship Models - NORMALIZED DESIGN
# Separate tables for following monsters and active party
# Proper foreign key relationships with cascade deletes

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class FollowingMonster(BaseModel):
    """
    Monsters that are following the player
    Many-to-many relationship between GameState and Monster
    """
    
    __tablename__ = 'following_monsters'
    
    # Foreign keys
    game_state_id = Column(Integer, ForeignKey('game_state.id'), nullable=False)
    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    
    # Relationships
    game_state = relationship('GameState', back_populates='following_monsters')
    monster = relationship('Monster', foreign_keys=[monster_id])
    
    # Unique constraint - each monster can only follow once
    __table_args__ = (
        UniqueConstraint('game_state_id', 'monster_id', name='unique_following_monster'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'game_state_id': self.game_state_id,
            'monster_id': self.monster_id
        })
        
        # Include monster details if loaded
        if self.monster:
            result['monster'] = self.monster.to_dict()
        
        return result
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<FollowingMonster(game_state_id={self.game_state_id}, monster_id={self.monster_id})>"

class ActiveParty(BaseModel):
    """
    Monsters in the active party
    Many-to-many relationship between GameState and Monster with position ordering
    """
    
    __tablename__ = 'active_party'
    
    # Foreign keys
    game_state_id = Column(Integer, ForeignKey('game_state.id'), nullable=False)
    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    
    # Party position (1-4) for ordering
    party_position = Column(Integer, nullable=False)
    
    # Relationships
    game_state = relationship('GameState', back_populates='active_party')
    monster = relationship('Monster', foreign_keys=[monster_id])
    
    # Unique constraints
    __table_args__ = (
        UniqueConstraint('game_state_id', 'monster_id', name='unique_party_monster'),
        UniqueConstraint('game_state_id', 'party_position', name='unique_party_position'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'game_state_id': self.game_state_id,
            'monster_id': self.monster_id,
            'party_position': self.party_position
        })
        
        # Include monster details if loaded
        if self.monster:
            result['monster'] = self.monster.to_dict()
        
        return result
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<ActiveParty(game_state_id={self.game_state_id}, monster_id={self.monster_id}, position={self.party_position})>"

class DungeonState(BaseModel):
    """
    Current dungeon state
    One-to-one relationship with GameState
    """
    
    __tablename__ = 'dungeon_state'
    
    # Foreign key (one-to-one)
    game_state_id = Column(Integer, ForeignKey('game_state.id'), nullable=False, unique=True)
    
    # Dungeon state fields
    current_location_name = Column(String(200), nullable=False)
    current_location_description = Column(Text, nullable=False)
    last_event_text = Column(Text, nullable=True)
    party_summary = Column(String(500), nullable=False)
    
    # Relationships
    game_state = relationship('GameState', back_populates='dungeon_state')
    doors = relationship('DungeonDoor', back_populates='dungeon_state', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'game_state_id': self.game_state_id,
            'current_location': {
                'name': self.current_location_name,
                'description': self.current_location_description
            },
            'last_event_text': self.last_event_text,
            'party_summary': self.party_summary,
            'available_doors': [door.to_dict() for door in self.doors]
        })
        
        return result
    
    def get_legacy_format(self):
        """Get data in legacy format for compatibility"""
        return {
            'current_location': {
                'name': self.current_location_name,
                'description': self.current_location_description
            },
            'available_doors': [door.to_legacy_format() for door in self.doors],
            'last_event_text': self.last_event_text,
            'party_summary': self.party_summary
        }
    
    def set_location(self, location_name: str, location_description: str):
        """Set current location"""
        self.current_location_name = location_name
        self.current_location_description = location_description
        self.save()
    
    def set_doors(self, doors_data: list):
        """Set available doors (replaces existing doors)"""
        # Clear existing doors
        for door in self.doors:
            door.delete()
        
        # Add new doors
        for door_data in doors_data:
            door = DungeonDoor(
                dungeon_state_id=self.id,
                door_id=door_data['id'],
                door_type=door_data['type'],
                door_name=door_data['name'],
                door_description=door_data['description']
            )
            door.save()
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<DungeonState(game_state_id={self.game_state_id}, location='{self.current_location_name}')>"

class DungeonDoor(BaseModel):
    """
    Available doors in current dungeon location
    One-to-many relationship with DungeonState
    """
    
    __tablename__ = 'dungeon_doors'
    
    # Foreign key
    dungeon_state_id = Column(Integer, ForeignKey('dungeon_state.id'), nullable=False)
    
    # Door fields
    door_id = Column(String(50), nullable=False)  # e.g., "location_1", "exit"
    door_type = Column(String(20), nullable=False)  # "location" or "exit"
    door_name = Column(String(200), nullable=False)
    door_description = Column(Text, nullable=False)
    
    # Relationships
    dungeon_state = relationship('DungeonState', back_populates='doors')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'dungeon_state_id': self.dungeon_state_id,
            'door_id': self.door_id,
            'door_type': self.door_type,
            'door_name': self.door_name,
            'door_description': self.door_description
        })
        
        return result
    
    def to_legacy_format(self):
        """Get data in legacy format for compatibility"""
        return {
            'id': self.door_id,
            'type': self.door_type,
            'name': self.door_name,
            'description': self.door_description
        }
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<DungeonDoor(dungeon_state_id={self.dungeon_state_id}, door_id='{self.door_id}', type='{self.door_type}')>"