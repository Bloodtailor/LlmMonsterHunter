# Flask Application Factory - CLEANED UP
# Creates and configures the Flask application

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures Flask app with all necessary components
    
    Args:
        config_name (str): Configuration environment
    
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Load environment variables
    load_dotenv()
    
    # Create and configure Flask app
    app = Flask(__name__)
    _configure_app(app)
    
    # Enable CORS for React frontend
    CORS(app, origins=['http://localhost:3000'])
    
    # Initialize database
    from backend.config.database import init_db, create_tables
    init_db(app)
    
    # Register all models and create tables
    with app.app_context():
        create_tables()
    
    # Initialize AI systems
    from backend.startup import initialize_ai_systems
    initialize_ai_systems(app)
    
    # Register routes
    _register_routes(app)
    
    return app

def _configure_app(app):
    """Configure Flask app settings"""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database configuration
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'monster_hunter_game')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def _register_routes(app):
    """Register all API route blueprints"""
    
    # Register blueprints
    from backend.routes.generation_routes import generation_bp
    from backend.routes.streaming_routes import streaming_bp
    from backend.routes.monster_routes import monster_bp
    from backend.routes.game_tester_routes import game_tester_bp
    from backend.routes.game_state_routes import game_state_bp
    from backend.routes.dungeon_routes import dungeon_bp
    
    app.register_blueprint(generation_bp)
    app.register_blueprint(streaming_bp)
    app.register_blueprint(monster_bp)
    app.register_blueprint(game_tester_bp)
    app.register_blueprint(game_state_bp)
    app.register_blueprint(dungeon_bp)
    
    # Simple health check
    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint"""
        return {
            'status': 'healthy',
            'message': 'Monster Hunter Game API is running',
            'api_version': '2.0'
        }
    
    # Game status with AI system info
    @app.route('/api/game/status')
    def game_status():
        """Get comprehensive game status"""
        
        try:
            from backend.startup import get_ai_status
            ai_status = get_ai_status()
        except Exception as e:
            ai_status = {'error': str(e)}
        
        return {
            'game_name': 'Monster Hunter Game',
            'version': '0.1.0-mvp',
            'status': 'development',
            'features': {
                'monster_generation': ai_status.get('llm_ready', False),
                'ability_generation': ai_status.get('llm_ready', False),
                'image_generation': ai_status.get('image_ready', False),
                'streaming_display': True,
                'unified_queue': True,
                'gpu_acceleration': ai_status.get('gpu_enabled', False),
                'battle_system': False,
                'chat_system': False,
                'save_system': True
            },
            'ai_systems': ai_status
        }
    
    # Generation test endpoint
    @app.route('/api/test/generation')
    def test_generation():
        """Test AI generation capabilities"""
        
        from backend.services import generation_service
        
        results = {
            'llm_test': 'not_tested',
            'image_test': 'not_tested',
            'overall_success': False
        }
        
        # Test LLM
        try:
            llm_result = generation_service.text_generation_request(
                prompt="Say 'LLM test successful'",
                wait_for_completion=True
            )
            results['llm_test'] = 'success' if llm_result['success'] else 'failed'
        except Exception as e:
            results['llm_test'] = 'error'
            results['llm_error'] = str(e)
        
        # Test image generation (if enabled)
        image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
        if image_enabled:
            try:
                image_result = generation_service.image_generation_request(
                    prompt_text="A goblin",
                    wait_for_completion=False
                )
                results['image_test'] = 'queued' if image_result['success'] else 'failed'
            except Exception as e:
                results['image_test'] = 'error'
                results['image_error'] = str(e)
        else:
            results['image_test'] = 'disabled'
        
        results['overall_success'] = (
            results['llm_test'] == 'success' and 
            results['image_test'] in ['success', 'queued', 'disabled']
        )
        
        return results