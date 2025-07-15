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
    'LLM Integration': check_llama_cpp_requirements,
    'Model Directory': check_model_directory_requirements,
}

def run_all_checks():
    """Run all component checks and return results"""
    
    print("Please wait for all checks to complete")
    print()

    results = {}
    for name, check_func in COMPONENT_CHECKS.items():
        print(f"🔍 Checking {name} requirements...")
        results[name] = check_func()
    return results


def check_component(component_name):
    """Run check for specific component"""
    return COMPONENT_CHECKS.get(component_name, lambda: False)()