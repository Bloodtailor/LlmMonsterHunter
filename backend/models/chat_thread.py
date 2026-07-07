# Chat Thread Database Model
# One row per monster the player has ever chatted with at home base.
# Holds per-thread housekeeping state - today just the memory-extraction
# watermark (the last message id an extraction pass has reviewed, whether
# or not it saved anything).
# Data storage only - extraction cadence lives in backend/game/chat.

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from .base import BaseModel


class ChatThread(BaseModel):
    """
    Chat thread model - housekeeping state for one monster's thread

    - last_extracted_message_id: every message with id <= this has been
      reviewed for memories (0 = nothing reviewed yet)
    """

    __tablename__ = 'chat_threads'

    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False)
    last_extracted_message_id = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('monster_id', name='unique_chat_thread_monster'),
    )

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'monster_id': self.monster_id,
            'last_extracted_message_id': self.last_extracted_message_id
        })
        return result

    @classmethod
    def get_or_create(cls, monster_id: int):
        """The monster's thread row, created on first use"""
        try:
            thread = cls.query.filter_by(monster_id=int(monster_id)).first()
            if thread:
                return thread
            thread = cls(monster_id=int(monster_id), last_extracted_message_id=0)
            return thread if thread.save() else None
        except Exception as e:
            print(f"❌ Error getting chat thread for monster {monster_id}: {e}")
            return None

    @classmethod
    def extraction_watermark(cls, monster_id: int) -> int:
        """The last message id already reviewed for memories (0 if none)"""
        try:
            thread = cls.query.filter_by(monster_id=int(monster_id)).first()
            return int(thread.last_extracted_message_id) if thread else 0
        except Exception as e:
            print(f"❌ Error reading extraction watermark for monster {monster_id}: {e}")
            return 0

    @classmethod
    def advance_extraction_watermark(cls, monster_id: int, message_id: int) -> bool:
        """Mark everything up to message_id as reviewed (never moves back)"""
        try:
            thread = cls.get_or_create(monster_id)
            if not thread:
                return False
            if int(message_id) <= int(thread.last_extracted_message_id or 0):
                return True
            thread.last_extracted_message_id = int(message_id)
            return thread.save()
        except Exception as e:
            print(f"❌ Error advancing extraction watermark for monster {monster_id}: {e}")
            return False

    def __repr__(self):
        return (f"<ChatThread(id={self.id}, monster_id={self.monster_id}, "
                f"extracted_through={self.last_extracted_message_id})>")
