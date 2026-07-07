# Monster Evolution Database Model
# One row per completed evolution ceremony: the permanent lineage record
# of the form a monster LEFT BEHIND and the form it became. The monster
# row itself is mutated in place (same id - memories, chat threads, and
# abilities all survive); these rows are the history that makes
# "it used to be..." possible. Data storage only - the transform logic
# lives in backend/game/monster/evolution.py.

from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON, Float, ForeignKey

class MonsterEvolution(BaseModel):
    """
    Monster evolution model - one completed evolution stage

    - stage: 1 for the first evolution, counting up (unlimited)
    - old_*: snapshot of the form left behind, including the art path
      (art files are never deleted, so past forms stay viewable)
    - new_*: the identity the ceremony produced
    - applied_boost_pct: the code-owned stat boost this stage granted
    - narrative: the streamed ceremony text, saved once it finishes
    - guidance: what the player whispered before the ceremony, if anything
    - details: structured extras (form_theme, reworded abilities, ...)
    """

    __tablename__ = 'monster_evolutions'

    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False, index=True)
    stage = Column(Integer, nullable=False, default=1)
    guidance = Column(String(240), nullable=True)
    narrative = Column(Text, nullable=True)

    old_name = Column(String(100), nullable=False)
    old_species = Column(String(100), nullable=False)
    old_rarity = Column(String(20), nullable=True)
    new_name = Column(String(100), nullable=False)
    new_species = Column(String(100), nullable=False)
    new_rarity = Column(String(20), nullable=False)

    old_stats = Column(JSON, nullable=True)
    applied_boost_pct = Column(Float, nullable=False, default=0.0)
    old_card_art_path = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'monster_id': self.monster_id,
            'stage': self.stage,
            'guidance': self.guidance,
            'narrative': self.narrative,
            'old_name': self.old_name,
            'old_species': self.old_species,
            'old_rarity': self.old_rarity,
            'new_name': self.new_name,
            'new_species': self.new_species,
            'new_rarity': self.new_rarity,
            'old_stats': self.old_stats or {},
            'applied_boost_pct': self.applied_boost_pct,
            'old_card_art_path': self.old_card_art_path,
            'details': self.details or {}
        })
        return result

    @classmethod
    def add(cls, monster_id: int, stage: int, old_name: str, old_species: str,
            old_rarity, new_name: str, new_species: str, new_rarity: str,
            old_stats: dict, applied_boost_pct: float,
            old_card_art_path: str = None, guidance: str = None, details: dict = None):
        """Record one evolution. Returns the saved row or None on error."""
        try:
            evolution = cls(
                monster_id=int(monster_id),
                stage=int(stage),
                old_name=old_name,
                old_species=old_species,
                old_rarity=old_rarity,
                new_name=new_name,
                new_species=new_species,
                new_rarity=new_rarity,
                old_stats=old_stats or None,
                applied_boost_pct=float(applied_boost_pct),
                old_card_art_path=old_card_art_path,
                guidance=guidance,
                details=details or None
            )
            return evolution if evolution.save() else None
        except Exception as e:
            print(f"❌ Error adding evolution for monster {monster_id}: {e}")
            return None

    @classmethod
    def for_monster(cls, monster_id: int):
        """A monster's evolutions, oldest first (its lineage in order)"""
        try:
            return cls.query.filter_by(monster_id=monster_id).order_by(cls.created_at, cls.id).all()
        except Exception as e:
            print(f"❌ Error fetching evolutions for monster {monster_id}: {e}")
            return []

    @classmethod
    def count_for_monster(cls, monster_id: int) -> int:
        """How many times this monster has evolved"""
        try:
            return cls.query.filter_by(monster_id=monster_id).count()
        except Exception as e:
            print(f"❌ Error counting evolutions for monster {monster_id}: {e}")
            return 0

    def __repr__(self):
        return (f"<MonsterEvolution(id={self.id}, monster_id={self.monster_id}, "
                f"stage={self.stage}, '{self.old_name}' -> '{self.new_name}')>")
