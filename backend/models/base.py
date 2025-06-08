# SQLAlchemy Base Configuration
# Sets up the database connection and base model class
# All other models inherit from this base

from config.database import db
from datetime import datetime

class BaseModel(db.Model):
    """Base model class with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        # Implementation will include all fields except sensitive ones
        pass
    
    def save(self):
        """Save model to database"""
        # Implementation for saving with error handling
        pass
    
    def delete(self):
        """Delete model from database"""
        # Implementation for deletion with error handling
        pass
