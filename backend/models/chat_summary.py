# Chat Summary Database Model
# One condensed batch of a monster's chat thread (rolling summaries -
# see backend/game/utils/rolling_summary.py). Raw chat_messages rows are
# kept forever; a summary covers every message with id <= its
# through_message_id so prompts can send "condensed old + verbatim
# recent" instead of the whole conversation.
# Data storage only - when/how to condense lives in backend/game/chat.

from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import BaseModel


class ChatSummary(BaseModel):
    """
    Chat summary model - one condensed stretch of a monster's thread

    - through_message_id: covers ALL of this monster's messages with
      id <= this (summaries never overlap; each new one extends coverage)
    - text: 2-4 sentences preserving what could matter later
    """

    __tablename__ = 'chat_summaries'

    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False, index=True)
    through_message_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'monster_id': self.monster_id,
            'through_message_id': self.through_message_id,
            'text': self.text
        })
        return result

    @classmethod
    def add(cls, monster_id: int, through_message_id: int, text: str):
        """Record one condensed batch. Returns the row or None on error."""
        try:
            summary = cls(
                monster_id=int(monster_id),
                through_message_id=int(through_message_id),
                text=str(text).strip()
            )
            return summary if summary.save() else None
        except Exception as e:
            print(f"❌ Error adding chat summary for monster {monster_id}: {e}")
            return None

    @classmethod
    def for_monster(cls, monster_id: int):
        """All summaries oldest first (their texts read in order)"""
        try:
            return (cls.query.filter_by(monster_id=monster_id)
                    .order_by(cls.through_message_id).all())
        except Exception as e:
            print(f"❌ Error reading chat summaries for monster {monster_id}: {e}")
            return []

    @classmethod
    def last_through_id(cls, monster_id: int) -> int:
        """The newest message id the summaries already cover (0 if none)"""
        try:
            last = (cls.query.filter_by(monster_id=monster_id)
                    .order_by(cls.through_message_id.desc()).first())
            return int(last.through_message_id) if last else 0
        except Exception as e:
            print(f"❌ Error reading chat summary coverage for monster {monster_id}: {e}")
            return 0

    def __repr__(self):
        return (f"<ChatSummary(id={self.id}, monster_id={self.monster_id}, "
                f"through={self.through_message_id})>")
