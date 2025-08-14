# AI Systems Initialization - CLEANED UP
# Loads LLM model and initializes unified AI generation queue
import os
from backend.core.utils.console import print_section, print_success, print_error, print_warning, print_info

def initialize_database(app):
    """
    Initialize database with Flask application
    
    Args:
        app (Flask): Flask application instance
    """
    print_section('Initializing Database')
    
    from backend.models.core import init_db, test_connection, create_tables, get_table_names
    
    # Initialize SQLAlchemy with app
    init_db(app)

    with app.app_context():
        # Test database connection
        connection_success, connection_message = test_connection()
        if connection_success:
            print(connection_message)
        else:
            print(connection_message)
            print("Database connection failed - some features may not work")
            return False
        
        # Create database tables
        tables_success, tables_message = create_tables()
        if tables_success:
            print(tables_message)
            
            # Show table names for verification
            names_success, table_names = get_table_names()
            if names_success:
                print("Tables available:")
                for table_name in sorted(table_names):
                    print(f"    {table_name}")
            else:
                print(f"Could not retrieve table names: {table_names}")
        else:
            print(tables_message)
            return False
    
    return True

def initialize_ai_systems(app):
    """
    Initialize AI systems in the correct order
    Call this from create_app() to ensure everything is ready
    
    Args:
        app: Flask application instance
    """
    
    # Load LLM Model
    print_section('Initializing LLM Systems...')
    if _load_llm_model():
        print("LLM model loaded and ready")
    else:
        print_error("LLM model failed to load - text generation disabled")
    
    # Initialize AI Queue
    print_section('Initializing AI Systems...')
    with app.app_context():
        if _initialize_ai_queue(app):
            print("AI generation queue ready")
        else:
            print_error("AI queue initialization failed")

    # Check image generation capability
    print_section('Initializing Image Generation Systems...')
    _check_image_generation()

def initialize_workflows(app):
    """
    Initialize workflow system with Flask application
    
    Args:
        app (Flask): Flask application instance
    """
    print_section('Initializing Workflows')

    # Initialize Game Queue
    with app.app_context():
        try:
            from backend.workflow.workflow_queue import get_queue
            from backend.core.workflow_registry import list_workflows

            game_queue = get_queue()
            game_queue.set_flask_app(app)

            print('Game Orchestration Queue initialized')
            
            # List available workflows
            available_workflows = list_workflows()
            if available_workflows:
                print("Workflows available:")
                for workflow_name in available_workflows:
                    print(f"    {workflow_name}")
            else:
                print("No workflows registered")
        
        except Exception as e:
            print(f"Game queue initialization error: {e}")
            return False
    
    return True


def _load_llm_model():
    """Load LLM model"""
    try:
        from backend.ai.llm.core import load_model
        
        if load_model():
            return True
        return False
        
    except Exception as e:
        print_error(f"LLM initialization error: {e}")
        return False

def _initialize_ai_queue(app):
    """Initialize unified AI queue with Flask context"""
    try:
        from backend.ai.queue import get_ai_queue
        
        ai_queue = get_ai_queue()
        ai_queue.set_flask_app(app)
        return True
        
    except Exception as e:
        print_error(f"AI queue initialization error: {e}")
        return False


def _check_image_generation():
    """Check image generation capability"""
    from backend.core.config.comfyui_config import IMAGE_GENERATION_ENABLED
    
    if not IMAGE_GENERATION_ENABLED:
        print_info("Image generation disabled")
        print("Skipping image generation initialization")
        return True
    
    try:
        from backend.ai.comfyui.client import ComfyUIClient
        client = ComfyUIClient()
        
        if client.is_server_running():
            print("ComfyUI server connection successful")
            print("image generation ready")
            return True
        else:
            print_warning("ComfyUI server not running")
            print_info("Please start the ComfyUI server before running this startup")
            print_info("To play the game without it, disable image generation in the .env")
            return False

    except Exception as e:
        print_warning(f"Image generation check failed: {e}")
        return False
