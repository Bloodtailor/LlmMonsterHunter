"""
Checks Package
Pure detection/validation logic for all system components
"""

from .basic_backend_checks import check_basic_backend_requirements, get_basic_backend_diagnostic
from .nodejs_checks import check_nodejs_requirements, get_nodejs_diagnostic
from .mysql_checks import check_mysql_requirements, get_mysql_diagnostic
from .database_checks import check_database_requirements, get_database_diagnostic
from .gpu_cuda_checks import check_gpu_cuda_requirements, get_gpu_cuda_diagnostic
from .vs_checks import check_visual_studio_requirements, get_vs_diagnostic
from .llm_env_checks import check_model_directory_requirements, get_llm_env_diagnostic
from .llama_cpp_checks import check_llama_cpp_requirements, get_llama_cpp_diagnostic



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
COMPONENT_DIAGNOSTICS = {
        'Basic Backend': get_basic_backend_diagnostic,
        'Node.js & npm': get_nodejs_diagnostic,
        'MySQL Server': get_mysql_diagnostic,
        'Database Connection': get_database_diagnostic,
        'NVIDIA GPU & CUDA': get_gpu_cuda_diagnostic,
        'Visual Studio Build Tools': get_vs_diagnostic,
        'Model Directory': get_llm_env_diagnostic,
        'LLM Integration': get_llama_cpp_diagnostic,
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

def run_component_diagnostic(component_name):
    """Run diagnostic for a component and display results"""

    from setup.utils.ux_utils import show_component_status_table

    print(f"Running diagnostic of {component_name}...")
    diagnostic_info = COMPONENT_DIAGNOSTICS.get(component_name, lambda: False)()

    # Extract just the boolean results for the status table
    status_only = {name: result[0] for name, result in diagnostic_info.items()}
    
    show_component_status_table(component_name, status_only)
    

def run_all_full_diagnostics():
    """
    Run comprehensive diagnostic across all components and display results.
    Shows detailed breakdown of each component's sub-checks.
    """
    from setup.utils.ux_utils import display_check_results
    print("Running comprehensive system diagnostic...")
    print("This will check all components and their sub-requirements.")
    print()
    
    # Run diagnostics for each component
    for component_name, diagnostic_func in COMPONENT_DIAGNOSTICS:
        print(f"🔍 Diagnosing {component_name}...")
        
        # Get diagnostic info with overall check
        diagnostic_info = diagnostic_func(include_overall=True)
        
        display_check_results(component_name, diagnostic_info)
        
        print()
    
    print("Diagnostic complete!")
    print("Use the individual component setup flows to fix any issues.")
    print()