# Following Monsters Database Model - SIMPLIFIED DESIGN  
# No game_state_id FK - true singleton behavior for single-player game
# Stores which monsters are currently following the player

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class FollowingMonster(BaseModel):
    """
    Following monsters model - stores monsters that are following the player
    
    Simplified design without game_state_id foreign key since there's only
    ever one game state in a single-player game.
    
    Features:
    - Direct reference to monsters via monster_id
    - Unique constraint to prevent duplicate followers
    - Class methods for easy management
    """
    
    __tablename__ = 'following_monsters'
    
    # === Core Fields ===
    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    
    # === Relationships ===
    monster = relationship('Monster', foreign_keys=[monster_id])
    
    # === Constraints ===
    __table_args__ = (
        UniqueConstraint('monster_id', name='unique_following_monster'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'monster_id': self.monster_id
        })
        
        # Include monster details if loaded
        if self.monster:
            result['monster'] = self.monster.to_dict()
        
        return result
    
    @classmethod
    def get_all_following(cls):
        """Get all following monsters ordered by when they started following"""
        return cls.query.order_by(cls.created_at).all()
    
    @classmethod
    def get_following_monster_ids(cls):
        """Get list of monster IDs that are following"""
        following = cls.get_all_following()
        return [follower.monster_id for follower in following]
    
    @classmethod
    def get_following_details(cls):
        """Get detailed monster data for all following monsters"""
        following = cls.query.options(db.joinedload(cls.monster)).all()
        return [follower.monster.to_dict() for follower in following if follower.monster]
    
    @classmethod
    def add_follower(cls, monster_id: int):
        """
        Add a monster to the following list
        
        Args:
            monster_id (int): Monster to add as follower
            
        Returns:
            bool: True if added successfully, False if already following
        """
        # Check if already following
        if cls.query.filter_by(monster_id=monster_id).first():
            return False
        
        follower = cls(monster_id=monster_id)
        return follower.save()
    
    @classmethod
    def remove_follower(cls, monster_id: int):
        """
        Remove a monster from the following list
        
        Args:
            monster_id (int): Monster to remove from followers
            
        Returns:
            bool: True if removed successfully, False if not following
        """
        follower = cls.query.filter_by(monster_id=monster_id).first()
        if not follower:
            return False
        
        return follower.delete()
    
    @classmethod
    def is_following(cls, monster_id: int):
        """
        Check if a monster is following
        
        Args:
            monster_id (int): Monster to check
            
        Returns:
            bool: True if monster is following
        """
        return cls.query.filter_by(monster_id=monster_id).first() is not None
    
    @classmethod
    def clear_all_followers(cls):
        """Remove all followers (for testing/reset)"""
        cls.query.delete()
        db.session.commit()
    
    @classmethod
    def get_following_count(cls):
        """Get number of monsters in following"""
        return cls.query.count()
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<FollowingMonster(id={self.id}, monster_id={self.monster_id})>"