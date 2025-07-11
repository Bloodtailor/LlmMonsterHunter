"""
Flows Package
Interactive setup orchestration for all system components
"""

from .nodejs_flow import run_nodejs_interactive_setup

# Interactive flow registry for orchestration
COMPONENT_FLOWS = {
    'Node.js & npm': run_nodejs_interactive_setup,
}

def run_component_flow(component_name):
    """Run interactive setup flow for specific component"""
    flow_func = COMPONENT_FLOWS.get(component_name)
    if flow_func:
        return flow_func()
    else:
        print(f"No interactive setup available for {component_name}")
        return False