# Game Settings - player configuration that OUTLIVES the world
# Key-value JSON storage shaped like GlobalVariable, with one deliberate
# difference: this table is absent from wipe_world()'s explicit list, so
# New Game erases the world but never the player's setup (LLM provider
# choice, DeepSeek API key). Do NOT add it to the wipe order - survival
# is a locked decision (docs/plans/game-settings.md) and test-asserted.

from typing import Any

from sqlalchemy import JSON, Column, String, UniqueConstraint

from .base import BaseModel


class GameSetting(BaseModel):
    """
    Player-facing settings model - key-value storage using native JSON

    Stores in-game panel configuration like:
    - "llm_provider" → {"provider": "deepseek",
                        "deepseek": {"api_key": "...", "model": "...",
                                     "context_window": 65536}}
    """

    __tablename__ = 'game_settings'

    # === Core Fields ===
    key = Column(String(100), nullable=False)  # Setting name (e.g., "llm_provider")
    value = Column(JSON, nullable=True)  # Setting value (native JSON)

    # === Constraints ===
    __table_args__ = (UniqueConstraint('key', name='unique_setting_key'),)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()

        result.update(
            {
                'key': self.key,
                'value': self.value,  # Already the correct Python type
            }
        )

        return result

    @classmethod
    def get(cls, key: str, default: Any = None):
        """
        Get a setting value by key

        Args:
            key (str): Setting key
            default: Default value if key not found

        Returns:
            Any: Setting value (correct Python type) or default
        """
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default

        return setting.value  # SQLAlchemy automatically converts JSON → Python

    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set a setting value by key (creates or updates)

        Args:
            key (str): Setting key
            value: Value to store (any JSON-serializable type)

        Returns:
            bool: True if successful
        """
        setting = cls.query.filter_by(key=key).first()

        if setting:
            setting.value = value  # SQLAlchemy automatically converts Python → JSON
            return setting.save()
        else:
            setting = cls(key=key, value=value)
            return setting.save()

    @classmethod
    def delete_key(cls, key: str):
        """
        Delete a setting by key

        Args:
            key (str): Setting key to delete

        Returns:
            bool: True if deleted, False if not found
        """
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.delete()
        return False

    def __repr__(self):
        """String representation for debugging"""
        value_text = str(self.value)
        if len(value_text) > 50:
            value_text = value_text[:50] + '...'
        return f"<GameSetting(id={self.id}, key='{self.key}', value={value_text})>"
