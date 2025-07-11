"""
Checks Package
Pure detection/validation logic for all system components
"""

from .nodejs_checks import check_nodejs_requirements

# Component-level checks registry for orchestration
COMPONENT_CHECKS = {
    'Node.js & npm': check_nodejs_requirements,
}

def run_all_checks():
    """Run all component checks and return results"""
    return {name: check_func() for name, check_func in COMPONENT_CHECKS.items()}

def check_component(component_name):
    """Run check for specific component"""
    return COMPONENT_CHECKS.get(component_name, lambda: False)()