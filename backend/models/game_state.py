# Game State Database Model - NORMALIZED DESIGN
# Single row representing current game state with proper relationships
# Follows database normalization principles

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

class GameState(BaseModel):
    """
    Main game state model - single row in database
    Related to following_monsters, active_party, and dungeon_state through relationships
    """
    
    __tablename__ = 'game_state'
    
    # === Core Game State ===
    in_dungeon = Column(Boolean, default=False, nullable=False)
    
    # === Relationships ===
    following_monsters = relationship('FollowingMonster', back_populates='game_state', 
                                    cascade='all, delete-orphan', lazy='dynamic')
    active_party = relationship('ActiveParty', back_populates='game_state', 
                              cascade='all, delete-orphan', lazy='dynamic')
    dungeon_state = relationship('DungeonState', back_populates='game_state', 
                               uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        # Add game state specific fields
        result.update({
            'in_dungeon': self.in_dungeon,
            'game_status': 'in_dungeon' if self.in_dungeon else 'home_base'
        })
        
        return result
    
    def get_following_monster_ids(self):
        """Get list of monster IDs that are following"""
        return [fm.monster_id for fm in self.following_monsters.all()]
    
    def get_active_party_ids(self):
        """Get list of monster IDs in active party, ordered by position"""
        party_members = self.active_party.order_by('party_position').all()
        return [ap.monster_id for ap in party_members]
    
    def get_following_monster_details(self):
        """Get detailed monster data for following monsters"""
        from backend.models.monster import Monster
        monster_ids = self.get_following_monster_ids()
        
        details = []
        for monster_id in monster_ids:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                details.append(monster.to_dict())
        
        return details
    
    def get_active_party_details(self):
        """Get detailed monster data for active party"""
        from backend.models.monster import Monster
        monster_ids = self.get_active_party_ids()
        
        details = []
        for monster_id in monster_ids:
            monster = Monster.get_monster_by_id(monster_id)
            if monster:
                details.append(monster.to_dict())
        
        return details
    
    def add_following_monster(self, monster_id: int) -> bool:
        """Add a monster to following list"""
        # Check if already following
        existing = self.following_monsters.filter_by(monster_id=monster_id).first()
        if existing:
            return False
        
        # Add to following
        from backend.models.game_state_relations import FollowingMonster
        following = FollowingMonster(game_state_id=self.id, monster_id=monster_id)
        following.save()
        
        return True
    
    def remove_following_monster(self, monster_id: int) -> bool:
        """Remove a monster from following list (and active party if present)"""
        # Remove from following
        following = self.following_monsters.filter_by(monster_id=monster_id).first()
        if following:
            following.delete()
        
        # Remove from active party if present
        party_member = self.active_party.filter_by(monster_id=monster_id).first()
        if party_member:
            party_member.delete()
        
        return True
    
    def set_active_party(self, monster_ids: list) -> bool:
        """Set active party (replaces existing party)"""
        # Clear existing party
        for party_member in self.active_party.all():
            party_member.delete()
        
        # Add new party members with positions
        from backend.models.game_state_relations import ActiveParty
        for position, monster_id in enumerate(monster_ids, 1):
            party_member = ActiveParty(
                game_state_id=self.id,
                monster_id=monster_id,
                party_position=position
            )
            party_member.save()
        
        return True
    
    def is_party_ready_for_dungeon(self) -> bool:
        """Check if party has at least one monster"""
        return self.active_party.count() > 0
    
    def get_party_summary(self) -> str:
        """Get text summary of active party"""
        from backend.models.monster import Monster
        monster_ids = self.get_active_party_ids()
        
        if not monster_ids:
            return "No active party"
        
        try:
            party_names = []
            for monster_id in monster_ids:
                monster = Monster.get_monster_by_id(monster_id)
                if monster:
                    party_names.append(monster.name)
            
            if len(party_names) == 1:
                return party_names[0]
            elif len(party_names) == 2:
                return f"{party_names[0]} and {party_names[1]}"
            else:
                return f"{', '.join(party_names[:-1])}, and {party_names[-1]}"
                
        except Exception:
            return f"{len(monster_ids)} monsters"
    
    def enter_dungeon(self) -> None:
        """Mark as entered dungeon"""
        self.in_dungeon = True
        self.save()
    
    def exit_dungeon(self) -> None:
        """Mark as exited dungeon and clear dungeon state"""
        self.in_dungeon = False
        if self.dungeon_state:
            self.dungeon_state.delete()
        self.save()
    
    @classmethod
    def get_current_game_state(cls):
        """Get or create the single game state row"""
        game_state = cls.query.first()
        
        if not game_state:
            # Create initial game state
            game_state = cls(in_dungeon=False)
            game_state.save()
        
        return game_state
    
    @classmethod
    def reset_game_state(cls):
        """Reset game state to initial values"""
        # Delete all existing game state data
        cls.query.delete()
        db.session.commit()
        
        # Create fresh game state
        return cls.get_current_game_state()
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<GameState(id={self.id}, in_dungeon={self.in_dungeon}, following={self.following_monsters.count()}, party={self.active_party.count()})>"