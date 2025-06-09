# SQLAlchemy Base Model Configuration
# Sets up the database connection and base model class
# All other models inherit from this base for consistency

from config.database import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

class BaseModel(db.Model):
    """
    Base model class with common fields and methods
    All game models (Player, Monster, etc.) inherit from this
    
    Provides:
    - Standard ID, created_at, updated_at fields
    - Common save/delete methods
    - JSON serialization
    """
    
    # This tells SQLAlchemy this is an abstract base class
    # It won't create a table for BaseModel itself
    __abstract__ = True
    
    # Standard fields that every model should have
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        Convert model to dictionary for JSON serialization
        Excludes private attributes (starting with _) and methods
        
        Returns:
            dict: Model data as dictionary
        """
        result = {}
        
        # Get all columns from the SQLAlchemy model
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Convert datetime objects to ISO format strings
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result
    
    def save(self):
        """
        Save model to database
        Handles both new records (INSERT) and updates to existing records
        
        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            # Update the updated_at timestamp
            self.updated_at = datetime.utcnow()
            
            # Add to session and commit
            db.session.add(self)
            db.session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            # Roll back the session on error
            db.session.rollback()
            print(f"❌ Error saving {self.__class__.__name__}: {str(e)}")
            return False
        except Exception as e:
            # Roll back on any other error
            db.session.rollback()
            print(f"❌ Unexpected error saving {self.__class__.__name__}: {str(e)}")
            return False
    
    def delete(self):
        """
        Delete model from database
        
        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            db.session.delete(self)
            db.session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ Error deleting {self.__class__.__name__}: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"❌ Unexpected error deleting {self.__class__.__name__}: {str(e)}")
            return False
    
    def __repr__(self):
        """
        String representation of the model for debugging
        Shows class name and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"