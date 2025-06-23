# Flask Application Factory - UPDATED FOR UNIFIED GENERATION SYSTEM
# Creates and configures the main Flask application
# 🔧 UPDATED: Uses unified AI generation system for both LLM and image generation

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures Flask app with all necessary components
    
    Args:
        config_name (str): Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Create Flask app instance
    app = Flask(__name__)
    
    # Configure app from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database configuration
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')
    
    # Build database URI for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable event system (saves memory)
    
    # Enable CORS for React frontend (localhost:3000)
    CORS(app, origins=['http://localhost:3000'])
    
    # Initialize database with app
    from backend.config.database import init_db
    init_db(app)
    
    # 🔧 CRITICAL: Initialize unified backend systems (LLM model + unified AI queue)
    from backend.startup import initialize_backend
    initialize_backend(app)
    
    # Register API routes (blueprints)
    register_blueprints(app)
    
    return app

def check_database_connection():
    """
    Test database connection
    Returns True if database is accessible, False otherwise
    """
    try:
        from backend.config.database import db
        from sqlalchemy import text
        # Try a simple query to test connection using modern SQLAlchemy syntax
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            result.close()
        return True
    except Exception:
        return False

def register_blueprints(app):
    """
    Register all API route blueprints with the Flask app
    Updated for unified generation system
    """
    
    # 🔧 NEW: Register unified generation routes (replaces llm_routes.py)
    from backend.routes.generation_routes import generation_bp
    app.register_blueprint(generation_bp)
    
    # Register streaming routes blueprint (updated for unified system)
    from backend.routes.streaming_routes import streaming_bp
    app.register_blueprint(streaming_bp)
    
    # Register monster generation routes
    from backend.routes.monster_routes import monster_bp
    app.register_blueprint(monster_bp)

    # Register game tester routes
    from backend.routes.game_tester_routes import game_tester_bp
    app.register_blueprint(game_tester_bp)
    
    # Health check route - simple test endpoint
    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint to verify API is working"""
        return {
            'status': 'healthy',
            'message': 'Monster Hunter Game API is running',
            'database': 'connected' if check_database_connection() else 'disconnected',
            'generation_system': 'unified',  # 🔧 NEW: indicates unified LLM + image system
            'api_version': '2.0'  # 🔧 NEW: version with unified generation
        }
    
    # Enhanced game status route with unified generation system status
    @app.route('/api/game/status')
    def game_status():
        """Get comprehensive game status information with unified generation system"""
        
        # Get system status from startup module
        try:
            from backend.startup import get_system_status
            system_status = get_system_status()
        except Exception as e:
            system_status = {'error': str(e)}
        
        # Determine which generation types are available
        available_generation_types = system_status.get('generation_types_supported', ['llm'])
        llm_ready = system_status.get('startup_complete', False)
        image_ready = 'image' in available_generation_types
        
        return {
            'game_name': 'Monster Hunter Game',
            'version': '0.1.0-mvp',
            'status': 'development',
            'features': {
                'monster_generation': llm_ready,              # ✅ LLM-based monster creation
                'ability_generation': llm_ready,              # ✅ LLM-based ability creation
                'image_generation': image_ready,              # ✅ ComfyUI-based image generation
                'streaming_display': True,                    # ✅ Real-time streaming updates
                'unified_queue': True,                        # ✅ Single queue for all generation
                'gpu_acceleration': system_status.get('llm', {}).get('gpu_layers', 0) > 0,
                'battle_system': False,                       # 🔄 Future feature
                'chat_system': False,                         # 🔄 Future feature
                'save_system': True                           # ✅ Database persistence
            },
            'generation_system': {
                'type': 'unified',                            # 🔧 NEW: unified system
                'supported_types': available_generation_types,
                'queue_status': system_status.get('queue', {}).get('worker_running', False),
                'database_type': 'normalized',                # 🔧 NEW: generation_log + child tables
                'llm_model_loaded': system_status.get('llm', {}).get('loaded', False),
                'image_server_running': system_status.get('image_generation', {}).get('server_running', False)
            },
            'database': {
                'connected': check_database_connection(),
                'generation_logs': system_status.get('database', {}).get('total_logs', 0),
                'llm_generations': system_status.get('database', {}).get('llm_generations', 0),
                'image_generations': system_status.get('database', {}).get('image_generations', 0)
            },
            'system_status': system_status  # Full details for debugging
        }
    
    # 🔧 NEW: Unified generation test endpoint
    @app.route('/api/test/generation')
    def test_generation():
        """Test both LLM and image generation capabilities"""
        
        results = {
            'llm_test': 'not_tested',
            'image_test': 'not_tested',
            'overall_success': False
        }
        
        # Test LLM generation
        try:
            from backend.services import generation_service
            
            llm_result = generation_service.text_generation_request(
                prompt="Say 'LLM test successful'",
                wait_for_completion=True
            )
            
            results['llm_test'] = 'success' if llm_result['success'] else 'failed'
            results['llm_details'] = {
                'generation_id': llm_result.get('generation_id'),
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0)
            }
        except Exception as e:
            results['llm_test'] = 'error'
            results['llm_error'] = str(e)
        
        # Test image generation (if enabled)
        image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
        if image_enabled:
            try:
                from backend.services import generation_service
                
                image_result = generation_service.image_generation_request(
                    monster_description="Test dragon",
                    wait_for_completion=False  # Don't wait for actual generation
                )
                
                results['image_test'] = 'queued' if image_result['success'] else 'failed'
                results['image_details'] = {
                    'generation_id': image_result.get('generation_id'),
                    'message': image_result.get('message')
                }
            except Exception as e:
                results['image_test'] = 'error'
                results['image_error'] = str(e)
        else:
            results['image_test'] = 'disabled'
            results['image_message'] = 'Image generation disabled in configuration'
        
        # Overall success
        results['overall_success'] = (
            results['llm_test'] == 'success' and 
            results['image_test'] in ['success', 'queued', 'disabled']
        )
        
        return results