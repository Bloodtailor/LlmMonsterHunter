# Database Configuration and Connection Management
# Sets up SQLAlchemy for MySQL database operations
# Handles connection pooling and session management

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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

def test_connection():
  """
  Test database connection and return status
  Attempts to execute a simple query to verify connectivity
  
  Returns:
      tuple: (success: bool, message: str)
  """
  
  try:
    # Try to execute a simple query using modern SQLAlchemy 2.x syntax
    with db.engine.connect() as connection:
      result = connection.execute(text('SELECT 1 as test'))
      result.close()
      return True, 'Database connection successful'
      
  except SQLAlchemyError as e:
    return False, f"Database connection failed: {str(e)}"
  except Exception as e:
    return False, f"Unexpected database error: {str(e)}"

def create_tables():
  """
  Create all database tables based on model definitions
  
  Returns:
      tuple: (success: bool, message: str)
  """

  try:
    # Import all models so they're registered with SQLAlchemy
    from .base import BaseModel  # Base model class
    from .monster import Monster  # Monster model
    from .ability import Ability  # Ability model
    from .generation_log import GenerationLog  # Parent table
    from .llm_log import LLMLog              # LLM child table
    from .image_log import ImageLog          # Image child table
    from .game_workflow import GameWorkflow
    
    # Create all tables
    db.create_all()
    return True, 'Database tables created successfully'
      
  except SQLAlchemyError as e:
    return False, f"Failed to create tables: {str(e)}"
  except Exception as e:
    return False, f"Unexpected error creating tables: {str(e)}"

def get_table_names():
  """
  Get names of all tables in the database
  
  Returns:
      tuple: (success: bool, data: list[str] or error_message: str)
  """
  
  try:
    # Use SQLAlchemy inspector to get table names
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    return True, table_names
      
  except SQLAlchemyError as e:
    return False, f"Failed to get table names: {str(e)}"
  except Exception as e:
    return False, f"Unexpected error getting table names: {str(e)}"