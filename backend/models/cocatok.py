# CoCaTok Database Model - Collectable Card Tokens
# Unique vanity keepsakes commemorating victories. Rendered on the frontend
# by the CoCaTok component from color + emoji (no AI art). Keepsakes are
# permanent - there is deliberately no delete path.

from .base import BaseModel
from sqlalchemy import Column, String, Text

class CoCaTok(BaseModel):
    """
    CoCaTok model - one row per commemorated victory

    - title/emoji/color drive the spinning card display
      (color is a curated frontend color-system name, e.g. 'purple-mystic')
    - commemoration is the LLM-written story of the moment it marks
    - event_type/location_name record what and where (battle_victory for now)
    """

    __tablename__ = 'cocatoks'

    title = Column(String(100), nullable=False)
    emoji = Column(String(16), nullable=False, default='🏆')
    color = Column(String(50), nullable=False, default='purple-mystic')
    commemoration = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=False, default='battle_victory')
    location_name = Column(String(100), nullable=True)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'title': self.title,
            'emoji': self.emoji or '🏆',
            'color': self.color or 'purple-mystic',
            'commemoration': self.commemoration,
            'event_type': self.event_type,
            'location_name': self.location_name
        })
        return result

    def __repr__(self):
        return f"<CoCaTok(id={self.id}, title='{self.title}', event='{self.event_type}')>"
