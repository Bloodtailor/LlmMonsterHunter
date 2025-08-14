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
    
    from backend.models.core import init_db, test_connection, create_tables
    init_db(app)

    with app.app_context():
        test_connection()
        create_tables()

def initialize_ai_systems(app):
    """
    Initialize AI systems in the correct order
    Call this from create_app() to ensure everything is ready
    
    Args:
        app: Flask application instance
    """
    
    print_section("Initializing AI Systems")
    
    # Load LLM Model
    if _load_llm_model():
        print_success("LLM model loaded and ready")
    else:
        print_error("LLM model failed to load - text generation disabled")
    
    # Initialize AI Queue
    with app.app_context():
        if _initialize_ai_queue(app):
            print_success("AI generation queue ready")
        else:
            print_error("AI queue initialization failed")
    
    # Check image generation capability
    _check_image_generation()
    
def initialize_workflows(app):

    print_section('Initializing Workflows')

    # Initialize Game Queue
    with app.app_context():
        try:
            from backend.workflow.workflow_queue import get_queue

            game_queue = get_queue()
            game_queue.set_flask_app(app)

            print_success('workflows initialized')
        
        except Exception as e:
            print_error(f"Game queue initialization error: {e}")


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
        return
    
    try:
        from backend.ai.comfyui.client import ComfyUIClient
        client = ComfyUIClient()
        
        if client.is_server_running():
            print_success("Image generation ready")
        else:
            print_warning("ComfyUI server not running - start with: python main.py --listen")
            
    except Exception as e:
        print_warning(f"Image generation check failed: {e}")
