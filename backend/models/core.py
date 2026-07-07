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
        # Import all models so they're registered with SQLAlchemy - these
        # imports ARE the point (string-based relationships like
        # GenerationLog -> "LLMLog" resolve only after every class loads)
        from .ability import Ability  # noqa: F401
        from .base import BaseModel  # noqa: F401
        from .chat_message import ChatMessage  # noqa: F401
        from .chat_summary import ChatSummary  # noqa: F401
        from .chat_thread import ChatThread  # noqa: F401
        from .cocatok import CoCaTok  # noqa: F401
        from .dungeon_run import DungeonRun  # noqa: F401
        from .game_setting import GameSetting  # noqa: F401
        from .game_workflow import GameWorkflow  # noqa: F401
        from .generation_log import GenerationLog  # noqa: F401
        from .image_log import ImageLog  # noqa: F401
        from .item import Item  # noqa: F401
        from .llm_log import LLMLog  # noqa: F401
        from .monster import Monster  # noqa: F401
        from .monster_evolution import MonsterEvolution  # noqa: F401
        from .monster_memory import MonsterMemory  # noqa: F401

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
