# Startup Module - Handles backend initialization
# Loads LLM model on startup and keeps it loaded for entire session
# Ensures everything is ready before accepting requests

import os
import time
from backend.llm.core import load_model, warm_up_model, get_llm_status
from backend.llm.queue import get_llm_queue

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
    
    # 2. Initialize Queue System with Flask Context
    print("📋 Step 2: Initializing Queue System...")
    with app.app_context():
        queue = get_llm_queue()
        queue.set_flask_app(app)  # CRITICAL for database operations
        print("✅ Queue system initialized with Flask context")
    
    # 3. Verify Everything is Ready
    print("📋 Step 3: System Verification...")
    status = get_llm_status()
    
    if status['model_loaded']:
        print(f"✅ Model Status: Loaded ({status.get('model_path', 'Unknown').split('/')[-1]})")
        print(f"✅ GPU Layers: {status.get('gpu_layers', 'Unknown')}")
        print(f"✅ Load Time: {status.get('load_duration', 'Unknown')}s")
    else:
        print("❌ Model Status: Not loaded")
    
    if status['currently_generating']:
        print("🔄 Generation Status: Busy")
    else:
        print("✅ Generation Status: Ready")
    
    print("=" * 60)
    print("🎮 Backend initialization complete!")
    print("💡 Model will stay loaded for the entire session")
    print("🔗 All generation requests will be queued, logged, and streamed")
    print("=" * 60)

def get_system_status():
    """
    Get comprehensive system status for debugging
    
    Returns:
        dict: Complete system status
    """
    
    # LLM Status
    llm_status = get_llm_status()
    
    # Queue Status
    try:
        from backend.llm.queue import get_llm_queue
        queue = get_llm_queue()
        queue_status = queue.get_queue_status()
    except Exception as e:
        queue_status = {'error': str(e)}
    
    # Database Status
    try:
        from backend.models.llm_log import LLMLog
        total_logs = LLMLog.query.count()
        recent_logs = LLMLog.query.order_by(LLMLog.created_at.desc()).limit(5).count()
        db_status = {
            'connected': True,
            'total_logs': total_logs,
            'recent_logs': recent_logs
        }
    except Exception as e:
        db_status = {'connected': False, 'error': str(e)}
    
    return {
        'llm': llm_status,
        'queue': queue_status,
        'database': db_status,
        'startup_complete': llm_status.get('model_loaded', False)
    }