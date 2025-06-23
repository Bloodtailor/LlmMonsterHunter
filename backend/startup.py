# Startup Module - Updated for AI folder structure
# Loads LLM model on startup and initializes unified AI generation queue
# Ensures everything is ready before accepting requests

import os
import time
from backend.ai.llm.core import load_model, warm_up_model, get_model_status
from backend.ai.queue import get_ai_queue  # 🔧 UPDATED: new queue location

def initialize_backend(app):
    """
    Initialize all backend systems in the correct order
    Call this from create_app() to ensure everything is ready
    
    Args:
        app: Flask application instance
    """
    
    print("🚀 Initializing Monster Hunter Game Backend...")
    print("=" * 60)
    
    # 1. Load LLM Model (CRITICAL - do this first)
    print("📋 Step 1: Loading LLM Model...")
    model_success = load_model()
    
    if not model_success:
        print("❌ CRITICAL: Failed to load LLM model!")
        print("   The backend will start but LLM features won't work")
        print("   Check your .env LLM_MODEL_PATH setting")
    else:
        print("✅ LLM Model loaded successfully")
        
        # Warm up the model for consistent performance
        print("🔥 Warming up model...")
        warmup_success = warm_up_model()
        if warmup_success:
            print("✅ Model warmed up and ready for generation")
        else:
            print("⚠️  Model warmup had issues - generation may be slower initially")
    
    # 2. Initialize Unified AI Queue System with Flask Context
    print("📋 Step 2: Initializing Unified AI Queue System...")
    with app.app_context():
        queue = get_ai_queue()  # 🔧 UPDATED: unified queue for both LLM and image
        queue.set_flask_app(app)  # CRITICAL for database operations
        print("✅ Unified AI generation queue initialized with Flask context")
        print("   Supports: LLM text generation + ComfyUI image generation")
    
    # 3. Verify Everything is Ready
    print("📋 Step 3: System Verification...")
    status = get_model_status()
    
    if status['loaded']:
        print(f"✅ Model Status: Loaded ({status.get('model_path', 'Unknown').split('/')[-1]})")
        print(f"✅ GPU Layers: {status.get('gpu_layers', 'Unknown')}")
        print(f"✅ Load Time: {status.get('load_duration', 'Unknown')}s")
    else:
        print("❌ Model Status: Not loaded")

    # 4. Check Image Generation Capability
    print("📋 Step 4: Checking Image Generation...")
    image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
    if image_enabled:
        print("✅ Image generation is ENABLED")
        try:
            from backend.ai.comfyui.client import ComfyUIClient
            client = ComfyUIClient()
            if client.is_server_running():
                print("✅ ComfyUI server is running and ready")
            else:
                print("⚠️  ComfyUI server not running - image generation will fail")
                print("   Start ComfyUI with: python main.py --listen")
        except ImportError:
            print("⚠️  ComfyUI components not available")
        except Exception as e:
            print(f"⚠️  ComfyUI check failed: {e}")
    else:
        print("ℹ️  Image generation is DISABLED (this is fine)")
        print("   Set ENABLE_IMAGE_GENERATION=true to enable")

def get_system_status():
    """
    Get comprehensive system status for debugging
    Updated for unified queue system
    
    Returns:
        dict: Complete system status
    """
    
    # LLM Status
    llm_status = get_model_status()
    
    # Unified Queue Status
    try:
        from backend.ai.queue import get_ai_queue
        queue = get_ai_queue()
        queue_status = queue.get_queue_status()
    except Exception as e:
        queue_status = {'error': str(e)}
    
    # Database Status
    try:
        from backend.models.generation_log import GenerationLog
        total_logs = GenerationLog.query.count()
        recent_logs = GenerationLog.query.order_by(GenerationLog.created_at.desc()).limit(5).count()
        
        # Get counts by generation type
        llm_count = GenerationLog.query.filter_by(generation_type='llm').count()
        image_count = GenerationLog.query.filter_by(generation_type='image').count()
        
        db_status = {
            'connected': True,
            'total_logs': total_logs,
            'recent_logs': recent_logs,
            'llm_generations': llm_count,
            'image_generations': image_count
        }
    except Exception as e:
        db_status = {'connected': False, 'error': str(e)}
    
    # Image Generation Status
    try:
        image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
        if image_enabled:
            from backend.ai.comfyui.client import ComfyUIClient
            client = ComfyUIClient()
            image_status = {
                'enabled': True,
                'server_running': client.is_server_running(),
                'available': client.is_server_running()
            }
        else:
            image_status = {
                'enabled': False,
                'server_running': False,
                'available': False
            }
    except Exception as e:
        image_status = {'enabled': image_enabled, 'error': str(e), 'available': False}
    
    return {
        'llm': llm_status,
        'queue': queue_status,
        'database': db_status,
        'image_generation': image_status,
        'startup_complete': llm_status.get('loaded', False),
        'generation_types_supported': ['llm'] + (['image'] if image_status.get('available') else [])
    }