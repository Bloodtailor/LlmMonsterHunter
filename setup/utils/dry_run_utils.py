# setup/dry_run_utils.py

from setup.utils.ux_utils import print_dry_run

DRY_RUN_SCENARIOS = {
    'check_nvidia_gpu': [
        (True, "NVIDIA GeForce RTX 3070"),
        (True, "NVIDIA GeForce GTX 1060 6GB"),
        (False, "nvidia-smi not found (NVIDIA drivers not installed)"),
        (False, "nvidia-smi failed (GPU or driver issues)")
    ],
    'check_nvidia_driver_version': [
        (True, "NVIDIA driver 535.98 (CUDA 12.x compatible)"),
        (False, "NVIDIA driver 472.84 is too old (need 530+ for CUDA 12.x)"),
        (False, "Could not parse NVIDIA driver version"),
        (False, "nvidia-smi not found (cannot check driver version)")
    ],
    'check_cuda_directories': [
        (True, "CUDA Toolkit found: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.2"),
        (False, "CUDA Toolkit directories not found"),
        (False, "Partial CUDA installation detected")
    ],
    'check_nvcc_compiler': [
        (True, "CUDA compiler (nvcc) available, version 12.2"),
        (False, "CUDA compiler (nvcc) not found in PATH"),
        (False, "CUDA compiler (nvcc) failed to run")
    ],
    'check_cuda_path_env': [
        (True, "CUDA_PATH environment variable: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.2"),
        (False, "CUDA_PATH environment variable not set or invalid")
    ],
    'check_gpu_compute_capability': [
        (True, "GPU compute capability 8.6 (excellent for AI)"),
        (True, "GPU compute capability 6.1 (good for AI)"),
        (False, "GPU compute capability 3.5 (limited AI support)"),
        (False, "Could not determine GPU compute capability")
    ],
    'check_visual_studio_installations': [
        (True, "Visual Studio 2022 found at C:\\Program Files\\Microsoft Visual Studio\\2022\\Community"),
        (True, "VS Build Tools 2022 found at C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools"),
        (True, "2 VS installations found (primary: Visual Studio 2022)"),
        (False, "No Visual Studio installations found in common directories")
    ],

    'check_windows_sdk': [
        (True, "Windows SDK found at C:\\Program Files (x86)\\Windows Kits\\10"),
        (True, "Windows SDK found at C:\\Program Files\\Windows Kits\\10"),
        (False, "Windows SDK not found in common directories")
    ],

    'check_cpp_build_tools': [
        (True, "C++ build tools found (MSVC 14.39.33519)"),
        (True, "C++ build tools found (MSVC 14.29.30133)"),
        (False, "C++ build tools not found in Visual Studio installations"),
        (False, "No Visual Studio installations to check for C++ tools")
    ],
    'check_llama_cpp_installed': [
        (True, "llama-cpp-python installed: 0.2.11"),
        (True, "llama-cpp-python installed: 0.2.20"),
        (False, "llama-cpp-python not installed"),
        (False, "Virtual environment pip not found")
    ],

    'test_llama_cpp_import': [
        (True, "llama-cpp-python imports successfully"),
        (False, "Import failed: No module named 'llama_cpp'"),
        (False, "llama-cpp-python not installed")
    ],

    'test_llama_cpp_performance': [
        (True, "52.3 tokens/sec (very fast - high-end GPU acceleration)"),
        (True, "28.7 tokens/sec (fast - good GPU acceleration)"),
        (True, "15.2 tokens/sec (decent - entry-level GPU acceleration)"),
        (False, "6.8 tokens/sec (slow - weak GPU or limited GPU offload)"),
        (False, "0.8 tokens/sec (very slow - CPU-only)"),
        (False, "Cannot test performance: Model file not found"),
    ],
    # Add this entry to the DRY_RUN_SCENARIOS dictionary in dry_run_utils.py:

    'check_env_model_path': [
        (True, "Model configured: llama-2-7b-chat.q4_K_M.gguf (3.8 GB)"),
        (False, "LLM_MODEL_PATH still set to placeholder value"),
        (False, "Model file not found: C:/AI/models/missing-model.gguf"),
        (False, ".env file not found or unreadable")
    ]
}

def set_dry_run(check_name):
    """Interactive dry run scenario selection"""

    fallback_choices = [(True, "Dry run error message not configured"), (False, "Dry run error message not configured")]
    scenarios = DRY_RUN_SCENARIOS.get(check_name, fallback_choices)
    
    print_dry_run(f"\nDry run options for: {check_name}")
    for i, (success, message) in enumerate(scenarios, 1):
        status = "✅" if success else "❌"
        print_dry_run(f"{i}. {status} {message}")
    
    while True:
        choice = input("Please enter your choice: ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(scenarios):
                selected = scenarios[index]
                print_dry_run(f"Selected: {'✅' if selected[0] else '❌'} {selected[1]}")
                return selected
            else:
                print_dry_run("Invalid choice, please try again.")
        except ValueError:
            print_dry_run("Please enter a number.")

def run_as_standalone_component(component_name, setup_function):
    print(f"🔧 Running {component_name} as a standalone component")
    print("You can perform a dry run to preview actions without making changes.\n")

    while True:
        choice = input("Would you like to run a dry run? [Y/n]: ").strip().lower()
        if choice in ["", "y", "yes"]:
            dry_run = True
            break
        elif choice in ["n", "no"]:
            dry_run = False
            break
        else:
            print("❌ Invalid input. Please enter 'y' or 'n'.\n")

    setup_function(dry_run=dry_run)
    input(f"\n{component_name} setup finished. Press Enter to exit...")