"""
Flows Package
Interactive setup orchestration for all system components
"""

from .basic_backend_flow import run_basic_backend_interactive_setup
from .database_flow import run_database_interactive_setup
from .gpu_cuda_flow import run_gpu_cuda_interactive_setup
from .llama_cpp_flow import run_llama_cpp_interactive_setup
from .llm_env_flow import run_llm_env_interactive_setup
from .mysql_flow import run_mysql_interactive_setup
from .nodejs_flow import run_nodejs_interactive_setup
from .vs_flow import run_visual_studio_interactive_setup

# Interactive flow registry for orchestration
COMPONENT_FLOWS = {
    'Basic Backend': run_basic_backend_interactive_setup,
    'Node.js & npm': run_nodejs_interactive_setup,
    'MySQL Server': run_mysql_interactive_setup,
    'Database Connection': run_database_interactive_setup,
    'NVIDIA GPU & CUDA': run_gpu_cuda_interactive_setup,
    'Visual Studio Build Tools': run_visual_studio_interactive_setup,
    'Model Directory': run_llm_env_interactive_setup,
    'LLM Integration': run_llama_cpp_interactive_setup,
}

# The API-first game needs NONE of these: they serve the unsupported
# local-LLM escape hatch (docs/plans/cloud-generation.md), so the
# orchestrator gates the whole chain behind one opt-in question.
LOCAL_EXTRA_COMPONENTS = (
    'NVIDIA GPU & CUDA',
    'Visual Studio Build Tools',
    'Model Directory',
    'LLM Integration',
)


def run_component_flow(component_name):
    """Run interactive setup flow for specific component"""
    flow_func = COMPONENT_FLOWS.get(component_name)
    if flow_func:
        return flow_func()
    else:
        print(f"No interactive setup available for {component_name}")
        return False
