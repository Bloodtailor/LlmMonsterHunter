# Database Configuration and Connection Management
# Sets up SQLAlchemy for MySQL database operations
# Handles connection pooling and session management

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

# Global SQLAlchemy instance
# This will be initialized in init_db() function
db = SQLAlchemy()

def init_db(app):
    """
    Initialize database with Flask application
    
    Args:
        app (Flask): Flask application instance
    """
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Test the database connection
    with app.app_context():
        test_connection()

def test_connection():
    """
    Test database connection and print status
    Attempts to execute a simple query to verify connectivity
    """
    
    try:
        # Try to execute a simple query using modern SQLAlchemy 2.x syntax
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1 as test'))
            result.close()
        print("✅ Database connection successful")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("💡 Check your .env file database configuration")
        return False
    except Exception as e:
        print(f"❌ Unexpected database error: {str(e)}")
        return False

def create_tables():
    """
    Create all database tables based on model definitions
    This will be called when we have models defined
    """
    
    try:
        # Import all models so they're registered with SQLAlchemy
        from models.base import BaseModel  # Base model class
        # Future imports will go here:
        # from models.player import Player
        # from models.monster import Monster
        # etc.
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating tables: {str(e)}")
        return False

def drop_tables():
    """
    Drop all database tables
    WARNING: This will delete all data! Only use for development/testing
    """
    
    try:
        db.drop_all()
        print("⚠️  All database tables dropped")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Failed to drop tables: {str(e)}")
        return False

def get_db_info():
    """
    Get basic database information for debugging
    
    Returns:
        dict: Database connection information
    """
    
    try:
        # Get database URL (without password for security)
        db_url = str(db.engine.url)
        # Remove password from URL for logging
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        
        return {
            'database_url': f"mysql://***:***@{safe_url}",
            'driver': db.engine.name,
            'connected': test_connection()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'connected': False
        }