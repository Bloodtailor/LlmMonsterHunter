# Monster Memory Database Model
# Permanent, per-monster records of what happened between a monster and
# the party - the foundation of returning monsters and growth. One row
# per remembered moment, written by the game layer (backend/game/memory).
# Data storage only - what gets remembered and how it is used lives there.

import contextlib

from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text

from .base import BaseModel
from .core import db


class MonsterMemory(BaseModel):
    """
    Monster memory model - one remembered moment from a monster's life

    - kind: machine-readable category (was_defeated, joined_party, ...)
    - content: one or two short past-tense sentences, written to be
      dropped straight into LLM prompts from the monster's perspective
    - details: structured extras (by/with/location/amount_pct/...)
    - run_id: which dungeon run it happened in (nullable - some moments
      happen outside a run, e.g. sanctuary battles)
    """

    __tablename__ = 'monster_memories'

    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False, index=True)
    run_id = Column(Integer, ForeignKey('dungeon_runs.id'), nullable=True)
    kind = Column(String(40), nullable=False)
    content = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'monster_id': self.monster_id,
            'run_id': self.run_id,
            'kind': self.kind,
            'content': self.content,
            'details': self.details or {}
        })
        return result

    @classmethod
    def add(cls, monster_id: int, kind: str, content: str, details: dict = None, run_id: int = None):
        """Record one memory. Returns the saved memory or None on error."""
        try:
            memory = cls(
                monster_id=int(monster_id),
                kind=kind,
                content=str(content).strip(),
                details=details or None,
                run_id=run_id
            )
            return memory if memory.save() else None
        except Exception as e:
            print(f"❌ Error adding memory for monster {monster_id}: {e}")
            return None

    @classmethod
    def for_monster(cls, monster_id: int, limit: int = None):
        """A monster's memories, oldest first (its life in order)"""
        try:
            query = cls.query.filter_by(monster_id=monster_id).order_by(cls.created_at, cls.id)
            memories = query.all()
            return memories[-limit:] if limit else memories
        except Exception as e:
            print(f"❌ Error fetching memories for monster {monster_id}: {e}")
            return []

    @classmethod
    def monster_ids_with_memories(cls, exclude_ids=None):
        """
        Distinct monster ids that have at least one memory, minus the
        excluded set (following/party/already-seen-this-run).
        """
        try:
            exclude = {int(mid) for mid in (exclude_ids or [])}
            rows = db.session.query(cls.monster_id).distinct().all()
            return [row[0] for row in rows if row[0] not in exclude]
        except Exception as e:
            print(f"❌ Error listing monsters with memories: {e}")
            return []

    @classmethod
    def count_kind(cls, monster_id: int, kind: str) -> int:
        """How many memories of one kind a monster has (e.g. returns)"""
        try:
            return cls.query.filter_by(monster_id=monster_id, kind=kind).count()
        except Exception as e:
            print(f"❌ Error counting '{kind}' memories for monster {monster_id}: {e}")
            return 0

    @classmethod
    def growth_total_pct(cls, monster_id: int, stat: str) -> float:
        """
        Total percent a stat has already been boosted by growth/return
        events - the lifetime caps read this. Sums details['amount_pct']
        over rows whose details name this stat. Python-side sum is fine
        at this scale (a handful of rows per monster).
        """
        try:
            total = 0.0
            for memory in cls.query.filter(
                cls.monster_id == monster_id,
                cls.kind.in_(('growth', 'returned'))
            ).all():
                details = memory.details or {}
                if details.get('stat') == stat:
                    with contextlib.suppress(TypeError, ValueError):
                        total += float(details.get('amount_pct') or 0)
            return total
        except Exception as e:
            print(f"❌ Error summing growth for monster {monster_id}: {e}")
            return 0.0

    def __repr__(self):
        return f"<MonsterMemory(id={self.id}, monster_id={self.monster_id}, kind='{self.kind}')>"
