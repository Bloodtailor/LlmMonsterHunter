# Chat Message Database Model
# One spoken line in the player's home-base conversation with a monster.
# Each monster has ONE persistent thread for the whole save - a
# relationship, not sessions. Raw messages are never deleted; old
# stretches get condensed into chat_summaries rows instead.
# Data storage only - conversation logic lives in backend/game/chat.

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from .base import BaseModel

# Who spoke a message
CHAT_ROLES = ('player', 'monster')


class ChatMessage(BaseModel):
    """
    Chat message model - one line of a monster's home-base thread

    - role: 'player' (the adventurer typed it) or 'monster' (the reply)
    - text: the words as spoken
    - Ordering is by id (autoincrement follows insertion order)
    """

    __tablename__ = 'chat_messages'

    monster_id = Column(Integer, ForeignKey('monsters.id'), nullable=False, index=True)
    role = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)

    def to_dict(self):
        result = super().to_dict()
        result.update({'monster_id': self.monster_id, 'role': self.role, 'text': self.text})
        return result

    @classmethod
    def add(cls, monster_id: int, role: str, text: str):
        """Record one line. Returns the saved message or None on error."""
        try:
            if role not in CHAT_ROLES:
                print(f"⚠️ Unknown chat role '{role}' - storing anyway")
            message = cls(monster_id=int(monster_id), role=role, text=str(text).strip())
            return message if message.save() else None
        except Exception as e:
            print(f"❌ Error adding chat message for monster {monster_id}: {e}")
            return None

    @classmethod
    def count_for_monster(cls, monster_id: int) -> int:
        """How many lines this monster's thread holds"""
        try:
            return cls.query.filter_by(monster_id=monster_id).count()
        except Exception as e:
            print(f"❌ Error counting chat messages for monster {monster_id}: {e}")
            return 0

    @classmethod
    def page_for_monster(cls, monster_id: int, limit: int = 50, before_id: int = None):
        """
        One page of the thread for display, OLDEST FIRST within the page.
        Pages walk backward from the newest message: no before_id gives
        the latest page, before_id=N gives the page of messages older
        than message N.
        """
        try:
            query = cls.query.filter_by(monster_id=monster_id)
            if before_id:
                query = query.filter(cls.id < int(before_id))
            newest_first = query.order_by(cls.id.desc()).limit(int(limit)).all()
            return list(reversed(newest_first))
        except Exception as e:
            print(f"❌ Error paging chat messages for monster {monster_id}: {e}")
            return []

    @classmethod
    def after_id(cls, monster_id: int, after_id: int, limit: int = None):
        """Messages with id > after_id, oldest first (extraction segments)"""
        try:
            query = (
                cls.query.filter_by(monster_id=monster_id)
                .filter(cls.id > int(after_id or 0))
                .order_by(cls.id)
            )
            if limit:
                query = query.limit(int(limit))
            return query.all()
        except Exception as e:
            print(f"❌ Error reading chat segment for monster {monster_id}: {e}")
            return []

    @classmethod
    def count_through_id(cls, monster_id: int, through_id: int) -> int:
        """How many of this monster's messages have id <= through_id"""
        try:
            if not through_id:
                return 0
            return (
                cls.query.filter_by(monster_id=monster_id).filter(cls.id <= int(through_id)).count()
            )
        except Exception as e:
            print(f"❌ Error counting covered chat messages for monster {monster_id}: {e}")
            return 0

    @classmethod
    def slice_for_monster(cls, monster_id: int, offset: int, count: int):
        """entries[offset:offset+count] of the thread, oldest first"""
        try:
            return (
                cls.query.filter_by(monster_id=monster_id)
                .order_by(cls.id)
                .offset(int(offset))
                .limit(int(count))
                .all()
            )
        except Exception as e:
            print(f"❌ Error slicing chat messages for monster {monster_id}: {e}")
            return []

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, monster_id={self.monster_id}, role='{self.role}')>"
