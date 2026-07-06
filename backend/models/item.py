# Item Database Model
# LLM-generated consumable items the party carries between encounters.
# The description is written FOR the LLM referee - it carries everything
# the referee needs to judge what the item does when used.
# Data storage only - consumption logic lives in the game layer.

from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text

class Item(BaseModel):
    """
    Item model for the party's inventory

    - name/emoji for display
    - description holds the item's nature AND effect in prose (referee-facing)
    - uses_remaining counts down on use; depleted items are deleted
    - source_note remembers where it came from
    """

    __tablename__ = 'items'

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    emoji = Column(String(16), nullable=True, default='🎁')
    uses_remaining = Column(Integer, nullable=False, default=1)
    source_note = Column(String(255), nullable=True)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'name': self.name,
            'description': self.description,
            'emoji': self.emoji or '🎁',
            'uses_remaining': self.uses_remaining,
            'source_note': self.source_note
        })
        return result

    @classmethod
    def get_usable_items(cls):
        """Every item with uses left, newest first (for use-item pickers)"""
        try:
            return cls.query.filter(cls.uses_remaining > 0).order_by(cls.created_at.desc()).all()
        except Exception as e:
            print(f"❌ Error fetching usable items: {e}")
            return []

    @classmethod
    def get_item_by_id(cls, item_id):
        try:
            return cls.query.get(item_id)
        except Exception as e:
            print(f"❌ Error fetching item {item_id}: {e}")
            return None

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', uses={self.uses_remaining})>"
