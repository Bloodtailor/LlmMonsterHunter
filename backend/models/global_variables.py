# Global Variables Database Model - NATIVE JSON STORAGE
# Simple key-value table using MySQL's native JSON column type
# Perfect for dungeon doors, current location, flags, etc.

from .core import db
from .base import BaseModel
from sqlalchemy import Column, String, JSON, UniqueConstraint
from typing import Any, Dict, Optional, List

class GlobalVariable(BaseModel):
    """
    Global variables model - key-value storage using native JSON
    
    Stores simple game state like:
    - "in_dungeon" → true  
    - "current_location_name" → "Crystal Cavern"
    - "door_1" → {"id": "door_1", "type": "location", "name": "Dark Passage", "description": "..."}
    - "party_summary" → "Fluffy, Shadowpaw, and Ember"
    
    Features:
    - Native JSON storage with automatic type conversion
    - Database-level JSON validation  
    - No parsing errors - SQLAlchemy handles all conversion
    - Class methods for easy get/set operations
    """
    
    __tablename__ = 'global_variables'
    
    # === Core Fields ===
    key = Column(String(100), nullable=False)      # Variable name (e.g., "in_dungeon")
    value = Column(JSON, nullable=True)            # Variable value (native JSON)
    
    # === Constraints ===
    __table_args__ = (
        UniqueConstraint('key', name='unique_variable_key'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        result.update({
            'key': self.key,
            'value': self.value  # Already the correct Python type
        })
        
        return result
    
    @classmethod
    def get(cls, key: str, default: Any = None):
        """
        Get a variable value by key
        
        Args:
            key (str): Variable key
            default: Default value if key not found
            
        Returns:
            Any: Variable value (correct Python type) or default
        """
        variable = cls.query.filter_by(key=key).first()
        if not variable:
            return default
        
        return variable.value  # SQLAlchemy automatically converts JSON → Python
    
    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set a variable value by key (creates or updates)
        
        Args:
            key (str): Variable key
            value: Value to store (any JSON-serializable type)
            
        Returns:
            bool: True if successful
        """
        variable = cls.query.filter_by(key=key).first()
        
        if variable:
            # Update existing
            variable.value = value  # SQLAlchemy automatically converts Python → JSON
            return variable.save()
        else:
            # Create new
            variable = cls(key=key, value=value)
            return variable.save()
    
    @classmethod
    def delete_key(cls, key: str):
        """
        Delete a variable by key
        
        Args:
            key (str): Variable key to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        variable = cls.query.filter_by(key=key).first()
        if variable:
            return variable.delete()
        return False
    
    @classmethod
    def get_all(cls):
        """
        Get all variables as a dictionary
        
        Returns:
            dict: All variables as key-value pairs
        """
        variables = cls.query.all()
        return {var.key: var.value for var in variables}
    
    @classmethod
    def clear_all(cls):
        """Clear all variables (for testing/reset)"""
        cls.query.delete()
        db.session.commit()
    
    @classmethod
    def exists(cls, key: str):
        """
        Check if a key exists
        
        Args:
            key (str): Variable key to check
            
        Returns:
            bool: True if key exists
        """
        return cls.query.filter_by(key=key).first() is not None
    
    def __repr__(self):
        """String representation for debugging"""
        value_str = str(self.value)[:50] + '...' if len(str(self.value)) > 50 else str(self.value)
        return f"<GlobalVariable(id={self.id}, key='{self.key}', value={value_str})>"