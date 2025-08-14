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
  Test database connection and print status
  Attempts to execute a simple query to verify connectivity
  """
  
  try:
    # Try to execute a simple query using modern SQLAlchemy 2.x syntax
    with db.engine.connect() as connection:
      result = connection.execute(text('SELECT 1 as test'))
      result.close()
      print('Database connection successful')
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
    from .base import BaseModel  # Base model class
    from .monster import Monster  # Monster model
    from .ability import Ability  # Ability model
    from .generation_log import GenerationLog  # Parent table
    from .llm_log import LLMLog              # LLM child table
    from .image_log import ImageLog          # Image child table
    from .game_state import GameState        # Main game state
    from .game_state_relations import (      # Relationship tables
      FollowingMonster,
      ActiveParty,
      DungeonState,
      DungeonDoor
    )
    from .game_workflow import GameWorkflow
    
    # Create all tables
    db.create_all()
    print('Database tables created')
    return True
      
  except SQLAlchemyError as e:
    print(f"❌ Failed to create tables: {str(e)}")
    return False
  except Exception as e:
    print(f"❌ Unexpected error creating tables: {str(e)}")
    return False