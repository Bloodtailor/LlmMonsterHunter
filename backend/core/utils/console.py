# Console Output Utilities
# Centralized decorative console output for consistent formatting across the app

def print_header(title: str):
    """Print a major header with decorative box"""
    print()
    print("=" * 60)
    print(f"                {title}")
    print("=" * 60)
    print()

def print_section(title: str):
    """Print a section header"""
    print()
    print(f"📋 {title}")
    print()

def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print an error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print a warning message"""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")

def print_separator():
    """Print a visual separator"""
    print("-" * 50)

def print_config_item(label: str, value: str):
    """Print a configuration item"""
    print(f"   {label}: {value}")

def print_status_item(status: bool, message: str):
    """Print a status item with success/failure indicator"""
    icon = "✅" if status else "❌"
    print(f"   {icon} {message}")