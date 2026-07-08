# Monster Database Model - UPDATED WITH CARD ART PATH
# Enhanced with abilities relationship, methods, and card art storage
# Focuses only on data storage and retrieval - NO game logic

from sqlalchemy import JSON, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .core import db


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
    species = Column(String(100), nullable=False)  # Mirrors taxonomy['species']
    description = Column(Text, nullable=False)  # Short description
    backstory = Column(Text, nullable=True)  # Longer backstory from AI

    # Game mechanics identity
    rarity = Column(String(20), nullable=True)  # common|uncommon|rare|epic|legendary
    party_role = Column(
        String(50), nullable=True
    )  # tank|striker|skirmisher|support|controller|trickster

    # How deeply it trusts the party: wary|familiar|trusting|devoted
    # (NULL reads as wary; ladder + effects live in game/monster/affinity.py)
    affinity = Column(String(20), nullable=True)

    # Staged generation progress: blueprint -> persona -> complete
    generation_stage = Column(String(20), nullable=True, default='complete')

    # CMDTS + persona (per-monster JSON - shapes in docs/plans/monster-depth-cmdts.md §2)
    taxonomy = Column(
        JSON, nullable=True
    )  # curated domain/kingdom + invented lineage + display labels
    class_taxonomy = Column(JSON, nullable=True)  # list of trained disciplines (0:m)
    ecology = Column(
        JSON, nullable=True
    )  # habitat, diet, social, sapience, elements, size, lifecycle
    persona = Column(JSON, nullable=True)  # wish, fears, secret, voice, social hooks, etc.
    appearance = Column(JSON, nullable=True)  # structured visuals feeding card art prompts

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
        result.update(
            {
                'name': self.name,
                'species': self.species,
                'description': self.description,
                'backstory': self.backstory,
                'stats': {
                    'max_health': self.max_health,
                    'current_health': self.current_health,
                    'attack': self.attack,
                    'defense': self.defense,
                    'speed': self.speed,
                },
                'personality_traits': self.personality_traits or [],
                'rarity': self.rarity,
                'party_role': self.party_role,
                'affinity': self.affinity or 'wary',
                'generation_stage': self.generation_stage or 'complete',
                'taxonomy': self.taxonomy or {},
                'class_taxonomy': self.class_taxonomy or [],
                'ecology': self.ecology or {},
                'persona': self.persona or {},
                'appearance': self.appearance or {},
                'abilities': [ability.to_dict() for ability in self.abilities],
                'ability_count': len(self.abilities),
                'card_art': self.get_card_art_info(),  # NEW: Card art information
            }
        )

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
                'exists': False,
            }

        # Existence check against THE outputs root - paths.outputs_root()
        # is the single source of truth (it also migrates legacy trees),
        # never a hand-built path that goes stale when the root moves
        try:
            from backend.ai.image.paths import outputs_root

            full_path = outputs_root() / self.card_art_path
            exists = full_path.exists()
        except Exception:
            exists = False

        return {
            'has_card_art': True,
            'relative_path': self.card_art_path,
            'full_path': str(full_path) if exists else None,
            'exists': exists,
            'url': f'/api/monsters/card-art/{self.card_art_path}' if exists else None,
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
        return f"<Monster(id={self.id}, name='{self.name}', species='{self.species}', abilities={len(self.abilities)}, has_art={bool(self.card_art_path)})>"
