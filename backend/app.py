# Flask Application Factory
# Creates and configures the main Flask application
# 🔧 FIXED: Proper startup sequence with model auto-loading

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
    
    # 🔧 CRITICAL FIX: Initialize backend systems (load model, setup queue)
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
    This keeps routes organized and modular
    """
    
    # Register LLM routes blueprint
    from backend.routes.llm_routes import llm_bp
    app.register_blueprint(llm_bp)
    
    # Register streaming routes blueprint
    from backend.routes.streaming_routes import streaming_bp
    app.register_blueprint(streaming_bp)
    
    # 🔧 NEW: Monster generation routes
    from backend.routes.monster_routes import monster_bp
    app.register_blueprint(monster_bp)

    from backend.routes.game_tester_routes import game_tester_bp
    app.register_blueprint(game_tester_bp)
    
    # Health check route - simple test endpoint
    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint to verify API is working"""
        return {
            'status': 'healthy',
            'message': 'Monster Hunter Game API is running',
            'database': 'connected' if check_database_connection() else 'disconnected'
        }
    
    # Enhanced game status route with startup verification
    @app.route('/api/game/status')
    def game_status():
        """Get comprehensive game status information"""
        
        # Get system status from startup module
        try:
            from backend.startup import get_system_status
            system_status = get_system_status()
        except Exception as e:
            system_status = {'error': str(e)}
        
        return {
            'game_name': 'Monster Hunter Game',
            'version': '0.1.0-mvp',
            'status': 'development',
            'features': {
                'monster_generation': system_status.get('startup_complete', False),  # ✅ Based on actual model status
                'streaming_display': True,    # ✅ Real-time streaming
                'prompt_queue': True,         # ✅ Queue system
                'gpu_acceleration': system_status.get('llm', {}).get('gpu_layers', 0) > 0,     # ✅ Based on actual GPU usage
                'battle_system': False,
                'chat_system': False,
                'save_system': False
            },
            'system_status': system_status  # Full details for debugging
        }