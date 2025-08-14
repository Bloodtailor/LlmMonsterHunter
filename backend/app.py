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
    from backend.startup import initialize_database
    initialize_database(app)
    
    # Initialize AI systems
    from backend.startup import initialize_ai_systems
    initialize_ai_systems(app)

    from backend.startup import initialize_workflows
    initialize_workflows(app)
    
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
    from backend.routes.sse_routes import sse_bp
    from backend.routes.monster_routes import monster_bp
    from backend.routes.game_tester_routes import game_tester_bp
    from backend.routes.game_state_routes import game_state_bp
    from backend.routes.dungeon_routes import dungeon_bp
    
    app.register_blueprint(generation_bp)
    app.register_blueprint(sse_bp)
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