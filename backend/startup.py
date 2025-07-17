# AI Systems Initialization - CLEANED UP
# Loads LLM model and initializes unified AI generation queue

import os
from backend.utils.console import print_section, print_success, print_error, print_warning, print_info

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

    # Initialize Game Queue
    with app.app_context():
        if _initialize_game_queue(app):
            print_success("Game orchestration queue ready")
        else:
            print_error("Game orchestration queue failed")
    
    # Check image generation capability
    _check_image_generation()

def _load_llm_model():
    """Load LLM model"""
    try:
        from backend.ai.llm.core import load_model, warm_up_model
        
        if load_model():
            warm_up_model()  # Quick warmup for consistent performance
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
    
def _initialize_game_queue(app):
    """Initialize unified AI queue with Flask context"""
    try:
        
        '''
        from backend.game.orchestration import get_game_orchestration_queue

        game_queue = get_game_orchestration_queue()
        game_queue.set_flask_app(app)

        print("attempting to view workflows... ")
        from backend.core.workflow_registry import list_workflows
        print(list_workflows())
        '''
        return True
    
    except Exception as e:
        print_error(f"Game queue initialization error: {e}")

def _check_image_generation():
    """Check image generation capability"""
    image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
    
    if not image_enabled:
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

def get_ai_status():
    """
    Get AI systems status for API endpoints
    
    Returns:
        dict: Current AI systems status
    """
    
    try:
        # LLM Status
        from backend.ai.llm.core import get_model_status
        llm_status = get_model_status()
        llm_ready = llm_status.get('loaded', False)
        
        # Queue Status
        from backend.ai.queue import get_ai_queue
        queue = get_ai_queue()
        queue_status = queue.get_queue_status()
        
        # Image Generation Status
        image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
        image_ready = False
        
        if image_enabled:
            try:
                from backend.ai.comfyui.client import ComfyUIClient
                client = ComfyUIClient()
                image_ready = client.is_server_running()
            except Exception:
                pass
        
        return {
            'llm_ready': llm_ready,
            'image_ready': image_ready,
            'gpu_enabled': llm_status.get('gpu_layers', 0) > 0,
            'queue_running': queue_status.get('worker_running', False),
            'queue_size': queue_status.get('queue_size', 0),
            'generation_types_supported': ['llm'] + (['image'] if image_ready else [])
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'llm_ready': False,
            'image_ready': False,
            'gpu_enabled': False
        }