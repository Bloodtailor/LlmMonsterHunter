# Application Runner - CLEANED UP
# Simply creates and runs the Flask app

from backend.app import create_app
from backend.utils.console import print_header, print_startup_complete

def main():
    """Main function to start the Flask application"""
    
    print_header("Monster Hunter Game Backend")
    
    # Create and run Flask app
    app = create_app()
    
    print_startup_complete()
    print(f"   Server: http://localhost:5000")
    print(f"   Press Ctrl+C to stop")
    print()
    
    # Start the Flask development server
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        use_reloader=False
    )

if __name__ == '__main__':
    main()