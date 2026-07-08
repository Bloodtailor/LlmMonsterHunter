# AI Systems Initialization - CLEANED UP
# Loads LLM model and initializes unified AI generation queue
from backend.core.utils.console import print_error, print_info, print_section


def initialize_database(app):
    """
    Initialize database with Flask application

    Args:
        app (Flask): Flask application instance
    """
    print_section('Initializing Database')

    from backend.models.core import create_tables, get_table_names, init_db, test_connection

    # Initialize SQLAlchemy with app
    init_db(app)

    with app.app_context():
        # Test database connection
        connection_success, connection_message = test_connection()
        if connection_success:
            print(connection_message)
        else:
            print(connection_message)
            print("Database connection failed - some features may not work")
            return False

        # Create database tables
        tables_success, tables_message = create_tables()
        if tables_success:
            print(tables_message)

            # Show table names for verification
            names_success, table_names = get_table_names()
            if names_success:
                print("Tables available:")
                for table_name in sorted(table_names):
                    print(f"    {table_name}")
            else:
                print(f"Could not retrieve table names: {table_names}")
        else:
            print(tables_message)
            return False

    return True


def initialize_ai_systems(app):
    """
    Initialize AI systems in the correct order
    Call this from create_app() to ensure everything is ready

    Args:
        app: Flask application instance
    """

    # Load LLM Model - unless the settings panel picked a cloud provider
    # (read inside app context; initialize_database already ran, so the
    # game_settings table exists). Switching back to local mid-session
    # still works: inference self-loads on first use.
    print_section('Initializing LLM Systems...')
    with app.app_context():
        from backend.ai.llm.provider_settings import PROVIDER_LOCAL, resolve_llm_settings

        llm_settings = resolve_llm_settings()

    if llm_settings['provider'] != PROVIDER_LOCAL:
        print_info(
            f"Text provider is '{llm_settings['provider']}' "
            f"({llm_settings['model_name']}) - skipping local model load"
        )
    elif _load_llm_model():
        print("LLM model loaded and ready")
    else:
        print_error("LLM model failed to load - text generation disabled")

    # Initialize AI Queue
    print_section('Initializing AI Systems...')
    with app.app_context():
        if _initialize_ai_queue(app):
            print("AI generation queue ready")
        else:
            print_error("AI queue initialization failed")

    # Check image generation capability
    print_section('Initializing Image Generation Systems...')
    _check_image_generation(app)


def initialize_workflows(app):
    """
    Initialize workflow system with Flask application

    Args:
        app (Flask): Flask application instance
    """
    print_section('Initializing Workflows')

    # Initialize Game Queue
    with app.app_context():
        try:
            from backend.core.workflow_registry import list_workflows
            from backend.models.game_workflow import GameWorkflow
            from backend.workflow.workflow_queue import get_queue

            # The queue is in-memory: rows still pending/processing in
            # the table are strays from the last shutdown, not live work
            orphaned_count = GameWorkflow.close_dangling()
            if orphaned_count:
                print(f"Closed {orphaned_count} workflow row(s) orphaned by the last shutdown")

            game_queue = get_queue()
            game_queue.set_flask_app(app)

            print('Game Orchestration Queue initialized')

            # List available workflows
            available_workflows = list_workflows()
            if available_workflows:
                print("Workflows available:")
                for workflow_name in available_workflows:
                    print(f"    {workflow_name}")
            else:
                print("No workflows registered")

        except Exception as e:
            print(f"Game queue initialization error: {e}")
            return False

    return True


def _load_llm_model():
    """Load LLM model"""
    try:
        from backend.ai.llm.core import load_model

        return bool(load_model())

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


def _check_image_generation(app):
    """Report image generation state (panel-configured, resolved per call)"""
    from backend.ai.image.image_settings import resolve_image_settings
    from backend.ai.image.paths import outputs_root

    # One lazy housekeeping pass: pre-cloud installs keep their art
    outputs_root()

    with app.app_context():
        settings = resolve_image_settings()

    if settings['enabled']:
        print(f"Image generation ready (Gemini: {settings['model']})")
        return True

    print_info("Image generation not configured")
    print("Add a Gemini API key in Settings (gear icon) to enable card art")
    return True
