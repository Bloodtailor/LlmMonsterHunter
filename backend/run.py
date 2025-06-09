# Application Runner
# Starts the Flask development server
# Entry point for running the Monster Hunter Game backend

from app import create_app
from config.database import create_tables, get_db_info
import os

def main():
    """
    Main function to start the Flask application
    """
    
    print("🎮 Starting Monster Hunter Game Backend...")
    print("=" * 50)
    
    # Create Flask app using application factory
    app = create_app()
    
    # Print configuration info
    print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    
    # Print database info
    db_info = get_db_info()
    print(f"🗄️  Database: {db_info.get('database_url', 'Not configured')}")
    
    if db_info.get('connected'):
        print("✅ Database connection verified")
        
        # Create tables if they don't exist
        with app.app_context():
            create_tables()
    else:
        print("❌ Database connection failed - check configuration")
        print("💡 The API will still start but database features won't work")
    
    # Print available endpoints
    print("\n📡 Available API endpoints:")
    print("   GET  /api/health      - Health check")
    print("   GET  /api/game/status - Game status")
    
    print(f"\n🚀 Starting server on http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask development server
    app.run(
        host='localhost',           # Only accept connections from localhost
        port=5000,                 # Standard Flask port
        debug=True,                # Enable debug mode for development
        use_reloader=True          # Auto-reload when files change
    )

if __name__ == '__main__':
    main()