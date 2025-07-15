"""
Checks Package
Pure detection/validation logic for all system components
"""

from .basic_backend_checks import check_basic_backend_requirements
from .nodejs_checks import check_nodejs_requirements
from .mysql_checks import check_mysql_requirements
from .database_checks import check_database_requirements
from .gpu_cuda_checks import check_gpu_cuda_requirements
from .vs_checks import check_visual_studio_requirements
from .llama_cpp_checks import check_llama_cpp_requirements
from .llm_env_checks import check_model_directory_requirements

# Component-level checks registry for orchestration
COMPONENT_CHECKS = {
    'Basic Backend': check_basic_backend_requirements,
    'Node.js & npm': check_nodejs_requirements,
    'MySQL Server': check_mysql_requirements,
    'Database Connection': check_database_requirements,
    'NVIDIA GPU & CUDA': check_gpu_cuda_requirements,
    'Visual Studio Build Tools': check_visual_studio_requirements,
    'Model Directory': check_model_directory_requirements,
    'LLM Integration': check_llama_cpp_requirements,
}

def run_all_checks():
    """Run all component checks and return results"""
    
    print("Please wait for all checks to complete")
    print()

    results = {}
    for name, check_func in COMPONENT_CHECKS.items():
        print(f"Checking {name} requirements...")
        results[name] = check_func()
    return results


def check_component(component_name):
    """Run check for specific component"""
    return COMPONENT_CHECKS.get(component_name, lambda: False)()

def run_full_diagnostic():
    """
    Run comprehensive diagnostic across all components and display results.
    Shows detailed breakdown of each component's sub-checks.
    """
    from setup.utils.ux_utils import display_check_results
    
    # Import all diagnostic functions
    from setup.checks.basic_backend_checks import get_diagnostic_info as get_basic_backend_diagnostic
    from setup.checks.nodejs_checks import get_diagnostic_info as get_nodejs_diagnostic
    from setup.checks.mysql_checks import get_diagnostic_info as get_mysql_diagnostic
    from setup.checks.database_checks import get_diagnostic_info as get_database_diagnostic
    from setup.checks.gpu_cuda_checks import get_diagnostic_info as get_gpu_cuda_diagnostic
    from setup.checks.vs_checks import get_diagnostic_info as get_vs_diagnostic
    from setup.checks.llama_cpp_checks import get_diagnostic_info as get_llama_cpp_diagnostic
    from setup.checks.llm_env_checks import get_diagnostic_info as get_llm_env_diagnostic
    
    print("Running comprehensive system diagnostic...")
    print("This will check all components and their sub-requirements.")
    print()
    
    # Define component diagnostics
    component_diagnostics = [
        ("Basic Backend", get_basic_backend_diagnostic),
        ("Node.js & npm", get_nodejs_diagnostic),
        ("MySQL Server", get_mysql_diagnostic),
        ("Database Connection", get_database_diagnostic),
        ("NVIDIA GPU & CUDA", get_gpu_cuda_diagnostic),
        ("Visual Studio Build Tools", get_vs_diagnostic),
        ("Model Directory", get_llm_env_diagnostic),
        ("LLM Integration", get_llama_cpp_diagnostic),
    ]
    
    # Run diagnostics for each component
    for component_name, diagnostic_func in component_diagnostics:
        print(f"🔍 Diagnosing {component_name}...")
        
        # Get diagnostic info with overall check
        diagnostic_info = diagnostic_func(include_overall=True)
        
        display_check_results(component_name, diagnostic_info)
        
        print()
    
    print("Diagnostic complete!")
    print("Use the individual component setup flows to fix any issues.")
    print()