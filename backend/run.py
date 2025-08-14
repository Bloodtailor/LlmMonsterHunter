# Application Runner - CLEANED UP
# Simply creates and runs the Flask app
from backend.app import create_app
from backend.core.utils.console import print_header

def main():
    """Main function to start the Flask application"""
    
    print_header("Monster Hunter Game Backend")
    
    # Create and run Flask app
    app = create_app()
    
    print_header("🚀 System ready - Backend is running!")

    # Start the Flask development server
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        use_reloader=False
    )

if __name__ == '__main__':
    main()